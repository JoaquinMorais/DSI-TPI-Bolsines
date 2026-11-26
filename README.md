# Bolsines - TP Diseño de Sistemas de Información (PPAI 2026)

Sistema **Bolsines** (UTN FRC, grupo 3K7). Implementa el caso de uso **CU 36 "Consultar seguimiento de bolsines"** con el patrón **Iterator** (Gamma).

Permite al Encargado de Bolsines ver en un mapa los bolsines **Enviados** de su Comisión Médica, seleccionar uno y notificar su ubicación (obtenida del GPS Tracker) al Gerente de la CM destino (CU 31).

## Equipo

- Fernández, Mateo Emanuel - 411626 - emanuel040812@gmail.com
- Guell, Tomas Mariano - 414109 - tomasguell123@gmail.com
- Herrera, Conrado - 410579 - herreraconradomaxi30@gmail.com
- Isasmendi, Matías - 409507 - isasmendi.matias1@gmail.com
- Morais, Joaquín - 410911 - joaquinmorais2005@gmail.com

## Requisitos

- Python 3.12.
- Node.js 18 o superior.
- Docker y Docker Compose (opcional, recomendado).
- Java 17+ solo si se levanta la API simulada del GPS de la cátedra.

## Cómo ejecutar

### Opción 1: scripts de desarrollo (recomendado)

Instalan dependencias si faltan, siembran la base y levantan backend y frontend en paralelo.

- Linux/macOS:
  ```
  ./scripts/dev.sh
  ```
- Windows (PowerShell):
  ```
  .\scripts\dev.ps1
  ```

Puertos:

- Backend: `http://localhost:8000` (documentación en `/docs`).
- Frontend: `http://localhost:5173`.

Variables que aceptan los scripts (opcionales): `BACKEND_PORT`, `FRONTEND_PORT`, `PYTHON_BIN`, `DATABASE_URL`, `CORS_ORIGINS`, `VITE_API_URL`, `GPS_BASE_URL`, `GPS_API_KEY`, `USUARIO_DEV`.

### Opción 2: Docker Compose

```
docker compose up --build
```

- Backend: `http://localhost:8020` (`/docs`).
- Frontend: `http://localhost:3020`.
- Sembrar datos:
  ```
  docker compose exec backend python -m data.seed --reset
  ```

### Opción 3: manual

```
python3.12 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

python -m backend.data.seed --reset

# Backend (puerto 8000)
CORS_ORIGINS=http://localhost:5173 uvicorn main:app --app-dir backend --port 8000

# Frontend (otra terminal)
cd frontend
npm install
VITE_API_URL=http://localhost:8000 npm run dev -- --port 5173
```

### API GPS de la cátedra (opcional)

Repositorio: `LiberaeMentis/dsi-api-bolsines`. Levanta en `http://localhost:8080`:

```
git clone https://github.com/LiberaeMentis/dsi-api-bolsines /tmp/dsi-api-bolsines
cd /tmp/dsi-api-bolsines
./mvnw spring-boot:run
```

Configurar `GPS_BASE_URL` y `GPS_API_KEY` (la key mock del modelo XTR). Probar el adaptador:

```
python backend/scripts/probar_gps.py 101 CM-CBA-01
```

## Variables de entorno

Plantilla del backend: `backend/.env.example`. Para Docker: `.env.example` en la raíz.

- `DATABASE_URL`: SQLite (default `backend/data/bolsines.db`).
- `CORS_ORIGINS`: default `http://localhost:5173`.
- `USUARIO_DEV`: usuario de desarrollo para las rutas del CU 36.
- `GPS_MODELO`: `xtr4500l` | `navtrack` | `geopulse`.
- `GPS_BASE_URL`, `GPS_API_KEY`.
- `VITE_API_URL` (frontend): URL del backend.

## Pruebas

Backend (desde la raíz):

```
pytest
```

Frontend:

```
cd frontend
npm run test
```

Cobertura del backend:

```
pytest --cov=config --cov=models --cov=services --cov=routes --cov=schemas --cov=utils --cov=integrations --cov=data --cov-report=term-missing
```

## Estructura del repositorio

```
backend/        FastAPI + SQLModel (models, services, routes, integrations, utils, tests)
frontend/       Vite + React + TypeScript (Tailwind, TanStack Query, Leaflet)
docs/           documentación del TP (00 a 10, 99, diagramas y referencias)
scripts/        dev.sh / dev.ps1 (entorno de desarrollo)
docker-compose.yml
pytest.ini
AGENTS.md       reglas permanentes del proyecto
```

## Documentación

- Índice: [`docs/README.md`](docs/README.md)
- Contexto y CU 36: [`docs/00-contexto.md`](docs/00-contexto.md)
- Arquitectura: [`docs/01-arquitectura.md`](docs/01-arquitectura.md)
- Modelo de datos: [`docs/02-modelo-datos.md`](docs/02-modelo-datos.md)
- Patrón Iterator: [`docs/03-patron-iterator.md`](docs/03-patron-iterator.md)
- Vista estática: [`docs/04-vista-estatica.md`](docs/04-vista-estatica.md)
- Vista dinámica: [`docs/05-vista-dinamica.md`](docs/05-vista-dinamica.md)
- Integraciones: [`docs/06-integraciones.md`](docs/06-integraciones.md)
- API REST: [`docs/07-api-rest.md`](docs/07-api-rest.md)
- Datos semilla: [`docs/08-datos-semilla.md`](docs/08-datos-semilla.md)
- Implementación y pruebas: [`docs/09-implementacion-y-pruebas.md`](docs/09-implementacion-y-pruebas.md)
- Frontend: [`docs/10-frontend.md`](docs/10-frontend.md)
- Decisiones y dudas: [`docs/99-decisiones-y-dudas.md`](docs/99-decisiones-y-dudas.md)
- Reglas del proyecto: [`AGENTS.md`](AGENTS.md)

## Checklist de defensa oral

1. **Modelo:** `docs/diagramas/clases-diseno.puml`. Señalar `IAgregado`, `IIterador`, `IteradorBolsin` y `GestorBuscarBolsines`.
2. **Interfaces:** `backend/models/iterator/i_agregado.py` e `i_iterador.py`. Mostrar que `crearIterador` devuelve `IIterador`.
3. **Iterator concreto:** abrir `backend/models/iterator/iterador_bolsin.py`. Mostrar `init(elementos, filtros)`, `posicionarEnValido()` y `comprobarFiltro()`, con las llamadas a `esTuCMOrigen` y `sosEnviado`.
4. **Llamada desde el gestor:** abrir `backend/services/gestor_buscar_bolsines.py`. Mostrar `obtenerBolsinesEnviados()`: `crearIterador`, `primero`, `haFinalizado`, `elementoActual`, `getNumeroBolsin`, `siguiente`. Señalar que no hay un `for` sobre la lista.
5. **Entidades:** `Bolsin.esTuCMOrigen` y `sosEnviado`, y la cadena hasta `Estado.esEnviado`.
6. **Boundary:** `backend/routes/seguimiento_bolsines.py`. Mostrar que solo traduce HTTP.
7. **Pruebas:** `pytest -k iterador -v` y luego `pytest -v`. Mostrar un caso de reutilización (CU 28).
8. **Flujo en vivo:** `docker compose up` con la API de la cátedra corriendo. Login como EB Córdoba 1 y mostrar A3 (111 en `sinUbicacion`). Después EB Tucumán y mostrar A1.
9. **Persistencia:** abrir la base y mostrar el `CambioEstado` vigente de un bolsín.
10. **Decisiones:** `docs/99-decisiones-y-dudas.md`. Mencionar `CambioEstado` vs `CambioEstadoBolsin`, `primero`/`siguiente` que avanzan a un válido, y el centro del mapa pendiente.

Preguntas probables:

- *¿Por qué Iterator y no un loop?* Desacopla el gestor de la colección y deja el filtro reutilizable (CU 28).
- *¿Por qué `comprobarFiltro` dentro de `primero`/`siguiente`?* Así `elementoActual` siempre devuelve un válido y el gestor no filtra.
- *¿Qué pasa con varios workers?* El estado en memoria se pierde; se documenta como limitación (un solo worker).


