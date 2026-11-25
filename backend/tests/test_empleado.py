import pytest
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, select

from models import ComisionMedica, Empleado, Rol, Usuario
from models.rol import NOMBRE_ENCARGADO_BOLSINES, NOMBRE_GCM

HASH = PasswordHash.recommended()
CLAVE = "secreta123"


def _engine():
    return create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )


def test_verify_password_y_mail_normalizado() -> None:
    usuario = Usuario(
        mail="  EB.CBA01@Example.TEST ", hashedPassword=HASH.hash(CLAVE)
    )
    assert usuario.getMail() == "eb.cba01@example.test"
    assert usuario.verify_password(CLAVE) is True
    assert usuario.verify_password("otra") is False


@pytest.mark.asyncio
async def test_relacion_1_a_1_y_obtener_gcm() -> None:
    engine = _engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        gcm_rol = Rol(nombre=NOMBRE_GCM)
        eb_rol = Rol(nombre=NOMBRE_ENCARGADO_BOLSINES)
        rosario = ComisionMedica(codigo="CM-ROS-02", nombre="Rosario")
        cordoba = ComisionMedica(codigo="CM-CBA-01", nombre="Cordoba")
        session.add(gcm_rol)
        session.add(eb_rol)
        session.add(rosario)
        session.add(cordoba)
        await session.commit()
        for obj in (gcm_rol, eb_rol, rosario, cordoba):
            await session.refresh(obj)

        u_gcm = Usuario(mail="gcm.ros@example.test", hashedPassword=HASH.hash(CLAVE))
        u_eb = Usuario(mail="eb.cba@example.test", hashedPassword=HASH.hash(CLAVE))
        session.add(u_gcm)
        session.add(u_eb)
        await session.commit()
        await session.refresh(u_gcm)
        await session.refresh(u_eb)

        e_gcm = Empleado(
            nombre="G",
            apellido="Rosario",
            idUser=u_gcm.id,
            rolId=gcm_rol.id,
            comisionMedicaId=rosario.id,
            usuario=u_gcm,
        )
        e_eb = Empleado(
            nombre="E",
            apellido="Cordoba",
            idUser=u_eb.id,
            rolId=eb_rol.id,
            comisionMedicaId=cordoba.id,
            usuario=u_eb,
        )
        session.add(e_gcm)
        session.add(e_eb)
        await session.commit()

        stmt = (
            select(Usuario)
            .where(Usuario.mail == "gcm.ros@example.test")
            .options(selectinload(Usuario.empleado))
        )
        usuario = (await session.exec(stmt)).first()
        assert usuario is not None
        assert usuario.getEmpleado() is not None
        assert usuario.getEmpleado().sosGCM() is True
        assert usuario.getEmpleado().getUsuario() is usuario
        assert usuario.getEmpleado().getCM().getCodigo() == "CM-ROS-02"

        gcm = await Empleado.obtenerGCMDeCM(session, "CM-ROS-02")
        assert gcm is not None
        assert gcm.sosGCM() is True
        assert gcm.getUsuario().getMail() == "gcm.ros@example.test"

        assert await Empleado.obtenerGCMDeCM(session, "CM-CBA-01") is None

    await engine.dispose()
