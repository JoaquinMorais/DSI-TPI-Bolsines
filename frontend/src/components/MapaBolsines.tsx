import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

import icono from "leaflet/dist/images/marker-icon.png";
import icono2x from "leaflet/dist/images/marker-icon-2x.png";
import sombra from "leaflet/dist/images/marker-shadow.png";
import type { MapaBolsinesOut } from "../types/seguimiento";

const iconoBase = L.icon({
  iconUrl: icono,
  iconRetinaUrl: icono2x,
  shadowUrl: sombra,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const iconoSeleccionado = L.icon({
  iconUrl: icono,
  iconRetinaUrl: icono2x,
  shadowUrl: sombra,
  iconSize: [36, 59],
  iconAnchor: [18, 59],
  popupAnchor: [1, -48],
  shadowSize: [50, 50],
});

export function MapaBolsines({
  mapa,
  seleccionado = null,
  onSeleccionar,
}: {
  mapa: MapaBolsinesOut;
  seleccionado?: number | null;
  onSeleccionar?: (numeroBolsin: number) => void;
}) {
  return (
    <div role="region" aria-label="Mapa de bolsines">
      <p className="sr-only">
        El mapa es complementario. Usa la lista de bolsines para navegar con el
        teclado.
      </p>
      <MapContainer
        center={[mapa.centro.latitud, mapa.centro.longitud]}
        zoom={mapa.zoom}
        className="h-96 w-full rounded-lg"
      >
        <TileLayer
          attribution="&copy; OpenStreetMap"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {mapa.marcadores.map((marcador) => (
          <Marker
            key={marcador.numeroBolsin}
            position={[marcador.latitud, marcador.longitud]}
            title={`Bolsin ${marcador.numeroBolsin}`}
            alt={`Bolsin ${marcador.numeroBolsin}`}
            icon={
              seleccionado === marcador.numeroBolsin
                ? iconoSeleccionado
                : iconoBase
            }
            eventHandlers={{
              click: () => onSeleccionar?.(marcador.numeroBolsin),
            }}
          >
            <Popup>Bolsin {marcador.numeroBolsin}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
