from sqlmodel import Field, SQLModel


class Estado(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)
    descripcion: str

    def esEnviado(self) -> bool:
        """Indica si el estado es Enviado (paso 6 del CU 36)."""
        return self.nombre == "Enviado"
