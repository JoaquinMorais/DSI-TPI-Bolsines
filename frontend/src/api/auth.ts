import type { EmpleadoMeOut } from "../types/auth";
import { pedir } from "./client";

export function getMe(): Promise<EmpleadoMeOut> {
  return pedir<EmpleadoMeOut>("/auth/me");
}
