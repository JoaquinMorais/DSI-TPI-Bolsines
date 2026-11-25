from integrations.google_maps.interfaz_google_maps import InterfazGoogleMaps
from models.mapa_bolsines import Coordenada, MapaBolsines
from models.ubicacion_bolsin import UbicacionBolsin

ZOOM_POR_DEFECTO = 6
CENTRO_POR_DEFECTO = Coordenada(latitud=-34.6037, longitud=-58.3816)


class GoogleMapsAdapter(InterfazGoogleMaps):
    def obtenerMapa(self, ubicaciones: list[UbicacionBolsin]) -> MapaBolsines:
        if ubicaciones:
            centro = Coordenada(
                latitud=sum(u.latitud for u in ubicaciones) / len(ubicaciones),
                longitud=sum(u.longitud for u in ubicaciones) / len(ubicaciones),
            )
        else:
            centro = CENTRO_POR_DEFECTO
        return MapaBolsines(
            centro=centro,
            zoom=ZOOM_POR_DEFECTO,
            marcadores=list(ubicaciones),
        )
