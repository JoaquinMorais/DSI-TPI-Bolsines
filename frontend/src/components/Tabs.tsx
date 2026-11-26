import { useRef } from "react";
import type { KeyboardEvent } from "react";

export type OpcionTab = { id: string; etiqueta: string };

export function Tabs({
  opciones,
  activa,
  onCambiar,
  etiqueta,
}: {
  opciones: OpcionTab[];
  activa: string;
  onCambiar: (id: string) => void;
  etiqueta: string;
}) {
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});

  function alTeclear(evento: KeyboardEvent<HTMLButtonElement>, indice: number) {
    const total = opciones.length;
    let destino = indice;
    if (evento.key === "ArrowRight") {
      destino = (indice + 1) % total;
    } else if (evento.key === "ArrowLeft") {
      destino = (indice - 1 + total) % total;
    } else if (evento.key === "Home") {
      destino = 0;
    } else if (evento.key === "End") {
      destino = total - 1;
    } else {
      return;
    }
    evento.preventDefault();
    const opcion = opciones[destino];
    onCambiar(opcion.id);
    refs.current[opcion.id]?.focus();
  }

  return (
    <div role="tablist" aria-label={etiqueta} className="flex gap-2">
      {opciones.map((opcion, indice) => {
        const seleccionada = opcion.id === activa;
        return (
          <button
            key={opcion.id}
            ref={(elemento) => {
              refs.current[opcion.id] = elemento;
            }}
            type="button"
            role="tab"
            aria-selected={seleccionada}
            tabIndex={seleccionada ? 0 : -1}
            onClick={() => onCambiar(opcion.id)}
            onKeyDown={(evento) => alTeclear(evento, indice)}
            className={`rounded border px-4 py-2 text-sm ${
              seleccionada
                ? "border-slate-900 bg-slate-900 text-white"
                : "border-slate-300 bg-white text-slate-700"
            }`}
          >
            {opcion.etiqueta}
          </button>
        );
      })}
    </div>
  );
}
