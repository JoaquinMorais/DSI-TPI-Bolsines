from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.cambio_estado import CambioEstado
    from models.comision_medica import ComisionMedica


class Bolsin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numeroBolsin: int = Field(unique=True, index=True)
    fecha: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=False))
    numeroPrecinto: Optional[str] = None
    peso: int
    cmOrigenId: int = Field(foreign_key="comisionmedica.id")
    cmDestinoId: int = Field(foreign_key="comisionmedica.id")

    origen: Optional["ComisionMedica"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Bolsin.cmOrigenId]",
            "lazy": "selectin",
        },
    )
    destino: Optional["ComisionMedica"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Bolsin.cmDestinoId]",
            "lazy": "selectin",
        },
    )
    cambiosEstado: List["CambioEstado"] = Relationship(
        back_populates="bolsin",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "lazy": "selectin",
        },
    )

    def esTuCMOrigen(self, codigoCM: str) -> bool:
        return self.origen is not None and self.origen.getCodigo() == codigoCM

    def sosEnviado(self) -> bool:
        for cambio in self.cambiosEstado:
            if cambio.sosActual():
                return cambio.sosEnviado()
        return False

    def getNumeroBolsin(self) -> int:
        return self.numeroBolsin

    def obtenerCMDestino(self) -> "Optional[ComisionMedica]":
        return self.destino
