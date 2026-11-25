import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "./client";
import {
  cancelarSeguimiento,
  iniciarSeguimiento,
  seleccionarBolsin,
} from "./seguimiento";

const CREADO = {
  idCU: "3f2a9c1e-7b4d-4e8a-9f10-2c5d6e7a8b90",
  codigoCM: "CM-CBA-02",
  bolsines: [
    { numeroBolsin: 110, numeroPrecinto: "P-0110", codigoCMDestino: "CM-ROS-02" },
  ],
  mapa: {
    centro: { latitud: -31.4167, longitud: -64.1833 },
    zoom: 6,
    marcadores: [],
  },
  sinUbicacion: [],
};

function json(cuerpo: unknown, status: number): Response {
  return new Response(JSON.stringify(cuerpo), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("api/seguimiento", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("iniciarSeguimiento devuelve la respuesta 201", async () => {
    const fetchMock = vi.fn().mockResolvedValue(json(CREADO, 201));
    vi.stubGlobal("fetch", fetchMock);

    const resultado = await iniciarSeguimiento();
    expect(resultado.idCU).toBe(CREADO.idCU);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/seguimiento-bolsines"),
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("iniciarSeguimiento propaga ApiError de A1", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        json(
          { codigo: "SIN_BOLSINES_ENVIADOS", mensaje: "No hay bolsines" },
          404,
        ),
      ),
    );

    const error = (await iniciarSeguimiento().catch((e) => e)) as ApiError;
    expect(error).toBeInstanceOf(ApiError);
    expect(error.codigo).toBe("SIN_BOLSINES_ENVIADOS");
    expect(error.status).toBe(404);
  });

  it("seleccionarBolsin envia numeroBolsin al endpoint", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(json({ ...CREADO, bolsin: CREADO.bolsines[0] }, 200));
    vi.stubGlobal("fetch", fetchMock);

    await seleccionarBolsin(CREADO.idCU, { numeroBolsin: 110 });

    const [url, opciones] = fetchMock.mock.calls[0];
    expect(url).toContain(`/seguimiento-bolsines/${CREADO.idCU}/seleccion`);
    expect(opciones).toMatchObject({
      method: "POST",
      body: JSON.stringify({ numeroBolsin: 110 }),
    });
  });

  it("cancelarSeguimiento usa DELETE y devuelve undefined", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(cancelarSeguimiento("abc")).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/seguimiento-bolsines/abc"),
      expect.objectContaining({ method: "DELETE" }),
    );
  });
});
