export type Marcador = {
  numeroBolsin: number;
  latitud: number;
  longitud: number;
  fechaHoraUltimaActualizacion: string;
};

export type Mapa = {
  centro: { latitud: number; longitud: number };
  zoom: number;
  marcadores: Marcador[];
};

export type Bolsin = {
  numeroBolsin: number;
  numeroPrecinto: string | null;
  codigoCMDestino: string;
};

export type SinUbicacion = {
  numeroBolsin: number;
  motivo: string;
};

export type Seguimiento = {
  idCU: string;
  codigoCM: string;
  bolsines: Bolsin[];
  mapa: Mapa;
  sinUbicacion: SinUbicacion[];
};

export type ErrorApi = {
  codigo: string;
  mensaje: string;
};
