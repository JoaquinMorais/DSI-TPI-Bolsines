import { useQuery } from "@tanstack/react-query";

import { getMe } from "../api/auth";

export function useUsuarioActual() {
  return useQuery({
    queryKey: ["usuarioActual"],
    queryFn: getMe,
    retry: 1,
  });
}
