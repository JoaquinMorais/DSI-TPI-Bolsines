import { BellRing } from "lucide-react";
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
  varianteConfirmar = "primario",
  icono,
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
  varianteConfirmar?: "primario" | "peligro";
  icono?: ReactNode;
}) {
  const cancelarRef = useRef<HTMLButtonElement>(null);
  const dialogoRef = useRef<HTMLDivElement>(null);

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
        return;
      }
      if (evento.key !== "Tab" || !dialogoRef.current) {
        return;
      }
      const botones = Array.from(
        dialogoRef.current.querySelectorAll<HTMLButtonElement>(
          "button:not([disabled])",
        ),
      );
      if (botones.length === 0) {
        return;
      }
      const primero = botones[0];
      const ultimo = botones[botones.length - 1];
      if (evento.shiftKey && document.activeElement === primero) {
        evento.preventDefault();
        ultimo.focus();
      } else if (!evento.shiftKey && document.activeElement === ultimo) {
        evento.preventDefault();
        primero.focus();
      }
    }
    document.addEventListener("keydown", alPresionar);
    return () => document.removeEventListener("keydown", alPresionar);
  }, [abierto, cargando, onCancelar]);

  if (!abierto) {
    return null;
  }

  const claseConfirmar =
    varianteConfirmar === "peligro"
      ? "bg-red-600 text-white hover:bg-red-700"
      : "bg-ink-900 text-white hover:bg-ink-800";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink-950/40 p-4 backdrop-blur-sm">
      <div
        ref={dialogoRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialogo-titulo"
        aria-describedby="dialogo-descripcion"
        className="w-full max-w-md animate-slide-up rounded-2xl border border-slate-200 bg-white p-5 shadow-card-hover"
      >
        <div className="flex items-start gap-3">
          <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-brand-50 text-brand-700">
            {icono ?? <BellRing className="h-5 w-5" aria-hidden="true" />}
          </span>
          <h2
            id="dialogo-titulo"
            className="mt-1 text-lg font-semibold tracking-tight text-ink-900"
          >
            {titulo}
          </h2>
        </div>
        <div
          id="dialogo-descripcion"
          className="mt-3 text-sm leading-relaxed text-slate-600"
        >
          {children}
        </div>
        <div className="mt-5 flex flex-wrap justify-end gap-2">
          <button
            ref={cancelarRef}
            type="button"
            onClick={onCancelar}
            disabled={cargando}
            className="btn btn-ghost"
          >
            Cancelar
          </button>
          {onRechazar && (
            <button
              type="button"
              onClick={onRechazar}
              disabled={cargando}
              className="btn btn-secondary"
            >
              {textoRechazar ?? "No enviar"}
            </button>
          )}
          <button
            type="button"
            onClick={onConfirmar}
            disabled={cargando}
            className={`btn ${claseConfirmar}`}
          >
            {cargando ? "Enviando..." : textoConfirmar}
          </button>
        </div>
      </div>
    </div>
  );
}
