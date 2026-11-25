from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from config.database import crear_tablas
from config.settings import settings
from routes.auth import router as auth_router
from utils.errores import ErrorDeApi
from routes.seguimiento_bolsines import router as seguimiento_router


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


@app.exception_handler(ErrorDeApi)
async def manejar_error_de_api(request: Request, exc: ErrorDeApi) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"codigo": exc.codigo, "mensaje": exc.mensaje},
    )


@app.exception_handler(StarletteHTTPException)
async def manejar_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"codigo": "ERROR_HTTP", "mensaje": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def manejar_validacion(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "codigo": "SOLICITUD_INVALIDA",
            "mensaje": "Datos de la solicitud invalidos",
        },
    )


app.include_router(auth_router)
app.include_router(seguimiento_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
