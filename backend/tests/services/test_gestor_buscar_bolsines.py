from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from integrations.correo.correo_fake import CorreoFake
from integrations.google_maps.google_maps_adapter import GoogleMapsAdapter
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
from services.errores import SinBolsinesEnviadosError
from services.gestor_buscar_bolsines import GestorBuscarBolsines

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
            "CM-BA-01",
            "CM-TUC-01",
        )
    }
    session.add_all([rol_eb, rol_gcm, *estados.values(), *cms.values()])
    await session.commit()
    for obj in (rol_eb, rol_gcm, *estados.values(), *cms.values()):
        await session.refresh(obj)

    async def crear_empleado(mail: str, rol: Rol, codigo_cm: str) -> None:
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

    await crear_empleado("eb.cba01@example.test", rol_eb, "CM-CBA-01")
    await crear_empleado("eb.cba02@example.test", rol_eb, "CM-CBA-02")
    await crear_empleado("eb.tuc01@example.test", rol_eb, "CM-TUC-01")
    await crear_empleado("gcm.ros@example.test", rol_gcm, "CM-ROS-02")
    await crear_empleado("gcm.mdz@example.test", rol_gcm, "CM-MDZ-03")

    async def crear_bolsin(
        numero: int, origen: str, destino: str, cadena: tuple[str, ...]
    ) -> None:
        bolsin = Bolsin(
            numeroBolsin=numero,
            fecha=INICIO,
            numeroPrecinto=f"P-0{numero}",
            peso=1000,
            cmOrigenId=cms[origen].id,
            cmDestinoId=cms[destino].id,
        )
        session.add(bolsin)
        await session.commit()
        await session.refresh(bolsin)
        momento = INICIO
        for indice, nombre in enumerate(cadena):
            fin = momento + timedelta(hours=1) if indice < len(cadena) - 1 else None
            session.add(
                CambioEstado(
                    fechaHoraInicio=momento,
                    fechaHoraFin=fin,
                    bolsinId=bolsin.id,
                    estadoId=estados[nombre].id,
                    estado=estados[nombre],
                )
            )
            if fin is not None:
                momento = fin
        await session.commit()

    await crear_bolsin(101, "CM-CBA-01", "CM-ROS-02", ("Creado", "Cerrado", "Enviado"))
    await crear_bolsin(110, "CM-CBA-02", "CM-ROS-02", ("Creado", "Cerrado", "Enviado"))
    await crear_bolsin(111, "CM-CBA-01", "CM-MDZ-03", ("Creado", "Cerrado", "Enviado"))
    await crear_bolsin(113, "CM-CBA-01", "CM-ROS-02", ("Creado",))
    await crear_bolsin(114, "CM-CBA-01", "CM-BA-01", ("Creado", "Cerrado"))
    await crear_bolsin(
        115, "CM-CBA-01", "CM-MDZ-03", ("Creado", "Cerrado", "Enviado", "Recibido")
    )
    await crear_bolsin(102, "CM-ROS-02", "CM-MDZ-03", ("Creado", "Cerrado", "Enviado"))


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as db:
        await _poblar(db)
        yield db
    await engine.dispose()


async def _usuario(session: AsyncSession, mail: str) -> Usuario:
    stmt = (
        select(Usuario)
        .where(Usuario.mail == mail)
        .options(
            selectinload(Usuario.empleado).selectinload(Empleado.comisionMedica),
            selectinload(Usuario.empleado).selectinload(Empleado.rol),
        )
    )
    usuario = (await session.exec(stmt)).first()
    assert usuario is not None
    return usuario


def _ubicacion(numero: int, lat: float, lon: float) -> UbicacionBolsin:
    return UbicacionBolsin(
        numeroBolsin=numero,
        latitud=lat,
        longitud=lon,
        fechaHoraUltimaActualizacion=datetime(2026, 3, 7, 12, 30),
    )


def _gestor(session, usuario, gps, correo):
    return GestorBuscarBolsines(
        session, usuario, gps, GoogleMapsAdapter(), correo
    )


@pytest.mark.asyncio
async def test_flujo_principal(session: AsyncSession) -> None:
    gps = GpsTrackerFake(ubicaciones={110: _ubicacion(110, -31.4167, -64.1833)})
    correo = CorreoFake()
    gestor = _gestor(session, await _usuario(session, "eb.cba02@example.test"), gps, correo)

    await gestor.opcionSeguirBolsines()
    assert gestor.codigoBolsin == [110]
    assert [b.getNumeroBolsin() for b in gestor.bolsinesEnviados] == [110]
    assert [m.numeroBolsin for m in gestor.mapa.marcadores] == [110]
    assert gestor.sinUbicacion == []

    gestor.tomarSeleccionBolsin(110)
    resultado = await gestor.tomarConfirmacionEnvioCorreo(True)
    assert resultado.notificado is True
    assert correo.enviados[0]["destinatario"] == "gcm.ros@example.test"
    cuerpo = correo.enviados[0]["cuerpo"]
    assert "110" in cuerpo
    assert "-31.4167" in cuerpo


@pytest.mark.asyncio
async def test_a1_sin_bolsines_enviados(session: AsyncSession) -> None:
    gestor = _gestor(
        session,
        await _usuario(session, "eb.tuc01@example.test"),
        GpsTrackerFake(),
        CorreoFake(),
    )
    with pytest.raises(SinBolsinesEnviadosError):
        await gestor.opcionSeguirBolsines()


@pytest.mark.asyncio
async def test_a2_filtro_por_precinto(session: AsyncSession) -> None:
    gestor = _gestor(
        session,
        await _usuario(session, "eb.cba01@example.test"),
        GpsTrackerFake(
            ubicaciones={
                101: _ubicacion(101, -31.4201, -64.1888),
                111: _ubicacion(111, -32.8895, -68.8458),
            }
        ),
        CorreoFake(),
    )
    await gestor.opcionSeguirBolsines()
    assert [b.getNumeroBolsin() for b in gestor.filtrarPorPrecinto("P-0101")] == [101]
    assert gestor.filtrarPorPrecinto("P-9999") == []
    assert any("P-9999" in aviso for aviso in gestor.advertencias)


@pytest.mark.asyncio
async def test_a3_gps_sin_ubicacion(session: AsyncSession) -> None:
    gestor = _gestor(
        session,
        await _usuario(session, "eb.cba01@example.test"),
        GpsTrackerFake(
            ubicaciones={101: _ubicacion(101, -31.4201, -64.1888)},
            sin_ubicacion={111},
        ),
        CorreoFake(),
    )
    await gestor.opcionSeguirBolsines()
    assert [m.numeroBolsin for m in gestor.mapa.marcadores] == [101]
    assert [s.numeroBolsin for s in gestor.sinUbicacion] == [111]
    assert any("111" in aviso for aviso in gestor.advertencias)


@pytest.mark.asyncio
async def test_a4_cancelar(session: AsyncSession) -> None:
    gestor = _gestor(
        session,
        await _usuario(session, "eb.cba02@example.test"),
        GpsTrackerFake(ubicaciones={110: _ubicacion(110, -31.4167, -64.1833)}),
        CorreoFake(),
    )
    await gestor.opcionSeguirBolsines()
    gestor.tomarSeleccionBolsin(110)
    gestor.cancelar()
    assert gestor.seleccionBolsin is None


@pytest.mark.asyncio
async def test_a5_no_confirma_correo(session: AsyncSession) -> None:
    correo = CorreoFake()
    gestor = _gestor(
        session,
        await _usuario(session, "eb.cba02@example.test"),
        GpsTrackerFake(ubicaciones={110: _ubicacion(110, -31.4167, -64.1833)}),
        correo,
    )
    await gestor.opcionSeguirBolsines()
    gestor.tomarSeleccionBolsin(110)
    resultado = await gestor.tomarConfirmacionEnvioCorreo(False)
    assert resultado.notificado is False
    assert correo.enviados == []
