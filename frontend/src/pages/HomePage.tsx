import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <section className="space-y-3">
      <h1 className="text-2xl font-semibold">Inicio</h1>
      <p className="text-slate-600">Panel del Encargado de Bolsines.</p>
      <Link
        to="/seguimiento"
        className="inline-block rounded bg-slate-900 px-4 py-2 text-white"
      >
        Consultar seguimiento
      </Link>
    </section>
  );
}
