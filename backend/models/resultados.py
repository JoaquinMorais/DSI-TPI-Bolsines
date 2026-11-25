from dataclasses import dataclass
from typing import Optional

from models.bolsin import Bolsin
from models.mapa_bolsines import MapaBolsines
from models.ubicacion_bolsin import UbicacionBolsin


@dataclass(frozen=True)
class SinUbicacion:
    numeroBolsin: int
    motivo: str


@dataclass(frozen=True)
class ResultadoSeguimiento:
    codigoCM: str
    bolsines: list[Bolsin]
    mapa: MapaBolsines
    sinUbicacion: list[SinUbicacion]


@dataclass(frozen=True)
class ResultadoSeleccion:
    bolsin: Bolsin
    ubicacion: Optional[UbicacionBolsin]


@dataclass(frozen=True)
class ResultadoConfirmacion:
    notificado: bool
    destinatario: Optional[str]
