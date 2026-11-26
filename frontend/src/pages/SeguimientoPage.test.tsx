import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "../api/client";
import { useCancelarSeguimiento } from "../hooks/useCancelarSeguimiento";
import { useConfirmarCorreo } from "../hooks/useConfirmarCorreo";
import { useIniciarSeguimiento } from "../hooks/useIniciarSeguimiento";
import { useSeleccionarBolsin } from "../hooks/useSeleccionarBolsin";
import { SeguimientoPage } from "./SeguimientoPage";

vi.mock("../hooks/useIniciarSeguimiento", () => ({
  useIniciarSeguimiento: vi.fn(),
}));
vi.mock("../hooks/useSeleccionarBolsin", () => ({
  useSeleccionarBolsin: vi.fn(),
}));
vi.mock("../hooks/useConfirmarCorreo", () => ({
  useConfirmarCorreo: vi.fn(),
}));
vi.mock("../hooks/useCancelarSeguimiento", () => ({
  useCancelarSeguimiento: vi.fn(),
}));
vi.mock("../components/MapaBolsines", () => ({
  MapaBolsines: () => <div data-testid="mapa" />,
}));

const iniciarMutate = vi.fn();
const seleccionarMutate = vi.fn();
const confirmarMutate = vi.fn();
const cancelarMutate = vi.fn();

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

const SELECCION = {
  idCU: DATA.idCU,
  bolsin: DATA.bolsines[0],
  ubicacion: {
    numeroBolsin: 101,
    latitud: -31.4201,
    longitud: -64.1888,
    fechaHoraUltimaActualizacion: "2026-03-07T12:30:00",
  },
  requiereConfirmacionCorreo: true,
};

function configurar({
  data = undefined as unknown,
  error = null as Error | null,
  isPending = false,
} = {}) {
  vi.mocked(useIniciarSeguimiento).mockReturnValue({
    data,
    error,
    isPending,
    mutate: iniciarMutate,
  } as unknown as ReturnType<typeof useIniciarSeguimiento>);
  vi.mocked(useSeleccionarBolsin).mockReturnValue({
    mutate: seleccionarMutate,
    isPending: false,
  } as unknown as ReturnType<typeof useSeleccionarBolsin>);
  vi.mocked(useConfirmarCorreo).mockReturnValue({
    mutate: confirmarMutate,
    isPending: false,
  } as unknown as ReturnType<typeof useConfirmarCorreo>);
  vi.mocked(useCancelarSeguimiento).mockReturnValue({
    mutate: cancelarMutate,
    isPending: false,
  } as unknown as ReturnType<typeof useCancelarSeguimiento>);
}

function renderPage() {
  return render(
    <MemoryRouter>
      <SeguimientoPage />
    </MemoryRouter>,
  );
}

describe("SeguimientoPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("A1 muestra el estado vacio", () => {
    configurar({
      error: new ApiError("SIN_BOLSINES_ENVIADOS", "sin bolsines", 404),
    });
    renderPage();
    expect(
      screen.getByText("No hay bolsines enviados desde tu comisión médica"),
    ).toBeInTheDocument();
    expect(iniciarMutate).toHaveBeenCalled();
  });

  it("error de red muestra reintentar", async () => {
    configurar({ error: new ApiError("ERROR_DE_RED", "fallo de red", 0) });
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: "Reintentar" }));
    expect(iniciarMutate).toHaveBeenCalledTimes(2);
  });

  it("A2 muestra mensaje cuando el filtro no devuelve nada", async () => {
    configurar({ data: DATA });
    renderPage();
    await userEvent.type(screen.getByLabelText("Precinto"), "ZZZ");
    expect(
      screen.getByText("No hay bolsines que coincidan con los filtros"),
    ).toBeInTheDocument();
  });

  it("A3 muestra el banner de bolsines sin ubicacion", () => {
    configurar({
      data: {
        ...DATA,
        sinUbicacion: [
          { numeroBolsin: 111, motivo: "El GPS no informo ubicacion" },
        ],
      },
    });
    renderPage();
    expect(screen.getByText("Bolsines sin ubicación")).toBeInTheDocument();
    expect(
      screen.getByText("Bolsin 111: El GPS no informo ubicacion"),
    ).toBeInTheDocument();
  });

  it("flujo principal muestra CM, lista y mapa", () => {
    configurar({ data: DATA });
    renderPage();
    expect(screen.getByText("CM CM-CBA-01")).toBeInTheDocument();
    expect(screen.getByText("Bolsin 101")).toBeInTheDocument();
    expect(screen.getByTestId("mapa")).toBeInTheDocument();
  });

  it("cambia entre Lista y Mapa en la vista movil", async () => {
    configurar({ data: DATA });
    renderPage();
    const tabMapa = screen.getByRole("tab", { name: "Mapa" });
    await userEvent.click(tabMapa);
    expect(tabMapa).toHaveAttribute("aria-selected", "true");
  });

  it("seleccionar llama a tomarSeleccionBolsin y muestra el detalle", async () => {
    configurar({ data: DATA });
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /Bolsin 101/ }));

    expect(seleccionarMutate).toHaveBeenCalledWith(
      { idCU: DATA.idCU, numeroBolsin: 101 },
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    );
    const opciones = seleccionarMutate.mock.calls[0][1];
    act(() => opciones.onSuccess(SELECCION));

    expect(screen.getByText("Coordenadas")).toBeInTheDocument();
    expect(
      screen.getByRole("button", {
        name: "Notificar ubicación al Gerente de la CM destino",
      }),
    ).toBeInTheDocument();
  });

  it("confirmar correo llama a tomarConfirmacionEnvioCorreo", async () => {
    configurar({ data: DATA });
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /Bolsin 101/ }));
    act(() => seleccionarMutate.mock.calls[0][1].onSuccess(SELECCION));

    await userEvent.click(
      screen.getByRole("button", {
        name: "Notificar ubicación al Gerente de la CM destino",
      }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Enviar correo" }));

    expect(confirmarMutate).toHaveBeenCalledWith(
      { idCU: DATA.idCU, confirma: true },
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    );
    act(() =>
      confirmarMutate.mock.calls[0][1].onSuccess({
        estado: "FINALIZADO",
        notificado: true,
        destinatarioEnmascarado: "g***@example.test",
      }),
    );
    expect(screen.getByText("Correo enviado.")).toBeInTheDocument();
    expect(screen.getByText(/Correo enviado el/)).toBeInTheDocument();
  });

  it("A5 no envia correo", async () => {
    configurar({ data: DATA });
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /Bolsin 101/ }));
    act(() => seleccionarMutate.mock.calls[0][1].onSuccess(SELECCION));

    await userEvent.click(
      screen.getByRole("button", {
        name: "Notificar ubicación al Gerente de la CM destino",
      }),
    );
    await userEvent.click(screen.getByRole("button", { name: "No enviar" }));

    expect(confirmarMutate).toHaveBeenCalledWith(
      { idCU: DATA.idCU, confirma: false },
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    );
    act(() =>
      confirmarMutate.mock.calls[0][1].onSuccess({
        estado: "FINALIZADO",
        notificado: false,
        destinatarioEnmascarado: null,
      }),
    );
    expect(screen.getByRole("status")).toHaveTextContent("No se envió el correo.");
  });
});
