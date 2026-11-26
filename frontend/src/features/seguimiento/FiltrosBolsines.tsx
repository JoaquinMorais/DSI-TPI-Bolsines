import { Building2, FilterX, Search, SlidersHorizontal } from "lucide-react";

export function FiltrosBolsines({
  precinto,
  cmDestino,
  opcionesCM,
  onPrecinto,
  onCMDestino,
  onLimpiar,
}: {
  precinto: string;
  cmDestino: string;
  opcionesCM: string[];
  onPrecinto: (valor: string) => void;
  onCMDestino: (valor: string) => void;
  onLimpiar: () => void;
}) {
  return (
    <div className="card p-4">
      <div className="mb-3 flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-slate-100 text-slate-600">
          <SlidersHorizontal className="h-4 w-4" aria-hidden="true" />
        </span>
        <h2 className="section-title">Filtros</h2>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <label className="text-sm font-medium text-slate-700">
          <span className="mb-1.5 flex items-center gap-1.5">
            <Search className="h-3.5 w-3.5 text-slate-400" aria-hidden="true" />
            Precinto
          </span>
          <input
            value={precinto}
            onChange={(evento) => onPrecinto(evento.target.value)}
            placeholder="Buscar precinto"
            className="input"
          />
        </label>
        <label className="text-sm font-medium text-slate-700">
          <span className="mb-1.5 flex items-center gap-1.5">
            <Building2
              className="h-3.5 w-3.5 text-slate-400"
              aria-hidden="true"
            />
            CM destino
          </span>
          <select
            value={cmDestino}
            onChange={(evento) => onCMDestino(evento.target.value)}
            className="input"
          >
            <option value="">Todas</option>
            {opcionesCM.map((codigo) => (
              <option key={codigo} value={codigo}>
                {codigo}
              </option>
            ))}
          </select>
        </label>
        <div className="flex items-end">
          <button
            type="button"
            onClick={onLimpiar}
            className="btn btn-secondary w-full sm:w-auto"
          >
            <FilterX className="h-4 w-4" aria-hidden="true" />
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>
  );
}
