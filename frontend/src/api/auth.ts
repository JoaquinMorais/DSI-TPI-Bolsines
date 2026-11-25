import type { UsuarioActual } from "../types/auth";
import { pedir } from "./cliente";

export function getMe(): Promise<UsuarioActual> {
  return pedir<UsuarioActual>("/auth/me");
}
