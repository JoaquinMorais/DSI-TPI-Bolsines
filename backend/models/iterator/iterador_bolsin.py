from __future__ import annotations

from typing import TYPE_CHECKING

from models.iterator.i_iterador import IIterador

if TYPE_CHECKING:
    from models.bolsin import Bolsin


class IteradorBolsin(IIterador):
    def __init__(self, elementos: list[Bolsin], filtros: list[str]) -> None:
        self._lista: list[Bolsin] = list(elementos)
        self._posicionActual = -1
        self._filtros: list[str] = list(filtros)

    def primero(self) -> None:
        self._posicionActual = -1
        self.posicionarEnValido()

    def siguiente(self) -> None:
        self.posicionarEnValido()

    def haFinalizado(self) -> bool:
        return self._posicionActual >= len(self._lista)

    def elementoActual(self) -> Bolsin:
        if self._posicionActual < 0 or self._posicionActual >= len(self._lista):
            raise IndexError("El iterador no tiene elemento actual")
        return self._lista[self._posicionActual]

    def comprobarFiltro(self, filtros: list[str]) -> bool:
        elemento = self._lista[self._posicionActual]
        tipoCM = filtros[0]
        codigoCM = filtros[1]
        if tipoCM == "destino":
            cmOk = elemento.obtenerCMDestino().getCodigo() == codigoCM
        else:
            cmOk = elemento.esTuCMOrigen(codigoCM)
        return cmOk and elemento.sosEnviado()

    def posicionarEnValido(self) -> None:
        self._posicionActual += 1
        while self._posicionActual < len(self._lista) and not self.comprobarFiltro(
            self._filtros
        ):
            self._posicionActual += 1
