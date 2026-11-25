export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type UsuarioActualOut = {
  id: number;
  mail: string;
};

export type EmpleadoMeOut = {
  id: number;
  mail: string;
  nombre: string;
  apellido: string;
  rol: string;
  codigoCM: string;
};
