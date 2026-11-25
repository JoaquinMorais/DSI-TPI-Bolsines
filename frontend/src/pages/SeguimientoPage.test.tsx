import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "../api/client";
import { useIniciarSeguimiento } from "../hooks/useIniciarSeguimiento";
import { SeguimientoPage } from "./SeguimientoPage";

vi.mock("../hooks/useIniciarSeguimiento", () => ({
  useIniciarSeguimiento: vi.fn(),
}));
vi.mock("../components/MapaBolsines", () => ({
  MapaBolsines: () => <div data-testid="mapa" />,
}));

const hook = vi.mocked(useIniciarSeguimiento);
const mutate = vi.fn();

function mockHook(valor: Record<string, unknown>) {
  hook.mockReturnValue(
    valor as unknown as ReturnType<typeof useIniciarSeguimiento>,
  );
}

const DATA = {
  idCU: "3f2a9c1e-7b4d-4e8a-9f10-2c5d6e7a8b90",
  codigoCM: "CM-CBA-01",
  bolsines: [
    { numeroBolsin: 101, numeroPrecinto: "P-0101", codigoCMDestino: "CM-ROS-02" },
  ],
  mapa: {
    centro: { latitud: -31.4201, longitud: -64.1888 },
    zoom: 6,
    marcadores: [],
  },
  sinUbicacion: [],
};

describe("SeguimientoPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("A1 muestra el estado vacio", () => {
    mockHook({
      data: undefined,
      error: new ApiError("SIN_BOLSINES_ENVIADOS", "sin bolsines", 404),
      isPending: false,
      mutate,
    });
    render(<SeguimientoPage />);
    expect(
      screen.getByText("No hay bolsines enviados desde tu comisión médica"),
    ).toBeInTheDocument();
    expect(mutate).toHaveBeenCalled();
  });

  it("error de red muestra reintentar", async () => {
    mockHook({
      data: undefined,
      error: new ApiError("ERROR_DE_RED", "fallo de red", 0),
      isPending: false,
      mutate,
    });
    render(<SeguimientoPage />);
    await userEvent.click(screen.getByRole("button", { name: "Reintentar" }));
    expect(mutate).toHaveBeenCalledTimes(2);
  });

  it("A2 muestra mensaje cuando el filtro no devuelve nada", async () => {
    mockHook({ data: DATA, error: null, isPending: false, mutate });
    render(<SeguimientoPage />);
    await userEvent.type(screen.getByLabelText("Precinto"), "ZZZ");
    expect(
      screen.getByText("No hay bolsines que coincidan con los filtros"),
    ).toBeInTheDocument();
  });

  it("A3 muestra el banner de bolsines sin ubicacion", () => {
    mockHook({
      data: {
        ...DATA,
        sinUbicacion: [
          { numeroBolsin: 111, motivo: "El GPS no informo ubicacion" },
        ],
      },
      error: null,
      isPending: false,
      mutate,
    });
    render(<SeguimientoPage />);
    expect(screen.getByText("Bolsines sin ubicación")).toBeInTheDocument();
    expect(
      screen.getByText("Bolsin 111: El GPS no informo ubicacion"),
    ).toBeInTheDocument();
  });

  it("flujo principal muestra la CM y la lista", () => {
    mockHook({ data: DATA, error: null, isPending: false, mutate });
    render(<SeguimientoPage />);
    expect(screen.getByText("CM CM-CBA-01")).toBeInTheDocument();
    expect(screen.getByText("Bolsin 101")).toBeInTheDocument();
    expect(screen.getByTestId("mapa")).toBeInTheDocument();
  });
});
