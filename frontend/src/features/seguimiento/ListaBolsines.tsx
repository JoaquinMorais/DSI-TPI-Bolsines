import {
  Building2,
  CalendarClock,
  MapPin,
  MapPinOff,
  Package,
} from "lucide-react";

import { formatearFecha } from "../../lib/formato";
import type { BolsinSeguimientoOut, MarcadorOut } from "../../types/seguimiento";

export type FilaBolsin = BolsinSeguimientoOut & { marcador?: MarcadorOut };

export function ListaBolsines({
  filas,
  seleccionado,
  onSeleccionar,
  deshabilitado = false,
}: {
  filas: FilaBolsin[];
  seleccionado: number | null;
  onSeleccionar: (numeroBolsin: number) => void;
  deshabilitado?: boolean;
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
              disabled={deshabilitado}
              onClick={() => onSeleccionar(fila.numeroBolsin)}
              className={`group w-full rounded-2xl border p-4 text-left transition duration-200 disabled:cursor-not-allowed disabled:opacity-60 ${
                activo
                  ? "border-brand-300 bg-brand-50/60 shadow-card ring-2 ring-brand-500/20"
                  : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 hover:shadow-card"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span
                    className={`grid h-10 w-10 shrink-0 place-items-center rounded-xl ${
                      activo
                        ? "bg-brand-700 text-white"
                        : "bg-slate-100 text-slate-600 group-hover:bg-slate-200"
                    }`}
                  >
                    <Package className="h-5 w-5" aria-hidden="true" />
                  </span>
                  <div>
                    <p className="font-semibold text-ink-900">
                      Bolsin {fila.numeroBolsin}
                    </p>
                    <p className="text-sm text-slate-500">
                      Precinto: {fila.numeroPrecinto ?? "—"}
                    </p>
                  </div>
                </div>
                <span className="badge bg-slate-100 text-slate-600">
                  <Building2 className="h-3 w-3" aria-hidden="true" />
                  {fila.codigoCMDestino}
                </span>
              </div>
              <div className="mt-3 flex items-center gap-1.5 text-xs">
                {fila.marcador ? (
                  <>
                    <MapPin
                      className="h-3.5 w-3.5 text-brand-600"
                      aria-hidden="true"
                    />
                    <span className="text-slate-600">
                      {formatearFecha(
                        fila.marcador.fechaHoraUltimaActualizacion,
                      )}
                    </span>
                  </>
                ) : (
                  <>
                    <MapPinOff
                      className="h-3.5 w-3.5 text-amber-600"
                      aria-hidden="true"
                    />
                    <span className="text-amber-700">Sin ubicación</span>
                  </>
                )}
                {fila.marcador && (
                  <CalendarClock
                    className="ml-auto h-3.5 w-3.5 text-slate-300"
                    aria-hidden="true"
                  />
                )}
              </div>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
