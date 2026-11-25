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
      className="rounded border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900"
    >
      <p className="font-medium">Bolsines sin ubicación</p>
      <ul className="list-disc pl-5">
        {sinUbicacion.map((item) => (
          <li key={item.numeroBolsin}>
            Bolsin {item.numeroBolsin}: {item.motivo}
          </li>
        ))}
      </ul>
    </div>
  );
}
