import { useEffect, useRef } from "react";
import type { Mapa } from "./api";

declare global {
  interface Window {
    google?: any;
    initBolsinesMap?: () => void;
  }
}

export function MapView({ mapa }: { mapa: Mapa }) {
  const contenedor = useRef<HTMLDivElement>(null);
  const clave = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

  useEffect(() => {
    if (!clave) {
      return;
    }

    const dibujar = () => {
      if (!contenedor.current || !window.google) {
        return;
      }
      const mapaGoogle = new window.google.maps.Map(contenedor.current, {
        center: { lat: mapa.centro.latitud, lng: mapa.centro.longitud },
        zoom: mapa.zoom,
      });
      mapa.marcadores.forEach((marcador) => {
        new window.google.maps.Marker({
          position: { lat: marcador.latitud, lng: marcador.longitud },
          map: mapaGoogle,
          title: `Bolsin ${marcador.numeroBolsin}`,
        });
      });
    };

    if (window.google) {
      dibujar();
      return;
    }

    window.initBolsinesMap = dibujar;
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${clave}&callback=initBolsinesMap`;
    script.async = true;
    document.head.appendChild(script);
  }, [clave, mapa]);

  if (!clave) {
    return (
      <p>
        Falta VITE_GOOGLE_MAPS_API_KEY. Marcadores:{" "}
        {mapa.marcadores.map((m) => m.numeroBolsin).join(", ") || "ninguno"}
      </p>
    );
  }

  return <div ref={contenedor} style={{ height: "420px", width: "100%" }} />;
}
