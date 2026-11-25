export const API_URL: string =
  import.meta.env.VITE_API_URL ?? "http://localhost:8020";

export async function pedir<T>(
  ruta: string,
  opciones: RequestInit = {},
): Promise<T> {
  const respuesta = await fetch(`${API_URL}${ruta}`, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      ...(opciones.headers ?? {}),
    },
  });

  if (!respuesta.ok) {
    let mensaje = `Error ${respuesta.status}`;
    try {
      const cuerpo = await respuesta.json();
      mensaje = cuerpo.mensaje ?? mensaje;
    } catch {
      // sin cuerpo JSON
    }
    throw new Error(mensaje);
  }

  if (respuesta.status === 204) {
    return undefined as T;
  }
  return respuesta.json();
}
