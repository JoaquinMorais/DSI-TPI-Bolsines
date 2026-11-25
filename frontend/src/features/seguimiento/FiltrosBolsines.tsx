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
    <div className="grid gap-3 sm:grid-cols-3">
      <label className="text-sm text-slate-700">
        Precinto
        <input
          value={precinto}
          onChange={(evento) => onPrecinto(evento.target.value)}
          placeholder="Buscar precinto"
          className="mt-1 w-full rounded border border-slate-300 p-2"
        />
      </label>
      <label className="text-sm text-slate-700">
        CM destino
        <select
          value={cmDestino}
          onChange={(evento) => onCMDestino(evento.target.value)}
          className="mt-1 w-full rounded border border-slate-300 p-2"
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
          className="rounded border border-slate-300 px-3 py-2 text-sm"
        >
          Limpiar filtros
        </button>
      </div>
    </div>
  );
}
