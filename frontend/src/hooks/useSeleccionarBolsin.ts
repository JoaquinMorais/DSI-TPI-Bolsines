import { useMutation } from "@tanstack/react-query";

import { seleccionarBolsin } from "../api/seguimiento";

type Variables = {
  idCU: string;
  numeroBolsin: number;
};

export function useSeleccionarBolsin() {
  return useMutation({
    mutationFn: ({ idCU, numeroBolsin }: Variables) =>
      seleccionarBolsin(idCU, { numeroBolsin }),
  });
}
