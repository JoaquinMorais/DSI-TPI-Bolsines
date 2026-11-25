from datetime import datetime

import pytest

from integrations.gps_tracker.errores import ErrorIntegracionGPS
from integrations.gps_tracker.gps_tracker_geopulse_mtr900 import (
    parsear_ubicacion_geopulse,
)
from integrations.gps_tracker.gps_tracker_navtrack_qx7a import (
    parsear_ubicacion_navtrack,
)
from integrations.gps_tracker.gps_tracker_xtr4500l import parsear_ubicacion

ITEM_XTR = {
    "numeroBolsin": 101,
    "latitud": -31.4201,
    "longitud": -64.1888,
    "fechaHoraUltimaActualizacion": "2026-03-07T12:30:00",
}


def test_parser_xtr() -> None:
    ubicacion = parsear_ubicacion(101, {"items": [ITEM_XTR]})
    assert ubicacion.numeroBolsin == 101
    assert ubicacion.latitud == -31.4201
    assert ubicacion.fechaHoraUltimaActualizacion == datetime(2026, 3, 7, 12, 30, 0)


@pytest.mark.parametrize("payload", [{"items": []}, {"items": [ITEM_XTR, ITEM_XTR]}, {}])
def test_parser_xtr_invalido(payload: dict) -> None:
    with pytest.raises(ErrorIntegracionGPS):
        parsear_ubicacion(101, payload)


def test_parser_navtrack_con_segundos() -> None:
    ubicacion = parsear_ubicacion_navtrack(
        101, "101,-31.4201,-64.1888,2026-03-07T12:30:00"
    )
    assert ubicacion.fechaHoraUltimaActualizacion == datetime(2026, 3, 7, 12, 30)


def test_parser_navtrack_sin_segundos() -> None:
    ubicacion = parsear_ubicacion_navtrack(
        101, "101,-31.4201,-64.1888,2026-03-07T12:30"
    )
    assert ubicacion.longitud == -64.1888


@pytest.mark.parametrize(
    "texto",
    ["basura", "101,-31.4201,-64.1888", "101,x,-64.1888,2026-03-07T12:30"],
)
def test_parser_navtrack_invalido(texto: str) -> None:
    with pytest.raises(ErrorIntegracionGPS):
        parsear_ubicacion_navtrack(101, texto)


def test_parser_navtrack_otro_bolsin() -> None:
    with pytest.raises(ErrorIntegracionGPS):
        parsear_ubicacion_navtrack(999, "101,-31.4201,-64.1888,2026-03-07T12:30")


def test_parser_geopulse() -> None:
    ubicacion = parsear_ubicacion_geopulse(
        101, [[101, -31.4201, -64.1888, "2026-03-07T12:30:00"]]
    )
    assert ubicacion.numeroBolsin == 101
    assert ubicacion.latitud == -31.4201


@pytest.mark.parametrize("payload", [[], [[101, -31.4201]], "basura", [[999, 1, 2, "2026-03-07T12:30:00"]]])
def test_parser_geopulse_invalido(payload: object) -> None:
    with pytest.raises(ErrorIntegracionGPS):
        parsear_ubicacion_geopulse(101, payload)
