export function SkeletonLista({ filas = 4 }: { filas?: number }) {
  return (
    <div className="space-y-2" aria-hidden="true">
      {Array.from({ length: filas }).map((_, indice) => (
        <div
          key={indice}
          className="h-16 animate-pulse rounded border border-slate-200 bg-slate-200"
        />
      ))}
    </div>
  );
}
