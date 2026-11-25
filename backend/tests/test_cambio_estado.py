from datetime import datetime

from models import CambioEstado, Estado

INICIO = datetime(2026, 11, 20, 9, 0)
FIN = datetime(2026, 11, 21, 8, 5)


def _cambio(nombre_estado: str, fin: datetime | None = None) -> CambioEstado:
    return CambioEstado(
        fechaHoraInicio=INICIO,
        fechaHoraFin=fin,
        bolsinId=1,
        estadoId=1,
        estado=Estado(nombre=nombre_estado, descripcion="test"),
    )


def test_sos_actual_sin_fin() -> None:
    assert _cambio("Enviado", fin=None).sosActual() is True


def test_sos_actual_cerrado() -> None:
    assert _cambio("Enviado", fin=FIN).sosActual() is False


def test_sos_enviado_delega_en_estado() -> None:
    assert _cambio("Enviado").sosEnviado() is True
    assert _cambio("Recibido").sosEnviado() is False


def test_set_fecha_hora_fin_cierra_el_cambio() -> None:
    cambio = _cambio("Enviado", fin=None)
    cambio.setFechaHoraFin(FIN)
    assert cambio.fechaHoraFin == FIN
    assert cambio.sosActual() is False
