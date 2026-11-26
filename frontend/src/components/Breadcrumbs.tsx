import { ChevronRight } from "lucide-react";
import { Link } from "react-router-dom";

export type Migaja = { etiqueta: string; to?: string };

export function Breadcrumbs({ items }: { items: Migaja[] }) {
  return (
    <nav aria-label="Migas de pan">
      <ol className="flex flex-wrap items-center gap-1.5 text-sm text-slate-500">
        {items.map((item, indice) => (
          <li key={item.etiqueta} className="flex items-center gap-1.5">
            {item.to ? (
              <Link
                to={item.to}
                className="rounded px-1 font-medium text-slate-600 transition hover:bg-slate-100 hover:text-ink-900"
              >
                {item.etiqueta}
              </Link>
            ) : (
              <span aria-current="page" className="px-1 font-medium text-ink-900">
                {item.etiqueta}
              </span>
            )}
            {indice < items.length - 1 && (
              <ChevronRight
                className="h-3.5 w-3.5 text-slate-300"
                aria-hidden="true"
              />
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
