/// <reference types="vitest" />
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, ".", "");
  const proxyTarget = env.PROXY_TARGET || "http://localhost:8020";

  return {
    plugins: [react()],
    server: {
      host: "0.0.0.0",
      port: 3020,
      allowedHosts: ["synodal-leora-unvolcanically.ngrok-free.dev"],
      proxy: {
        "/auth": { target: proxyTarget, changeOrigin: true },
        "/seguimiento-bolsines": { target: proxyTarget, changeOrigin: true },
      },
    },
    test: {
      environment: "jsdom",
      setupFiles: "./src/test/setup.ts",
      globals: true,
    },
  };
});
