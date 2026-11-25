import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ListaBolsines } from "./ListaBolsines";
import type { FilaBolsin } from "./ListaBolsines";

const FILAS: FilaBolsin[] = [
  {
    numeroBolsin: 101,
    numeroPrecinto: "P-0101",
    codigoCMDestino: "CM-ROS-02",
    marcador: {
      numeroBolsin: 101,
      latitud: -31.4201,
      longitud: -64.1888,
      fechaHoraUltimaActualizacion: "2026-03-07T12:30:00",
    },
  },
  {
    numeroBolsin: 111,
    numeroPrecinto: "P-0111",
    codigoCMDestino: "CM-MDZ-03",
  },
];

describe("ListaBolsines", () => {
  it("muestra numero, CM destino y fecha o sin ubicacion", () => {
    render(
      <ListaBolsines filas={FILAS} seleccionado={null} onSeleccionar={vi.fn()} />,
    );
    expect(screen.getByText("Bolsin 101")).toBeInTheDocument();
    expect(screen.getByText("CM-ROS-02")).toBeInTheDocument();
    expect(screen.getByText("Sin ubicación")).toBeInTheDocument();
  });

  it("selecciona un bolsin con clic", async () => {
    const onSeleccionar = vi.fn();
    render(
      <ListaBolsines
        filas={FILAS}
        seleccionado={null}
        onSeleccionar={onSeleccionar}
      />,
    );
    await userEvent.click(
      screen.getByRole("button", { name: /Bolsin 111/ }),
    );
    expect(onSeleccionar).toHaveBeenCalledWith(111);
  });

  it("se puede usar con teclado (Enter)", async () => {
    const onSeleccionar = vi.fn();
    render(
      <ListaBolsines
        filas={FILAS}
        seleccionado={null}
        onSeleccionar={onSeleccionar}
      />,
    );
    const boton = screen.getByRole("button", { name: /Bolsin 101/ });
    boton.focus();
    await userEvent.keyboard("{Enter}");
    expect(onSeleccionar).toHaveBeenCalledWith(101);
  });

  it("marca el bolsin seleccionado con aria-pressed", () => {
    render(
      <ListaBolsines filas={FILAS} seleccionado={111} onSeleccionar={vi.fn()} />,
    );
    expect(
      screen.getByRole("button", { name: /Bolsin 111/ }),
    ).toHaveAttribute("aria-pressed", "true");
  });
});
