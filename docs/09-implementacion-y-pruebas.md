# 09 - Implementacion y pruebas (CU 36)

Estado: **plan de implementacion**. El codigo de aplicacion todavia no existe: `backend/` tiene `index.py`, `Dockerfile` y carpetas con `.gitkeep`. Por eso la evidencia de cada criterio figura como pendiente.

## 1. Detalles de implementacion

| Aspecto | Eleccion | Justificacion |
|---|---|---|
| a) Lenguaje | Python 3.12 | Lo fija el equipo (`AGENTS.md` §1). Anotaciones de tipo, `datetime` y `dataclass` cubren el modelo sin dependencias extra. |
| b) Framework | FastAPI | Rutas tipadas con Pydantic, `Depends` para `user_dependency`, `TestClient` para probar endpoints. El `APIRouter` cumple el rol de la pantalla del CU. |
| c) Tecnologia web | Backend: FastAPI en `8020`. Frontend: Vite + React + TypeScript en `3020` | Requerimiento 1 de la ERS (tecnologia web). El frontend solo consume la API, filtra por precinto (A2) y renderiza el mapa. |
| d) Base y persistencia | SQLite con SQLModel (sobre SQLAlchemy async y aiosqlite) | Pedido por el TP. Un archivo, sin servidor. SQLModel une entidades y esquema, y las entidades llevan los metodos de negocio. |

Restricciones de ejecucion (`AGENTS.md` §9, `docs/07-api-rest.md`):
- Un solo worker de uvicorn. El registro de gestores vive en memoria y no se comparte entre procesos.
- La visualizacion del mapa vive en el frontend. El backend entrega centro y marcadores (`docs/06-integraciones.md` §3).

## 2. Criterios de correccion: criterio -> evidencia

| Criterio (`docs/00-contexto.md` §4.5) | Evidencia prevista | Estado |
|---|---|---|
| Flujo principal ejecutado | Test de endpoints: POST `/seguimiento-bolsines` -> POST `.../seleccion` -> POST `.../confirmacion-correo` con EB Cordoba 2 (bolsin 110), con GPS fake y correo fake. Esperado: 201, 200, 200 con `notificado: true`. | Pendiente |
| Alternativo A1 ejecutado | Test con EB Tucuman: POST responde 200 `SinBolsinesResponse`, sin llamadas al GPS ni al correo. | Pendiente |
| Alternativo A3 ejecutado | Test con EB Cordoba 1: bolsin 111 con GPS fake que lanza `UbicacionNoDisponibleError`. Aparece en `sinUbicacion` y la sesion sigue abierta. Prueba adicional contra la API real (§3), donde 111 responde 404. | Pendiente |
| Alternativo A5 ejecutado | Test de confirmacion con `confirma: false`: 200 con `notificado: false`, el correo fake no recibe envios. | Pendiente |
| Iterator visible y usado por el gestor | Revision de codigo: `GestorBuscarBolsines` implementa `IAgregado` y solo llama a `primero`, `haFinalizado`, `elementoActual`, `siguiente`. Un test verifica que el gestor no accede a la lista. | Pendiente |
| Filtro dentro de `comprobarFiltro()` | Tests unitarios del iterador (§4.1). | Pendiente |
| Consistencia con el modelado | Nombres de clases y metodos iguales a `docs/04-vista-estatica.md`. Revision cruzada con `docs/02-modelo-datos.md` y `docs/07-api-rest.md`. | Pendiente |
| Persistencia en DB | Test de integracion: el seed carga una SQLite temporal y la consulta del gestor devuelve los bolsines esperados (101, 110 y 111 segun el escenario). Verifica un solo `CambioEstado` vigente por bolsin. | Pendiente |
| Defensa del patron | Checklist de §5. | Pendiente |

## 3. Integracion contra la API real del GPS Tracker

Fuente: repositorio de la catedra `LiberaeMentis/dsi-api-bolsines`, corriendo en `http://localhost:8080` (Java 17, `./mvnw spring-boot:run`). El contrato esta en `docs/06-integraciones.md` §1.

Pruebas de integracion en `backend/tests/integracion/test_gps_tracker_xtr4500l_real.py`:
- Marcadas como `integracion`. Se saltan si la API no responde en `GPS_BASE_URL`. La suite normal corre sin la API.
- Casos:
  - Bolsin 101 con `codigoComisionMedicaOrigen=CM-CBA-01`: devuelve `UbicacionBolsin` con latitud -31.4201 y longitud -64.1888.
  - Bolsin 111 (no existe en la API): 404, el adaptador lanza `UbicacionNoDisponibleError`.
  - Bolsin 101 con codigo `CM-ROS-02` (no es su origen): 404, lanza `UbicacionNoDisponibleError`.
  - API key incorrecta: 401, se propaga como error de configuracion, no como A3.
- Las fechas se parsean sin zona horaria, tambien el caso sin segundos (`2026-03-07T12:30`).

Las pruebas de parseo (funciones puras) corren siempre, con respuestas de ejemplo copiadas de la API.

## 4. Plan de pruebas pytest

Ubicacion: `backend/tests/` (`pytest.ini` apunta a esa carpeta y se ejecuta desde la raiz). Fixtures en `conftest.py`: base SQLite en memoria, `gestores_activos` reseteado, fakes de GPS y correo, `TestClient` con la composicion de tests.

### 4.1 Iterator (`test_iterador_bolsin.py`)

| Caso | Entrada | Resultado esperado |
|---|---|---|
| primero con coleccion vacia | `elementos=[]`, filtros CBA y Enviado | `haFinalizado()` es `True` |
| primero posiciona en el primer valido | [102 (origen ROS), 101 (CBA Enviado), 111 (CBA Enviado)] | `elementoActual()` es 101 |
| siguiente salta los no validos | Mismo caso, luego `siguiente()` | `elementoActual()` es 111 |
| haFinalizado tras el ultimo valido | Despues de 111, `siguiente()` | `haFinalizado()` es `True` |
| comprobarFiltro con CM distinta | Bolsin 102, filtro CBA | `False` |
| comprobarFiltro con estado no Enviado | Bolsin 113 (Creado), filtro CBA | `False` |
| comprobarFiltro con ambos cumplidos | Bolsin 101, filtro CBA y Enviado | `True` |
| Todos no validos | [113, 114, 117] | `haFinalizado()` es `True` desde `primero()` |
| elementoActual sin elemento | `haFinalizado()` es `True` y se llama `elementoActual()` | Lanza `IndexError` (documentado) |
| Reutilizacion (CU 28) | Mismo iterador con filtro por CM destino ROS-02 | Devuelve 101 y 110, no 111 |
| Orden preservado | Varios validos | Devuelve en el orden de la coleccion |

### 4.2 Entidades (`test_bolsin.py`, `test_cambio_estado.py`)

| Caso | Entrada | Resultado esperado |
|---|---|---|
| `Bolsin.esTuCMOrigen` coincide | Bolsin 101, `"CM-CBA-01"` | `True` |
| `Bolsin.esTuCMOrigen` no coincide | Bolsin 101, `"CM-ROS-02"` | `False` |
| `Bolsin.sosEnviado` con vigente Enviado | Bolsin 101 | `True` |
| `Bolsin.sosEnviado` con vigente Cerrado | Bolsin 114 | `False` |
| `Bolsin.sosEnviado` con historial Enviado y vigente Recibido | Bolsin 115 | `False` (solo cuenta el cambio vigente) |
| `Bolsin.getNumeroBolsin` | Bolsin 101 | `101` |
| `CambioEstado.sosActual` sin fin | Cambio con `fechaHoraFin` nula | `True` |
| `CambioEstado.sosActual` cerrado | Cambio con `fechaHoraFin` cargada | `False` |
| Cadena `CambioEstado.sosEnviado` | Cambio con `Estado` Enviado | Delega en `Estado.esEnviado()` y devuelve `True` |
| `Estado.esEnviado` | Estado "Recibido" | `False` |

### 4.3 Gestor con GPS y correo mockeados (`test_gestor_buscar_bolsines.py`)

| Caso | Entrada | Resultado esperado |
|---|---|---|
| Flujo principal | EB Cordoba 2, GPS fake con 110 ubicado | `obtenerCodigoBolsinesEnviados()` = [110]. Un marcador. Un correo al GCM Rosario. |
| A1 | EB Tucuman | Lista vacia. Sin llamadas al GPS. Sin correos. |
| A3 | EB Cordoba 1, GPS fake lanza `UbicacionNoDisponibleError` para 111 | 111 en `sinUbicacion`, 101 con marcador. Sesion abierta. |
| A3 total | GPS fake lanza para todos | `marcadores` vacio, todos en `sinUbicacion`. Sesion abierta. |
| A5 | `confirma: false` | `enviarMailGCM` no se llama. Correo fake sin envios. |
| Gestor no recorre lista | Inyeccion de una lista espia | El gestor solo usa los metodos del iterador. |

### 4.4 Endpoints (`test_routes_seguimiento.py`, `TestClient`)

| Caso | Entrada | Resultado esperado |
|---|---|---|
| POST sin JWT | Sin header | 401 |
| POST con usuario sin rol EB | JWT de un GCM | 403 |
| POST flujo principal | JWT de EB Cordoba 2 | 201 con `idCU` y `bolsines` |
| POST A1 | JWT de EB Tucuman | 200 `estado: SIN_BOLSINES`, sin `idCU` |
| POST A3 | JWT de EB Cordoba 1 | 201, 111 en `sinUbicacion` |
| POST seleccion | `numeroBolsin: 0` | 422 |
| POST seleccion con `idCU` vencido | UUID inexistente | 404 `CASO_USO_NO_ENCONTRADO` |
| POST confirmacion A5 | `confirma: false` | 200, `notificado: false` |
| POST confirmacion con correo caido | Correo fake lanza error | 502, sesion abierta |
| DELETE A4 | `idCU` existente | 204. El `idCU` ya no existe. |
| Documentacion | Acceso a `/docs` (OpenAPI) | 200 |

### 4.5 Parseo GPS (`test_gps_tracker_xtr4500l.py`)

| Caso | Entrada | Resultado esperado |
|---|---|---|
| JSON con un item | `{"items":[{...}]}` | `UbicacionBolsin` correcto |
| Fecha sin segundos | `"2026-03-07T12:30"` | `datetime(2026, 3, 7, 12, 30)` |
| Lista vacia o con dos items | `{"items":[]}` | Error de respuesta invalida (no A3) |

### 4.6 Persistencia (`test_seed.py`)

| Caso | Entrada | Resultado esperado |
|---|---|---|
| Seed idempotente | Ejecutar dos veces | Mismo conteo de filas |
| Un cambio vigente por bolsin | Tras el seed | Exactamente un `CambioEstado` con `fechaHoraFin` nula por bolsin |
| Origen de 101, 102, 103, 104 y 110 | Tras el seed | Igual al de la API |

## 5. Checklist de defensa oral

Orden sugerido (unos 15 minutos):

1. **Modelo:** `docs/diagramas/clases-diseno.puml`. Senalar `IAgregado`, `IIterador`, `IteradorBolsin` y `GestorBuscarBolsines`.
2. **Interfaces:** `backend/models/iterator/i_agregado.py` e `i_iterador.py`. Mostrar que `crearIterador` devuelve `IIterador`.
3. **Iterator concreto:** abrir `backend/models/iterator/iterador_bolsin.py`. Mostrar `init(elementos, filtros)`, `posicionarEnValido()` y `comprobarFiltro()`, con las llamadas a `esTuCMOrigen` y `sosEnviado`.
4. **Llamada desde el gestor:** abrir `backend/services/gestor_buscar_bolsines.py`. Mostrar `obtenerCodigoBolsinesEnviados()`: `crearIterador`, `primero`, `haFinalizado`, `elementoActual`, `getNumeroBolsin`, `siguiente`. Senalar que no hay `for` sobre la lista.
5. **Entidades:** `Bolsin.esTuCMOrigen` y `sosEnviado`, y la cadena hasta `Estado.esEnviado`.
6. **Boundary:** `backend/routes/pantalla_buscar_bolsines.py`. Mostrar que solo traduce HTTP.
7. **Pruebas:** `pytest -k iterador -v` y luego `pytest -v`. Mostrar un caso de reutilizacion (CU 28).
8. **Flujo en vivo:** `docker compose up` con la API de la catedra corriendo. Login como EB Cordoba 1 y mostrar A3 (111 en `sinUbicacion`). Despues EB Tucuman y mostrar A1.
9. **Persistencia:** abrir la base y mostrar el `CambioEstado` vigente de un bolsin.
10. **Decisiones:** `docs/99-decisiones-y-dudas.md`. Mencionar `CambioEstado` vs `CambioEstadoBolsin`, `primero`/`siguiente` que avanzan a un valido, y el centro del mapa pendiente.

Preguntas probables y respuesta corta:
- *Por que Iterator y no un loop?* Desacopla el gestor de la coleccion y deja el filtro reutilizable (CU 28).
- *Por que `comprobarFiltro` dentro de `primero`/`siguiente`?* Asi `elementoActual` siempre devuelve un valido y el gestor no filtra.
- *Que pasa con varios workers?* El estado en memoria se pierde. Se documenta como limitacion.

## 6. Orden de implementacion sugerido

Cada paso se verifica antes de pasar al siguiente.

1. Configuracion: `backend/config/settings.py` (pydantic-settings) y `backend/config/database.py` (engine async). Verificar: `settings` carga desde `.env`.
2. Interfaces del iterador: `models/iterator/i_iterador.py` e `i_agregado.py` (ABC). Verificar: importan sin errores.
3. `IteradorBolsin` con lista en memoria, sin base, con objetos simples. Verificar: tests de §4.1.
4. Entidades sin relaciones: `Estado`, `ComisionMedica`, `Rol`. Verificar: `esEnviado`, `getCodigo`, `esGCM`, `esEncargadoBolsines`.
5. `CambioEstado` y `Bolsin` con relaciones SQLModel. Verificar: tests de §4.2 con base en memoria.
6. `Empleado` y `Usuario` (1 a 1). Verificar: relacion cargada con `selectinload`.
7. `UbicacionBolsin` y `UbicacionNoDisponibleError`. Verificar: importacion.
8. Adaptador GPS XTR-4500L con parseo puro. Verificar: tests de §4.5 sin red.
9. Fakes de GPS y correo. Verificar: cumplen la interfaz.
10. `GestorBuscarBolsines` con `IAgregado` y `gestores_activos`. Verificar: tests de §4.3.
11. `utils/security.py` y `utils/auth.py` (login, `user_dependency`). Verificar: el login devuelve JWT y un token invalido da 401.
12. `schemas/seguimiento.py` y `schemas/auth.py`. Verificar: `numeroBolsin > 0`.
13. `routes/pantalla_buscar_bolsines.py` y `routes/auth.py`, incluidos en `index.py`. Verificar: tests de §4.4 con `TestClient`.
14. `data/seed.py`. Verificar: tests de §4.6 y `docker compose exec backend python -m data.seed`.
15. Integracion real contra la API de la catedra. Verificar: tests de §3 con la API corriendo.
16. Frontend minimo: login, lista de bolsines, filtro por precinto (A2) y mapa con marcadores. Verificar: flujo principal en el navegador. Va despues de cerrar el backend (pasos 1 a 15).
17. Revision final: `pytest` desde la raiz, `docker compose up --build` y el checklist de §5.

## 7. Decisiones tomadas para esta fase

1. **Escenario A3 en la defensa:** bolsin 111 con EB Cordoba 1, como en `docs/08-datos-semilla.md`.
2. **Tests de integracion:** marcados como `integracion` y se saltan si la API no responde. No bloquean la suite normal.
3. **Frontend:** paso 16, despues del backend.
