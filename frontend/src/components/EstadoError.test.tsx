import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { EstadoError } from "./EstadoError";

describe("EstadoError", () => {
  it("muestra el mensaje y reintenta", async () => {
    const onReintentar = vi.fn();
    render(
      <EstadoError mensaje="Fallo de red" onReintentar={onReintentar} />,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Fallo de red");
    await userEvent.click(screen.getByRole("button", { name: "Reintentar" }));
    expect(onReintentar).toHaveBeenCalled();
  });
});
