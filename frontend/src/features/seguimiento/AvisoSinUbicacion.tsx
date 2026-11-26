import { TriangleAlert } from "lucide-react";

import type { SinUbicacionOut } from "../../types/seguimiento";

export function AvisoSinUbicacion({
  sinUbicacion,
}: {
  sinUbicacion: SinUbicacionOut[];
}) {
  if (sinUbicacion.length === 0) {
    return null;
  }

  return (
    <div
      role="status"
      className="animate-fade-in rounded-2xl border border-amber-200 bg-amber-50/80 p-4"
    >
      <div className="flex items-start gap-3">
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-amber-100 text-amber-700">
          <TriangleAlert className="h-5 w-5" aria-hidden="true" />
        </span>
        <div>
          <p className="font-semibold text-amber-900">Bolsines sin ubicación</p>
          <ul className="mt-2 flex flex-wrap gap-2">
            {sinUbicacion.map((item) => (
              <li
                key={item.numeroBolsin}
                className="badge bg-white/70 text-amber-900 ring-1 ring-amber-200"
              >
                Bolsin {item.numeroBolsin}: {item.motivo}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
