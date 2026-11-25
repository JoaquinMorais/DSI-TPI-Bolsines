import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from config.settings import settings

ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expira}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
