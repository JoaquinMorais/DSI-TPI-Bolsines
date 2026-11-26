import { CircleCheck, CircleX, X } from "lucide-react";

export type TipoToast = "exito" | "error";

export function Toast({
  mensaje,
  tipo,
  onCerrar,
}: {
  mensaje: string | null;
  tipo: TipoToast;
  onCerrar: () => void;
}) {
  if (!mensaje) {
    return null;
  }

  const Icono = tipo === "exito" ? CircleCheck : CircleX;

  return (
    <div
      role="status"
      aria-live="polite"
      className={`fixed bottom-5 right-5 z-50 flex max-w-sm items-start gap-3 rounded-2xl px-4 py-3 text-sm text-white shadow-lg animate-slide-up ${
        tipo === "exito" ? "bg-emerald-600" : "bg-red-600"
      }`}
    >
      <Icono className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
      <span className="flex-1">{mensaje}</span>
      <button
        type="button"
        onClick={onCerrar}
        aria-label="Cerrar notificación"
        className="rounded-full p-1 transition hover:bg-white/15"
      >
        <X className="h-4 w-4" aria-hidden="true" />
      </button>
    </div>
  );
}
