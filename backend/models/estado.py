from sqlmodel import Field, SQLModel


class Estado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)
    descripcion: str

    def esEnviado(self) -> bool:
        return self.nombre == "Enviado"
