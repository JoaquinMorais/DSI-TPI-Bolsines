import { Loader2 } from "lucide-react";

export function EstadoCarga({ mensaje = "Cargando..." }: { mensaje?: string }) {
  return (
    <p
      role="status"
      className="inline-flex items-center gap-2 text-sm text-slate-500"
    >
      <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
      {mensaje}
    </p>
  );
}
