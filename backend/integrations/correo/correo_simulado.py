import logging
from pathlib import Path
from typing import Optional

from integrations.correo.interfaz_correo import InterfazCorreo

logger = logging.getLogger(__name__)

_LOG_POR_DEFECTO = (
    Path(__file__).resolve().parents[2] / "data" / "mails_enviados.log"
)


class CorreoSimulado(InterfazCorreo):
    def __init__(self, archivo: Optional[str] = None) -> None:
        self._archivo = Path(archivo) if archivo else _LOG_POR_DEFECTO

    async def enviarMail(
        self, destinatario: str, asunto: str, cuerpo: str
    ) -> None:
        logger.info(
            "Correo simulado a=%s asunto=%s cuerpo=%s",
            destinatario,
            asunto,
            cuerpo,
        )
        self._archivo.parent.mkdir(parents=True, exist_ok=True)
        with self._archivo.open("a", encoding="utf-8") as archivo:
            archivo.write(
                f"Para: {destinatario}\nAsunto: {asunto}\n{cuerpo}\n---\n"
            )
