from sqlmodel import Field, SQLModel

NOMBRE_GCM = "Gerente de Comisión Médica"
NOMBRE_ENCARGADO_BOLSINES = "Encargado de Bolsines"


class Rol(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True)

    def esGCM(self) -> bool:
        """Indica si el rol es Gerente de Comision Medica (paso 12 del CU 36)."""
        return self.nombre == NOMBRE_GCM

    def esEncargadoBolsines(self) -> bool:
        """Indica si el rol es Encargado de Bolsines (control de acceso del CU 36)."""
        return self.nombre == NOMBRE_ENCARGADO_BOLSINES
