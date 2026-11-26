import { describe, expect, it } from "vitest";

import { ApiError } from "../api/client";
import { mensajeDeError } from "./errores";

describe("mensajeDeError", () => {
  it("traduce errores conocidos a mensajes claros", () => {
    expect(mensajeDeError(new ApiError("ERROR_DE_RED", "x", 0))).toMatch(
      /No pudimos conectarnos/,
    );
    expect(mensajeDeError(new ApiError("CASO_USO_NO_ENCONTRADO", "x", 404))).toMatch(
      /ya no está disponible/,
    );
    expect(mensajeDeError(new ApiError("CORREO_NO_ENVIADO", "x", 502))).toMatch(
      /No se pudo enviar el correo/,
    );
  });

  it("usa un mensaje generico para errores desconocidos", () => {
    expect(mensajeDeError(new Error("otro"))).toBe(
      "Ocurrió un error. Intenta nuevamente.",
    );
  });
});
