import { Outlet } from "react-router-dom";

import { Header } from "./Header";

export function AppShell() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:py-10">
        <Outlet />
      </main>
      <footer className="mx-auto w-full max-w-7xl px-4 pb-8 text-xs text-slate-400 sm:px-6">
        Bolsines · UTN FRC · Diseño de Sistemas de Información 2026
      </footer>
    </div>
  );
}
