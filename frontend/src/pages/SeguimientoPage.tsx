import { useEffect, useMemo, useRef, useState } from "react";

import { ApiError } from "../api/client";
import { EstadoError } from "../components/EstadoError";
import { EstadoVacio } from "../components/EstadoVacio";
import { MapaBolsines } from "../components/MapaBolsines";
import { SkeletonLista } from "../components/SkeletonLista";
import { AvisoSinUbicacion } from "../features/seguimiento/AvisoSinUbicacion";
import { FiltrosBolsines } from "../features/seguimiento/FiltrosBolsines";
import { ListaBolsines } from "../features/seguimiento/ListaBolsines";
import type { FilaBolsin } from "../features/seguimiento/ListaBolsines";
import { useIniciarSeguimiento } from "../hooks/useIniciarSeguimiento";

const MENSAJE_A1 = "No hay bolsines enviados desde tu comisión médica";

export function SeguimientoPage() {
  const { data, error, isPending, mutate } = useIniciarSeguimiento();
  const iniciado = useRef(false);
  const [precinto, setPrecinto] = useState("");
  const [cmDestino, setCmDestino] = useState("");
  const [seleccionado, setSeleccionado] = useState<number | null>(null);

  useEffect(() => {
    if (!iniciado.current) {
      iniciado.current = true;
      mutate();
    }
  }, [mutate]);

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
    () =>
      Array.from(new Set(filas.map((fila) => fila.codigoCMDestino))).sort(),
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
  const esA1 = error instanceof ApiError && error.codigo === "SIN_BOLSINES_ENVIADOS";

  function limpiarFiltros() {
    setPrecinto("");
    setCmDestino("");
  }

  return (
    <section className="space-y-4">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Consultar seguimiento</h1>
        {data && (
          <span className="rounded bg-slate-200 px-3 py-1 text-sm font-medium">
            CM {data.codigoCM}
          </span>
        )}
      </header>

      {isPending && (
        <div className="space-y-3" aria-busy="true">
          <p role="status" className="sr-only">
            Cargando seguimiento...
          </p>
          <SkeletonLista />
        </div>
      )}

      {!isPending && esA1 && (
        <EstadoVacio
          titulo={MENSAJE_A1}
          descripcion="No hay bolsines en estado Enviado para tu comisión médica."
        />
      )}

      {!isPending && error && !esA1 && (
        <EstadoError mensaje={error.message} onReintentar={() => mutate()} />
      )}

      {!isPending && !error && data && (
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
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              {filasFiltradas.length === 0 ? (
                <EstadoVacio
                  titulo="No hay bolsines que coincidan con los filtros"
                  descripcion="Probá con otro precinto o CM destino."
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
                  onSeleccionar={setSeleccionado}
                />
              )}
            </div>
            <div>
              {mapaFiltrado && (
                <MapaBolsines
                  mapa={mapaFiltrado}
                  seleccionado={seleccionado}
                  onSeleccionar={setSeleccionado}
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
    </section>
  );
}
