import { mensajeDeError } from "../lib/errores";
import { useUsuarioActual } from "../hooks/useUsuarioActual";
import { EstadoCarga } from "./EstadoCarga";
import { EstadoError } from "./EstadoError";

export function Header() {
  const { data, isLoading, isError, error, refetch } = useUsuarioActual();

  return (
    <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3">
      <span className="text-lg font-semibold text-slate-900">Bolsines</span>
      <div className="text-right">
        {isLoading && <EstadoCarga mensaje="Cargando usuario..." />}
        {isError && (
          <EstadoError
            mensaje={mensajeDeError(error)}
            onReintentar={() => refetch()}
          />
        )}
        {data && (
          <div className="leading-tight">
            <p className="text-sm font-medium text-slate-900">
              {data.nombre} {data.apellido}
            </p>
            <p className="text-xs text-slate-600">
              {data.rol} · {data.codigoCM}
            </p>
            <p className="text-xs text-slate-600">{data.mail}</p>
          </div>
        )}
      </div>
    </header>
  );
}
