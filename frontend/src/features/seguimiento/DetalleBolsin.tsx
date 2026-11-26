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
    <aside className="rounded border border-slate-200 bg-white p-4">
      <h2 className="text-lg font-semibold">Bolsin {bolsin.numeroBolsin}</h2>
      <dl className="mt-2 grid grid-cols-2 gap-1 text-sm">
        <dt className="text-slate-500">CM destino</dt>
        <dd>{bolsin.codigoCMDestino}</dd>
        <dt className="text-slate-500">Precinto</dt>
        <dd>{bolsin.numeroPrecinto ?? "—"}</dd>
        <dt className="text-slate-500">Coordenadas</dt>
        <dd>
          {ubicacion
            ? `${ubicacion.latitud}, ${ubicacion.longitud}`
            : "Sin ubicación"}
        </dd>
        <dt className="text-slate-500">Última actualización</dt>
        <dd>
          {ubicacion
            ? formatearFecha(ubicacion.fechaHoraUltimaActualizacion)
            : "—"}
        </dd>
      </dl>
      {correoEnviadoEn && (
        <p className="mt-3 text-sm text-emerald-700">
          Correo enviado el {correoEnviadoEn}
        </p>
      )}
      {resultado && <p className="mt-3 text-sm text-slate-700">{resultado}</p>}
      {onNotificar && (
        <button
          type="button"
          onClick={onNotificar}
          disabled={notificarDeshabilitado}
          className="mt-4 w-full rounded bg-slate-900 px-3 py-2 text-sm text-white disabled:opacity-50"
        >
          Notificar ubicación al Gerente de la CM destino
        </button>
      )}
    </aside>
  );
}
