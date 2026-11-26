import { ApiError } from "../api/client";

const MENSAJES: Record<string, string> = {
  ERROR_DE_RED:
    "No pudimos conectarnos. Revisa tu conexión e intenta de nuevo.",
  SIN_BOLSINES_ENVIADOS:
    "No hay bolsines enviados desde tu comisión médica.",
  CASO_USO_NO_ENCONTRADO:
    "La consulta ya no está disponible. Vuelve a iniciar el seguimiento.",
  BOLSIN_FUERA_DE_ENVIADOS:
    "Ese bolsín ya no está disponible. Elige otro.",
  CORREO_NO_ENVIADO:
    "No se pudo enviar el correo. Intenta nuevamente.",
  GPS_NO_DISPONIBLE:
    "No se pudo consultar el GPS de los bolsines. Revisa la configuración del GPS (API key) e intenta de nuevo.",
  ROL_INSUFICIENTE: "No tienes permiso para consultar el seguimiento.",
  SOLICITUD_INVALIDA:
    "Los datos enviados no son válidos. Intenta nuevamente.",
};

export function mensajeDeError(error: unknown): string {
  if (error instanceof ApiError) {
    return MENSAJES[error.codigo] ?? "Ocurrió un error. Intenta nuevamente.";
  }
  return "Ocurrió un error. Intenta nuevamente.";
}
