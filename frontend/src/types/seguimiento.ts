export type BolsinSeguimientoOut = {
  numeroBolsin: number;
  numeroPrecinto: string | null;
  codigoCMDestino: string;
};

export type CoordenadaOut = {
  latitud: number;
  longitud: number;
};

export type MarcadorOut = {
  numeroBolsin: number;
  latitud: number;
  longitud: number;
  fechaHoraUltimaActualizacion: string;
};

export type MapaBolsinesOut = {
  centro: CoordenadaOut;
  zoom: number;
  marcadores: MarcadorOut[];
};

export type SinUbicacionOut = {
  numeroBolsin: number;
  motivo: string;
};

export type SeguimientoCreadoResponse = {
  idCU: string;
  codigoCM: string;
  bolsines: BolsinSeguimientoOut[];
  mapa: MapaBolsinesOut;
  sinUbicacion: SinUbicacionOut[];
};

export type SeleccionBolsinRequest = {
  numeroBolsin: number;
};

export type SeleccionBolsinResponse = {
  idCU: string;
  bolsin: BolsinSeguimientoOut;
  ubicacion: MarcadorOut | null;
  requiereConfirmacionCorreo: boolean;
};

export type ConfirmacionCorreoRequest = {
  confirma: boolean;
};

export type ConfirmacionCorreoResponse = {
  estado: "FINALIZADO";
  notificado: boolean;
  destinatarioEnmascarado: string | null;
};

export type ErrorResponse = {
  codigo: string;
  mensaje: string;
};
