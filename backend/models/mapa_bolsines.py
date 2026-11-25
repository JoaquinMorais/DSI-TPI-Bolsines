from dataclasses import dataclass

from models.ubicacion_bolsin import UbicacionBolsin


@dataclass(frozen=True)
class Coordenada:
    latitud: float
    longitud: float


@dataclass(frozen=True)
class MapaBolsines:
    centro: Coordenada
    zoom: int
    marcadores: list[UbicacionBolsin]
