import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

import icono from "leaflet/dist/images/marker-icon.png";
import icono2x from "leaflet/dist/images/marker-icon-2x.png";
import sombra from "leaflet/dist/images/marker-shadow.png";
import type { MapaBolsinesOut } from "../types/seguimiento";

L.Icon.Default.mergeOptions({
  iconUrl: icono,
  iconRetinaUrl: icono2x,
  shadowUrl: sombra,
});

export function MapaBolsines({ mapa }: { mapa: MapaBolsinesOut }) {
  return (
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
        >
          <Popup>Bolsin {marcador.numeroBolsin}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
