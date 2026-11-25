from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from config.database import db_dependency
from models.refresh_token import RefreshToken
from models.usuario import Usuario
from schemas.auth import EmpleadoMeOut, TokenResponse
from utils.auth import (
    REFRESH_COOKIE,
    usuario_dev_dependency,
    authenticate_user,
    clear_refresh_cookie,
    issue_tokens,
)
from utils.security import hash_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
async def login(
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    db: db_dependency = None,
) -> dict:
    usuario = await authenticate_user(db, form.username, form.password)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )
    return await issue_tokens(db, usuario, response)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    db: db_dependency = None,
) -> dict:
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Sin refresh token"
        )
    stmt = select(RefreshToken).where(RefreshToken.tokenHash == hash_token(token))
    registro = (await db.exec(stmt)).first()
    if registro is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh invalido"
        )
    vencimiento = registro.expiresAt
    if vencimiento.tzinfo is None:
        vencimiento = vencimiento.replace(tzinfo=timezone.utc)
    if vencimiento < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh vencido"
        )
    usuario = await db.get(Usuario, registro.idUser)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario invalido"
        )
    return await issue_tokens(db, usuario, response)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    clear_refresh_cookie(response)


@router.get("/me", response_model=EmpleadoMeOut)
async def me(usuario: usuario_dev_dependency) -> EmpleadoMeOut:
    empleado = usuario.getEmpleado()
    cm = empleado.getCM() if empleado is not None else None
    if empleado is None or empleado.rol is None or cm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no tiene empleado, rol o CM asociada",
        )
    return EmpleadoMeOut(
        id=usuario.id,
        mail=usuario.getMail(),
        nombre=empleado.nombre,
        apellido=empleado.apellido,
        rol=empleado.rol.nombre,
        codigoCM=cm.getCodigo(),
    )
