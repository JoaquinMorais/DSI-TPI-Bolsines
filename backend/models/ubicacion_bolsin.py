from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UbicacionBolsin:
    numeroBolsin: int
    latitud: float
    longitud: float
    fechaHoraUltimaActualizacion: datetime
