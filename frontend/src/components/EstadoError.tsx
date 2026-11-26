import { CircleAlert, RotateCcw } from "lucide-react";

export function EstadoError({
  mensaje,
  onReintentar,
  compacto = false,
}: {
  mensaje: string;
  onReintentar?: () => void;
  compacto?: boolean;
}) {
  if (compacto) {
    return (
      <div role="alert" className="flex flex-col items-end gap-1 text-sm text-red-700">
        <span className="inline-flex items-center gap-1.5">
          <CircleAlert className="h-4 w-4" aria-hidden="true" />
          {mensaje}
        </span>
        {onReintentar && (
          <button
            type="button"
            onClick={onReintentar}
            className="inline-flex items-center gap-1 text-xs font-medium text-red-800 underline"
          >
            <RotateCcw className="h-3 w-3" aria-hidden="true" />
            Reintentar
          </button>
        )}
      </div>
    );
  }

  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50/70 p-4 text-sm text-red-800"
    >
      <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-red-100 text-red-700">
        <CircleAlert className="h-5 w-5" aria-hidden="true" />
      </span>
      <div className="flex-1">
        <p>{mensaje}</p>
        {onReintentar && (
          <button
            type="button"
            onClick={onReintentar}
            className="btn btn-secondary mt-3"
          >
            <RotateCcw className="h-4 w-4" aria-hidden="true" />
            Reintentar
          </button>
        )}
      </div>
    </div>
  );
}
