export function EstadoError({
  mensaje,
  onReintentar,
}: {
  mensaje: string;
  onReintentar?: () => void;
}) {
  return (
    <div role="alert" className="text-sm text-red-700">
      <span>{mensaje}</span>
      {onReintentar && (
        <button
          type="button"
          onClick={onReintentar}
          className="ml-2 underline"
        >
          Reintentar
        </button>
      )}
    </div>
  );
}
