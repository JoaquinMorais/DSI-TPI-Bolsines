from datetime import datetime

from models import Bolsin, CambioEstado, ComisionMedica, Estado

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


def _bolsin(
    historial: list[CambioEstado],
    origen: str = "CM-CBA-01",
    destino: str = "CM-ROS-02",
    numero: int = 101,
) -> Bolsin:
    bolsin = Bolsin(
        numeroBolsin=numero,
        fecha=INICIO,
        numeroPrecinto="P-0101",
        peso=4200,
        cmOrigenId=1,
        cmDestinoId=2,
    )
    bolsin.origen = ComisionMedica(codigo=origen, nombre="Origen")
    bolsin.destino = ComisionMedica(codigo=destino, nombre="Destino")
    bolsin.cambiosEstado = historial
    return bolsin


def test_es_tu_cm_origen_coincide() -> None:
    bolsin = _bolsin([_cambio("Enviado")])
    assert bolsin.esTuCMOrigen("CM-CBA-01") is True


def test_es_tu_cm_origen_no_coincide() -> None:
    bolsin = _bolsin([_cambio("Enviado")])
    assert bolsin.esTuCMOrigen("CM-ROS-02") is False


def test_sos_enviado_con_vigente_enviado() -> None:
    bolsin = _bolsin([_cambio("Cerrado", fin=FIN), _cambio("Enviado", fin=None)])
    assert bolsin.sosEnviado() is True


def test_sos_enviado_con_vigente_cerrado() -> None:
    bolsin = _bolsin([_cambio("Creado", fin=FIN), _cambio("Cerrado", fin=None)])
    assert bolsin.sosEnviado() is False


def test_sos_enviado_con_historial_enviado_y_vigente_recibido() -> None:
    bolsin = _bolsin([_cambio("Enviado", fin=FIN), _cambio("Recibido", fin=None)])
    assert bolsin.sosEnviado() is False


def test_sos_enviado_sin_cambios() -> None:
    assert _bolsin([]).sosEnviado() is False


def test_get_numero_bolsin() -> None:
    assert _bolsin([_cambio("Enviado")], numero=101).getNumeroBolsin() == 101


def test_obtener_cm_destino() -> None:
    bolsin = _bolsin([_cambio("Enviado")], destino="CM-MDZ-03")
    cm_destino = bolsin.obtenerCMDestino()
    assert cm_destino is not None
    assert cm_destino.getCodigo() == "CM-MDZ-03"
