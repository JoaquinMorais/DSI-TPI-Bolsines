import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, pedir } from "./client";

function respuestaJson(cuerpo: unknown, status: number): Response {
  return new Response(JSON.stringify(cuerpo), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("pedir / ApiError", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("404 SIN_BOLSINES_ENVIADOS lanza ApiError con codigo y status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        respuestaJson(
          {
            codigo: "SIN_BOLSINES_ENVIADOS",
            mensaje: "No hay bolsines Enviados",
          },
          404,
        ),
      ),
    );

    const error = (await pedir("/seguimiento-bolsines", {
      method: "POST",
    }).catch((e) => e)) as ApiError;

    expect(error).toBeInstanceOf(ApiError);
    expect(error.codigo).toBe("SIN_BOLSINES_ENVIADOS");
    expect(error.status).toBe(404);
    expect(error.message).toBe("No hay bolsines Enviados");
  });

  it("usa ERROR_HTTP cuando el error no trae JSON", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("no json", { status: 500 })),
    );

    const error = (await pedir("/x").catch((e) => e)) as ApiError;
    expect(error.codigo).toBe("ERROR_HTTP");
    expect(error.status).toBe(500);
  });

  it("error de red lanza ApiError ERROR_DE_RED", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("fallo de red")),
    );

    const error = (await pedir("/x").catch((e) => e)) as ApiError;
    expect(error.codigo).toBe("ERROR_DE_RED");
    expect(error.status).toBe(0);
  });

  it("204 devuelve undefined", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(null, { status: 204 })),
    );

    await expect(pedir("/x", { method: "DELETE" })).resolves.toBeUndefined();
  });
});
