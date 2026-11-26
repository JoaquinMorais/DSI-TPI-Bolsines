import {
  ArrowRight,
  Boxes,
  Building2,
  MapPinned,
  ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";

import { useUsuarioActual } from "../hooks/useUsuarioActual";

const FLUJOS = ["A1", "A2", "A3", "A4", "A5"];

export function HomePage() {
  const { data, isLoading } = useUsuarioActual();

  return (
    <section className="animate-fade-in space-y-6">
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-ink-950 via-ink-900 to-brand-800 px-6 py-10 text-white shadow-card sm:px-10 sm:py-14">
        <div
          className="absolute -right-20 -top-24 h-64 w-64 rounded-full bg-brand-400/20 blur-3xl"
          aria-hidden="true"
        />
        <div
          className="absolute -bottom-28 left-1/3 h-64 w-64 rounded-full bg-brand-300/10 blur-3xl"
          aria-hidden="true"
        />
        <div className="relative max-w-2xl space-y-4">
          <span className="badge bg-white/10 text-brand-100 ring-1 ring-white/15">
            <MapPinned className="h-3.5 w-3.5" aria-hidden="true" />
            Sistema de Bolsines
          </span>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
            Seguimiento de bolsines entre comisiones médicas
          </h1>
          <p className="max-w-xl text-sm text-slate-200 sm:text-base">
            Consultá en el mapa los bolsines enviados desde tu comisión médica,
            revisá su última ubicación y notificá al gerente de la CM destino.
          </p>
          <Link
            to="/seguimiento"
            className="btn bg-white text-ink-900 shadow-sm hover:bg-brand-50"
          >
            <MapPinned className="h-4 w-4" aria-hidden="true" />
            Consultar seguimiento
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="card p-5 md:col-span-2">
          <div className="flex items-start gap-4">
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-brand-50 text-brand-700">
              <Boxes className="h-5 w-5" aria-hidden="true" />
            </span>
            <div>
              <h2 className="section-title">Acceso rápido</h2>
              <p className="mt-1 text-sm text-slate-600">
                Iniciá el seguimiento para ver los bolsines Enviados de tu CM,
                filtrarlos por precinto o CM destino y notificar su ubicación.
              </p>
              <Link
                to="/seguimiento"
                className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-brand-700 hover:text-brand-800"
              >
                Ir a seguimiento
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            </div>
          </div>
        </div>

        <div className="card p-5">
          <div className="flex items-start gap-3">
            <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-ink-50 text-ink-700">
              <Building2 className="h-5 w-5" aria-hidden="true" />
            </span>
            <div className="min-w-0">
              <h2 className="section-title">Tu comisión</h2>
              {isLoading && (
                <p className="mt-1 text-sm text-slate-500">Cargando...</p>
              )}
              {data && (
                <>
                  <p className="mt-1 truncate text-sm font-medium text-slate-800">
                    {data.nombre} {data.apellido}
                  </p>
                  <p className="text-sm text-slate-600">{data.rol}</p>
                  <span className="badge mt-2 bg-brand-50 text-brand-800">
                    {data.codigoCM}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="card flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-slate-100 text-slate-600">
            <ShieldCheck className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <h2 className="section-title">Flujos cubiertos</h2>
            <p className="text-sm text-slate-600">
              Flujo principal y alternativos del CU 36.
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {FLUJOS.map((flujo) => (
            <span
              key={flujo}
              className="badge border border-slate-200 bg-slate-50 text-slate-600"
            >
              {flujo}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
