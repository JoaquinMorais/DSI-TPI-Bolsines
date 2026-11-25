from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.database import crear_tablas
from config.settings import settings
from routes.auth import router as auth_router
from routes.pantalla_buscar_bolsines import router as seguimiento_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await crear_tablas()
    yield


app = FastAPI(title="Bolsines API", lifespan=lifespan)

cors_origins = [
    origen.strip()
    for origen in settings.CORS_ORIGINS.split(",")
    if origen.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(seguimiento_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
