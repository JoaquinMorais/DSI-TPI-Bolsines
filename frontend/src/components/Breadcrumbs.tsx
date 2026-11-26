import { Link } from "react-router-dom";

export type Migaja = { etiqueta: string; to?: string };

export function Breadcrumbs({ items }: { items: Migaja[] }) {
  return (
    <nav aria-label="Migas de pan">
      <ol className="flex flex-wrap items-center gap-2 text-sm text-slate-600">
        {items.map((item, indice) => (
          <li key={item.etiqueta} className="flex items-center gap-2">
            {item.to ? (
              <Link to={item.to} className="underline">
                {item.etiqueta}
              </Link>
            ) : (
              <span aria-current="page">{item.etiqueta}</span>
            )}
            {indice < items.length - 1 && <span aria-hidden="true">/</span>}
          </li>
        ))}
      </ol>
    </nav>
  );
}
