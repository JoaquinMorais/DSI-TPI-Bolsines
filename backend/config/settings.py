from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ENV_FILE = _BACKEND_DIR / ".env"
_DEFAULT_DB_PATH = _BACKEND_DIR / "data" / "bolsines.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DATABASE_URL: str = f"sqlite+aiosqlite:///{_DEFAULT_DB_PATH}"
    CORS_ORIGINS: str = "http://localhost:5173"
    USUARIO_DEV: str = "eb.cba01@example.test"

    GPS_MODELO: str = "xtr4500l"
    GPS_BASE_URL: str = "http://localhost:8080"
    GPS_API_KEY: str = ""

    CORREO_MODO: str = "simulado"
    CORREO_ARCHIVO: str = ""
    CORREO_TENANT_ID: str = ""
    CORREO_CLIENT_ID: str = ""
    CORREO_CLIENT_SECRET: str = ""

    SEED_PASSWORD_DEV: str = ""

    SECRET_KEY: str = "dev-insecure-secret-change-me-0123456789"
    ACCESS_TOKEN_MINUTES: int = 30
    REFRESH_DAYS: int = 7
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"


settings = Settings()
