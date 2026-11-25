// URL del backend. El navegador hace la llamada, por eso es localhost y no el nombre del contenedor.
export const API_URL: string =
  import.meta.env.VITE_API_URL ?? "http://localhost:8020";

export function App() {
  return (
    <main>
      <h1>Bolsines</h1>
      <p>Frontend listo. API: {API_URL}</p>
    </main>
  );
}
