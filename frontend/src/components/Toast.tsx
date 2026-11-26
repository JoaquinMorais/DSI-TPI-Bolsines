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
  return (
    <div
      role="status"
      aria-live="polite"
      className={`fixed bottom-4 right-4 z-50 max-w-sm rounded px-4 py-3 text-sm text-white shadow ${
        tipo === "exito" ? "bg-emerald-600" : "bg-red-600"
      }`}
    >
      <span>{mensaje}</span>
      <button type="button" onClick={onCerrar} className="ml-3 underline">
        Cerrar
      </button>
    </div>
  );
}
