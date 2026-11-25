from datetime import datetime, timedelta
from uuid import uuid4

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from config import composicion
from config.database import get_db
from index import app
from integrations.correo.correo_fake import CorreoFake
from integrations.gps_tracker.gps_tracker_fake import GpsTrackerFake
from models import (
    Bolsin,
    CambioEstado,
    ComisionMedica,
    Empleado,
    Estado,
    Rol,
    Usuario,
)
from models.rol import NOMBRE_ENCARGADO_BOLSINES, NOMBRE_GCM
from models.ubicacion_bolsin import UbicacionBolsin
from services import registro_casos_uso
from utils.security import create_access_token

INICIO = datetime(2026, 11, 20, 9, 0)


async def _poblar(session: AsyncSession) -> None:
    rol_eb = Rol(nombre=NOMBRE_ENCARGADO_BOLSINES)
    rol_gcm = Rol(nombre=NOMBRE_GCM)
    estados = {
        nombre: Estado(nombre=nombre, descripcion=nombre)
        for nombre in ("Creado", "Cerrado", "Enviado", "Recibido")
    }
    cms = {
        codigo: ComisionMedica(codigo=codigo, nombre=codigo)
        for codigo in (
            "CM-CBA-01",
            "CM-CBA-02",
            "CM-ROS-02",
            "CM-MDZ-03",
            "CM-TUC-01",
        )
    }
    session.add_all([rol_eb, rol_gcm, *estados.values(), *cms.values()])
    await session.commit()
    for obj in (rol_eb, rol_gcm, *estados.values(), *cms.values()):
        await session.refresh(obj)

    async def empleado(mail: str, rol: Rol, codigo_cm: str) -> None:
        usuario = Usuario(mail=mail, hashedPassword="x")
        session.add(usuario)
        await session.commit()
        await session.refresh(usuario)
        session.add(
            Empleado(
                nombre="N",
                apellido="A",
                idUser=usuario.id,
                rolId=rol.id,
                comisionMedicaId=cms[codigo_cm].id,
                usuario=usuario,
            )
        )
        await session.commit()

    await empleado("eb.cba01@example.test", rol_eb, "CM-CBA-01")
    await empleado("eb.cba02@example.test", rol_eb, "CM-CBA-02")
    await empleado("eb.tuc01@example.test", rol_eb, "CM-TUC-01")
    await empleado("gcm.ros@example.test", rol_gcm, "CM-ROS-02")

    async def bolsin(numero: int, origen: str, destino: str) -> None:
        registro = Bolsin(
            numeroBolsin=numero,
            fecha=INICIO,
            numeroPrecinto=f"P-0{numero}",
            peso=1000,
            cmOrigenId=cms[origen].id,
            cmDestinoId=cms[destino].id,
        )
        session.add(registro)
        await session.commit()
        await session.refresh(registro)
        momento = INICIO
        for indice, nombre in enumerate(("Creado", "Cerrado", "Enviado")):
            fin = momento + timedelta(hours=1) if indice < 2 else None
            session.add(
                CambioEstado(
                    fechaHoraInicio=momento,
                    fechaHoraFin=fin,
                    bolsinId=registro.id,
                    estadoId=estados[nombre].id,
                    estado=estados[nombre],
                )
            )
            if fin is not None:
                momento = fin
        await session.commit()

    await bolsin(101, "CM-CBA-01", "CM-ROS-02")
    await bolsin(110, "CM-CBA-02", "CM-ROS-02")
    await bolsin(111, "CM-CBA-01", "CM-MDZ-03")


def _ubicacion(numero: int, lat: float, lon: float) -> UbicacionBolsin:
    return UbicacionBolsin(
        numeroBolsin=numero,
        latitud=lat,
        longitud=lon,
        fechaHoraUltimaActualizacion=datetime(2026, 3, 7, 12, 30),
    )


@pytest_asyncio.fixture
async def entorno(monkeypatch):
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = maker()
    await _poblar(session)

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    gps = GpsTrackerFake(
        ubicaciones={101: _ubicacion(101, -31.4201, -64.1888), 110: _ubicacion(110, -31.4167, -64.1833)},
        sin_ubicacion={111},
    )
    correo = CorreoFake()
    monkeypatch.setattr(composicion, "crear_gps", lambda: gps)
    monkeypatch.setattr(composicion, "crear_correo", lambda: correo)
    registro_casos_uso.reset()

    tokens = {}
    for mail in ("eb.cba01", "eb.cba02", "eb.tuc01", "gcm.ros"):
        stmt = select(Usuario).where(Usuario.mail == f"{mail}@example.test")
        usuario = (await session.exec(stmt)).first()
        tokens[mail] = create_access_token(usuario.id)

    with TestClient(app) as client:
        yield client, tokens, correo

    app.dependency_overrides.clear()
    registro_casos_uso.reset()
    await session.close()
    await engine.dispose()


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_post_sin_token(entorno) -> None:
    client, _, _ = entorno
    assert client.post("/seguimiento-bolsines").status_code == 401


def test_post_con_rol_gcm_da_403(entorno) -> None:
    client, tokens, _ = entorno
    respuesta = client.post(
        "/seguimiento-bolsines", headers=_auth(tokens["gcm.ros"])
    )
    assert respuesta.status_code == 403


def test_flujo_principal(entorno) -> None:
    client, tokens, correo = entorno
    respuesta = client.post(
        "/seguimiento-bolsines", headers=_auth(tokens["eb.cba02"])
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert [b["numeroBolsin"] for b in cuerpo["bolsines"]] == [110]
    assert [m["numeroBolsin"] for m in cuerpo["mapa"]["marcadores"]] == [110]

    seleccion = client.post(
        f"/seguimiento-bolsines/{cuerpo['idCU']}/seleccion",
        json={"numeroBolsin": 110},
        headers=_auth(tokens["eb.cba02"]),
    )
    assert seleccion.status_code == 200
    assert seleccion.json()["requiereConfirmacionCorreo"] is True

    confirmacion = client.post(
        f"/seguimiento-bolsines/{cuerpo['idCU']}/confirmacion-correo",
        json={"confirma": True},
        headers=_auth(tokens["eb.cba02"]),
    )
    assert confirmacion.status_code == 200
    assert confirmacion.json()["notificado"] is True
    assert correo.enviados[0]["destinatario"] == "gcm.ros@example.test"


def test_a1_sin_bolsines(entorno) -> None:
    client, tokens, _ = entorno
    respuesta = client.post(
        "/seguimiento-bolsines", headers=_auth(tokens["eb.tuc01"])
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "SIN_BOLSINES"
    assert respuesta.json()["idCU"] is None


def test_a3_gps_sin_ubicacion(entorno) -> None:
    client, tokens, _ = entorno
    respuesta = client.post(
        "/seguimiento-bolsines", headers=_auth(tokens["eb.cba01"])
    )
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert [s["numeroBolsin"] for s in cuerpo["sinUbicacion"]] == [111]
    assert [m["numeroBolsin"] for m in cuerpo["mapa"]["marcadores"]] == [101]


def test_a5_no_confirma(entorno) -> None:
    client, tokens, correo = entorno
    creado = client.post(
        "/seguimiento-bolsines", headers=_auth(tokens["eb.cba02"])
    ).json()
    client.post(
        f"/seguimiento-bolsines/{creado['idCU']}/seleccion",
        json={"numeroBolsin": 110},
        headers=_auth(tokens["eb.cba02"]),
    )
    respuesta = client.post(
        f"/seguimiento-bolsines/{creado['idCU']}/confirmacion-correo",
        json={"confirma": False},
        headers=_auth(tokens["eb.cba02"]),
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["notificado"] is False
    assert correo.enviados == []


def test_seleccion_invalida_da_422(entorno) -> None:
    client, tokens, _ = entorno
    creado = client.post(
        "/seguimiento-bolsines", headers=_auth(tokens["eb.cba02"])
    ).json()
    respuesta = client.post(
        f"/seguimiento-bolsines/{creado['idCU']}/seleccion",
        json={"numeroBolsin": 0},
        headers=_auth(tokens["eb.cba02"]),
    )
    assert respuesta.status_code == 422


def test_idcu_inexistente_da_404(entorno) -> None:
    client, tokens, _ = entorno
    respuesta = client.post(
        f"/seguimiento-bolsines/{uuid4()}/seleccion",
        json={"numeroBolsin": 110},
        headers=_auth(tokens["eb.cba02"]),
    )
    assert respuesta.status_code == 404


def test_delete_y_404_posterior(entorno) -> None:
    client, tokens, _ = entorno
    creado = client.post(
        "/seguimiento-bolsines", headers=_auth(tokens["eb.cba02"])
    ).json()
    assert (
        client.delete(
            f"/seguimiento-bolsines/{creado['idCU']}",
            headers=_auth(tokens["eb.cba02"]),
        ).status_code
        == 204
    )
    assert (
        client.delete(
            f"/seguimiento-bolsines/{creado['idCU']}",
            headers=_auth(tokens["eb.cba02"]),
        ).status_code
        == 404
    )


def test_health(entorno) -> None:
    client, _, _ = entorno
    assert client.get("/health").status_code == 200
