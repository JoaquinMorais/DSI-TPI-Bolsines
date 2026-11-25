from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
_DEFAULT_DB_PATH = _BACKEND_DIR / "data" / "bolsines.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DB_URL: str = f"sqlite+aiosqlite:///{_DEFAULT_DB_PATH}"
    CORS_ORIGINS: str = "http://localhost:3020"

    GPS_MODELO: str = "XTR-4500L"
    GPS_BASE_URL: str = "http://localhost:8080"
    GPS_API_KEY_XTR4500L: str = ""
    GPS_API_KEY_NAVTRACK: str = ""
    GPS_API_KEY_GEOPULSE: str = ""

    CORREO_MODO: str = "simulado"
    CORREO_ARCHIVO: str = ""
    CORREO_TENANT_ID: str = ""
    CORREO_CLIENT_ID: str = ""
    CORREO_CLIENT_SECRET: str = ""

    SEED_PASSWORD_DEV: str = ""

    REFRESH_DAYS: int = 7
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"


settings = Settings()
