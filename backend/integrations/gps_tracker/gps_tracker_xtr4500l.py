from datetime import datetime
from typing import Any, Optional

import httpx

from integrations.gps_tracker.errores import (
    ErrorIntegracionGPS,
    UbicacionNoDisponibleError,
)
from integrations.gps_tracker.interfaz_gps_tracker import InterfazGPSTracker
from models.ubicacion_bolsin import UbicacionBolsin

RUTA = "/api/xtr-4500l/getBolsinLocation"


def parsear_ubicacion(numeroBolsin: int, payload: dict[str, Any]) -> UbicacionBolsin:
    items = payload.get("items")
    if not isinstance(items, list) or len(items) != 1:
        raise ErrorIntegracionGPS("Respuesta del GPS invalida: se esperaba un item")
    item = items[0]
    try:
        return UbicacionBolsin(
            numeroBolsin=int(item["numeroBolsin"]),
            latitud=float(item["latitud"]),
            longitud=float(item["longitud"]),
            fechaHoraUltimaActualizacion=datetime.fromisoformat(
                str(item["fechaHoraUltimaActualizacion"])
            ),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ErrorIntegracionGPS("Respuesta del GPS invalida") from exc


class GpsTrackerXtr4500l(InterfazGPSTracker):
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
        params = {
            "numeroBolsin": numeroBolsin,
            "codigoComisionMedicaOrigen": codigoCM,
        }
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

        return parsear_ubicacion(numeroBolsin, respuesta.json())
