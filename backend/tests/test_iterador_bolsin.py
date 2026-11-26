from dataclasses import dataclass

import pytest

from models.iterator.iterador_bolsin import IteradorBolsin


@dataclass
class _CM:
    codigo: str

    def getCodigo(self) -> str:
        return self.codigo


@dataclass
class _Bolsin:
    numero: int
    origen: str
    destino: str
    enviado: bool

    def getNumeroBolsin(self) -> int:
        return self.numero

    def esTuCMOrigen(self, codigoCM: str) -> bool:
        return self.origen == codigoCM

    def obtenerCMDestino(self) -> _CM:
        return _CM(self.destino)

    def sosEnviado(self) -> bool:
        return self.enviado


FILTRO_CBA = ["origen", "CM-CBA-01"]
FILTRO_DESTINO_ROSARIO = ["destino", "CM-ROS-02"]


def _bolsines() -> list[_Bolsin]:
    return [
        _Bolsin(102, "CM-ROS-02", "CM-MDZ-03", True),
        _Bolsin(101, "CM-CBA-01", "CM-ROS-02", True),
        _Bolsin(110, "CM-CBA-02", "CM-ROS-02", True),
        _Bolsin(111, "CM-CBA-01", "CM-MDZ-03", True),
        _Bolsin(113, "CM-CBA-01", "CM-ROS-02", False),
        _Bolsin(114, "CM-CBA-01", "CM-BA-01", False),
        _Bolsin(117, "CM-TUC-01", "CM-CBA-01", False),
    ]


def _codigos(iterador: IteradorBolsin) -> list[int]:
    codigos: list[int] = []
    iterador.primero()
    while not iterador.haFinalizado():
        bolsin = iterador.elementoActual()
        if bolsin is not None:
            codigos.append(bolsin.getNumeroBolsin())
        iterador.siguiente()
    return codigos


def test_primero_con_coleccion_vacia() -> None:
    iterador = IteradorBolsin([], FILTRO_CBA)
    iterador.primero()
    assert iterador.haFinalizado() is True


def test_primero_posiciona_en_el_primer_elemento() -> None:
    iterador = IteradorBolsin(_bolsines(), FILTRO_CBA)
    iterador.primero()
    # 102 es de Rosario: no cumple el filtro, elementoActual devuelve None.
    assert iterador.elementoActual() is None


def test_elemento_actual_devuelve_el_bolsin_si_cumple_filtro() -> None:
    iterador = IteradorBolsin(_bolsines(), FILTRO_CBA)
    iterador.primero()
    iterador.siguiente()
    assert iterador.elementoActual().getNumeroBolsin() == 101


def test_siguiente_avanza_de_a_uno() -> None:
    iterador = IteradorBolsin(_bolsines(), FILTRO_CBA)
    iterador.primero()
    for _ in range(3):
        iterador.siguiente()
    assert iterador.elementoActual().getNumeroBolsin() == 111


def test_ha_finalizado_tras_el_ultimo_elemento() -> None:
    bolsines = _bolsines()
    iterador = IteradorBolsin(bolsines, FILTRO_CBA)
    iterador.primero()
    for _ in range(len(bolsines) - 1):
        iterador.siguiente()
    assert iterador.haFinalizado() is False
    iterador.siguiente()
    assert iterador.haFinalizado() is True


def test_comprobar_filtro_cm_distinta() -> None:
    bolsin = _Bolsin(102, "CM-ROS-02", "CM-MDZ-03", True)
    iterador = IteradorBolsin([bolsin], ["origen", "CM-ROS-02"])
    iterador.primero()
    assert iterador.comprobarFiltro(FILTRO_CBA) is False


def test_comprobar_filtro_estado_no_enviado() -> None:
    bolsin = _Bolsin(113, "CM-CBA-01", "CM-ROS-02", False)
    iterador = IteradorBolsin([bolsin], FILTRO_CBA)
    iterador._posicionActual = 0
    assert iterador.comprobarFiltro(FILTRO_CBA) is False


def test_comprobar_filtro_ambos_cumplidos() -> None:
    bolsin = _Bolsin(101, "CM-CBA-01", "CM-ROS-02", True)
    iterador = IteradorBolsin([bolsin], FILTRO_CBA)
    iterador.primero()
    assert iterador.comprobarFiltro(FILTRO_CBA) is True


def test_todos_no_validos() -> None:
    no_validos = [
        _Bolsin(113, "CM-CBA-01", "CM-ROS-02", False),
        _Bolsin(114, "CM-CBA-01", "CM-BA-01", False),
        _Bolsin(117, "CM-TUC-01", "CM-CBA-01", False),
    ]
    iterador = IteradorBolsin(no_validos, FILTRO_CBA)
    assert _codigos(iterador) == []


def test_todos_cumplen() -> None:
    todos_validos = [
        _Bolsin(101, "CM-CBA-01", "CM-ROS-02", True),
        _Bolsin(111, "CM-CBA-01", "CM-MDZ-03", True),
    ]
    iterador = IteradorBolsin(todos_validos, FILTRO_CBA)
    assert _codigos(iterador) == [101, 111]


def test_elemento_actual_sin_elemento() -> None:
    iterador = IteradorBolsin([], FILTRO_CBA)
    iterador.primero()
    with pytest.raises(IndexError):
        iterador.elementoActual()


def test_reutilizacion_cu28_filtro_por_destino() -> None:
    iterador = IteradorBolsin(_bolsines(), FILTRO_DESTINO_ROSARIO)
    assert _codigos(iterador) == [101, 110]


def test_orden_preservado() -> None:
    iterador = IteradorBolsin(_bolsines(), FILTRO_CBA)
    assert _codigos(iterador) == [101, 111]
