class SinBolsinesEnviadosError(Exception):
    """A1: no hay bolsines Enviados para la CM del usuario."""

    def __init__(self, codigoCM: str) -> None:
        self.codigoCM = codigoCM
        super().__init__(f"No hay bolsines Enviados para la CM {codigoCM}")
