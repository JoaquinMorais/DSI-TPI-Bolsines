import {
  Bell,
  Building2,
  Clock,
  MapPin,
  MapPinOff,
  Package,
  ScanBarcode,
} from "lucide-react";

import { formatearFecha } from "../../lib/formato";
import type { SeleccionBolsinResponse } from "../../types/seguimiento";

export function DetalleBolsin({
  detalle,
  correoEnviadoEn,
  resultado,
  onNotificar,
  notificarDeshabilitado = false,
}: {
  detalle: SeleccionBolsinResponse;
  correoEnviadoEn?: string | null;
  resultado?: string | null;
  onNotificar?: () => void;
  notificarDeshabilitado?: boolean;
}) {
  const { bolsin, ubicacion } = detalle;

  return (
    <aside className="card animate-slide-up p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-ink-900 text-white">
            <Package className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-ink-900">
              Bolsin {bolsin.numeroBolsin}
            </h2>
            <p className="text-xs text-slate-500">Detalle de ubicación</p>
          </div>
        </div>
        <span
          className={`badge ${
            ubicacion
              ? "bg-emerald-50 text-emerald-700"
              : "bg-amber-50 text-amber-800"
          }`}
        >
          {ubicacion ? (
            <MapPin className="h-3 w-3" aria-hidden="true" />
          ) : (
            <MapPinOff className="h-3 w-3" aria-hidden="true" />
          )}
          {ubicacion ? "Con ubicación" : "Sin ubicación"}
        </span>
      </div>

      <dl className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-xl bg-slate-50 p-3">
          <dt className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">
            <Building2 className="h-3.5 w-3.5" aria-hidden="true" />
            CM destino
          </dt>
          <dd className="mt-1 text-sm font-medium text-ink-900">
            {bolsin.codigoCMDestino}
          </dd>
        </div>
        <div className="rounded-xl bg-slate-50 p-3">
          <dt className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">
            <ScanBarcode className="h-3.5 w-3.5" aria-hidden="true" />
            Precinto
          </dt>
          <dd className="mt-1 text-sm font-medium text-ink-900">
            {bolsin.numeroPrecinto ?? "—"}
          </dd>
        </div>
        <div className="rounded-xl bg-slate-50 p-3">
          <dt className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">
            <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
            Coordenadas
          </dt>
          <dd className="mt-1 text-sm font-medium text-ink-900">
            {ubicacion
              ? `${ubicacion.latitud}, ${ubicacion.longitud}`
              : "Sin ubicación"}
          </dd>
        </div>
        <div className="rounded-xl bg-slate-50 p-3">
          <dt className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-slate-500">
            <Clock className="h-3.5 w-3.5" aria-hidden="true" />
            Última actualización
          </dt>
          <dd className="mt-1 text-sm font-medium text-ink-900">
            {ubicacion
              ? formatearFecha(ubicacion.fechaHoraUltimaActualizacion)
              : "—"}
          </dd>
        </div>
      </dl>

      {!ubicacion && (
        <p className="mt-3 rounded-xl border border-amber-200 bg-amber-50/70 p-3 text-sm text-amber-800">
          El GPS no informó una ubicación para este bolsín. La sesión sigue
          abierta para consultar otros bolsines.
        </p>
      )}

      {correoEnviadoEn && (
        <p className="mt-3 rounded-xl bg-emerald-50 p-3 text-sm text-emerald-700">
          Correo enviado el {correoEnviadoEn}
        </p>
      )}

      {resultado && (
        <p className="mt-3 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
          {resultado}
        </p>
      )}

      {onNotificar && (
        <button
          type="button"
          onClick={onNotificar}
          disabled={notificarDeshabilitado}
          className="btn btn-primary mt-4 w-full"
        >
          <Bell className="h-4 w-4" aria-hidden="true" />
          Notificar ubicación al Gerente de la CM destino
        </button>
      )}
    </aside>
  );
}
