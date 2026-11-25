from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.usuario import Usuario


class RefreshToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idUser: int = Field(foreign_key="usuario.id")
    tokenHash: str
    expiresAt: datetime

    usuario: Optional["Usuario"] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"},
    )
