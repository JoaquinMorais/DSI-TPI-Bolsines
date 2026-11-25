from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel, select

from models.comision_medica import ComisionMedica
from models.rol import NOMBRE_GCM, Rol

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from models.usuario import Usuario


class Empleado(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellido: str
    idUser: int = Field(foreign_key="usuario.id", unique=True, index=True)
    rolId: int = Field(foreign_key="rol.id")
    comisionMedicaId: int = Field(foreign_key="comisionmedica.id")

    usuario: Optional["Usuario"] = Relationship(
        back_populates="empleado",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    rol: Optional[Rol] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    comisionMedica: Optional[ComisionMedica] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def esTuCM(self, codigoCM: str) -> bool:
        return (
            self.comisionMedica is not None
            and self.comisionMedica.getCodigo() == codigoCM
        )

    def sosGCM(self) -> bool:
        return self.rol is not None and self.rol.esGCM()

    def getCM(self) -> Optional[ComisionMedica]:
        return self.comisionMedica

    def getUsuario(self) -> "Optional[Usuario]":
        return self.usuario

    @classmethod
    async def obtenerGCMDeCM(
        cls, db: "AsyncSession", codigoCM: str
    ) -> Optional["Empleado"]:
        stmt = (
            select(cls)
            .join(Rol, Rol.id == cls.rolId)
            .join(ComisionMedica, ComisionMedica.id == cls.comisionMedicaId)
            .where(ComisionMedica.codigo == codigoCM)
            .where(Rol.nombre == NOMBRE_GCM)
        )
        resultado = await db.exec(stmt)
        return resultado.first()
