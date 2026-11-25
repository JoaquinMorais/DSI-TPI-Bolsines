from abc import ABC, abstractmethod


class InterfazCorreo(ABC):
    @abstractmethod
    async def enviarMail(self, destinatario: str, asunto: str, cuerpo: str) -> None: ...
