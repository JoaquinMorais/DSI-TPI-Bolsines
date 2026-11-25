import { useState } from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { FiltrosBolsines } from "./FiltrosBolsines";

function FiltrosConEstado({
  onPrecinto,
  onCMDestino,
  onLimpiar,
}: {
  onPrecinto: (valor: string) => void;
  onCMDestino: (valor: string) => void;
  onLimpiar: () => void;
}) {
  const [precinto, setPrecinto] = useState("");
  const [cmDestino, setCmDestino] = useState("");
  return (
    <FiltrosBolsines
      precinto={precinto}
      cmDestino={cmDestino}
      opcionesCM={["CM-MDZ-03", "CM-ROS-02"]}
      onPrecinto={(valor) => {
        setPrecinto(valor);
        onPrecinto(valor);
      }}
      onCMDestino={(valor) => {
        setCmDestino(valor);
        onCMDestino(valor);
      }}
      onLimpiar={onLimpiar}
    />
  );
}

describe("FiltrosBolsines", () => {
  it("emite el precinto al escribir", async () => {
    const onPrecinto = vi.fn();
    render(
      <FiltrosConEstado
        onPrecinto={onPrecinto}
        onCMDestino={vi.fn()}
        onLimpiar={vi.fn()}
      />,
    );
    await userEvent.type(screen.getByLabelText("Precinto"), "P-01");
    expect(onPrecinto).toHaveBeenLastCalledWith("P-01");
  });

  it("emite la CM destino al elegir", async () => {
    const onCMDestino = vi.fn();
    render(
      <FiltrosConEstado
        onPrecinto={vi.fn()}
        onCMDestino={onCMDestino}
        onLimpiar={vi.fn()}
      />,
    );
    await userEvent.selectOptions(
      screen.getByLabelText("CM destino"),
      "CM-ROS-02",
    );
    expect(onCMDestino).toHaveBeenLastCalledWith("CM-ROS-02");
  });

  it("llama a limpiar filtros", async () => {
    const onLimpiar = vi.fn();
    render(
      <FiltrosConEstado
        onPrecinto={vi.fn()}
        onCMDestino={vi.fn()}
        onLimpiar={onLimpiar}
      />,
    );
    await userEvent.click(
      screen.getByRole("button", { name: "Limpiar filtros" }),
    );
    expect(onLimpiar).toHaveBeenCalled();
  });
});
