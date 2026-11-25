# Backend Bolsines (CU 36)

Backend FastAPI del TP "Bolsines" (UTN FRC, DSI, PPAI 2026, grupo 3K7). Implementa el CU 36 "Consultar seguimiento de bolsines" con el patron Iterator.

## Requisitos

- Python 3.12.
- Docker y Docker Compose (opcional, recomendado).
- Java 17+ solo si se levanta la API simulada del GPS de la catedra.

## Instalacion

Con Docker (recomendado):

```
docker compose build backend
```

Local (requiere Python 3.12):

```
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## Variables de entorno

Copiar la plantilla y ajustar:

```
cp backend/.env.example backend/.env
```

Variables principales:

- `DATABASE_URL`: SQLite. Default `sqlite+aiosqlite:///.../backend/data/bolsines.db`.
- `CORS_ORIGINS`: default `http://localhost:5173`.
- `USUARIO_DEV`: usuario de desarrollo para las rutas de seguimiento (`eb.cba01@example.test`).
- `GPS_MODELO`: `xtr4500l` | `navtrack` | `geopulse` (default `xtr4500l`).
- `GPS_BASE_URL`: default `http://localhost:8080`.
- `GPS_API_KEY`: API key del modelo (mock de la catedra para XTR: `sk_xtr_9F3a7C21bE6d4A10f2c8e5b7d913`).
- `SEED_PASSWORD_DEV`: contrasena de los usuarios del seed (default `bolsines-dev`).
- `SECRET_KEY`, `ACCESS_TOKEN_MINUTES`, `REFRESH_DAYS`, `COOKIE_*`: autenticacion JWT.

## Sembrar datos

Desde la raiz del repo:

```
python -m backend.data.seed --reset
```

En Docker:

```
docker compose run --rm backend python -m data.seed --reset
```

El seed es idempotente (sin `--reset` no recarga si ya hay datos) e imprime los bolsines **Enviados por CM**.

## Correr

Desde la raiz:

```
uvicorn main:app --app-dir backend --port 8020
```

Con Docker:

```
docker compose up --build
```

Documentacion interactiva:

- Swagger UI: `http://localhost:8020/docs`
- OpenAPI: `http://localhost:8020/openapi.json`

## API GPS de la catedra (opcional)

Repositorio: `LiberaeMentis/dsi-api-bolsines`.

```
git clone https://github.com/LiberaeMentis/dsi-api-bolsines /tmp/dsi-api-bolsines
cd /tmp/dsi-api-bolsines
./mvnw spring-boot:run
```

Levanta en `http://localhost:8080`. Probar el adaptador real:

```
python backend/scripts/probar_gps.py 101 CM-CBA-01
```

## Pruebas

Desde la raiz (con `pytest.ini`):

```
pytest
```

Con cobertura:

```
pytest --cov=config --cov=models --cov=services --cov=routes --cov=schemas --cov=utils --cov=integrations --cov=data --cov-report=term-missing
```

En Docker (sin instalar dependencias en el host):

```
docker compose run --rm -v "$PWD/backend:/app" backend python -m pytest -q
```

Notas:
- Los tests de `tests/integracion/` requieren la API GPS levantada y `GPS_API_KEY`; si no, se saltean.
- Un solo worker de uvicorn: el registro de casos de uso vive en memoria.
