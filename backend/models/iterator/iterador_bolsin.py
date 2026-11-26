from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from models.iterator.i_iterador import IIterador

if TYPE_CHECKING:
    from models.bolsin import Bolsin


class IteradorBolsin(IIterador):
    """Iterador concreto del CU 36 (Entrega 2).

    Sigue el diagrama de secuencia de diseno: primero() y siguiente() solo
    mueven la posicion; elementoActual() llama a comprobarFiltro() y devuelve
    el bolsin si cumple el filtro, o None si no lo cumple.
    """

    def __init__(self, elementos: list[Bolsin], filtros: list[str]) -> None:
        # Equivalente a new(elementos, filtros) del diagrama.
        self._lista: list[Bolsin] = list(elementos)
        self._posicionActual = 0
        self._filtros: list[str] = list(filtros)

    def primero(self) -> None:
        self._posicionActual = 0

    def siguiente(self) -> None:
        self._posicionActual += 1

    def haFinalizado(self) -> bool:
        return self._posicionActual >= len(self._lista)

    def elementoActual(self) -> Optional[Bolsin]:
        if self.haFinalizado():
            raise IndexError("El iterador no tiene elemento actual")
        if self.comprobarFiltro(self._filtros):
            return self._lista[self._posicionActual]
        return None

    def comprobarFiltro(self, filtros: list[str]) -> bool:
        elemento = self._lista[self._posicionActual]
        tipoCM = filtros[0]
        codigoCM = filtros[1]
        if tipoCM == "destino":
            # Reutilizacion del iterador para el CU 28 (filtro por CM destino).
            cmOk = elemento.obtenerCMDestino().getCodigo() == codigoCM
        else:
            cmOk = elemento.esTuCMOrigen(codigoCM)
        return cmOk and elemento.sosEnviado()
