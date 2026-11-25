from models.comision_medica import ComisionMedica
from models.estado import Estado
from models.rol import NOMBRE_ENCARGADO_BOLSINES, NOMBRE_GCM, Rol


def test_estado_es_enviado_true() -> None:
    estado = Estado(nombre="Enviado", descripcion="En transito")
    assert estado.esEnviado() is True


def test_estado_es_enviado_false() -> None:
    estado = Estado(nombre="Recibido", descripcion="Recibido en CM destino")
    assert estado.esEnviado() is False


def test_comision_medica_get_codigo() -> None:
    cm = ComisionMedica(codigo="CM-CBA-01", nombre="Comision Medica Cordoba")
    assert cm.getCodigo() == "CM-CBA-01"


def test_rol_es_gcm() -> None:
    assert Rol(nombre=NOMBRE_GCM).esGCM() is True
    assert Rol(nombre=NOMBRE_ENCARGADO_BOLSINES).esGCM() is False


def test_rol_es_encargado_bolsines() -> None:
    assert Rol(nombre=NOMBRE_ENCARGADO_BOLSINES).esEncargadoBolsines() is True
    assert Rol(nombre=NOMBRE_GCM).esEncargadoBolsines() is False
