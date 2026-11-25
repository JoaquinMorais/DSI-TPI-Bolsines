import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

_BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from pwdlib import PasswordHash
from sqlalchemy import delete
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from config.database import async_session, create_db_and_tables
from config.settings import settings
from models import (
    Bolsin,
    CambioEstado,
    ComisionMedica,
    Empleado,
    Estado,
    RefreshToken,
    Rol,
    Usuario,
)
from models.rol import (
    NOMBRE_ENCARGADO_BOLSINES,
    NOMBRE_GCM,
)

_password_hash = PasswordHash.recommended()
CLAVE_POR_DEFECTO = "bolsines-dev"

ESTADOS = [
    ("Creado", "Bolsin armado, sin precinto"),
    ("Cerrado", "Cerrado con precinto, pendiente de retiro"),
    ("Enviado", "Retirado por el correo, en transito"),
    ("Recibido", "Recibido en CM destino"),
    ("De baja", "Dado de baja"),
]

ROLES = [
    NOMBRE_ENCARGADO_BOLSINES,
    NOMBRE_GCM,
    "Encargado de Documentación",
    "Parametrizador del sistema",
]

COMISIONES = [
    ("CM-CBA-01", "Comisión Médica Córdoba"),
    ("CM-CBA-02", "Comisión Médica Córdoba 2"),
    ("CM-ROS-02", "Comisión Médica Rosario"),
    ("CM-MDZ-03", "Comisión Médica Mendoza"),
    ("CM-TUC-01", "Comisión Médica Tucumán"),
    ("CM-BA-01", "Comisión Médica Central"),
]

EMPLEADOS = [
    ("eb.cba01@example.test", "Encargado", NOMBRE_ENCARGADO_BOLSINES, "CM-CBA-01"),
    ("eb.cba02@example.test", "Encargado", NOMBRE_ENCARGADO_BOLSINES, "CM-CBA-02"),
    ("eb.tuc01@example.test", "Encargado", NOMBRE_ENCARGADO_BOLSINES, "CM-TUC-01"),
    ("gcm.cba-01@example.test", "Gerente", NOMBRE_GCM, "CM-CBA-01"),
    ("gcm.cba-02@example.test", "Gerente", NOMBRE_GCM, "CM-CBA-02"),
    ("gcm.ros-02@example.test", "Gerente", NOMBRE_GCM, "CM-ROS-02"),
    ("gcm.mdz-03@example.test", "Gerente", NOMBRE_GCM, "CM-MDZ-03"),
    ("gcm.tuc-01@example.test", "Gerente", NOMBRE_GCM, "CM-TUC-01"),
    ("gcm.ba-01@example.test", "Gerente", NOMBRE_GCM, "CM-BA-01"),
]

D20 = datetime(2026, 11, 20, 9, 0)
D20_1730 = datetime(2026, 11, 20, 17, 30)
D21_0805 = datetime(2026, 11, 21, 8, 5)
D22_1000 = datetime(2026, 11, 22, 10, 0)

ENVIADO = ("Creado", D20, D20_1730), ("Cerrado", D20_1730, D21_0805), ("Enviado", D21_0805, None)

BOLSINES = [
    (101, "CM-CBA-01", "CM-ROS-02", "P-0101", 4200, ENVIADO),
    (110, "CM-CBA-02", "CM-ROS-02", "P-0110", 3800, ENVIADO),
    (111, "CM-CBA-01", "CM-MDZ-03", "P-0111", 2950, ENVIADO),
    (102, "CM-ROS-02", "CM-MDZ-03", "P-0102", 1500, ENVIADO),
    (103, "CM-MDZ-03", "CM-BA-01", "P-0103", 2100, ENVIADO),
    (104, "CM-BA-01", "CM-CBA-01", "P-0104", 900, ENVIADO),
    (114, "CM-CBA-01", "CM-BA-01", "P-0114", 2600,
     (("Creado", D20, D20_1730), ("Cerrado", D20_1730, None))),
    (113, "CM-CBA-01", "CM-ROS-02", None, 1200,
     (("Creado", datetime(2026, 11, 24, 9, 0), None),)),
    (115, "CM-CBA-01", "CM-MDZ-03", "P-0115", 1800,
     (("Creado", D20, D20_1730), ("Cerrado", D20_1730, D21_0805),
      ("Enviado", D21_0805, D22_1000), ("Recibido", D22_1000, None))),
    (117, "CM-TUC-01", "CM-CBA-01", None, 500,
     (("Creado", datetime(2026, 11, 19, 9, 0), datetime(2026, 11, 19, 12, 0)),
      ("De baja", datetime(2026, 11, 19, 12, 0), None))),
    (118, "CM-CBA-01", "CM-TUC-01", None, 800,
     (("Creado", datetime(2026, 11, 22, 9, 0), datetime(2026, 11, 23, 11, 0)),
      ("De baja", datetime(2026, 11, 23, 11, 0), None))),
    (116, "CM-TUC-01", "CM-BA-01", None, 700,
     (("Creado", datetime(2026, 11, 24, 10, 0), None),)),
]


async def _cargar(session: AsyncSession) -> None:
    clave = settings.SEED_PASSWORD_DEV or CLAVE_POR_DEFECTO
    hashed = _password_hash.hash(clave)

    estados = {nombre: Estado(nombre=nombre, descripcion=desc) for nombre, desc in ESTADOS}
    roles = {nombre: Rol(nombre=nombre) for nombre in ROLES}
    comisiones = {codigo: ComisionMedica(codigo=codigo, nombre=nombre) for codigo, nombre in COMISIONES}
    session.add_all([*estados.values(), *roles.values(), *comisiones.values()])
    await session.commit()
    for obj in (*estados.values(), *roles.values(), *comisiones.values()):
        await session.refresh(obj)

    for mail, nombre, rol, codigo_cm in EMPLEADOS:
        usuario = Usuario(mail=mail, hashedPassword=hashed)
        session.add(usuario)
        await session.commit()
        await session.refresh(usuario)
        session.add(
            Empleado(
                nombre=nombre,
                apellido="Seed",
                idUser=usuario.id,
                rolId=roles[rol].id,
                comisionMedicaId=comisiones[codigo_cm].id,
                usuario=usuario,
            )
        )
    await session.commit()

    for numero, origen, destino, precinto, peso, historia in BOLSINES:
        bolsin = Bolsin(
            numeroBolsin=numero,
            fecha=historia[0][1],
            numeroPrecinto=precinto,
            peso=peso,
            cmOrigenId=comisiones[origen].id,
            cmDestinoId=comisiones[destino].id,
        )
        session.add(bolsin)
        await session.commit()
        await session.refresh(bolsin)
        for nombre_estado, inicio, fin in historia:
            session.add(
                CambioEstado(
                    fechaHoraInicio=inicio,
                    fechaHoraFin=fin,
                    bolsinId=bolsin.id,
                    estadoId=estados[nombre_estado].id,
                    estado=estados[nombre_estado],
                )
            )
        await session.commit()


async def _verificar(session: AsyncSession) -> None:
    bolsines = (await session.exec(select(Bolsin))).all()
    for bolsin in bolsines:
        actuales = [c for c in bolsin.cambiosEstado if c.fechaHoraFin is None]
        if len(actuales) != 1:
            raise RuntimeError(
                f"El bolsin {bolsin.numeroBolsin} tiene {len(actuales)} cambios vigentes"
            )

    esperados = {
        101: ("CM-CBA-01", "CM-ROS-02"),
        102: ("CM-ROS-02", "CM-MDZ-03"),
        103: ("CM-MDZ-03", "CM-BA-01"),
        104: ("CM-BA-01", "CM-CBA-01"),
        110: ("CM-CBA-02", "CM-ROS-02"),
    }
    por_numero = {bolsin.numeroBolsin: bolsin for bolsin in bolsines}
    for numero, (origen, destino) in esperados.items():
        bolsin = por_numero.get(numero)
        if (
            bolsin is None
            or bolsin.origen is None
            or bolsin.destino is None
            or bolsin.origen.getCodigo() != origen
            or bolsin.destino.getCodigo() != destino
        ):
            raise RuntimeError(
                f"El bolsin {numero} no coincide con la API del GPS"
            )


async def sembrar(session: AsyncSession, reset: bool = False) -> bool:
    existente = (await session.exec(select(Estado))).first()
    if existente is not None:
        if not reset:
            return False
        for modelo in (
            CambioEstado,
            Bolsin,
            Empleado,
            RefreshToken,
            Usuario,
            ComisionMedica,
            Rol,
            Estado,
        ):
            await session.execute(delete(modelo))
        await session.commit()

    await _cargar(session)
    await _verificar(session)
    return True


async def _imprimir_resumen() -> None:
    async with async_session() as session:
        bolsines = (await session.exec(select(Bolsin))).all()
        grupos: dict[str, list[int]] = {}
        for bolsin in bolsines:
            if bolsin.sosEnviado() and bolsin.origen is not None:
                grupos.setdefault(bolsin.origen.getCodigo(), []).append(
                    bolsin.getNumeroBolsin()
                )
    print("Enviados por CM:")
    for codigo in sorted(grupos):
        numeros = ", ".join(str(n) for n in sorted(grupos[codigo]))
        print(f"  {codigo}: {numeros}")


async def seed(reset: bool = False) -> bool:
    await create_db_and_tables()
    async with async_session() as session:
        return await sembrar(session, reset)


async def _ejecutar(reset: bool) -> None:
    cargado = await seed(reset)
    if cargado:
        print("Datos semilla cargados.")
    else:
        print("La base ya tiene datos; use --reset para recargar.")
    await _imprimir_resumen()


def main(argv: Optional[list[str]] = None) -> None:
    argumentos = sys.argv[1:] if argv is None else argv
    asyncio.run(_ejecutar("--reset" in argumentos))


if __name__ == "__main__":
    main()
