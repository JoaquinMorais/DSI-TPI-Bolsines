from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import selectinload
from sqlmodel import select

from config.database import db_dependency
from config.settings import settings
from models.empleado import Empleado
from models.refresh_token import RefreshToken
from models.usuario import Usuario
from utils.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_token,
)

REFRESH_COOKIE = "refresh_token"
REFRESH_COOKIE_PATH = "/auth"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


def set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=token,
        max_age=settings.REFRESH_DAYS * 86400,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path=REFRESH_COOKIE_PATH,
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_COOKIE_PATH)


async def get_user_by_mail(db, mail: str) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.mail == mail.strip().lower())
    return (await db.exec(stmt)).first()


async def authenticate_user(db, mail: str, password: str) -> Usuario | None:
    user = await get_user_by_mail(db, mail)
    if not user or not user.verify_password(password):
        return None
    return user


async def issue_tokens(db, user: Usuario, response: Response) -> dict:
    refresh = generate_refresh_token()
    db.add(
        RefreshToken(
            idUser=user.id,
            tokenHash=hash_token(refresh),
            expiresAt=datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_DAYS),
        )
    )
    await db.commit()
    set_refresh_cookie(response, refresh)
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    db: db_dependency,
) -> Usuario:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    stmt = (
        select(Usuario)
        .where(Usuario.id == int(payload["sub"]))
        .options(
            selectinload(Usuario.empleado).selectinload(Empleado.rol),
            selectinload(Usuario.empleado).selectinload(Empleado.comisionMedica),
        )
    )
    user = (await db.exec(stmt)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return user


user_dependency = Annotated[Usuario, Depends(get_current_user)]
