export function EstadoCarga({ mensaje = "Cargando..." }: { mensaje?: string }) {
  return (
    <p role="status" className="text-sm text-slate-500">
      {mensaje}
    </p>
  );
}
