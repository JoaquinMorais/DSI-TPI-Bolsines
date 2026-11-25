import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { HomePage } from "./pages/HomePage";
import { SeguimientoPage } from "./pages/SeguimientoPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "seguimiento", element: <SeguimientoPage /> },
    ],
  },
]);
