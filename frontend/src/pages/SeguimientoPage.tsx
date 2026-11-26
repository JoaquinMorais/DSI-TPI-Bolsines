import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ApiError } from "../api/client";
import { Breadcrumbs } from "../components/Breadcrumbs";
import { DialogoConfirmacion } from "../components/DialogoConfirmacion";
import { EstadoError } from "../components/EstadoError";
import { EstadoVacio } from "../components/EstadoVacio";
import { MapaBolsines } from "../components/MapaBolsines";
import { SkeletonLista } from "../components/SkeletonLista";
import { Tabs } from "../components/Tabs";
import { Toast } from "../components/Toast";
import type { TipoToast } from "../components/Toast";
import { mensajeDeError } from "../lib/errores";
import { AvisoSinUbicacion } from "../features/seguimiento/AvisoSinUbicacion";
import { DetalleBolsin } from "../features/seguimiento/DetalleBolsin";
import { FiltrosBolsines } from "../features/seguimiento/FiltrosBolsines";
import { ListaBolsines } from "../features/seguimiento/ListaBolsines";
import type { FilaBolsin } from "../features/seguimiento/ListaBolsines";
import { useCancelarSeguimiento } from "../hooks/useCancelarSeguimiento";
import { useConfirmarCorreo } from "../hooks/useConfirmarCorreo";
import { useIniciarSeguimiento } from "../hooks/useIniciarSeguimiento";
import { useSeleccionarBolsin } from "../hooks/useSeleccionarBolsin";
import type { SeleccionBolsinResponse } from "../types/seguimiento";

const MENSAJE_A1 = "No hay bolsines enviados desde tu comisión médica";
const MIGAJAS = [
  { etiqueta: "Inicio", to: "/" },
  { etiqueta: "Seguimiento de bolsines" },
];

export function SeguimientoPage() {
  const navigate = useNavigate();
  const iniciar = useIniciarSeguimiento();
  const seleccionar = useSeleccionarBolsin();
  const confirmar = useConfirmarCorreo();
  const cancelar = useCancelarSeguimiento();

  const iniciado = useRef(false);
  const [precinto, setPrecinto] = useState("");
  const [cmDestino, setCmDestino] = useState("");
  const [seleccionado, setSeleccionado] = useState<number | null>(null);
  const [vista, setVista] = useState<"lista" | "mapa">("lista");
  const [detalle, setDetalle] = useState<SeleccionBolsinResponse | null>(null);
  const [dialogoCorreo, setDialogoCorreo] = useState(false);
  const [dialogoCancelar, setDialogoCancelar] = useState(false);
  const [toast, setToast] = useState<{ mensaje: string; tipo: TipoToast } | null>(
    null,
  );
  const [correoEnviadoEn, setCorreoEnviadoEn] = useState<string | null>(null);
  const [resultadoFinal, setResultadoFinal] = useState<string | null>(null);
  const [finalizado, setFinalizado] = useState(false);

  useEffect(() => {
    if (!iniciado.current) {
      iniciado.current = true;
      iniciar.mutate();
    }
  }, [iniciar.mutate]);

  const data = iniciar.data;

  const filas = useMemo<FilaBolsin[]>(() => {
    if (!data) {
      return [];
    }
    const marcadores = new Map(
      data.mapa.marcadores.map((marcador) => [
        marcador.numeroBolsin,
        marcador,
      ]),
    );
    return data.bolsines.map((bolsin) => ({
      ...bolsin,
      marcador: marcadores.get(bolsin.numeroBolsin),
    }));
  }, [data]);

  const opcionesCM = useMemo(
    () => Array.from(new Set(filas.map((fila) => fila.codigoCMDestino))).sort(),
    [filas],
  );

  const filasFiltradas = useMemo(() => {
    const texto = precinto.trim().toLowerCase();
    return filas.filter((fila) => {
      const coincidePrecinto =
        !texto || (fila.numeroPrecinto ?? "").toLowerCase().includes(texto);
      const coincideCM = !cmDestino || fila.codigoCMDestino === cmDestino;
      return coincidePrecinto && coincideCM;
    });
  }, [filas, precinto, cmDestino]);

  const mapaFiltrado = useMemo(() => {
    if (!data) {
      return null;
    }
    const marcadores = filasFiltradas.flatMap((fila) =>
      fila.marcador ? [fila.marcador] : [],
    );
    return { ...data.mapa, marcadores };
  }, [data, filasFiltradas]);

  const hayFiltros = precinto.trim() !== "" || cmDestino !== "";
  const esA1 =
    iniciar.error instanceof ApiError &&
    iniciar.error.codigo === "SIN_BOLSINES_ENVIADOS";

  function limpiarFiltros() {
    setPrecinto("");
    setCmDestino("");
  }

  function elegirBolsin(numeroBolsin: number) {
    if (!data || finalizado) {
      return;
    }
    setSeleccionado(numeroBolsin);
    setDetalle(null);
    setCorreoEnviadoEn(null);
    setResultadoFinal(null);
    seleccionar.mutate(
      { idCU: data.idCU, numeroBolsin },
      {
        onSuccess: (respuesta) => setDetalle(respuesta),
        onError: (error) =>
          setToast({ mensaje: mensajeDeError(error), tipo: "error" }),
      },
    );
  }

  function confirmarEnvio() {
    if (!data || !detalle) {
      return;
    }
    confirmar.mutate(
      { idCU: data.idCU, confirma: true },
      {
        onSuccess: (respuesta) => {
          setDialogoCorreo(false);
          setFinalizado(true);
          setCorreoEnviadoEn(new Date().toLocaleString("es-AR"));
          setToast({ mensaje: "Correo enviado.", tipo: "exito" });
        },
        onError: (error) => {
          setDialogoCorreo(false);
          setToast({ mensaje: mensajeDeError(error), tipo: "error" });
        },
      },
    );
  }

  function rechazarEnvio() {
    if (!data) {
      return;
    }
    confirmar.mutate(
      { idCU: data.idCU, confirma: false },
      {
        onSuccess: () => {
          setDialogoCorreo(false);
          setFinalizado(true);
          setResultadoFinal("No se envió el correo.");
          setToast({ mensaje: "No se envió el correo.", tipo: "exito" });
        },
        onError: (error) => {
          setDialogoCorreo(false);
          setToast({ mensaje: mensajeDeError(error), tipo: "error" });
        },
      },
    );
  }

  function abrirCancelacion() {
    if (finalizado) {
      navigate("/");
      return;
    }
    setDialogoCancelar(true);
  }

  function confirmarCancelacion() {
    if (!data) {
      setDialogoCancelar(false);
      navigate("/");
      return;
    }
    cancelar.mutate(data.idCU, {
      onSuccess: () => {
        setDialogoCancelar(false);
        navigate("/");
      },
      onError: (error) => {
        setDialogoCancelar(false);
        if (error instanceof ApiError && error.status === 404) {
          navigate("/");
          return;
        }
        setToast({ mensaje: mensajeDeError(error), tipo: "error" });
      },
    });
  }

  return (
    <section className="space-y-4">
      <Breadcrumbs items={MIGAJAS} />
      <header className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-semibold">Consultar seguimiento</h1>
          {data && (
            <span className="rounded bg-slate-200 px-3 py-1 text-sm font-medium">
              CM {data.codigoCM}
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={abrirCancelacion}
          className="rounded border border-red-300 px-3 py-2 text-sm text-red-700"
        >
          Cancelar consulta
        </button>
      </header>

      {iniciar.isPending && (
        <div className="space-y-3" aria-busy="true">
          <p role="status" className="sr-only">
            Cargando seguimiento...
          </p>
          <SkeletonLista />
        </div>
      )}

      {!iniciar.isPending && esA1 && (
        <EstadoVacio
          titulo={MENSAJE_A1}
          descripcion="No hay bolsines en estado Enviado para tu comisión médica."
        />
      )}

      {!iniciar.isPending && iniciar.error && !esA1 && (
        <EstadoError
          mensaje={mensajeDeError(iniciar.error)}
          onReintentar={() => iniciar.mutate()}
        />
      )}

      {!iniciar.isPending && !iniciar.error && data && (
        <div className="space-y-4">
          <AvisoSinUbicacion sinUbicacion={data.sinUbicacion} />
          <FiltrosBolsines
            precinto={precinto}
            cmDestino={cmDestino}
            opcionesCM={opcionesCM}
            onPrecinto={setPrecinto}
            onCMDestino={setCmDestino}
            onLimpiar={limpiarFiltros}
          />
          <div className="md:hidden">
            <Tabs
              etiqueta="Vista de resultados"
              opciones={[
                { id: "lista", etiqueta: "Lista" },
                { id: "mapa", etiqueta: "Mapa" },
              ]}
              activa={vista}
              onCambiar={(id) => setVista(id as "lista" | "mapa")}
            />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div className={vista === "mapa" ? "hidden md:block" : "block"}>
              {filasFiltradas.length === 0 ? (
                <EstadoVacio
                  titulo="No hay bolsines que coincidan con los filtros"
                  descripcion="Prueba con otro precinto o CM destino."
                  accion={
                    <button
                      type="button"
                      onClick={limpiarFiltros}
                      className="underline"
                    >
                      Limpiar filtros
                    </button>
                  }
                />
              ) : (
                <ListaBolsines
                  filas={filasFiltradas}
                  seleccionado={seleccionado}
                  onSeleccionar={elegirBolsin}
                  deshabilitado={finalizado}
                />
              )}
            </div>
            <div
              className={`space-y-4 ${
                vista === "lista" ? "hidden md:block" : "block"
              }`}
            >
              {mapaFiltrado && (
                <MapaBolsines
                  mapa={mapaFiltrado}
                  seleccionado={seleccionado}
                  onSeleccionar={finalizado ? undefined : elegirBolsin}
                />
              )}
              {detalle && (
                <DetalleBolsin
                  detalle={detalle}
                  correoEnviadoEn={correoEnviadoEn}
                  resultado={resultadoFinal}
                  onNotificar={
                    finalizado ? undefined : () => setDialogoCorreo(true)
                  }
                  notificarDeshabilitado={finalizado}
                />
              )}
            </div>
          </div>
          {hayFiltros && filasFiltradas.length > 0 && (
            <p className="text-sm text-slate-500">
              Mostrando {filasFiltradas.length} de {filas.length} bolsines.
            </p>
          )}
        </div>
      )}

      <DialogoConfirmacion
        abierto={dialogoCorreo}
        titulo="Notificar ubicación"
        textoConfirmar="Enviar correo"
        textoRechazar="No enviar"
        onConfirmar={confirmarEnvio}
        onRechazar={rechazarEnvio}
        onCancelar={() => setDialogoCorreo(false)}
        cargando={confirmar.isPending}
      >
        {detalle && (
          <p>
            Se enviará la ubicación del bolsín {detalle.bolsin.numeroBolsin} al
            Gerente de la CM {detalle.bolsin.codigoCMDestino}.
          </p>
        )}
      </DialogoConfirmacion>

      <DialogoConfirmacion
        abierto={dialogoCancelar}
        titulo="Cancelar consulta"
        textoConfirmar="Sí, cancelar"
        onConfirmar={confirmarCancelacion}
        onCancelar={() => setDialogoCancelar(false)}
        cargando={cancelar.isPending}
      >
        <p>Se descartará la consulta de seguimiento en curso.</p>
      </DialogoConfirmacion>

      <Toast
        mensaje={toast?.mensaje ?? null}
        tipo={toast?.tipo ?? "exito"}
        onCerrar={() => setToast(null)}
      />
    </section>
  );
}
