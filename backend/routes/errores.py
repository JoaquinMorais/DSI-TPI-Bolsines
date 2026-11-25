class ErrorDeApi(Exception):
    def __init__(self, status_code: int, codigo: str, mensaje: str) -> None:
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje
        super().__init__(mensaje)
