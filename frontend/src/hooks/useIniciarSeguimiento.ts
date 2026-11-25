import { useMutation } from "@tanstack/react-query";

import { iniciarSeguimiento } from "../api/seguimiento";

export function useIniciarSeguimiento() {
  return useMutation({ mutationFn: iniciarSeguimiento });
}
