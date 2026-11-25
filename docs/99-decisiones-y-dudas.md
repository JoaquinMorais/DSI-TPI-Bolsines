# 99 - Decisiones y dudas

| fecha | duda | decisión tomada |
|---|---|---|
| 2026-11-25 | La tarea pedía `backend/docs/`, pero la estructura de docs del proyecto no lo define. | Documentación en `/docs` (raíz del proyecto). Decisión del equipo. |
| 2026-11-25 | ERS: el CU de "Notificar ubicación de bolsín" aparece como 31 en el diagrama de casos de uso y como 30 en el listado. | Se usa **31**, según el diagrama de casos de uso (ERS p. 8) y la referencia del CU 36. |
| 2026-11-25 | Entrega 1 usa `obtenerBolsinesEnviados()`; Entrega 2 usa `obtenerCodigoBolsinesEnviados(): int[]` pero el iterador devuelve objetos `Bolsin`. | Se usa el nombre de la **Entrega 2**: `obtenerCodigoBolsinesEnviados()`. Los objetos que recorre el iterador son `Bolsin`; los códigos se obtienen de `numeroBolsin`. Revisar si el equipo prefiere cambiar la firma del diagrama. |
| 2026-11-25 | Entrega 1 define `esTuCMOrigen()` sin parámetros; Entrega 2 usa `esTuCMOrigen(codigoCM: String)`. | Se usa la firma de la **Entrega 2** (con `codigoCM`). |
| 2026-11-25 | Existen `sosEnviado()` en `CambioEstado` y `esEnviado()` en `Estado`. | Ambos se mantienen. `Bolsin.sosEnviado()` delega en `sosActual()` / `sosEnviado()` de `CambioEstado`, que delega en `Estado.esEnviado()`. |
| 2026-11-25 | `Bolsin` en los diagramas solo tiene `numeroBolsin`, pero el dominio y la ERS exigen fecha, nro. de precinto y peso. El CU 36 filtra por precinto y muestra fecha de última actualización. | **Se agregan** `fecha`, `numeroPrecinto` y `peso` a `Bolsin`. |
| 2026-11-25 | Entrega 1 usa `Usuario` y `Sesion`; el modelo de dominio tiene `Empleado` y `Rol`, y la ERS pide autenticación. | Pendiente de definir. Mientras tanto, el usuario logueado se representa como `Empleado`, con `Rol`. |
| 2026-11-25 | Naming: los métodos en camelCase contradicen PEP 8 (ruff/pylint). | Se mantiene **camelCase** por decisión del equipo (ver `AGENTS.md` §5). |
| 2026-11-25 | El diagrama de clases de Entrega 2 llama `CambioEstado`; la ERS y Entrega 1 usan `CambioEstadoBolsin`. | Se usa **`CambioEstado`** (Entrega 2). |
| 2026-11-25 | La ERS define tres modelos de GPS Tracker (XTR-4500L, NavTrack QX-7A, GeoPulse MTR-900) con endpoints distintos. | Se implementa solo **XTR-4500L** (`getBolsinLocation()`), que es el que usa la Entrega 2. Los otros dos quedan fuera hasta que el equipo lo defina. |
| 2026-11-25 | No hay URL, documentación ni API key reales del GPS Tracker XTR-4500L. | **Pendiente.** Cuando se defina: URL y API key por variable de entorno, adaptador en `integrations/`, y fake para tests. No se inventan endpoints. |
| 2026-11-25 | Servidor de correo: la ERS pide Microsoft Graph (Outlook). Sin credenciales ni datos de prueba. | **Pendiente.** Adaptador en `integrations/` detrás de una interfaz; el proveedor concreto se define después. |
| 2026-11-25 | Google Maps: sin API key ni definición de cómo se muestra el mapa en backend vs. frontend. | **Pendiente.** El backend entrega los datos de ubicación; la visualización queda sin definir. |
| 2026-11-25 | Entrega 2 usa `Estado` con `nombre` y `descripcion`; la ERS define estados como "De baja", "Creado", "Cerrado", "Enviado", "Recibido". | Se usa el nombre del estado como texto; el conjunto de estados sigue la máquina de la Entrega 1. |
| 2026-11-25 | Se propuso una carpeta `backend/` que contenga toda la estructura. | **Revertido** (ver filas siguientes). |
| 2026-11-25 | Punto de entrada de la aplicación (`main.py` en `backend/` o raíz). | Se usa **`index.py`**, dentro de `backend/`. Se ejecuta desde la raíz con `uvicorn index:app --app-dir backend`. |
| 2026-11-25 | `utils/auth.py` y `utils/security.py` (JWT, refresh token en cookie, hash de contraseña) no están en los diagramas ni en el CU 36. | **Se incluyen** como agregado pedido por el equipo, para cubrir el requisito no funcional 4 de la ERS (seguridad de usuarios). Fuera del alcance del CU 36 (AGENTS.md §2). |
| 2026-11-25 | El modelo de dominio no tiene `Usuario` ni `Sesion` con contraseña; el código de referencia de auth usa `User` (mail, contraseña) y `RefreshToken`. | Se usa **`User`** como entidad de login, con `mail` y contraseña hasheada (`verify_password`). `RefreshToken` guarda el hash del refresh token. Reemplaza a `Usuario` y `Sesion` de los diagramas en el alcance de auth. |
| 2026-11-25 | Relación entre `User` (login) y `Empleado` (dato de negocio con `Rol`). | **Relación 1 a 1**: `Empleado` tiene `idUser` único que referencia a `User.id`. |
| 2026-11-25 | `Empleado` del dominio tiene atributo `email`, y `User` también tiene `mail`. | Se usa **`User.mail`** como único correo (login y notificaciones). `Empleado` no duplica el dato. |
| 2026-11-25 | Convención de nombres en el código de referencia de auth (snake_case: `id_user`, `token_hash`, `expires_at`, `verify_password`) vs. camelCase de AGENTS.md §5. | Primera decisión: entidades de auth en snake_case. **Superada** por la fila siguiente. Las funciones de `utils/auth.py` mantienen el nombre de referencia. |
| 2026-11-25 | Columnas de las entidades de auth (`User`, `RefreshToken`) en snake_case vs. camelCase. | **camelCase en todas las columnas** (`idUser`, `tokenHash`, `expiresAt`, `hashedPassword`), decision del equipo. Se actualiza AGENTS.md §5. Detalle en `docs/02-modelo-datos.md`. |
| 2026-11-25 | Dependencias para JWT, hash de contraseña, async y tests. | Se crea `requirements.txt` aprobado por el equipo: FastAPI, SQLModel, aiosqlite, uvicorn, PyJWT, pwdlib (argon2), python-multipart, pytest, pytest-asyncio, httpx. Las versiones se fijan con `pip freeze` después de instalar. |
| 2026-11-25 | Estructura del repositorio: 2 repos (front y back) o monorepo. | **Monorepo.** `backend/` (Python, con `index.py`, `models/`, `services/`, etc.), `frontend/` (Vite + React + TS) y `docs/` en la raíz. |
| 2026-11-25 | Ubicación de `docs/`. | **Raíz del monorepo.** Documenta el TP completo, no solo el backend. |
| 2026-11-25 | Desde dónde se ejecuta el backend y pytest. | Backend: `uvicorn index:app --app-dir backend --port 8020` desde la raíz. Pytest desde la raíz, con `pythonpath = backend` en `pytest.ini`. Los imports son `from models import ...`. |
| 2026-11-25 | Puertos y CORS. | Backend `8020`, frontend `3020`. El frontend llama a `http://localhost:8020` (`VITE_API_URL`). CORS permite `http://localhost:3020` por `CORS_ORIGINS`. |
| 2026-11-25 | Stack del frontend (no definido por el equipo). | **Vite + React + TypeScript** en `frontend/`. Dev server en `3020`. Sin lógica de negocio: solo consume la API. |
| 2026-11-25 | Docker. | `docker-compose.yml` en la raíz levanta `backend` y `frontend`. La base SQLite va en el volumen `bolsines-data`. Las variables se cargan desde `.env` (no se commitea); `.env.example` lista las claves sin secretos. |
| 2026-11-25 | Un solo worker de uvicorn. | Obligatorio: el registro de gestores de casos de uso vive en memoria (ver `docs/01-arquitectura.md` §4). |
| 2026-11-25 | `README.md` con datos del equipo. | Se commitea como está (ejemplo por ahora). |
| 2026-11-25 | `CambioEstado` (E2) vs `CambioEstadoBolsin` (E1, dominio). | Se usa **`CambioEstado`** (E2). Detalle en `docs/02-modelo-datos.md` §5. |
| 2026-11-25 | `IAgregado.crearIterador` devuelve `IIterator` en el texto de E2 y `IIterador` en el diagrama. | Se usa **`IIterador`** (diagrama y AGENTS.md §6). |
| 2026-11-25 | `Usuario` y `Sesion` (E1) no existen en el dominio. | Se usan **`User`** (login) y **`RefreshToken`** (sesion). `Sesion` no tiene tabla propia. |
| 2026-11-25 | Origen y destino de `Bolsin`: E1 los tiene como asociacion; E2 no los modela. | Dos FK en `Bolsin` (`cmOrigenId`, `cmDestinoId`), con `foreign_keys` explicito en SQLModel. |
| 2026-11-25 | `numeroPrecinto` no aparece en E1 ni E2; si en dominio y ERS. | Se agrega como `str \| None`. El string evita perder ceros a la izquierda. |
| 2026-11-25 | Estados de Bolsin: E1 usa "Creado, Cerrado, Enviado, Recibido, De baja"; ERS usa "Recibido en CM destino". | Se usa el nombre de **E1**. |
| 2026-11-25 | `numeroBolsin` aparece como atributo y como `getNumeroBolsin()` en E2. | Atributo publico; el getter devuelve el mismo valor. |
| 2026-11-25 | `Empleado` tiene `email` en el dominio y el login necesita `mail`. | El correo es solo **`User.mail`**. `Empleado` no lo duplica. |
| 2026-11-25 | `Remito` esta en E1 y dominio, pero no en el CU 36. | **Fuera** del modelo del CU 36. Se agrega cuando se implemente el CU 15. |
| 2026-11-25 | `Estado` en E2 tiene `nombre` y `descripcion`; en dominio tiene ademas `ambito`. | Se usa **E2** (sin `ambito`). |
| 2026-11-25 | Modelo del CU 36: remito, usuario y sesion. | **Confirmado**: Remito fuera del CU 36; `RefreshToken` cubre la sesion sin entidad `Sesion` aparte; `Empleado` 1 a 1 con `User`. |
