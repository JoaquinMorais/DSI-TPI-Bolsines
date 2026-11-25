class UbicacionNoDisponibleError(Exception):
    def __init__(self, numeroBolsin: int, motivo: str) -> None:
        self.numeroBolsin = numeroBolsin
        self.motivo = motivo
        super().__init__(f"Bolsin {numeroBolsin}: {motivo}")


class ErrorIntegracionGPS(Exception):
    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__(motivo)


ErrorServicioGPS = ErrorIntegracionGPS
