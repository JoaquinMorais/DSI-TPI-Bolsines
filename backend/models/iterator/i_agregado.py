from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.bolsin import Bolsin
    from models.iterator.i_iterador import IIterador


class IAgregado(ABC):
    @abstractmethod
    def crearIterador(self, elementos: list[Bolsin]) -> IIterador: ...
