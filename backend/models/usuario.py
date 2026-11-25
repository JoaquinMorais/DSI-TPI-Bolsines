from typing import TYPE_CHECKING, Optional

from pwdlib import PasswordHash
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.empleado import Empleado

_password_hash = PasswordHash.recommended()


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mail: str = Field(unique=True, index=True)
    hashedPassword: str

    empleado: Optional["Empleado"] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"uselist": False, "lazy": "selectin"},
    )

    def __init__(self, **data: object) -> None:
        super().__init__(**data)
        self.mail = self.mail.strip().lower()

    def verify_password(self, password: str) -> bool:
        return _password_hash.verify(password, self.hashedPassword)

    def getEmpleado(self) -> "Optional[Empleado]":
        return self.empleado

    def getMail(self) -> str:
        return self.mail
