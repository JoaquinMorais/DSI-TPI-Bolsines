from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.bolsin import Bolsin


class IIterador(ABC):
    @abstractmethod
    def primero(self) -> None: ...

    @abstractmethod
    def siguiente(self) -> None: ...

    @abstractmethod
    def haFinalizado(self) -> bool: ...

    @abstractmethod
    def elementoActual(self) -> Bolsin: ...

    @abstractmethod
    def comprobarFiltro(self, filtros: list[str]) -> bool: ...
