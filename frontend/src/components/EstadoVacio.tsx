import { PackageOpen } from "lucide-react";
import type { ReactNode } from "react";

export function EstadoVacio({
  titulo,
  descripcion,
  accion,
}: {
  titulo: string;
  descripcion?: string;
  accion?: ReactNode;
}) {
  return (
    <div className="card flex flex-col items-center gap-3 p-8 text-center">
      <span className="grid h-12 w-12 place-items-center rounded-2xl bg-brand-50 text-brand-700">
        <PackageOpen className="h-6 w-6" aria-hidden="true" />
      </span>
      <p className="text-base font-semibold text-ink-900">{titulo}</p>
      {descripcion && (
        <p className="max-w-md text-sm text-slate-600">{descripcion}</p>
      )}
      {accion && <div className="mt-1">{accion}</div>}
    </div>
  );
}
