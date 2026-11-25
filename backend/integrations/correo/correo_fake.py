from integrations.correo.interfaz_correo import InterfazCorreo


class CorreoFake(InterfazCorreo):
    def __init__(self) -> None:
        self.enviados: list[dict[str, str]] = []
        self.fallar = False

    async def enviarMail(
        self, destinatario: str, asunto: str, cuerpo: str
    ) -> None:
        if self.fallar:
            raise RuntimeError("Fallo simulado del correo")
        self.enviados.append(
            {"destinatario": destinatario, "asunto": asunto, "cuerpo": cuerpo}
        )
