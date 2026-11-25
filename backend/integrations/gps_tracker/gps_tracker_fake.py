from typing import Optional

from integrations.gps_tracker.errores import UbicacionNoDisponibleError
from integrations.gps_tracker.interfaz_gps_tracker import InterfazGPSTracker
from models.ubicacion_bolsin import UbicacionBolsin


class GpsTrackerFake(InterfazGPSTracker):
    def __init__(
        self,
        ubicaciones: Optional[dict[int, UbicacionBolsin]] = None,
        sin_ubicacion: Optional[set[int]] = None,
    ) -> None:
        self._ubicaciones = ubicaciones or {}
        self._sin_ubicacion = sin_ubicacion or set()
        self.llamadas: list[tuple[int, str]] = []

    async def getBolsinLocation(
        self, numeroBolsin: int, codigoCM: str
    ) -> UbicacionBolsin:
        self.llamadas.append((numeroBolsin, codigoCM))
        if numeroBolsin in self._sin_ubicacion:
            raise UbicacionNoDisponibleError(
                numeroBolsin, "El GPS no informo ubicacion"
            )
        if numeroBolsin not in self._ubicaciones:
            raise UbicacionNoDisponibleError(
                numeroBolsin, "El GPS no informo ubicacion"
            )
        return self._ubicaciones[numeroBolsin]
