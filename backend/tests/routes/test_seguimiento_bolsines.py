from datetime import datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload
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
from utils.auth import get_usuario_dev

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
        ubicaciones={
            101: _ubicacion(101, -31.4201, -64.1888),
            110: _ubicacion(110, -31.4167, -64.1833),
        },
        sin_ubicacion={111},
    )
    correo = CorreoFake()
    monkeypatch.setattr(composicion, "crear_gps", lambda: gps)
    monkeypatch.setattr(composicion, "crear_correo", lambda: correo)
    registro_casos_uso.reset()

    async def cargar(mail: str) -> Usuario:
        stmt = (
            select(Usuario)
            .where(Usuario.mail == mail)
            .options(
                selectinload(Usuario.empleado).selectinload(Empleado.rol),
                selectinload(Usuario.empleado).selectinload(Empleado.comisionMedica),
            )
        )
        usuario = (await session.exec(stmt)).first()
        assert usuario is not None
        return usuario

    with TestClient(app) as client:
        yield client, cargar, correo

    app.dependency_overrides.clear()
    registro_casos_uso.reset()
    await session.close()
    await engine.dispose()


async def _usar(cargar, mail: str) -> None:
    usuario = await cargar(mail)
    app.dependency_overrides[get_usuario_dev] = lambda: usuario


def _auth_codigo(respuesta) -> str:
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"codigo", "mensaje"}
    return cuerpo["codigo"]


@pytest.mark.asyncio
async def test_flujo_principal(entorno) -> None:
    client, cargar, correo = entorno
    await _usar(cargar, "eb.cba02@example.test")

    creado = client.post("/seguimiento-bolsines")
    assert creado.status_code == 201
    cuerpo = creado.json()
    assert [b["numeroBolsin"] for b in cuerpo["bolsines"]] == [110]
    assert [m["numeroBolsin"] for m in cuerpo["mapa"]["marcadores"]] == [110]

    seleccion = client.post(
        f"/seguimiento-bolsines/{cuerpo['idCU']}/seleccion",
        json={"numeroBolsin": 110},
    )
    assert seleccion.status_code == 200

    confirmacion = client.post(
        f"/seguimiento-bolsines/{cuerpo['idCU']}/confirmacion-correo",
        json={"confirma": True},
    )
    assert confirmacion.status_code == 200
    assert confirmacion.json()["notificado"] is True
    assert correo.enviados[0]["destinatario"] == "gcm.ros@example.test"


@pytest.mark.asyncio
async def test_a1_sin_bolsines_da_404(entorno) -> None:
    client, cargar, _ = entorno
    await _usar(cargar, "eb.tuc01@example.test")
    respuesta = client.post("/seguimiento-bolsines")
    assert respuesta.status_code == 404
    assert _auth_codigo(respuesta) == "SIN_BOLSINES_ENVIADOS"


@pytest.mark.asyncio
async def test_a3_gps_sin_ubicacion(entorno) -> None:
    client, cargar, _ = entorno
    await _usar(cargar, "eb.cba01@example.test")
    respuesta = client.post("/seguimiento-bolsines")
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert [s["numeroBolsin"] for s in cuerpo["sinUbicacion"]] == [111]
    assert [m["numeroBolsin"] for m in cuerpo["mapa"]["marcadores"]] == [101]


@pytest.mark.asyncio
async def test_gps_api_key_invalida_da_502(entorno, monkeypatch) -> None:
    """Sin GPS_API_KEY la API de la catedra responde 401: antes daba 500."""
    import httpx

    from integrations.gps_tracker.gps_tracker_xtr4500l import GpsTrackerXtr4500l

    def responder(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-API-Key"] == ""
        return httpx.Response(401, json={"error": "API_KEY_INVALIDA"})

    cliente = httpx.AsyncClient(transport=httpx.MockTransport(responder))
    gps = GpsTrackerXtr4500l("http://gps.test", "", cliente)
    monkeypatch.setattr(composicion, "crear_gps", lambda: gps)

    client, cargar, _ = entorno
    await _usar(cargar, "eb.cba02@example.test")
    respuesta = client.post("/seguimiento-bolsines")
    assert respuesta.status_code == 502
    assert _auth_codigo(respuesta) == "GPS_NO_DISPONIBLE"


@pytest.mark.asyncio
async def test_a4_cancelar(entorno) -> None:
    client, cargar, _ = entorno
    await _usar(cargar, "eb.cba02@example.test")
    creado = client.post("/seguimiento-bolsines").json()
    assert client.delete(f"/seguimiento-bolsines/{creado['idCU']}").status_code == 204
    segunda = client.delete(f"/seguimiento-bolsines/{creado['idCU']}")
    assert segunda.status_code == 404
    assert _auth_codigo(segunda) == "CASO_USO_NO_ENCONTRADO"


@pytest.mark.asyncio
async def test_a5_no_confirma(entorno) -> None:
    client, cargar, correo = entorno
    await _usar(cargar, "eb.cba02@example.test")
    creado = client.post("/seguimiento-bolsines").json()
    client.post(
        f"/seguimiento-bolsines/{creado['idCU']}/seleccion",
        json={"numeroBolsin": 110},
    )
    respuesta = client.post(
        f"/seguimiento-bolsines/{creado['idCU']}/confirmacion-correo",
        json={"confirma": False},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["notificado"] is False
    assert correo.enviados == []


@pytest.mark.asyncio
async def test_rol_insuficiente_da_403(entorno) -> None:
    client, cargar, _ = entorno
    await _usar(cargar, "gcm.ros@example.test")
    respuesta = client.post("/seguimiento-bolsines")
    assert respuesta.status_code == 403
    assert _auth_codigo(respuesta) == "ROL_INSUFICIENTE"


@pytest.mark.asyncio
async def test_validacion_da_422(entorno) -> None:
    client, cargar, _ = entorno
    await _usar(cargar, "eb.cba02@example.test")
    creado = client.post("/seguimiento-bolsines").json()
    respuesta = client.post(
        f"/seguimiento-bolsines/{creado['idCU']}/seleccion",
        json={"numeroBolsin": 0},
    )
    assert respuesta.status_code == 422
    assert _auth_codigo(respuesta) == "SOLICITUD_INVALIDA"


@pytest.mark.asyncio
async def test_idcu_inexistente_da_404(entorno) -> None:
    client, cargar, _ = entorno
    await _usar(cargar, "eb.cba02@example.test")
    respuesta = client.post(
        f"/seguimiento-bolsines/{uuid4()}/seleccion",
        json={"numeroBolsin": 110},
    )
    assert respuesta.status_code == 404
    assert _auth_codigo(respuesta) == "CASO_USO_NO_ENCONTRADO"


@pytest.mark.asyncio
async def test_me_devuelve_empleado(entorno) -> None:
    client, cargar, _ = entorno
    await _usar(cargar, "eb.cba01@example.test")
    respuesta = client.get("/auth/me")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["mail"] == "eb.cba01@example.test"
    assert cuerpo["rol"] == NOMBRE_ENCARGADO_BOLSINES
    assert cuerpo["codigoCM"] == "CM-CBA-01"
