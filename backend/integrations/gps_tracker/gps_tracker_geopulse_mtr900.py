from datetime import datetime
from typing import Any, Optional

import httpx

from integrations.gps_tracker.errores import (
    ErrorIntegracionGPS,
    UbicacionNoDisponibleError,
)
from integrations.gps_tracker.interfaz_gps_tracker import InterfazGPSTracker
from models.ubicacion_bolsin import UbicacionBolsin

RUTA = "/api/geopulse-mtr-900/fetchCargoPositions"


def parsear_ubicacion_geopulse(
    numeroBolsin: int, payload: Any
) -> UbicacionBolsin:
    if not isinstance(payload, list) or len(payload) != 1:
        raise ErrorIntegracionGPS("Respuesta GeoPulse invalida: se esperaba una fila")
    fila = payload[0]
    if not isinstance(fila, list) or len(fila) != 4:
        raise ErrorIntegracionGPS("Respuesta GeoPulse invalida: fila incompleta")
    try:
        numero = int(fila[0])
        latitud = float(fila[1])
        longitud = float(fila[2])
        fecha = datetime.fromisoformat(str(fila[3]))
    except (TypeError, ValueError) as exc:
        raise ErrorIntegracionGPS("Respuesta GeoPulse invalida") from exc
    if numero != numeroBolsin:
        raise ErrorIntegracionGPS(
            f"GeoPulse devolvio el bolsin {numero}, se esperaba {numeroBolsin}"
        )
    return UbicacionBolsin(
        numeroBolsin=numero,
        latitud=latitud,
        longitud=longitud,
        fechaHoraUltimaActualizacion=fecha,
    )


class GpsTrackerGeoPulseMtr900(InterfazGPSTracker):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        cliente: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._cliente = cliente

    async def getBolsinLocation(
        self, numeroBolsin: int, codigoCM: str
    ) -> UbicacionBolsin:
        url = f"{self._base_url}{RUTA}"
        params = {"numeroBolsin": numeroBolsin}
        headers = {"X-API-Key": self._api_key}

        try:
            if self._cliente is not None:
                respuesta = await self._cliente.get(
                    url, params=params, headers=headers
                )
            else:
                async with httpx.AsyncClient() as cliente:
                    respuesta = await cliente.get(
                        url, params=params, headers=headers, timeout=10
                    )
        except httpx.HTTPError as exc:
            raise UbicacionNoDisponibleError(
                numeroBolsin, f"Error de red: {exc}"
            ) from exc

        if respuesta.status_code == 404:
            raise UbicacionNoDisponibleError(
                numeroBolsin, "El GPS no informo ubicacion (404)"
            )
        if respuesta.status_code in (400, 401):
            raise ErrorIntegracionGPS(
                f"El GPS respondio {respuesta.status_code}: {respuesta.text}"
            )
        if respuesta.status_code != 200:
            raise UbicacionNoDisponibleError(
                numeroBolsin, f"El GPS respondio {respuesta.status_code}"
            )

        return parsear_ubicacion_geopulse(numeroBolsin, respuesta.json())
