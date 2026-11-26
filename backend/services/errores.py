class SinBolsinesEnviadosError(Exception):
    """A1: no hay bolsines Enviados para la CM del usuario."""

    def __init__(self, codigoCM: str) -> None:
        self.codigoCM = codigoCM
        super().__init__(f"No hay bolsines Enviados para la CM {codigoCM}")


class GPSNoDisponibleError(Exception):
    """El GPS Tracker rechazo la consulta (API key invalida, 400, formato invalido).

    No es el alternativo A3 (un bolsin sin ubicacion): es un error de
    configuracion o de integracion que impide consultar cualquier ubicacion.
    """

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__(f"No se pudo consultar el GPS Tracker: {motivo}")
