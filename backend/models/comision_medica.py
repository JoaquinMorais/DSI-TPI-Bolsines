from sqlmodel import Field, SQLModel


class ComisionMedica(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(unique=True, index=True)
    nombre: str

    def getCodigo(self) -> str:
        return self.codigo
