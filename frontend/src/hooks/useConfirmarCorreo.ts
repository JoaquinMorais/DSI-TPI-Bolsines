import { useMutation } from "@tanstack/react-query";

import { confirmarCorreo } from "../api/seguimiento";

type Variables = {
  idCU: string;
  confirma: boolean;
};

export function useConfirmarCorreo() {
  return useMutation({
    mutationFn: ({ idCU, confirma }: Variables) =>
      confirmarCorreo(idCU, { confirma }),
  });
}
