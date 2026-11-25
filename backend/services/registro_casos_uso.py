import threading
import time
import uuid
from typing import Optional

from services.gestor_buscar_bolsines import GestorBuscarBolsines

TTL_SEGUNDOS = 15 * 60

_lock = threading.Lock()
_casos: dict[str, tuple[GestorBuscarBolsines, float]] = {}


def crear(gestor: GestorBuscarBolsines) -> str:
    idCU = str(uuid.uuid4())
    with _lock:
        _limpiarVencidos()
        _casos[idCU] = (gestor, time.monotonic())
    return idCU


def obtener(idCU: str) -> Optional[GestorBuscarBolsines]:
    with _lock:
        _limpiarVencidos()
        entrada = _casos.get(idCU)
        if entrada is None:
            return None
        gestor, _ = entrada
        _casos[idCU] = (gestor, time.monotonic())
        return gestor


def eliminar(idCU: str) -> bool:
    with _lock:
        return _casos.pop(idCU, None) is not None


def reset() -> None:
    with _lock:
        _casos.clear()


def _limpiarVencidos() -> None:
    ahora = time.monotonic()
    vencidos = [
        clave
        for clave, (_, marca) in _casos.items()
        if ahora - marca > TTL_SEGUNDOS
    ]
    for clave in vencidos:
        del _casos[clave]
