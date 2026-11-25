from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.bolsin import Bolsin
    from models.estado import Estado


class CambioEstado(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fechaHoraInicio: datetime
    fechaHoraFin: Optional[datetime] = None
    bolsinId: int = Field(foreign_key="bolsin.id")
    estadoId: int = Field(foreign_key="estado.id")

    bolsin: Optional["Bolsin"] = Relationship(
        back_populates="cambiosEstado",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    estado: Optional["Estado"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def sosActual(self) -> bool:
        return self.fechaHoraFin is None

    def sosEnviado(self) -> bool:
        return self.estado is not None and self.estado.esEnviado()

    def setFechaHoraFin(self, fecha: datetime) -> None:
        self.fechaHoraFin = fecha
