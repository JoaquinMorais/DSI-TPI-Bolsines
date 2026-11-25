from datetime import datetime

import httpx
import pytest

from integrations.gps_tracker.errores import (
    ErrorIntegracionGPS,
    UbicacionNoDisponibleError,
)
from integrations.gps_tracker.gps_tracker_xtr4500l import (
    GpsTrackerXtr4500l,
    parsear_ubicacion,
)

ITEM = {
    "numeroBolsin": 101,
    "latitud": -31.4201,
    "longitud": -64.1888,
    "fechaHoraUltimaActualizacion": "2026-03-07T12:30:00",
}
PAYLOAD = {"items": [ITEM]}


def test_parseo_con_un_item() -> None:
    ubicacion = parsear_ubicacion(101, PAYLOAD)
    assert ubicacion.numeroBolsin == 101
    assert ubicacion.latitud == -31.4201
    assert ubicacion.longitud == -64.1888
    assert ubicacion.fechaHoraUltimaActualizacion == datetime(2026, 3, 7, 12, 30, 0)


def test_parseo_fecha_sin_segundos() -> None:
    item = dict(ITEM, fechaHoraUltimaActualizacion="2026-03-07T12:30")
    ubicacion = parsear_ubicacion(101, {"items": [item]})
    assert ubicacion.fechaHoraUltimaActualizacion == datetime(2026, 3, 7, 12, 30)


@pytest.mark.parametrize(
    "payload",
    [
        {"items": []},
        {"items": [ITEM, ITEM]},
        {},
    ],
)
def test_parseo_respuesta_invalida_no_es_a3(payload: dict) -> None:
    with pytest.raises(ErrorIntegracionGPS):
        parsear_ubicacion(101, payload)


@pytest.mark.asyncio
async def test_adapter_ok() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-API-Key"] == "clave"
        assert request.url.params["numeroBolsin"] == "101"
        assert request.url.params["codigoComisionMedicaOrigen"] == "CM-CBA-01"
        return httpx.Response(200, json=PAYLOAD)

    cliente = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adaptador = GpsTrackerXtr4500l("http://gps", "clave", cliente=cliente)
    ubicacion = await adaptador.getBolsinLocation(101, "CM-CBA-01")
    assert ubicacion.numeroBolsin == 101
    await cliente.aclose()


@pytest.mark.asyncio
async def test_adapter_404_es_ubicacion_no_disponible() -> None:
    cliente = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(404))
    )
    adaptador = GpsTrackerXtr4500l("http://gps", "clave", cliente=cliente)
    with pytest.raises(UbicacionNoDisponibleError) as excinfo:
        await adaptador.getBolsinLocation(111, "CM-CBA-01")
    assert excinfo.value.numeroBolsin == 111
    await cliente.aclose()


@pytest.mark.asyncio
async def test_adapter_401_es_error_de_integracion() -> None:
    cliente = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda request: httpx.Response(401))
    )
    adaptador = GpsTrackerXtr4500l("http://gps", "mala", cliente=cliente)
    with pytest.raises(ErrorIntegracionGPS):
        await adaptador.getBolsinLocation(101, "CM-CBA-01")
    await cliente.aclose()
