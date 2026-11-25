import pytest
import pytest_asyncio
from fastapi import HTTPException, Response
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Usuario
from utils.auth import authenticate_user, get_current_user, issue_tokens
from utils.security import (
    decode_access_token,
    hash_token,
)

CLAVE = "secreta123"
HASH = PasswordHash.recommended()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as db:
        usuario = Usuario(mail="eb.cba01@example.test", hashedPassword=HASH.hash(CLAVE))
        db.add(usuario)
        await db.commit()
        await db.refresh(usuario)
        yield db
    await engine.dispose()


def test_hash_token_es_estable() -> None:
    assert hash_token("abc") == hash_token("abc")
    assert hash_token("abc") != hash_token("abd")


@pytest.mark.asyncio
async def test_authenticate_user(session: AsyncSession) -> None:
    assert await authenticate_user(session, "EB.CBA01@example.test", CLAVE) is not None
    assert await authenticate_user(session, "eb.cba01@example.test", "mala") is None
    assert await authenticate_user(session, "noexiste@example.test", CLAVE) is None


@pytest.mark.asyncio
async def test_login_emite_token_y_cookie(session: AsyncSession) -> None:
    usuario = await authenticate_user(session, "eb.cba01@example.test", CLAVE)
    assert usuario is not None

    response = Response()
    tokens = await issue_tokens(session, usuario, response)

    assert tokens["token_type"] == "bearer"
    payload = decode_access_token(tokens["access_token"])
    assert payload is not None
    assert payload["sub"] == str(usuario.id)
    assert "refresh_token=" in response.headers.get("set-cookie", "")

    actual = await get_current_user(tokens["access_token"], session)
    assert actual.id == usuario.id


@pytest.mark.asyncio
async def test_token_invalido_da_401(session: AsyncSession) -> None:
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user("token-invalido", session)
    assert excinfo.value.status_code == 401
