import type { ReactElement } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Header } from "./Header";

function renderConQuery(ui: ReactElement) {
  const cliente = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={cliente}>{ui}</QueryClientProvider>,
  );
}

describe("Header", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("muestra el usuario logueado del backend", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            id: 1,
            mail: "eb.cba01@example.test",
            nombre: "Elena",
            apellido: "Bolsin",
            rol: "Encargado de Bolsines",
            codigoCM: "CM-CBA-01",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    renderConQuery(<Header />);

    expect(await screen.findByText("Elena Bolsin")).toBeInTheDocument();
    expect(screen.getByText(/CM-CBA-01/)).toBeInTheDocument();
    expect(screen.getByText("eb.cba01@example.test")).toBeInTheDocument();
  });
});
