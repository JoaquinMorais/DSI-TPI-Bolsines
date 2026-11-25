from datetime import datetime
from typing import Optional

import httpx

from integrations.gps_tracker.errores import (
    ErrorIntegracionGPS,
    UbicacionNoDisponibleError,
)
from integrations.gps_tracker.interfaz_gps_tracker import InterfazGPSTracker
from models.ubicacion_bolsin import UbicacionBolsin

RUTA = "/api/navtrack-qx-7a/retrieveTrackingData"


def parsear_ubicacion_navtrack(numeroBolsin: int, texto: str) -> UbicacionBolsin:
    partes = [parte.strip() for parte in texto.strip().split(",")]
    if len(partes) != 4:
        raise ErrorIntegracionGPS("Respuesta NavTrack invalida: se esperaban 4 campos")
    try:
        numero = int(partes[0])
        latitud = float(partes[1])
        longitud = float(partes[2])
        fecha = datetime.fromisoformat(partes[3])
    except ValueError as exc:
        raise ErrorIntegracionGPS("Respuesta NavTrack invalida") from exc
    if numero != numeroBolsin:
        raise ErrorIntegracionGPS(
            f"NavTrack devolvio el bolsin {numero}, se esperaba {numeroBolsin}"
        )
    return UbicacionBolsin(
        numeroBolsin=numero,
        latitud=latitud,
        longitud=longitud,
        fechaHoraUltimaActualizacion=fecha,
    )


class GpsTrackerNavTrackQx7a(InterfazGPSTracker):
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
            "codigoComisionMedicaDestino": codigoCM,
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

        return parsear_ubicacion_navtrack(numeroBolsin, respuesta.text)
