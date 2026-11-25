import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from data.seed import sembrar
from models import Bolsin, CambioEstado, ComisionMedica, Empleado, Estado, Rol, Usuario


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
        yield db
    await engine.dispose()


async def _conteos(session: AsyncSession) -> dict[str, int]:
    resultado = {}
    for nombre, modelo in (
        ("estado", Estado),
        ("rol", Rol),
        ("cm", ComisionMedica),
        ("usuario", Usuario),
        ("empleado", Empleado),
        ("bolsin", Bolsin),
        ("cambio", CambioEstado),
    ):
        resultado[nombre] = len((await session.exec(select(modelo))).all())
    return resultado


@pytest.mark.asyncio
async def test_seed_idempotente(session: AsyncSession) -> None:
    assert await sembrar(session) is True
    primero = await _conteos(session)
    assert primero["estado"] == 5
    assert primero["rol"] == 4
    assert primero["cm"] == 6
    assert primero["usuario"] == 9
    assert primero["empleado"] == 9
    assert primero["bolsin"] == 12

    assert await sembrar(session) is False
    assert await _conteos(session) == primero


@pytest.mark.asyncio
async def test_un_cambio_vigente_por_bolsin(session: AsyncSession) -> None:
    await sembrar(session)
    for bolsin in (await session.exec(select(Bolsin))).all():
        vigentes = [c for c in bolsin.cambiosEstado if c.fechaHoraFin is None]
        assert len(vigentes) == 1


@pytest.mark.asyncio
async def test_origenes_coinciden_con_la_api(session: AsyncSession) -> None:
    await sembrar(session)
    por_numero = {
        b.numeroBolsin: b for b in (await session.exec(select(Bolsin))).all()
    }
    assert por_numero[101].origen.getCodigo() == "CM-CBA-01"
    assert por_numero[101].destino.getCodigo() == "CM-ROS-02"
    assert por_numero[110].origen.getCodigo() == "CM-CBA-02"
    assert por_numero[102].origen.getCodigo() == "CM-ROS-02"
    assert por_numero[103].origen.getCodigo() == "CM-MDZ-03"
    assert por_numero[104].origen.getCodigo() == "CM-BA-01"


@pytest.mark.asyncio
async def test_reset_recarga(session: AsyncSession) -> None:
    await sembrar(session)
    assert await sembrar(session, reset=True) is True
    conteos = await _conteos(session)
    assert conteos["bolsin"] == 12
    assert conteos["usuario"] == 9
