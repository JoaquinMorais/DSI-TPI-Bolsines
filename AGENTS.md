# AGENTS.md - Reglas permanentes del proyecto Bolsines

Proyecto: TP universitario UTN FRC, Diseno de Sistemas de Informacion, PPAI 2026, grupo 3K7 (Grupo 7). Sistema "Bolsines".

Estructura: monorepo. Backend en `backend/`, frontend en `frontend/`, documentacion del TP en `docs/` (raiz).

## 1. Stack

- Backend: Python 3.12, FastAPI, SQLModel con SQLAlchemy async y aiosqlite, SQLite, pytest y pytest-asyncio. Dependencias en `backend/requirements.txt`.
- Frontend: Vite + React + TypeScript (`frontend/`).
- Docker: `docker-compose.yml` en la raiz levanta backend y frontend.
- Puertos: backend `8020`, frontend `3020`. El frontend llama al backend por `http://localhost:8020` (`VITE_API_URL`). CORS permite `http://localhost:3020`.
- Variables de entorno: `.env` (no se commitea), con plantilla en `.env.example`.

## 2. Alcance

- Caso de uso a implementar: **CU 36 "Consultar seguimiento de bolsines"** (ERS v1.2, nro. de orden 36).
- Flujo principal y alternativos A1..A5 segun ERS (ver `docs/00-contexto.md`).
- Implementacion con patron **Iterator (Gamma)** segun Entrega 2 (`docs/referencias/PPAI2026_3K7_Grupo7_Entrega2_Diseño.pdf`).
- Autenticacion (`utils/auth.py`, `utils/security.py`, entidades `Usuario` y `RefreshToken`): agregado pedido por el equipo para cubrir el requisito no funcional 4 de la ERS ("Seguridad de usuarios"). No forma parte del CU 36.
- Fuentes, por orden de prevalencia:
  1. Entrega 2 (diseno del CU 36, clases y secuencias).
  2. Entrega 1 (analisis: clases y maquina de estados de Bolsin).
  3. ERS v1.2 (requisitos, flujo, alternativos, GPS).
  4. Modelo de dominio y Descripcion del caso (atributos y reglas).

## 3. Estructura de carpetas (no alterar)

```
docs/                     documentacion del TP (raiz, no dentro de backend/)
docs/referencias/         documentos fuente (solo lectura)
docker-compose.yml        levanta backend y frontend
.env.example              plantilla de variables (.env no se commitea)
pytest.ini                pythonpath = backend, testpaths = backend/tests
backend/
  main.py                 entrypoint FastAPI: app, CORS, include_router, composicion
  index.py                alias de main (reexporta app, compatibilidad)
  Dockerfile
  requirements.txt        dependencias del backend
  config/                 settings, conexion a DB, composicion (composition root)
  models/                 entidades SQLModel CON metodos de negocio
  models/iterator/        patron Iterator (IAgregado, IIterador, IteradorBolsin)
  data/                   base SQLite y seed
  routes/                 routers FastAPI (boundary)
  schemas/                schemas Pydantic request/response
  services/               gestores del caso de uso (GestorBuscarBolsines)
  utils/                  cross-cutting: auth y seguridad (sin logica de negocio)
  integrations/           adaptadores a sistemas externos (GPS, Google Maps, correo)
  tests/                  pytest
frontend/
  Dockerfile
  package.json, vite.config.ts, src/
```

## 4. Reglas de arquitectura

- **Negocio en `models` y `services`.** Las reglas viven en metodos de las entidades (ej.: `Bolsin.esTuCMOrigen`, `Bolsin.sosEnviado`) y en el gestor (`GestorBuscarBolsines`). Prohibido modelos anemicos.
- **`routes` solo traduce HTTP <-> gestor.** Sin logica de negocio, sin acceso directo a la DB ni a integraciones. Es la pantalla `PantallaBuscarBolsines` del diagrama de secuencia.
- **`schemas` solo validacion y serializacion.** Sin logica de negocio.
- **Integraciones solo en `integrations/`.** Ningun otro modulo habla directamente con GPS, Google Maps o el servidor de correo. Se accede mediante interfaces (`InterfazGPSTracker`, `InterfazGoogleMaps`, `InterfazCorreo`) con implementacion real y una implementacion fake para tests.
- **`utils/` solo cross-cutting** (auth, seguridad). No contiene reglas de negocio ni integraciones.
- **Visualizacion del mapa en el frontend.** El backend devuelve `MapaBolsines` (centro, zoom y marcadores). El frontend renderiza con la libreria de Google Maps usando `VITE_GOOGLE_MAPS_API_KEY`. El backend no llama a la API de Google Maps.
- **Persistencia:** SQLModel. Los accesos a la base van en `models`/`services`/`utils/auth.py`, nunca en `routes`.
- Reglas de importacion completas en `docs/01-arquitectura.md` (seccion 5).

## 5. Nombres

- Clases y metodos de dominio tomados de los diagramas de la Entrega 1 y 2, en espanol. No renombrar ni traducir.
- Metodos de dominio en **camelCase** (ej.: `esTuCMOrigen`, `sosEnviado`, `obtenerCodigoBolsinesEnviados`, `comprobarFiltro`, `haFinalizado`). Esto contradice PEP 8; es decision del equipo. No "corregirlo" a snake_case.
- Clases en PascalCase (ej.: `GestorBuscarBolsines`, `IteradorBolsin`, `CambioEstado`, `Estado`, `Bolsin`, `Remito`).
- Atributos de dominio en camelCase (ej.: `numeroBolsin`, `fechaHoraInicio`).
- Interfaces con prefijo I (`IIterador`, `IAgregado`, `InterfazGPSTracker`, `InterfazCorreo`).
- Columnas y atributos de todas las entidades (dominio y auth) en camelCase (`idUser`, `tokenHash`, `expiresAt`, `hashedPassword`). Las funciones de `utils/auth.py` mantienen el nombre del codigo de referencia. Ver `docs/02-modelo-datos.md`.

## 6. Patron Iterator (regla central)

- El Iterator debe ser **claramente visible** y **usado por el gestor**.
- Jerarquia obligatoria: `IAgregado` (implementado por `GestorBuscarBolsines`, expone `crearIterador`), `IIterador` (`primero`, `siguiente`, `haFinalizado`, `elementoActual`, `comprobarFiltro`), `IteradorBolsin` (concreto, en `backend/models/iterator/`).
- El nombre de la interfaz es siempre **`IIterador`**. `IIterator` (texto de la Entrega 2) es un error de escritura; no usarlo.
- El constructor de `IteradorBolsin` es **`init(elementos, filtros)`**, equivalente al `new` del diagrama. `primero()` y `siguiente()` avanzan hasta el proximo elemento que cumple `comprobarFiltro()`.
- El gestor recorre los bolsines **solo** con `primero()`, `haFinalizado()`, `elementoActual()`, `siguiente()`. No recorre listas ni consulta bolsines en bucles propios.
- El filtrado (CM origen = CM del usuario logueado y estado Enviado) vive en `comprobarFiltro()` del iterador.
- **Prohibido** agregar otros patrones que oculten al Iterator: repositorios genericos, fabricas adicionales, query builders, `Specification`, `Strategy` de filtros, mapeos intermedios, etc. Si la base se consulta para cargar bolsines, la consulta debe ser simple y el recorrido sigue siendo el del iterador.

## 7. Ambiguedades e inconsistencias

- Si un documento fuente es ambiguo o contradice a otro: **no inventar**.
- Registrar la duda en `docs/99-decisiones-y-dudas.md` (fecha | duda | decision tomada).
- Elegir la opcion mas simple y coherente con la Entrega 2 y seguir.
- Si un archivo de referencia no se puede leer, avisar; no inventar su contenido.

## 8. Integraciones externas

- GPS Tracker: API simulada de la catedra, repositorio `LiberaeMentis/dsi-api-bolsines`. Modelo XTR-4500L (endpoint `getBolsinLocation`). Base por defecto `http://localhost:8080` (`GPS_BASE_URL`). Una API key por modelo por variable de entorno (`GPS_API_KEY_XTR4500L`, `GPS_API_KEY_NAVTRACK`, `GPS_API_KEY_GEOPULSE`); nunca en el codigo ni en el repo. Detalle en `docs/06-integraciones.md`.
- Google Maps: la visualizacion vive en el frontend (`VITE_GOOGLE_MAPS_API_KEY`). El backend no llama a la API de Maps.
- Servidor de correo: implementacion simulada (log/archivo) por defecto; Microsoft Graph documentado, sin implementar. Detalle en `docs/06-integraciones.md`.

## 9. Flujo de trabajo

- No escribir codigo sin que el usuario lo pida explicitamente en la tarea.
- Cada cambio debe mantener la estructura de carpetas de la seccion 3.
- Antes de cerrar una tarea de codigo: ejecutar `pytest` desde la raiz del repositorio (`pytest.ini` apunta a `backend/`).
- Levantar backend desde la raiz: `uvicorn main:app --app-dir backend --port 8020`. Con Docker: `docker compose up --build`.
- Un solo worker de uvicorn: el registro de gestores de casos de uso vive en memoria.
- No commitear ni hacer push sin pedido explicito.
- Cada tarea termina con un commit (salvo que el usuario pida lo contrario).
