from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BolsinSeguimientoOut(BaseModel):
    numeroBolsin: int
    numeroPrecinto: Optional[str] = None
    codigoCMDestino: str


class CoordenadaOut(BaseModel):
    latitud: float
    longitud: float


class MarcadorOut(BaseModel):
    numeroBolsin: int
    latitud: float
    longitud: float
    fechaHoraUltimaActualizacion: datetime


class MapaBolsinesOut(BaseModel):
    centro: CoordenadaOut
    zoom: int
    marcadores: list[MarcadorOut]


class SinUbicacionOut(BaseModel):
    numeroBolsin: int
    motivo: str


class SeguimientoCreadoResponse(BaseModel):
    idCU: UUID
    codigoCM: str
    bolsines: list[BolsinSeguimientoOut]
    mapa: MapaBolsinesOut
    sinUbicacion: list[SinUbicacionOut]


class SeleccionBolsinRequest(BaseModel):
    numeroBolsin: int = Field(gt=0)


class SeleccionBolsinResponse(BaseModel):
    idCU: UUID
    bolsin: BolsinSeguimientoOut
    ubicacion: Optional[MarcadorOut] = None
    requiereConfirmacionCorreo: bool = True


class ConfirmacionCorreoRequest(BaseModel):
    confirma: bool


class ConfirmacionCorreoResponse(BaseModel):
    estado: Literal["FINALIZADO"] = "FINALIZADO"
    notificado: bool
    destinatarioEnmascarado: Optional[str] = None


class ErrorResponse(BaseModel):
    codigo: str
    mensaje: str
