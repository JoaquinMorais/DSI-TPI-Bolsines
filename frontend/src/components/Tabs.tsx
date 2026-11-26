import { useRef } from "react";
import type { KeyboardEvent, ReactNode } from "react";

export type OpcionTab = { id: string; etiqueta: string; icono?: ReactNode };

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
    <div
      role="tablist"
      aria-label={etiqueta}
      className="inline-flex gap-1 rounded-full border border-slate-200 bg-slate-100 p-1"
    >
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
            className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
              seleccionada
                ? "bg-white text-ink-900 shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            {opcion.icono}
            {opcion.etiqueta}
          </button>
        );
      })}
    </div>
  );
}
