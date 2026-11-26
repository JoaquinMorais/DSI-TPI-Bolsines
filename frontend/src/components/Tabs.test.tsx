import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Tabs } from "./Tabs";

const OPCIONES = [
  { id: "lista", etiqueta: "Lista" },
  { id: "mapa", etiqueta: "Mapa" },
];

describe("Tabs", () => {
  it("cambia con clic", async () => {
    const onCambiar = vi.fn();
    render(
      <Tabs
        etiqueta="Vista"
        opciones={OPCIONES}
        activa="lista"
        onCambiar={onCambiar}
      />,
    );
    await userEvent.click(screen.getByRole("tab", { name: "Mapa" }));
    expect(onCambiar).toHaveBeenCalledWith("mapa");
  });

  it("navega con flechas", async () => {
    const onCambiar = vi.fn();
    render(
      <Tabs
        etiqueta="Vista"
        opciones={OPCIONES}
        activa="lista"
        onCambiar={onCambiar}
      />,
    );
    screen.getByRole("tab", { name: "Lista" }).focus();
    await userEvent.keyboard("{ArrowRight}");
    expect(onCambiar).toHaveBeenCalledWith("mapa");
  });
});
