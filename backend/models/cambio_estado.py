from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.bolsin import Bolsin
    from models.estado import Estado


class CambioEstado(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fechaHoraInicio: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    fechaHoraFin: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=False), nullable=True))
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
        """Indica si el cambio es el vigente (fechaHoraFin nula, paso 6 del CU 36)."""
        return self.fechaHoraFin is None

    def sosEnviado(self) -> bool:
        """Delega en Estado.esEnviado (paso 6 del CU 36)."""
        return self.estado is not None and self.estado.esEnviado()

    def setFechaHoraFin(self, fecha: datetime) -> None:
        """Cierra el cambio de estado con la fecha indicada."""
        self.fechaHoraFin = fecha
