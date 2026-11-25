export const API_URL: string =
  import.meta.env.VITE_API_URL ?? "http://localhost:8020";

export type Marcador = {
  numeroBolsin: number;
  latitud: number;
  longitud: number;
  fechaHoraUltimaActualizacion: string;
};

export type Mapa = {
  centro: { latitud: number; longitud: number };
  zoom: number;
  marcadores: Marcador[];
};

export type Bolsin = {
  numeroBolsin: number;
  numeroPrecinto: string | null;
  codigoCMDestino: string;
};

export type SinUbicacion = { numeroBolsin: number; motivo: string };

export type Seguimiento = {
  idCU: string;
  codigoCM: string;
  bolsines: Bolsin[];
  mapa: Mapa;
  sinUbicacion: SinUbicacion[];
};

export type SinBolsines = {
  idCU: null;
  codigoCM: string;
  estado: "SIN_BOLSINES";
};

export type Confirmacion = {
  estado: "FINALIZADO";
  notificado: boolean;
  destinatarioEnmascarado: string | null;
};

async function leerError(response: Response): Promise<string> {
  try {
    const cuerpo = await response.json();
    return cuerpo.detail ?? `Error ${response.status}`;
  } catch {
    return `Error ${response.status}`;
  }
}

export async function login(mail: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username: mail, password });
  const response = await fetch(`${API_URL}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    credentials: "include",
    body,
  });
  if (!response.ok) {
    throw new Error(await leerError(response));
  }
  const datos = await response.json();
  return datos.access_token as string;
}

export async function iniciarSeguimiento(
  token: string,
): Promise<Seguimiento | SinBolsines> {
  const response = await fetch(`${API_URL}/seguimiento-bolsines`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error(await leerError(response));
  }
  return response.json();
}

export async function seleccionarBolsin(
  token: string,
  idCU: string,
  numeroBolsin: number,
): Promise<void> {
  const response = await fetch(
    `${API_URL}/seguimiento-bolsines/${idCU}/seleccion`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ numeroBolsin }),
    },
  );
  if (!response.ok) {
    throw new Error(await leerError(response));
  }
}

export async function confirmarCorreo(
  token: string,
  idCU: string,
  confirma: boolean,
): Promise<Confirmacion> {
  const response = await fetch(
    `${API_URL}/seguimiento-bolsines/${idCU}/confirmacion-correo`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ confirma }),
    },
  );
  if (!response.ok) {
    throw new Error(await leerError(response));
  }
  return response.json();
}

export async function cancelarCasoUso(
  token: string,
  idCU: string,
): Promise<void> {
  const response = await fetch(`${API_URL}/seguimiento-bolsines/${idCU}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok && response.status !== 404) {
    throw new Error(await leerError(response));
  }
}
