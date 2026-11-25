from config.settings import settings
from integrations.correo.correo_simulado import CorreoSimulado
from integrations.correo.interfaz_correo import InterfazCorreo
from integrations.google_maps.google_maps_adapter import GoogleMapsAdapter
from integrations.google_maps.interfaz_google_maps import InterfazGoogleMaps
from integrations.gps_tracker.gps_tracker_geopulse_mtr900 import (
    GpsTrackerGeoPulseMtr900,
)
from integrations.gps_tracker.gps_tracker_navtrack_qx7a import (
    GpsTrackerNavTrackQx7a,
)
from integrations.gps_tracker.gps_tracker_xtr4500l import GpsTrackerXtr4500l
from integrations.gps_tracker.interfaz_gps_tracker import InterfazGPSTracker
from services.gestor_buscar_bolsines import GestorBuscarBolsines


def crear_gps() -> InterfazGPSTracker:
    modelo = settings.GPS_MODELO.strip().lower()
    if modelo == "xtr4500l":
        return GpsTrackerXtr4500l(settings.GPS_BASE_URL, settings.GPS_API_KEY)
    if modelo == "navtrack":
        return GpsTrackerNavTrackQx7a(settings.GPS_BASE_URL, settings.GPS_API_KEY)
    if modelo == "geopulse":
        return GpsTrackerGeoPulseMtr900(settings.GPS_BASE_URL, settings.GPS_API_KEY)
    raise ValueError(
        f"GPS_MODELO '{settings.GPS_MODELO}' no soportado "
        "(usar xtr4500l, navtrack o geopulse)"
    )


def crear_maps() -> InterfazGoogleMaps:
    return GoogleMapsAdapter()


def crear_correo() -> InterfazCorreo:
    return CorreoSimulado(settings.CORREO_ARCHIVO or None)


def crear_gestor(db) -> GestorBuscarBolsines:
    return GestorBuscarBolsines(db, crear_gps(), crear_maps(), crear_correo())
