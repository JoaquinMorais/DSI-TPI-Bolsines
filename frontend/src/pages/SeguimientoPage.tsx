import {
  BellRing,
  Boxes,
  Building2,
  List,
  Map as MapIcon,
  MapPin,
  MapPinOff,
  MapPinned,
  TriangleAlert,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
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
import { AvisoSinUbicacion } from "../features/seguimiento/AvisoSinUbicacion";
import { DetalleBolsin } from "../features/seguimiento/DetalleBolsin";
import { FiltrosBolsines } from "../features/seguimiento/FiltrosBolsines";
import { ListaBolsines } from "../features/seguimiento/ListaBolsines";
import type { FilaBolsin } from "../features/seguimiento/ListaBolsines";
import { useCancelarSeguimiento } from "../hooks/useCancelarSeguimiento";
import { useConfirmarCorreo } from "../hooks/useConfirmarCorreo";
import { useIniciarSeguimiento } from "../hooks/useIniciarSeguimiento";
import { useSeleccionarBolsin } from "../hooks/useSeleccionarBolsin";
import { mensajeDeError } from "../lib/errores";
import type { SeleccionBolsinResponse } from "../types/seguimiento";

const MENSAJE_A1 = "No hay bolsines enviados desde tu comisión médica";
const MIGAJAS = [
  { etiqueta: "Inicio", to: "/" },
  { etiqueta: "Seguimiento de bolsines" },
];

const TONOS = {
  ink: "bg-ink-50 text-ink-700",
  brand: "bg-brand-50 text-brand-700",
  amber: "bg-amber-50 text-amber-700",
};

function TarjetaResumen({
  icono,
  etiqueta,
  valor,
  tono,
}: {
  icono: ReactNode;
  etiqueta: string;
  valor: number;
  tono: keyof typeof TONOS;
}) {
  return (
    <div className="card flex items-center gap-3 p-4">
      <span
        className={`grid h-11 w-11 shrink-0 place-items-center rounded-2xl ${TONOS[tono]}`}
      >
        {icono}
      </span>
      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
          {etiqueta}
        </p>
        <p className="text-2xl font-semibold tracking-tight text-ink-900">
          {valor}
        </p>
      </div>
    </div>
  );
}

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

  const total = data?.bolsines.length ?? 0;
  const conUbicacion = data?.mapa.marcadores.length ?? 0;
  const sinUbicacion = data?.sinUbicacion.length ?? 0;

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
        onSuccess: () => {
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
    <section className="animate-fade-in space-y-5">
      <div className="space-y-3">
        <Breadcrumbs items={MIGAJAS} />
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div className="space-y-2">
            <h1 className="page-title">Consultar seguimiento</h1>
            <div className="flex flex-wrap items-center gap-2 text-sm text-slate-600">
              {data && (
                <span className="badge bg-brand-50 text-brand-800">
                  <Building2 className="h-3 w-3" aria-hidden="true" />
                  Mi CM: {data.codigoCM}
                </span>
              )}
              <span>Bolsines en estado Enviado de tu comisión médica.</span>
            </div>
          </div>
          <button
            type="button"
            onClick={abrirCancelacion}
            className="btn btn-danger self-start sm:self-auto"
          >
            Cancelar consulta
          </button>
        </div>
      </div>

      {iniciar.isPending && (
        <div className="space-y-4" aria-busy="true">
          <p role="status" className="sr-only">
            Cargando seguimiento...
          </p>
          <div className="grid gap-3 sm:grid-cols-3">
            {Array.from({ length: 3 }).map((_, indice) => (
              <div
                key={indice}
                className="h-20 animate-pulse rounded-2xl border border-slate-200/70 bg-gradient-to-r from-slate-100 via-slate-200/80 to-slate-100"
              />
            ))}
          </div>
          <div className="card p-4">
            <SkeletonLista filas={5} />
          </div>
        </div>
      )}

      {!iniciar.isPending && esA1 && (
        <EstadoVacio
          titulo={MENSAJE_A1}
          descripcion="No hay bolsines en estado Enviado para tu comisión médica."
          accion={
            <button
              type="button"
              onClick={() => navigate("/")}
              className="btn btn-secondary"
            >
              Volver al inicio
            </button>
          }
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
          <div className="grid gap-3 sm:grid-cols-3">
            <TarjetaResumen
              icono={<Boxes className="h-5 w-5" aria-hidden="true" />}
              etiqueta="Bolsines enviados"
              valor={total}
              tono="ink"
            />
            <TarjetaResumen
              icono={<MapPin className="h-5 w-5" aria-hidden="true" />}
              etiqueta="Con ubicación"
              valor={conUbicacion}
              tono="brand"
            />
            <TarjetaResumen
              icono={<MapPinOff className="h-5 w-5" aria-hidden="true" />}
              etiqueta="Sin ubicación"
              valor={sinUbicacion}
              tono="amber"
            />
          </div>

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
                {
                  id: "lista",
                  etiqueta: "Lista",
                  icono: <List className="h-4 w-4" aria-hidden="true" />,
                },
                {
                  id: "mapa",
                  etiqueta: "Mapa",
                  icono: <MapIcon className="h-4 w-4" aria-hidden="true" />,
                },
              ]}
              activa={vista}
              onCambiar={(id) => setVista(id as "lista" | "mapa")}
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-5">
            <div
              className={`lg:col-span-2 ${
                vista === "mapa" ? "hidden md:block" : "block"
              }`}
            >
              <div className="card p-4">
                <div className="mb-3 flex items-start justify-between gap-2">
                  <div>
                    <h2 className="section-title">Bolsines</h2>
                    <p className="text-xs text-slate-500">
                      Seleccioná uno para ver el detalle
                    </p>
                  </div>
                  <span className="badge bg-slate-100 text-slate-600">
                    {filasFiltradas.length} de {filas.length}
                  </span>
                </div>
                {filasFiltradas.length === 0 ? (
                  <EstadoVacio
                    titulo="No hay bolsines que coincidan con los filtros"
                    descripcion="Prueba con otro precinto o CM destino."
                    accion={
                      <button
                        type="button"
                        onClick={limpiarFiltros}
                        className="btn btn-secondary"
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
            </div>

            <div
              className={`space-y-4 lg:col-span-3 ${
                vista === "lista" ? "hidden md:block" : "block"
              }`}
            >
              {mapaFiltrado && (
                <div className="card overflow-hidden">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-50 text-brand-700">
                        <MapPinned className="h-4 w-4" aria-hidden="true" />
                      </span>
                      <h2 className="section-title">Mapa de bolsines</h2>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                      <span className="inline-flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-brand-500" />
                        Con ubicación
                      </span>
                      <span className="inline-flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-amber-500" />
                        Sin ubicación
                      </span>
                    </div>
                  </div>
                  <MapaBolsines
                    mapa={mapaFiltrado}
                    seleccionado={seleccionado}
                    onSeleccionar={finalizado ? undefined : elegirBolsin}
                  />
                </div>
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
        icono={<BellRing className="h-5 w-5" aria-hidden="true" />}
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
        varianteConfirmar="peligro"
        icono={<TriangleAlert className="h-5 w-5" aria-hidden="true" />}
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
