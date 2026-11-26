import { useEffect, useRef } from "react";
import type { ReactNode } from "react";

export function DialogoConfirmacion({
  abierto,
  titulo,
  children,
  textoConfirmar = "Confirmar",
  textoRechazar,
  onConfirmar,
  onRechazar,
  onCancelar,
  cargando = false,
}: {
  abierto: boolean;
  titulo: string;
  children?: ReactNode;
  textoConfirmar?: string;
  textoRechazar?: string;
  onConfirmar: () => void;
  onRechazar?: () => void;
  onCancelar: () => void;
  cargando?: boolean;
}) {
  const cancelarRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (abierto) {
      cancelarRef.current?.focus();
    }
  }, [abierto]);

  useEffect(() => {
    if (!abierto) {
      return;
    }
    function alPresionar(evento: KeyboardEvent) {
      if (evento.key === "Escape" && !cargando) {
        onCancelar();
      }
    }
    document.addEventListener("keydown", alPresionar);
    return () => document.removeEventListener("keydown", alPresionar);
  }, [abierto, cargando, onCancelar]);

  if (!abierto) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialogo-titulo"
        className="w-full max-w-md rounded bg-white p-5 shadow-lg"
      >
        <h2 id="dialogo-titulo" className="text-lg font-semibold">
          {titulo}
        </h2>
        <div className="mt-2 text-sm text-slate-700">{children}</div>
        <div className="mt-5 flex flex-wrap justify-end gap-2">
          <button
            ref={cancelarRef}
            type="button"
            onClick={onCancelar}
            disabled={cargando}
            className="rounded border border-slate-300 px-3 py-2 text-sm"
          >
            Cancelar
          </button>
          {onRechazar && (
            <button
              type="button"
              onClick={onRechazar}
              disabled={cargando}
              className="rounded border border-slate-300 px-3 py-2 text-sm"
            >
              {textoRechazar ?? "No enviar"}
            </button>
          )}
          <button
            type="button"
            onClick={onConfirmar}
            disabled={cargando}
            className="rounded bg-slate-900 px-3 py-2 text-sm text-white disabled:opacity-50"
          >
            {cargando ? "Enviando..." : textoConfirmar}
          </button>
        </div>
      </div>
    </div>
  );
}
