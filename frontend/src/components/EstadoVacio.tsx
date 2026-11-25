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
    <div className="rounded border border-dashed border-slate-300 bg-white p-6 text-center">
      <p className="text-lg font-medium text-slate-800">{titulo}</p>
      {descripcion && <p className="mt-1 text-sm text-slate-600">{descripcion}</p>}
      {accion && <div className="mt-4">{accion}</div>}
    </div>
  );
}
