from abc import ABC, abstractmethod

from models.ubicacion_bolsin import UbicacionBolsin


class InterfazGPSTracker(ABC):
    @abstractmethod
    async def getBolsinLocation(
        self, numeroBolsin: int, codigoCM: str
    ) -> UbicacionBolsin: ...
