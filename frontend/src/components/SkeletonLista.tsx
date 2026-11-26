export function SkeletonLista({ filas = 4 }: { filas?: number }) {
  return (
    <div className="space-y-3" aria-hidden="true">
      {Array.from({ length: filas }).map((_, indice) => (
        <div
          key={indice}
          className="h-20 animate-pulse rounded-2xl border border-slate-200/70 bg-gradient-to-r from-slate-100 via-slate-200/80 to-slate-100"
        />
      ))}
    </div>
  );
}
