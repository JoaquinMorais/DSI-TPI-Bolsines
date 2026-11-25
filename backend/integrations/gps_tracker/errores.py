class UbicacionNoDisponibleError(Exception):
    def __init__(self, numeroBolsin: int, motivo: str) -> None:
        self.numeroBolsin = numeroBolsin
        self.motivo = motivo
        super().__init__(f"Bolsin {numeroBolsin}: {motivo}")
