import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EstadoVacio } from "./EstadoVacio";

describe("EstadoVacio", () => {
  it("muestra titulo, descripcion y accion", () => {
    render(
      <EstadoVacio
        titulo="Sin datos"
        descripcion="No hay nada para mostrar"
        accion={<button type="button">Accion</button>}
      />,
    );
    expect(screen.getByText("Sin datos")).toBeInTheDocument();
    expect(screen.getByText("No hay nada para mostrar")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Accion" })).toBeInTheDocument();
  });
});
