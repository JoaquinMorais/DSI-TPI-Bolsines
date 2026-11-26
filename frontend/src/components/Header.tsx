import { Boxes, Home, MapPinned, UserRound } from "lucide-react";
import { Link, NavLink } from "react-router-dom";

import { useUsuarioActual } from "../hooks/useUsuarioActual";
import { mensajeDeError } from "../lib/errores";
import { EstadoCarga } from "./EstadoCarga";
import { EstadoError } from "./EstadoError";

function claseNav({ isActive }: { isActive: boolean }) {
  return `inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-medium transition ${
    isActive
      ? "bg-brand-50 text-brand-800"
      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
  }`;
}

function iniciales(nombre: string, apellido: string) {
  return `${nombre.charAt(0)}${apellido.charAt(0)}`.toUpperCase();
}

export function Header() {
  const { data, isLoading, isError, error, refetch } = useUsuarioActual();

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
        <Link to="/" className="flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-gradient-to-br from-ink-900 to-brand-700 text-white shadow-sm">
            <Boxes className="h-5 w-5" aria-hidden="true" />
          </span>
          <span>
            <span className="block text-base font-semibold tracking-tight text-ink-900">
              Bolsines
            </span>
            <span className="hidden text-xs text-slate-500 sm:block">
              Seguimiento entre comisiones médicas
            </span>
          </span>
        </Link>

        <nav
          aria-label="Navegación principal"
          className="order-3 flex w-full items-center gap-1 border-t border-slate-100 pt-2 md:order-none md:w-auto md:border-0 md:pt-0"
        >
          <NavLink to="/" end className={claseNav}>
            <Home className="h-4 w-4" aria-hidden="true" />
            Inicio
          </NavLink>
          <NavLink to="/seguimiento" className={claseNav}>
            <MapPinned className="h-4 w-4" aria-hidden="true" />
            Seguimiento
          </NavLink>
        </nav>

        <div className="text-right">
          {isLoading && <EstadoCarga mensaje="Cargando usuario..." />}
          {isError && (
            <EstadoError
              mensaje={mensajeDeError(error)}
              onReintentar={() => refetch()}
              compacto
            />
          )}
          {data && (
            <div className="flex items-center gap-3">
              <div className="hidden text-right sm:block">
                <p className="text-sm font-medium text-ink-900">
                  {data.nombre} {data.apellido}
                </p>
                <div className="mt-1 flex flex-wrap items-center justify-end gap-1.5">
                  <span className="badge bg-brand-50 text-brand-800">
                    <UserRound className="h-3 w-3" aria-hidden="true" />
                    {data.rol}
                  </span>
                  <span className="badge bg-slate-100 text-slate-600">
                    {data.codigoCM}
                  </span>
                </div>
                <p className="mt-1 hidden text-xs text-slate-500 lg:block">
                  {data.mail}
                </p>
              </div>
              <span
                className="grid h-10 w-10 place-items-center rounded-full bg-ink-900 text-sm font-semibold text-white ring-4 ring-white"
                aria-hidden="true"
              >
                {iniciales(data.nombre, data.apellido)}
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
