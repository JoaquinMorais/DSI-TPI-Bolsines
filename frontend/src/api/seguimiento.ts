import type {
  ConfirmacionCorreoRequest,
  ConfirmacionCorreoResponse,
  SeguimientoCreadoResponse,
  SeleccionBolsinRequest,
  SeleccionBolsinResponse,
} from "../types/seguimiento";
import { pedir } from "./client";

export function iniciarSeguimiento(): Promise<SeguimientoCreadoResponse> {
  return pedir<SeguimientoCreadoResponse>("/seguimiento-bolsines", {
    method: "POST",
  });
}

export function seleccionarBolsin(
  idCU: string,
  datos: SeleccionBolsinRequest,
): Promise<SeleccionBolsinResponse> {
  return pedir<SeleccionBolsinResponse>(
    `/seguimiento-bolsines/${idCU}/seleccion`,
    { method: "POST", body: JSON.stringify(datos) },
  );
}

export function confirmarCorreo(
  idCU: string,
  datos: ConfirmacionCorreoRequest,
): Promise<ConfirmacionCorreoResponse> {
  return pedir<ConfirmacionCorreoResponse>(
    `/seguimiento-bolsines/${idCU}/confirmacion-correo`,
    { method: "POST", body: JSON.stringify(datos) },
  );
}

export function cancelarSeguimiento(idCU: string): Promise<void> {
  return pedir<void>(`/seguimiento-bolsines/${idCU}`, { method: "DELETE" });
}
