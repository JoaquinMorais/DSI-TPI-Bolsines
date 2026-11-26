import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";

import type { MapaBolsinesOut } from "../types/seguimiento";

function crearIcono(numeroBolsin: number, activo: boolean) {
  const tamano = activo ? 38 : 30;
  return L.divIcon({
    className: "",
    html: `<span style="display:flex;align-items:center;justify-content:center;width:${tamano}px;height:${tamano}px;border-radius:9999px;background:${
      activo ? "#0f2a43" : "#0f766e"
    };border:3px solid #ffffff;box-shadow:0 8px 20px rgba(15,42,67,0.35);color:#ffffff;font-size:11px;font-weight:700;line-height:1;">${numeroBolsin}</span>`,
    iconSize: [tamano, tamano],
    iconAnchor: [tamano / 2, tamano / 2],
    popupAnchor: [0, -tamano / 2],
  });
}

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
        scrollWheelZoom={false}
        className="h-[26rem] w-full"
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="mapa-tiles"
        />
        {mapa.marcadores.map((marcador) => (
          <Marker
            key={marcador.numeroBolsin}
            position={[marcador.latitud, marcador.longitud]}
            title={`Bolsin ${marcador.numeroBolsin}`}
            alt={`Bolsin ${marcador.numeroBolsin}`}
            icon={crearIcono(
              marcador.numeroBolsin,
              seleccionado === marcador.numeroBolsin,
            )}
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
