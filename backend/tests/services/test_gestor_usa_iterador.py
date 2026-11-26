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
        elemento = self._elementos[self._posicion]
        return elemento if self.comprobarFiltro([]) and elemento is not None else None

    def siguiente(self) -> None:
        self.llamadas.append("siguiente")
        self._posicion += 1

    def comprobarFiltro(self, filtros) -> bool:
        return True


def test_obtener_codigo_bolsines_enviados_usa_el_iterador() -> None:
    gestor = object.__new__(GestorBuscarBolsines)
    # None simula un bolsin que no cumple comprobarFiltro().
    gestor.bolsines = [_BolsinStub(101), None, _BolsinStub(111)]
    gestor.bolsinesEnviados = []
    gestor.codigoBolsin = []

    fake = _IteradorFake(gestor.bolsines)
    gestor.crearIterador = lambda elementos: fake

    resultado = gestor.obtenerCodigoBolsinesEnviados()

    assert resultado == [101, 111]
    assert [b.getNumeroBolsin() for b in gestor.bolsinesEnviados] == [101, 111]
    assert gestor.codigoBolsin == [101, 111]
    assert "primero" in fake.llamadas
    assert "haFinalizado" in fake.llamadas
    assert "elementoActual" in fake.llamadas
    assert "siguiente" in fake.llamadas
