import { useMemo, useState } from "react";
import {
  API_URL,
  cancelarCasoUso,
  confirmarCorreo,
  iniciarSeguimiento,
  login,
  seleccionarBolsin,
} from "./api";
import type { Seguimiento, SinBolsines } from "./api";
import { MapView } from "./MapView";

type Datos = Seguimiento | SinBolsines;

export function App() {
  const [mail, setMail] = useState("eb.cba01@example.test");
  const [password, setPassword] = useState("bolsines-dev");
  const [token, setToken] = useState<string | null>(null);
  const [datos, setDatos] = useState<Datos | null>(null);
  const [seleccion, setSeleccion] = useState<number | null>(null);
  const [filtro, setFiltro] = useState("");
  const [mensaje, setMensaje] = useState<string>("");

  const esSeguimiento = (valor: Datos | null): valor is Seguimiento =>
    valor !== null && valor.idCU !== null;

  const bolsinesFiltrados = useMemo(() => {
    if (!datos || !esSeguimiento(datos)) {
      return [];
    }
    const texto = filtro.trim().toLowerCase();
    if (!texto) {
      return datos.bolsines;
    }
    return datos.bolsines.filter((b) =>
      (b.numeroPrecinto ?? "").toLowerCase().includes(texto),
    );
  }, [datos, filtro]);

  async function entrar(evento: React.FormEvent) {
    evento.preventDefault();
    setMensaje("");
    try {
      setToken(await login(mail, password));
    } catch (error) {
      setMensaje((error as Error).message);
    }
  }

  async function consultar() {
    if (!token) {
      return;
    }
    setMensaje("");
    try {
      setDatos(await iniciarSeguimiento(token));
      setSeleccion(null);
    } catch (error) {
      setMensaje((error as Error).message);
    }
  }

  async function elegir(numeroBolsin: number, idCU: string) {
    if (!token) {
      return;
    }
    try {
      await seleccionarBolsin(token, idCU, numeroBolsin);
      setSeleccion(numeroBolsin);
      setMensaje("");
    } catch (error) {
      setMensaje((error as Error).message);
    }
  }

  async function responder(confirma: boolean, idCU: string) {
    if (!token) {
      return;
    }
    try {
      const resultado = await confirmarCorreo(token, idCU, confirma);
      setMensaje(
        resultado.notificado
          ? `Correo enviado a ${resultado.destinatarioEnmascarado}`
          : "No se envio correo.",
      );
      setDatos(null);
      setSeleccion(null);
    } catch (error) {
      setMensaje((error as Error).message);
    }
  }

  async function cancelar(idCU: string) {
    if (!token) {
      return;
    }
    await cancelarCasoUso(token, idCU);
    setDatos(null);
    setSeleccion(null);
    setMensaje("Caso de uso cancelado.");
  }

  return (
    <main style={{ fontFamily: "system-ui", padding: "1rem", maxWidth: 900 }}>
      <h1>Bolsines - Seguimiento (CU 36)</h1>
      <p style={{ color: "#666" }}>API: {API_URL}</p>

      {!token && (
        <form onSubmit={entrar} style={{ display: "grid", gap: 8, maxWidth: 320 }}>
          <label>
            Mail
            <input value={mail} onChange={(e) => setMail(e.target.value)} />
          </label>
          <label>
            Contraseña
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          <button type="submit">Ingresar</button>
        </form>
      )}

      {token && (
        <div style={{ display: "grid", gap: 12 }}>
          <div>
            <button onClick={consultar}>Consultar seguimiento</button>
            <button
              onClick={() => {
                setToken(null);
                setDatos(null);
                setSeleccion(null);
              }}
              style={{ marginLeft: 8 }}
            >
              Salir
            </button>
          </div>

          {mensaje && <p style={{ color: "#a00" }}>{mensaje}</p>}

          {datos && !esSeguimiento(datos) && (
            <p>No hay bolsines Enviados para tu comisión.</p>
          )}

          {datos && esSeguimiento(datos) && (
            <>
              <p>
                CM: <strong>{datos.codigoCM}</strong> | Caso de uso:{" "}
                <code>{datos.idCU}</code>
              </p>
              <label>
                Filtrar por precinto:{" "}
                <input
                  value={filtro}
                  onChange={(e) => setFiltro(e.target.value)}
                  placeholder="ej. P-0101"
                />
              </label>

              <table style={{ borderCollapse: "collapse", width: "100%" }}>
                <thead>
                  <tr>
                    <th>Bolsin</th>
                    <th>Precinto</th>
                    <th>CM destino</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {bolsinesFiltrados.map((b) => (
                    <tr
                      key={b.numeroBolsin}
                      style={{
                        background:
                          seleccion === b.numeroBolsin ? "#ffe9a8" : undefined,
                      }}
                    >
                      <td>{b.numeroBolsin}</td>
                      <td>{b.numeroPrecinto ?? "-"}</td>
                      <td>{b.codigoCMDestino}</td>
                      <td>
                        <button
                          onClick={() => elegir(b.numeroBolsin, datos.idCU)}
                        >
                          Seleccionar
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {datos.sinUbicacion.length > 0 && (
                <p>
                  Sin ubicacion:{" "}
                  {datos.sinUbicacion
                    .map((s) => `${s.numeroBolsin} (${s.motivo})`)
                    .join(", ")}
                </p>
              )}

              <MapView mapa={datos.mapa} />

              {seleccion !== null && (
                <div>
                  <p>¿Enviar la ubicacion del bolsin {seleccion} al GCM destino?</p>
                  <button onClick={() => responder(true, datos.idCU)}>
                    Confirmar envio
                  </button>
                  <button
                    onClick={() => responder(false, datos.idCU)}
                    style={{ marginLeft: 8 }}
                  >
                    No enviar
                  </button>
                </div>
              )}

              <button onClick={() => cancelar(datos.idCU)}>Cancelar</button>
            </>
          )}
        </div>
      )}
    </main>
  );
}
