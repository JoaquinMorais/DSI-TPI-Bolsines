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
@pytest.mark.parametrize(
    ("numero", "origen", "latitud", "longitud"),
    [
        (120, "CM-CBA-01", -32.4075, -63.2402),
        (121, "CM-CBA-01", -31.4279, -62.0820),
        (123, "CM-CBA-02", -32.8895, -68.8458),
        (124, "CM-CBA-02", -34.6037, -58.3816),
    ],
)
async def test_bolsines_nuevos_ubicados(
    numero: int, origen: str, latitud: float, longitud: float
) -> None:
    ubicacion = await _adaptador().getBolsinLocation(numero, origen)
    assert ubicacion.numeroBolsin == numero
    assert round(ubicacion.latitud, 4) == latitud
    assert round(ubicacion.longitud, 4) == longitud


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("numero", "origen"),
    [
        (111, "CM-CBA-01"),
        (122, "CM-CBA-01"),
        (125, "CM-CBA-03"),
        (126, "CM-CBA-03"),
        (127, "CM-CBA-03"),
    ],
)
async def test_bolsines_ausentes_en_la_api(numero: int, origen: str) -> None:
    with pytest.raises(UbicacionNoDisponibleError):
        await _adaptador().getBolsinLocation(numero, origen)


@pytest.mark.asyncio
async def test_codigo_de_cm_que_no_coincide() -> None:
    with pytest.raises(UbicacionNoDisponibleError):
        await _adaptador().getBolsinLocation(101, "CM-ROS-02")


@pytest.mark.asyncio
async def test_api_key_invalida() -> None:
    with pytest.raises(ErrorIntegracionGPS):
        await _adaptador("clave-invalida").getBolsinLocation(101, "CM-CBA-01")
