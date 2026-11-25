import { formatearFecha } from "../../lib/formato";
import type { BolsinSeguimientoOut, MarcadorOut } from "../../types/seguimiento";

export type FilaBolsin = BolsinSeguimientoOut & { marcador?: MarcadorOut };

export function ListaBolsines({
  filas,
  seleccionado,
  onSeleccionar,
}: {
  filas: FilaBolsin[];
  seleccionado: number | null;
  onSeleccionar: (numeroBolsin: number) => void;
}) {
  return (
    <ul className="space-y-2" aria-label="Bolsines enviados">
      {filas.map((fila) => {
        const activo = seleccionado === fila.numeroBolsin;
        return (
          <li key={fila.numeroBolsin}>
            <button
              type="button"
              aria-pressed={activo}
              onClick={() => onSeleccionar(fila.numeroBolsin)}
              className={`w-full rounded border p-3 text-left ${
                activo
                  ? "border-slate-900 bg-amber-50"
                  : "border-slate-200 bg-white hover:bg-slate-50"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold">Bolsin {fila.numeroBolsin}</span>
                <span className="text-sm text-slate-600">
                  {fila.codigoCMDestino}
                </span>
              </div>
              <div className="text-sm text-slate-600">
                Precinto: {fila.numeroPrecinto ?? "—"}
              </div>
              <div className="text-xs text-slate-500">
                {fila.marcador
                  ? formatearFecha(fila.marcador.fechaHoraUltimaActualizacion)
                  : "Sin ubicación"}
              </div>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
