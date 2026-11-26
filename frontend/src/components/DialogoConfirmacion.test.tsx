import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { DialogoConfirmacion } from "./DialogoConfirmacion";

function renderDialogo(overrides: Partial<Parameters<typeof DialogoConfirmacion>[0]> = {}) {
  const props = {
    abierto: true,
    titulo: "Notificar ubicación",
    onConfirmar: vi.fn(),
    onRechazar: vi.fn(),
    onCancelar: vi.fn(),
    textoConfirmar: "Enviar correo",
    textoRechazar: "No enviar",
    ...overrides,
  };
  render(<DialogoConfirmacion {...props}>Contenido</DialogoConfirmacion>);
  return props;
}

describe("DialogoConfirmacion", () => {
  it("no renderiza si esta cerrado", () => {
    render(
      <DialogoConfirmacion
        abierto={false}
        titulo="X"
        onConfirmar={vi.fn()}
        onCancelar={vi.fn()}
      />,
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("confirma", async () => {
    const props = renderDialogo();
    await userEvent.click(screen.getByRole("button", { name: "Enviar correo" }));
    expect(props.onConfirmar).toHaveBeenCalled();
  });

  it("rechaza (no enviar)", async () => {
    const props = renderDialogo();
    await userEvent.click(screen.getByRole("button", { name: "No enviar" }));
    expect(props.onRechazar).toHaveBeenCalled();
  });

  it("cancela/cierra", async () => {
    const props = renderDialogo();
    await userEvent.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(props.onCancelar).toHaveBeenCalled();
  });

  it("cancela con Escape", async () => {
    const props = renderDialogo();
    await userEvent.keyboard("{Escape}");
    expect(props.onCancelar).toHaveBeenCalled();
  });
});
