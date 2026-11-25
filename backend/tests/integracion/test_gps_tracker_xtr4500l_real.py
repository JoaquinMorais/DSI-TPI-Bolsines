import httpx
import pytest

from config.settings import settings
from integrations.gps_tracker.errores import (
    ErrorIntegracionGPS,
    UbicacionNoDisponibleError,
)
from integrations.gps_tracker.gps_tracker_xtr4500l import GpsTrackerXtr4500l

pytestmark = pytest.mark.integracion


def _api_disponible() -> bool:
    if not settings.GPS_API_KEY:
        return False
    try:
        respuesta = httpx.get(f"{settings.GPS_BASE_URL}/health", timeout=2)
    except httpx.HTTPError:
        return False
    return respuesta.status_code == 200


@pytest.fixture(autouse=True)
def _requiere_api() -> None:
    if not _api_disponible():
        pytest.skip("API GPS no disponible o falta GPS_API_KEY")


def _adaptador(api_key: str | None = None) -> GpsTrackerXtr4500l:
    return GpsTrackerXtr4500l(
        settings.GPS_BASE_URL, api_key or settings.GPS_API_KEY
    )


@pytest.mark.asyncio
async def test_bolsin_101_ubicado() -> None:
    ubicacion = await _adaptador().getBolsinLocation(101, "CM-CBA-01")
    assert ubicacion.numeroBolsin == 101
    assert round(ubicacion.latitud, 4) == -31.4201
    assert round(ubicacion.longitud, 4) == -64.1888


@pytest.mark.asyncio
async def test_bolsin_111_no_existe_en_la_api() -> None:
    with pytest.raises(UbicacionNoDisponibleError):
        await _adaptador().getBolsinLocation(111, "CM-CBA-01")


@pytest.mark.asyncio
async def test_codigo_de_cm_que_no_coincide() -> None:
    with pytest.raises(UbicacionNoDisponibleError):
        await _adaptador().getBolsinLocation(101, "CM-ROS-02")


@pytest.mark.asyncio
async def test_api_key_invalida() -> None:
    with pytest.raises(ErrorIntegracionGPS):
        await _adaptador("clave-invalida").getBolsinLocation(101, "CM-CBA-01")
