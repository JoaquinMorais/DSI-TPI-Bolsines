from datetime import datetime

import pytest

from integrations.correo.correo_fake import CorreoFake
from integrations.correo.correo_simulado import CorreoSimulado
from integrations.correo.interfaz_correo import InterfazCorreo
from integrations.gps_tracker.errores import UbicacionNoDisponibleError
from integrations.gps_tracker.gps_tracker_fake import GpsTrackerFake
from integrations.gps_tracker.interfaz_gps_tracker import InterfazGPSTracker
from models.ubicacion_bolsin import UbicacionBolsin

UBICACION_101 = UbicacionBolsin(
    numeroBolsin=101,
    latitud=-31.4201,
    longitud=-64.1888,
    fechaHoraUltimaActualizacion=datetime(2026, 3, 7, 12, 30),
)


def test_gps_fake_cumple_interfaz() -> None:
    fake = GpsTrackerFake(ubicaciones={101: UBICACION_101})
    assert isinstance(fake, InterfazGPSTracker)


def test_correo_fake_cumple_interfaz() -> None:
    assert isinstance(CorreoFake(), InterfazCorreo)
    assert isinstance(CorreoSimulado(), InterfazCorreo)


@pytest.mark.asyncio
async def test_gps_fake_devuelve_y_falla() -> None:
    fake = GpsTrackerFake(ubicaciones={101: UBICACION_101}, sin_ubicacion={111})
    assert await fake.getBolsinLocation(101, "CM-CBA-01") is UBICACION_101
    with pytest.raises(UbicacionNoDisponibleError):
        await fake.getBolsinLocation(111, "CM-CBA-01")
    assert fake.llamadas == [(101, "CM-CBA-01"), (111, "CM-CBA-01")]


@pytest.mark.asyncio
async def test_correo_fake_acumula_y_falla() -> None:
    fake = CorreoFake()
    await fake.enviarMail("gcm@example.test", "Asunto", "Cuerpo")
    assert fake.enviados[0]["destinatario"] == "gcm@example.test"
    fake.fallar = True
    with pytest.raises(RuntimeError):
        await fake.enviarMail("gcm@example.test", "Asunto", "Cuerpo")
