import threading
import time
import uuid
from typing import Optional

from services.gestor_buscar_bolsines import GestorBuscarBolsines

TTL_SEGUNDOS = 15 * 60

_lock = threading.Lock()
_gestores: dict[str, tuple[GestorBuscarBolsines, float]] = {}


def registrar(gestor: GestorBuscarBolsines) -> str:
    idCU = str(uuid.uuid4())
    with _lock:
        _limpiarVencidos()
        _gestores[idCU] = (gestor, time.monotonic())
    return idCU


def obtener(idCU: str) -> Optional[GestorBuscarBolsines]:
    with _lock:
        _limpiarVencidos()
        entrada = _gestores.get(idCU)
        if entrada is None:
            return None
        gestor, _ = entrada
        _gestores[idCU] = (gestor, time.monotonic())
        return gestor


def eliminar(idCU: str) -> bool:
    with _lock:
        return _gestores.pop(idCU, None) is not None


def reset() -> None:
    with _lock:
        _gestores.clear()


def _limpiarVencidos() -> None:
    ahora = time.monotonic()
    vencidos = [
        clave
        for clave, (_, marca) in _gestores.items()
        if ahora - marca > TTL_SEGUNDOS
    ]
    for clave in vencidos:
        del _gestores[clave]
