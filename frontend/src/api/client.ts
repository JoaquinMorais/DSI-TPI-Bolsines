export const API_URL: string = import.meta.env.VITE_API_URL ?? "";

export class ApiError extends Error {
  readonly codigo: string;
  readonly status: number;

  constructor(codigo: string, mensaje: string, status: number) {
    super(mensaje);
    this.name = "ApiError";
    this.codigo = codigo;
    this.status = status;
  }
}

async function leerError(
  respuesta: Response,
): Promise<{ codigo: string; mensaje: string }> {
  try {
    const cuerpo = await respuesta.json();
    return {
      codigo: typeof cuerpo.codigo === "string" ? cuerpo.codigo : "ERROR_HTTP",
      mensaje:
        typeof cuerpo.mensaje === "string"
          ? cuerpo.mensaje
          : `Error ${respuesta.status}`,
    };
  } catch {
    return { codigo: "ERROR_HTTP", mensaje: `Error ${respuesta.status}` };
  }
}

export async function pedir<T>(
  ruta: string,
  opciones: RequestInit = {},
): Promise<T> {
  let respuesta: Response;
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, {
      ...opciones,
      headers: {
        "Content-Type": "application/json",
        ...(opciones.headers ?? {}),
      },
    });
  } catch (error) {
    throw new ApiError("ERROR_DE_RED", (error as Error).message, 0);
  }

  if (!respuesta.ok) {
    const { codigo, mensaje } = await leerError(respuesta);
    throw new ApiError(codigo, mensaje, respuesta.status);
  }

  if (respuesta.status === 204) {
    return undefined as T;
  }
  return respuesta.json();
}
