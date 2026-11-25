"""Stub de Microsoft Graph (no implementado).

Se deja documentado para una futura implementacion real del envio de correo.
Cuando se implemente, debe cumplir la interfaz `InterfazCorreo` y elegirse con
`CORREO_MODO=graph`, usando CORREO_TENANT_ID, CORREO_CLIENT_ID y
CORREO_CLIENT_SECRET.

Esquema previsto (sin implementar):

    # from integrations.correo.interfaz_correo import InterfazCorreo
    #
    # class OutlookGraph(InterfazCorreo):
    #     def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:
    #         ...
    #
    #     async def enviarMail(self, destinatario: str, asunto: str, cuerpo: str) -> None:
    #         # 1. Obtener token en https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
    #         # 2. POST https://graph.microsoft.com/v1.0/users/{remitente}/sendMail
    #         raise NotImplementedError
"""
