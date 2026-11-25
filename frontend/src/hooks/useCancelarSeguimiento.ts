import { useMutation } from "@tanstack/react-query";

import { cancelarSeguimiento } from "../api/seguimiento";

export function useCancelarSeguimiento() {
  return useMutation({ mutationFn: cancelarSeguimiento });
}
