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
| 2026-11-25 | El CU 28 (recepcion de bolsin) necesita recorrer bolsines enviados a la CM del usuario (filtro por CM destino), no por CM origen. | Se reutiliza **el mismo IteradorBolsin** con otros filtros pasados en `init(elementos, filtros)`. No se implementa en esta entrega. Detalle en `docs/03-patron-iterator.md` §1. |
| 2026-11-25 | Clase de estado del bolsin: el pedido de tarea dice `CambioEstadoBolsin`, E2 dice `CambioEstado`. | Se usa **`CambioEstado`**. |
| 2026-11-25 | Nombre de la entidad de login: `User` (codigo de referencia) o `Usuario` (diagramas). | Se usa **`Usuario`**. `RefreshToken` se mantiene. |
| 2026-11-25 | Visibilidad de atributos: E2 usa `-`; `02-modelo-datos` los definia publicos. | Se usa **privado (`-`)**, accedidos por `get`/`set` cuando hace falta. En SQLModel la privacidad es convencional. |
| 2026-11-25 | Constructor: E2 usa `new`. | Se implementa como **`init`** (Python). |
| 2026-11-25 | Metodos de `InterfazGoogleMaps.obtenerMapa` y parametros de `InterfazCorreo.enviarMail`: la ERS no los define. | Propuestas del equipo, aceptadas. Se revisan cuando se defina la integracion. |
| 2026-11-25 | Validacion del diagrama PlantUML. | `.puml` valido (`java -jar plantuml.jar -checkonly`). El render PNG necesita Graphviz (`dot`), que no esta instalado en el entorno; el layout no se pudo revisar visualmente. |
| 2026-11-25 | Donde se aplica `comprobarFiltro`: en E2 esta dentro del bucle del gestor, despues de `elementoActual()`. | **`primero()` y `siguiente()` avanzan internamente** al proximo elemento que cumple el filtro. `elementoActual()` siempre devuelve un bolsin valido y el gestor no filtra. Detalle en `docs/05-vista-dinamica.md` §2 y §6. |
| 2026-11-25 | Loop de empleados GCM en el paso 12 (E1: `esTuCM`, `sosGCM`, `esGCM`). | Se reemplaza por la consulta simple **`Empleado.obtenerGCMDeCM(codigoCM)`** (sin bucle en el gestor). Metodo nuevo: agregar a `docs/04-vista-estatica.md` al implementar. |
| 2026-11-25 | Usuario logueado en `buscarUsuarioLogueado`: E1 usa `Sesion`. | Sin `Sesion`: el usuario llega por `user_dependency` (JWT) -> `Usuario` -> `Empleado`. |
| 2026-11-25 | Nombre del estado en secuencias: `CambioEstadoBolsin` (pedido) vs `CambioEstado`. | Se usa **`CambioEstado`** en los diagramas. |
| 2026-11-25 | CU 31 en la secuencia completa. | Se modela como `<<include>>` del CU 36 (paso 13), segun el diagrama de casos de uso de la ERS. |
| 2026-11-25 | Guia de la API simulada del GPS (`docs/referencias/api-gps-guia.md`) no existe en el repo. | Seccion 1 de `docs/06-integraciones.md` queda **pendiente**. No se inventan endpoints ni formatos. |
| 2026-11-25 | Modelo de GPS usado contra la API de la catedra. | Pendiente de la guia. `GPS_MODELO` en `config/settings.py` elige el adaptador. |
| 2026-11-25 | Metodo de la interfaz GPS: `getBolsinLocation` por bolsin (diagrama) u `obtenerUbicaciones` por lote. | Pendiente de confirmar. |
| 2026-11-25 | Errores del GPS (A3). | Excepcion propia `UbicacionNoDisponibleError`; el gestor la traduce a A3 por bolsin. |
| 2026-11-25 | Google Maps. | El backend devuelve `MapaBolsines` (centro, zoom, marcadores). El frontend renderiza con la libreria de Google Maps; no hay llamadas a Maps desde el servidor. |
| 2026-11-25 | Correo (CU 31). | `InterfazCorreo` con implementacion simulada (log/archivo) y fake para tests. Microsoft Graph documentado, no implementado. |
| 2026-11-25 | Reparto de pasos entre endpoints del CU 36. Proponia pasos 2 a 6 en el POST inicial. | El POST inicial ejecuta pasos **2 a 9** (el mapa va en la misma respuesta). `/seleccion` ejecuta paso 10 y `/confirmacion-correo` pasos 11 a 13. Detalle en `docs/07-api-rest.md`. |
| 2026-11-25 | Autenticacion en desarrollo: token fijo por header o login real. | **Login real** con JWT (`user_dependency`) y usuario de seed con rol Encargado de Bolsines. Sin bypass. |
| 2026-11-25 | A1 (sin bolsines Enviados): 200 sin sesion o 201 con sesion vacia. | **200** `SinBolsinesResponse` con `idCU: null`. No hay sesion. |
| 2026-11-25 | A2 (filtro por precinto). | Se hace en el **frontend** sobre `bolsines` y `marcadores`. Sin endpoint ni metodo nuevo en el gestor. |
| 2026-11-25 | A3 cuando ningun bolsin tiene ubicacion. | La sesion **queda abierta** con `marcadores: []` y todos los bolsines en `sinUbicacion`. Corrige la version de `06-integraciones` §2 y `05-vista-dinamica` §5. |
| 2026-11-25 | Nombre del parametro de ruta: `{idCasoUso}` o `{idCU}`. | **`{idCU}`** (UUID4). Se actualiza `docs/01-arquitectura.md`. |
| 2026-11-25 | Validacion de rol en la API. | En `routes`: si el `Empleado` no es Encargado de Bolsines, `403`. Requiere `Rol.esEncargadoBolsines()`. |
| 2026-11-25 | Email del GCM en la respuesta. | Solo `destinatarioEnmascarado` (ej. `g***@dominio.gob`). La direccion completa no sale de la API. |
| 2026-11-25 | Guia de la API GPS: el repositorio de la catedra es `LiberaeMentis/dsi-api-bolsines`, no un archivo en `docs/referencias/`. | Se toma como fuente de la seccion 1 de `06-integraciones`. La guia no se copia al repo. |
| 2026-11-25 | La API expone los tres modelos (XTR-4500L, NavTrack QX-7A, GeoPulse MTR-900), cada uno con su API key. | El CU 36 usa **XTR-4500L** (`GPS_MODELO` default). Los otros dos quedan disponibles pero no se usan en el flujo. |
| 2026-11-25 | La API responde **404** (no 200 vacio) cuando el bolsin no existe o el codigo de CM no coincide. | El adaptador traduce 404 a `UbicacionNoDisponibleError`, es decir, A3. |
| 2026-11-25 | Interfaz GPS: consulta por lote (`obtenerUbicaciones`) u por bolsin (`getBolsinLocation`, diagrama). | **Por bolsin**, firma del diagrama. Lote descartado. |
| 2026-11-25 | Fechas de la API sin zona horaria (`2026-03-07T12:30:00`), a veces sin segundos. | Se parsean con `datetime.fromisoformat`. |
| 2026-11-25 | Codigos de CM: los ejemplos de `07-api-rest` usaban `CM-CORDOBA`, `CM-ROSARIO`, etc. | Se usan los codigos de la API: `CM-CBA-01`, `CM-CBA-02`, `CM-ROS-02`, `CM-MDZ-03`, `CM-TUC-01`, `CM-BA-01`. Ejemplos corregidos. |
| 2026-11-25 | Datos semilla: bolsines 101 a 104 y 110 con origen/destino igual a la API; 111 no existe en la API (caso A3). | Aprobado. Detalle en `docs/08-datos-semilla.md`. |
| 2026-11-25 | Datos semilla: EB Córdoba 2 con bolsin 110 como escenario principal limpio. | Aprobado. |
| 2026-11-25 | Datos semilla: `CM-BA-01` como CMC; nombre de `CM-CBA-02`; dominio `example.test`; contrasena en `SEED_PASSWORD_DEV`. | Aprobado (supuestos registrados en `docs/08-datos-semilla.md` §8). |
| 2026-11-25 | Credenciales de la API GPS: el repositorio de la catedra las publica en `application.properties`. | No se copian al repo. Van en `.env` como `GPS_API_KEY_*`. |
| 2026-11-25 | Centro del mapa cuando no hay marcadores. | **Pendiente**: valor por defecto a definir (`docs/07-api-rest.md` §5.3, `docs/06` §7). |
| 2026-11-25 | Escenario A3 en la defensa: bolsin 111 con EB Cordoba 1. | Aprobado. Detalle en `docs/09-implementacion-y-pruebas.md` §7. |
| 2026-11-25 | Tests de integracion contra la API GPS real. | Marcados como `integracion`, se saltan si la API no responde. No bloquean la suite normal. |
| 2026-11-25 | Frontend en esta entrega. | Se implementa despues de cerrar el backend (paso 16 del orden de implementacion). |
| 2026-11-25 | Evidencia de criterios de correccion. | Todas pendientes: todavia no hay codigo de aplicacion. Se actualiza `docs/09` §2 al implementar. |
| 2026-11-25 | `IIterator` (texto de la Entrega 2) vs `IIterador`. | `IIterator` es un error de escritura. Se usa **`IIterador`** en documentos, diagramas y codigo. |
| 2026-11-25 | Tipos de la Entrega 2: `IteradorBolsin.filtros`/`comprobarFiltro` en `Object[]`, `elementoActual()` devuelve `Object`, `crearIterador` recibe `Object[]`. | Se usa `str[]`, `Bolsin` y `Bolsin[]` respectivamente. Registrado en `04-vista-estatica.md` §3 (decision 9). |
| 2026-11-25 | `Bolsin`–`CambioEstado`: E2 muestra asociacion simple con `1..*`. | Se modela como **composicion** (`*--`): el historial se elimina con el bolsin. |
| 2026-11-25 | `obtenerMapa` devuelve `str` (04) o `MapaBolsines` (06). | Devuelve **`MapaBolsines`** (centro, zoom, marcadores). Corregido en 04 y en `clases-diseno.puml`. |
| 2026-11-25 | `IteradorBolsin.posicionarEnValido()` se usa en 05 y 08/09 pero no estaba declarado. | Se declara como **privado** (`-`) en `IteradorBolsin` (04 y `.puml`). |
| 2026-11-25 | Metodos del gestor usados en 05 y 07 (`opcionSeguirBolsines`, `tomarSeleccionBolsin`, `tomarConfirmacionEnvioCorreo`, `cancelar`, `enviarMailGCM`). | Se declaran en `GestorBuscarBolsines` (04 y `.puml`). `enviarMailGCM` es privado. |
| 2026-11-25 | Accesos `Usuario.getEmpleado()`, `Empleado.getUsuario()`, `Usuario.getMail()`, `Empleado.obtenerGCMDeCM()` usados en 05. | Se agregan a `Usuario` y `Empleado` (02, 04 y `.puml`). |
| 2026-11-25 | `00-contexto` decia que la visualizacion en mapa estaba "pendiente de definir". | Se actualiza: el backend devuelve `MapaBolsines` y el frontend renderiza con Google Maps (`VITE_GOOGLE_MAPS_API_KEY`). |
| 2026-11-25 | Relacion `Usuario`–`Empleado` en 02: `user`/`USER` en relacion y diagrama ER. | Se unifica a **`usuario`/`USUARIO`**, igual que el nombre de la entidad. |
| 2026-11-25 | Metodo de la interfaz GPS por bolsin o por lote. | **Por bolsin** (`getBolsinLocation`): el gestor consulta un bolsin por llamada. |
| 2026-11-25 | La guia de la API GPS no estaba en el repo. | La fuente es el repositorio **`LiberaeMentis/dsi-api-bolsines`**. `06-integraciones` §1 completo. |
| 2026-11-25 | SQLAlchemy async requiere `greenlet`; SQLModel no lo trae. | Se agrega `sqlalchemy[asyncio]` a `backend/requirements.txt` (instala `greenlet`). |
| 2026-11-25 | `crearIterador` recibe `filtros` (texto de 03) o solo `elementos` (04 y 05). | Se implementa per **04**: `crearIterador(elementos: list[Bolsin]) -> IIterador`. Los `filtros` los recibe `IteradorBolsin.init`. |
| 2026-11-25 | Formato de `filtros` en `IteradorBolsin` (la 03 lo mostraba como `[codigoCM, ESTADO_ENVIADO]`), necesario para reutilizar el iterador en el CU 28 (filtro por CM destino). | `filtros = [tipoCM, codigoCM]`, con `tipoCM` en `{"origen", "destino"}`. `comprobarFiltro` exige ademas `sosEnviado()`. CU 36: `["origen", codigoCM]`; CU 28: `["destino", codigoDestino]`. |
| 2026-11-25 | `init`/`new` del diagrama en Python. | Es **`__init__`**: constructor de la clase. Los diagramas lo abrevian como `init`/`new`. |
| 2026-11-25 | `comprobarFiltro(filtros)` no recibe el elemento; evalua el elemento en la posicion actual. | Se mantiene la firma de 04. El test unitario del predicado fija `_posicionActual` (prueba de caja blanca). |
| 2026-11-25 | Visibilidad `-` de atributos en SQLModel. | Pydantic trata los nombres con `_` como privados y no los mapea a columnas, asi que las entidades usan atributos publicos (`nombre`, `codigo`) y exponen getters. La privacidad queda documental (ver 04 decision 2). |
| 2026-11-25 | Tests de `Estado`, `ComisionMedica` y `Rol` no tenian archivo en 09 §4.2. | Se agregan en `backend/tests/test_entidades.py`. |
| 2026-11-25 | `from __future__ import annotations` con `Relationship` rompe la resolucion del target (`"Clase | None"`). | Los modelos usan `Optional["Clase"]` / `List["Clase"]` sin future annotations, patron de SQLModel; las relaciones llevan `lazy="selectin"`. |
| 2026-11-25 | `Empleado.obtenerGCMDeCM(codigoCM)` en 04 no recibe sesion, pero consultar la base la necesita. | Se implementa como `@classmethod async obtenerGCMDeCM(db, codigoCM)`. Se actualiza 02, 04 y el `.puml`. |
| 2026-11-25 | SQLModel `table=True` no ejecuta validadores pydantic en `__init__`. | `Usuario.__init__` normaliza `mail` a minusculas (strip + lower). Se usa la `AsyncSession` de `sqlmodel.ext.asyncio.session` (tiene `.exec`) en `config/database.py`. |
| 2026-11-25 | `InterfazGPSTracker.getBolsinLocation` en 04 figura sin async; el acceso HTTP es asincrono. | Se implementa como `async def` (y el gestor la `await`ea) para no bloquear el event loop. Se registra en 99. |
| 2026-11-25 | 06 §2 decia que un error de autenticacion se tradujera a A3; §1.3 dice 401 = error de configuracion. | Prevalece §1.3: 404/red/5xx -> `UbicacionNoDisponibleError` (A3); 400/401/formato invalido -> `ErrorIntegracionGPS` (no A3). Se agrega `ErrorIntegracionGPS` en `errores.py`. |
| 2026-11-25 | `InterfazCorreo.enviarMail` en 04 figura sync. | Se implementa `async def` (I/O), igual que el GPS. La implementacion simulada escribe log/archivo. |
| 2026-11-25 | SQLite via SQLModel exige datetimes con zona y rechaza naive; la API y el dominio usan fechas naive. | Las fechas de `Bolsin` y `CambioEstado` se mapean con `Column(DateTime(timezone=False))` (naive). `RefreshToken` usara UTC aware. |
| 2026-11-25 | `MapaBolsines` estaba como schema en `schemas/` pero lo produce la integracion y lo usa el gestor (services no puede importar schemas). | Pasa a **value object en `models/mapa_bolsines.py`** (`Coordenada` + `MapaBolsines`). `routes` lo serializa a `MapaBolsinesOut`. |
| 2026-11-25 | El gestor devuelve `void` en 04, pero `routes` necesita los datos para la respuesta. | Devuelve value objects: `ResultadoSeguimiento`, `ResultadoSeleccion`, `ResultadoConfirmacion` (`models/resultados.py`). Actualizado en 04 y `.puml`. |
| 2026-11-25 | Centro por defecto del mapa sin marcadores. | Se usa CABA (`-34.6037, -58.3816`) por ahora. Sigue pendiente de confirmar. |
| 2026-11-25 | `SECRET_KEY` sin valor en dev rompe los tokens. | Default de desarrollo largo (`dev-insecure-...`); en produccion va por `.env`. `ACCESS_TOKEN_MINUTES=30`, `REFRESH_DAYS=7`. |
| 2026-11-25 | Mapeo de errores en `routes`: seleccion inexistente, correo caido, `idCU` vencido. | `422` si el bolsin no esta entre los enviados; `502` si el correo no sale (la sesion queda abierta); `404` si el `idCU` no existe o vencio. |
| 2026-11-25 | El volumen de la base en `/app/data` tapaba `data/seed.py` dentro del contenedor. | El volumen `bolsines-data` se monta en `/app/db` y `DB_URL` (compose y `.env.example`) apunta a `/app/db/bolsines.db`. El codigo de `backend/data/` queda visible. |
| 2026-11-25 | Entrypoint `index.py` (docs/01) vs `main.py` (pedido del equipo). | Se usa **`main.py`**. `index.py` queda como alias que reexporta `app` (compatibilidad con tests y Docker previo). Dockerfile usa `main:app`. |
| 2026-11-25 | `DB_URL` vs `DATABASE_URL`. | Se renombra a **`DATABASE_URL`** en `settings.py` y en `config/database.py` (y compose). |
| 2026-11-25 | Funciones de base: `get_db`/`create_db_and_tables` vs `get_session`/`crear_tablas`. | Se agregan **`get_session`** y **`crear_tablas`** como canonicas; `get_db`/`create_db_and_tables` quedan como alias para no romper imports existentes. |
| 2026-11-25 | GPS: una `GPS_API_KEY` y `GPS_MODELO` en minusculas (`xtr4500l`/`navtrack`/`geopulse`) vs claves por modelo y nombres largos. | Se usa **`GPS_API_KEY`** unica y `GPS_MODELO` en minusculas. Solo `xtr4500l` esta implementado; `navtrack`/`geopulse` lanzan error de configuracion hasta implementarse. |
| 2026-11-25 | `CORS_ORIGINS` default `5173` (pedido) vs `3020` (frontend/docs). | Default en settings **`http://localhost:5173`**; docker compose fija `CORS_ORIGINS=http://localhost:3020` para el frontend. |
| 2026-11-25 | `USUARIO_DEV`. | Se agrega a `Settings` (default `eb.cba01@example.test`) y a `.env.example`. Por ahora informativo; el seed mantiene sus usuarios. |
| 2026-11-25 | `.env.example` en la raiz vs en `backend/`. | Se crea **`backend/.env.example`** (lo lee `settings` desde `backend/.env`). Se mantiene el `.env.example` de la raiz para `docker compose`. |
| 2026-11-25 | Requirements: pedido de 8 paquetes pinneados. | Se pinnean los 8 y se agregan las dependencias que el CU 36 ya usa: `aiosqlite`, `sqlalchemy[asyncio]`, `PyJWT`, `pwdlib[argon2]`, `python-multipart`. |
| 2026-11-25 | Paquetes sin `__init__.py`. | Se agregan `__init__.py` en todas las carpetas de `backend/`. |
| 2026-11-25 | La guia de la API GPS no estaba en el repo; se tomaba solo del repositorio de la catedra. | Se crea **`docs/referencias/api-gps-guia.md`** (adaptada del repo, con API keys mock literales, tabla 101-110 y codigos de error exactos). Reemplaza las filas anteriores que indicaban que la guia no existia. |
| 2026-11-25 | Adaptadores GPS: solo XTR implementado; NavTrack/GeoPulse en la API pero sin codigo. | Se implementan los **tres adaptadores reales** (httpx) con su parser propio. La fabrica `crear_gps()` elige por `GPS_MODELO` (`xtr4500l`/`navtrack`/`geopulse`). |
| 2026-11-25 | Nombre del error de integracion: `ErrorIntegracionGPS` vs `ErrorServicioGPS`. | Se mantiene `ErrorIntegracionGPS` y se agrega **`ErrorServicioGPS` como alias** en `errores.py`. |
| 2026-11-25 | Correo simulado: archivo configurable vs ruta fija. | `CorreoSimulado` escribe por defecto en **`backend/data/mails_enviados.log`** (ademas del log); `CORREO_ARCHIVO` puede sobreescribirlo. Se agrega `outlook_graph.py` como stub comentado. |
| 2026-11-25 | Tests de integraciones y script de prueba. | Nuevos tests en **`backend/tests/integrations/`** (parsers y adaptadores con httpx mockeado) y script **`backend/scripts/probar_gps.py`**. |
| 2026-11-25 | Nombre del metodo del gestor: `obtenerCodigoBolsinesEnviados` (docs/04) vs `obtenerBolsinesEnviados` (pedido). | Se usa **`obtenerBolsinesEnviados`**; revierte la decision anterior. Devuelve `list[Bolsin]` y setea `codigoBolsin`. |
| 2026-11-25 | `opcionSeguirBolsines(usuario)` vs sin args con `buscarUsuarioLogueado`. | El gestor recibe el **usuario por constructor**; `opcionSeguirBolsines()` no recibe args y usa `buscarUsuarioLogueado()`/`getCMUsuarioLogueado()`. |
| 2026-11-25 | A1: resultado vacio vs excepcion. | **`SinBolsinesEnviadosError`** en `services/errores.py`; el route la traduce a 200 `SinBolsinesResponse`. |
| 2026-11-25 | A2: filtro en el frontend vs en el gestor. | Se agrega **`GestorBuscarBolsines.filtrarPorPrecinto`**: devuelve lista vacia y agrega advertencia si no hay coincidencias. |
| 2026-11-25 | Mail: `Empleado.obtenerGCMDeCM` vs loop `esTuCM`/`sosGCM`/`esGCM`. | Se usa el **loop sobre empleados** en `enviarMailGCM` (revierte la decision anterior). |
| 2026-11-25 | Registro en memoria: `gestores_activos.py` vs `registro_casos_uso.py`. | Se usa **`services/registro_casos_uso.py`** con `crear`/`obtener`/`eliminar` (+ `reset`). |
| 2026-11-25 | Visibilidad de atributos del gestor. | Nombres **publicos en Python** (`nombreComisionMedica`, `bolsines`, ...) tratados como privados; el `-` del diagrama es documental. |
| 2026-11-25 | Ubicacion de los tests del gestor. | **`backend/tests/services/`** (dentro de `testpaths`), con principal, A1-A5 y test de uso del iterador. |
| 2026-11-25 | Archivo de rutas: `pantalla_buscar_bolsines.py` vs `seguimiento_bolsines.py`. | Se usa **`routes/seguimiento_bolsines.py`** (el rol de pantalla se mantiene conceptualmente). |
| 2026-11-25 | A1: 200 `SIN_BOLSINES` vs 404. | Se usa **404 con `{codigo: "SIN_BOLSINES_ENVIADOS", mensaje}`**. Se elimina `SinBolsinesResponse`. |
| 2026-11-25 | Formato de error: `{codigo, detalle}` vs `{codigo, mensaje}`. | Se usa **`{codigo, mensaje}`** en todas las respuestas de error (handlers en `main.py`). |
| 2026-11-25 | Autenticacion de las rutas de seguimiento: JWT vs usuario de desarrollo. | Se usa **`usuario_dev_dependency`** (`USUARIO_DEV`); el login JWT sigue disponible en `routes/auth.py`. |
| 2026-11-25 | `GET /me`. | Se agrega en `routes/auth.py`; devuelve `{id, mail, nombre, apellido, rol, codigoCM}` del usuario de desarrollo. |
| 2026-11-25 | Ubicacion de tests de rutas. | **`backend/tests/routes/`** con `TestClient`, `dependency_overrides` del usuario dev y GPS mockeado. |
| 2026-11-25 | Ejecucion del seed: `python -m data.seed` vs `python -m backend.data.seed`. | Se soporta **`python -m backend.data.seed`** desde la raiz (bootstrap de `sys.path`), ademas de `python -m data.seed` en Docker. El seed imprime los Enviados por CM. Verificado contra la API GPS real: 110 con coordenadas reales, A1 404 y A3 con 111 sin ubicacion. |
| 2026-11-25 | Logica en rutas: refresh con DB y chequeo de rol de dominio. | El refresh pasa a `utils/auth.refrescar_sesion` y el chequeo de rol a `utils/auth.encargado_bolsines_dependency`. Las rutas solo traducen. |
| 2026-11-25 | `ErrorDeApi` vivia en `routes/errores.py` y `utils` necesitaba usarlo. | Se mueve a **`utils/errores.py`** (cross-cutting); `main.py` y las rutas lo importan desde ahi. |
| 2026-11-25 | `routes` importaba modelos (`Bolsin`, `MapaBolsines`, `UbicacionBolsin`, `Usuario`). | Se eliminan esos imports runtime; el mapeo usa atributos (duck typing). `routes` ya no importa `models`. |
| 2026-11-25 | `docs/01` §5 prohibia a `routes` importar `config` y `services`, pero necesita sesion, fabrica y registro. | Se actualiza §5: `routes` puede importar `config.database`, `config.composicion`, `services.registro_casos_uso`/`services.errores` y `utils` solo para wiring; sigue sin logica de negocio. |
| 2026-11-25 | Cobertura de tests. | Se agrega **`pytest-cov==7.1.0`**. Cobertura del codigo de la app: **89%**; suite 101 passed, 4 skipped. |
| 2026-11-25 | Mapa del frontend: Google Maps JS vs Leaflet/OpenStreetMap. | Se usa **Leaflet + react-leaflet (OSM)**: libre y sin API key. El backend entrega `centro`, `zoom` y `marcadores`; cambiar a Google Maps JS es reemplazar solo el componente de mapa. |
| 2026-11-25 | Login del frontend: JWT real vs simulado. | El frontend usa **login simulado** (selector de usuario); el backend del CU 36 resuelve `USUARIO_DEV`. El login JWT existe en `routes/auth.py` pero no lo usan estas rutas. |
| 2026-11-25 | Artefactos de UX (empatia, journey, board) no estan en el repo. | Se dejan **placeholders** en `docs/10-frontend.md` apuntando a `docs/imagenes/`; el equipo pega las imagenes. |
