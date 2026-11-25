from services.gestor_buscar_bolsines import GestorBuscarBolsines


class _BolsinStub:
    def __init__(self, numero: int) -> None:
        self._numero = numero

    def getNumeroBolsin(self) -> int:
        return self._numero


class _IteradorFake:
    def __init__(self, elementos) -> None:
        self._elementos = elementos
        self._posicion = -1
        self.llamadas: list[str] = []

    def primero(self) -> None:
        self.llamadas.append("primero")
        self._posicion = 0

    def haFinalizado(self) -> bool:
        self.llamadas.append("haFinalizado")
        return self._posicion >= len(self._elementos)

    def elementoActual(self):
        self.llamadas.append("elementoActual")
        return self._elementos[self._posicion]

    def siguiente(self) -> None:
        self.llamadas.append("siguiente")
        self._posicion += 1

    def comprobarFiltro(self, filtros) -> bool:
        return True


def test_obtener_bolsines_enviados_usa_el_iterador() -> None:
    gestor = object.__new__(GestorBuscarBolsines)
    gestor.bolsines = [_BolsinStub(101), _BolsinStub(111)]
    gestor.bolsinesEnviados = []
    gestor.codigoBolsin = []

    fake = _IteradorFake(gestor.bolsines)
    gestor.crearIterador = lambda elementos: fake

    resultado = gestor.obtenerBolsinesEnviados()

    assert [b.getNumeroBolsin() for b in resultado] == [101, 111]
    assert gestor.codigoBolsin == [101, 111]
    assert "primero" in fake.llamadas
    assert "haFinalizado" in fake.llamadas
    assert "elementoActual" in fake.llamadas
    assert "siguiente" in fake.llamadas
