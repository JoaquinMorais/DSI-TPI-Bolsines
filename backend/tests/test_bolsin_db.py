from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Bolsin, CambioEstado, ComisionMedica, Estado

INICIO = datetime(2026, 11, 20, 9, 0)


async def _crear_historial(
    session: AsyncSession,
    bolsin: Bolsin,
    cambios: list[tuple[str, Estado]],
) -> None:
    momento = INICIO
    for indice, (_, estado) in enumerate(cambios):
        fin = momento + timedelta(hours=1) if indice < len(cambios) - 1 else None
        session.add(
            CambioEstado(
                fechaHoraInicio=momento,
                fechaHoraFin=fin,
                bolsinId=bolsin.id,
                estadoId=estado.id,
                estado=estado,
            )
        )
        if fin is not None:
            momento = fin
    await session.commit()


@pytest.mark.asyncio
async def test_bolsin_con_historial_en_sqlite_memoria() -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        origen = ComisionMedica(codigo="CM-CBA-01", nombre="Cordoba")
        destino = ComisionMedica(codigo="CM-ROS-02", nombre="Rosario")
        creado = Estado(nombre="Creado", descripcion="Creado")
        cerrado = Estado(nombre="Cerrado", descripcion="Cerrado")
        enviado = Estado(nombre="Enviado", descripcion="Enviado")
        session.add_all([origen, destino, creado, cerrado, enviado])
        await session.commit()
        for obj in (origen, destino, creado, cerrado, enviado):
            await session.refresh(obj)

        bolsin_enviado = Bolsin(
            numeroBolsin=101,
            fecha=INICIO,
            numeroPrecinto="P-0101",
            peso=4200,
            cmOrigenId=origen.id,
            cmDestinoId=destino.id,
        )
        bolsin_cerrado = Bolsin(
            numeroBolsin=102,
            fecha=INICIO,
            numeroPrecinto="P-0102",
            peso=1500,
            cmOrigenId=origen.id,
            cmDestinoId=destino.id,
        )
        session.add(bolsin_enviado)
        session.add(bolsin_cerrado)
        await session.commit()
        await session.refresh(bolsin_enviado)
        await session.refresh(bolsin_cerrado)

        await _crear_historial(
            session,
            bolsin_enviado,
            [("Creado", creado), ("Cerrado", cerrado), ("Enviado", enviado)],
        )
        await _crear_historial(
            session,
            bolsin_cerrado,
            [("Creado", creado), ("Cerrado", cerrado)],
        )

        session.expire_all()
        bolsines = {
            b.numeroBolsin: b for b in (await session.exec(select(Bolsin))).all()
        }
        enviado_db = bolsines[101]
        cerrado_db = bolsines[102]

        assert enviado_db.esTuCMOrigen("CM-CBA-01") is True
        assert enviado_db.esTuCMOrigen("CM-ROS-02") is False
        assert enviado_db.sosEnviado() is True
        assert enviado_db.getNumeroBolsin() == 101
        assert enviado_db.obtenerCMDestino().getCodigo() == "CM-ROS-02"

        assert cerrado_db.sosEnviado() is False

        for bolsin in (enviado_db, cerrado_db):
            vigentes = [c for c in bolsin.cambiosEstado if c.fechaHoraFin is None]
            assert len(vigentes) == 1

    await engine.dispose()
