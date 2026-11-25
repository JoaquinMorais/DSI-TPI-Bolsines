from abc import ABC, abstractmethod

from models.mapa_bolsines import MapaBolsines
from models.ubicacion_bolsin import UbicacionBolsin


class InterfazGoogleMaps(ABC):
    @abstractmethod
    def obtenerMapa(self, ubicaciones: list[UbicacionBolsin]) -> MapaBolsines: ...
