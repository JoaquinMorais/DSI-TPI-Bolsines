import logging
from typing import Optional

from integrations.correo.interfaz_correo import InterfazCorreo

logger = logging.getLogger(__name__)


class CorreoSimulado(InterfazCorreo):
    def __init__(self, archivo: Optional[str] = None) -> None:
        self._archivo = archivo

    async def enviarMail(
        self, destinatario: str, asunto: str, cuerpo: str
    ) -> None:
        logger.info(
            "Correo simulado a=%s asunto=%s cuerpo=%s",
            destinatario,
            asunto,
            cuerpo,
        )
        if self._archivo:
            with open(self._archivo, "a", encoding="utf-8") as archivo:
                archivo.write(
                    f"Para: {destinatario}\nAsunto: {asunto}\n{cuerpo}\n---\n"
                )
