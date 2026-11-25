from integrations.correo.correo_simulado import CorreoSimulado
from integrations.correo.interfaz_correo import InterfazCorreo
from integrations.google_maps.google_maps_adapter import GoogleMapsAdapter
from integrations.google_maps.interfaz_google_maps import InterfazGoogleMaps
from integrations.gps_tracker.gps_tracker_xtr4500l import GpsTrackerXtr4500l
from integrations.gps_tracker.interfaz_gps_tracker import InterfazGPSTracker
from config.settings import settings
from services.gestor_buscar_bolsines import GestorBuscarBolsines


def crear_gps() -> InterfazGPSTracker:
    return GpsTrackerXtr4500l(settings.GPS_BASE_URL, settings.GPS_API_KEY_XTR4500L)


def crear_maps() -> InterfazGoogleMaps:
    return GoogleMapsAdapter()


def crear_correo() -> InterfazCorreo:
    return CorreoSimulado(settings.CORREO_ARCHIVO or None)


def crear_gestor(db) -> GestorBuscarBolsines:
    return GestorBuscarBolsines(db, crear_gps(), crear_maps(), crear_correo())
