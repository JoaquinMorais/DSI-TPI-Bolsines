from sqlmodel import Field, SQLModel

NOMBRE_GCM = "Gerente de Comisión Médica"
NOMBRE_ENCARGADO_BOLSINES = "Encargado de Bolsines"


class Rol(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)

    def esGCM(self) -> bool:
        return self.nombre == NOMBRE_GCM

    def esEncargadoBolsines(self) -> bool:
        return self.nombre == NOMBRE_ENCARGADO_BOLSINES
