from datetime import datetime

import httpx
import pytest

from integrations.gps_tracker.errores import (
    ErrorIntegracionGPS,
    UbicacionNoDisponibleError,
)
from integrations.gps_tracker.gps_tracker_geopulse_mtr900 import (
    GpsTrackerGeoPulseMtr900,
)
from integrations.gps_tracker.gps_tracker_navtrack_qx7a import (
    GpsTrackerNavTrackQx7a,
)
from integrations.gps_tracker.gps_tracker_xtr4500l import GpsTrackerXtr4500l

ITEM_XTR = {
    "numeroBolsin": 101,
    "latitud": -31.4201,
    "longitud": -64.1888,
    "fechaHoraUltimaActualizacion": "2026-03-07T12:30:00",
}


def _cliente(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


@pytest.mark.asyncio
async def test_xtr_valido() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-API-Key"] == "k"
        assert request.url.params["numeroBolsin"] == "101"
        assert request.url.params["codigoComisionMedicaOrigen"] == "CM-CBA-01"
        return httpx.Response(200, json={"items": [ITEM_XTR]})

    cliente = _cliente(handler)
    ubicacion = await GpsTrackerXtr4500l(
        "http://gps", "k", cliente=cliente
    ).getBolsinLocation(101, "CM-CBA-01")
    assert ubicacion.numeroBolsin == 101
    await cliente.aclose()


@pytest.mark.asyncio
async def test_xtr_404_es_a3() -> None:
    cliente = _cliente(lambda request: httpx.Response(404))
    with pytest.raises(UbicacionNoDisponibleError):
        await GpsTrackerXtr4500l("http://gps", "k", cliente=cliente).getBolsinLocation(
            111, "CM-CBA-01"
        )
    await cliente.aclose()


@pytest.mark.asyncio
async def test_xtr_401_es_error_de_integracion() -> None:
    cliente = _cliente(lambda request: httpx.Response(401))
    with pytest.raises(ErrorIntegracionGPS):
        await GpsTrackerXtr4500l("http://gps", "k", cliente=cliente).getBolsinLocation(
            101, "CM-CBA-01"
        )
    await cliente.aclose()


@pytest.mark.asyncio
async def test_xtr_payload_invalido() -> None:
    cliente = _cliente(lambda request: httpx.Response(200, json={"items": []}))
    with pytest.raises(ErrorIntegracionGPS):
        await GpsTrackerXtr4500l("http://gps", "k", cliente=cliente).getBolsinLocation(
            101, "CM-CBA-01"
        )
    await cliente.aclose()


@pytest.mark.asyncio
async def test_xtr_timeout_es_a3() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timeout")

    cliente = _cliente(handler)
    with pytest.raises(UbicacionNoDisponibleError):
        await GpsTrackerXtr4500l("http://gps", "k", cliente=cliente).getBolsinLocation(
            101, "CM-CBA-01"
        )
    await cliente.aclose()


@pytest.mark.asyncio
async def test_navtrack_valido() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["codigoComisionMedicaDestino"] == "CM-ROS-02"
        return httpx.Response(200, text="101,-31.4201,-64.1888,2026-03-07T12:30")

    cliente = _cliente(handler)
    ubicacion = await GpsTrackerNavTrackQx7a(
        "http://gps", "k", cliente=cliente
    ).getBolsinLocation(101, "CM-ROS-02")
    assert ubicacion.fechaHoraUltimaActualizacion == datetime(2026, 3, 7, 12, 30)
    await cliente.aclose()


@pytest.mark.asyncio
async def test_navtrack_404_es_a3() -> None:
    cliente = _cliente(lambda request: httpx.Response(404))
    with pytest.raises(UbicacionNoDisponibleError):
        await GpsTrackerNavTrackQx7a(
            "http://gps", "k", cliente=cliente
        ).getBolsinLocation(101, "CM-XXX-99")
    await cliente.aclose()


@pytest.mark.asyncio
async def test_navtrack_timeout_es_a3() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timeout")

    cliente = _cliente(handler)
    with pytest.raises(UbicacionNoDisponibleError):
        await GpsTrackerNavTrackQx7a(
            "http://gps", "k", cliente=cliente
        ).getBolsinLocation(101, "CM-ROS-02")
    await cliente.aclose()


@pytest.mark.asyncio
async def test_geopulse_valido() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["numeroBolsin"] == "101"
        assert "codigoComisionMedicaDestino" not in request.url.params
        return httpx.Response(
            200, json=[[101, -31.4201, -64.1888, "2026-03-07T12:30:00"]]
        )

    cliente = _cliente(handler)
    ubicacion = await GpsTrackerGeoPulseMtr900(
        "http://gps", "k", cliente=cliente
    ).getBolsinLocation(101, "CM-CBA-01")
    assert ubicacion.numeroBolsin == 101
    await cliente.aclose()


@pytest.mark.asyncio
async def test_geopulse_404_es_a3() -> None:
    cliente = _cliente(lambda request: httpx.Response(404))
    with pytest.raises(UbicacionNoDisponibleError):
        await GpsTrackerGeoPulseMtr900(
            "http://gps", "k", cliente=cliente
        ).getBolsinLocation(999, "CM-CBA-01")
    await cliente.aclose()


@pytest.mark.asyncio
async def test_geopulse_payload_invalido() -> None:
    cliente = _cliente(lambda request: httpx.Response(200, json=[]))
    with pytest.raises(ErrorIntegracionGPS):
        await GpsTrackerGeoPulseMtr900(
            "http://gps", "k", cliente=cliente
        ).getBolsinLocation(101, "CM-CBA-01")
    await cliente.aclose()
