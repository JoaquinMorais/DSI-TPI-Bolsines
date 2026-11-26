# 09 - Implementacion y pruebas (CU 36)

Estado: **implementado** (pasos 1 a 17 del orden de implementacion). La suite completa en Docker da **116 passed** con la API GPS corriendo; los tests de integracion se saltan si la API no responde. El chequeo en vivo con `docker compose up` responde login, seguimiento, A3 parcial (101/120/121 con ubicacion; 111/122 sin ubicacion) y A3 total (EB Cordoba 3); el frontend sirve en `3020`.

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
| Flujo principal ejecutado | Test de endpoints: POST `/seguimiento-bolsines` -> POST `.../seleccion` -> POST `.../confirmacion-correo` con EB Cordoba 2 (bolsin 110), con GPS fake y correo fake. Esperado: 201, 200, 200 con `notificado: true`. | Cumplido (`tests/routes/test_seguimiento_bolsines.py::test_flujo_principal`) |
| Alternativo A1 ejecutado | Test con EB Tucuman: POST responde 404 `SIN_BOLSINES_ENVIADOS`, sin llamadas al GPS ni al correo. | Cumplido (`test_a1_sin_bolsines_da_404`) |
| Alternativo A3 ejecutado | Test con EB Cordoba 1: bolsin 111 con GPS fake que lanza `UbicacionNoDisponibleError`. Aparece en `sinUbicacion` y la sesion sigue abierta. Prueba adicional contra la API real (§3), donde 111 responde 404. | Cumplido (`test_a3_gps_sin_ubicacion` y test de integracion) |
| Alternativo A5 ejecutado | Test de confirmacion con `confirma: false`: 200 con `notificado: false`, el correo fake no recibe envios. | Cumplido (`test_a5_no_confirma`) |
| Iterator visible y usado por el gestor | Revision de codigo: `GestorBuscarBolsines` implementa `IAgregado` y solo llama a `primero`, `haFinalizado`, `elementoActual`, `siguiente`. Un test verifica que el gestor no accede a la lista. | Cumplido (`test_obtener_codigos_usa_iterador` y revision) |
| Filtro dentro de `comprobarFiltro()` | Tests unitarios del iterador (§4.1). | Cumplido (`tests/test_iterador_bolsin.py`) |
| Consistencia con el modelado | Nombres de clases y metodos iguales a `docs/04-vista-estatica.md`. Revision cruzada con `docs/02-modelo-datos.md` y `docs/07-api-rest.md`. | Cumplido (nombres iguales a `docs/04`; revision cruzada) |
| Persistencia en DB | Test de integracion: el seed carga una SQLite temporal y la consulta del gestor devuelve los bolsines esperados (101, 110 y 111 para los escenarios base; 120-127 en el set ampliado). Verifica un solo `CambioEstado` vigente por bolsin. | Cumplido (`tests/test_seed.py` y chequeo en vivo con SQLite) |
| Defensa del patron | Checklist de §5. | Pendiente (defensa oral) |

## 3. Integracion contra la API real del GPS Tracker

Fuente: repositorio de la catedra `LiberaeMentis/dsi-api-bolsines`, corriendo en `http://localhost:8080` (Java 17, `./mvnw spring-boot:run`). El contrato esta en `docs/06-integraciones.md` §1.

Pruebas de integracion en `backend/tests/integracion/test_gps_tracker_xtr4500l_real.py`:
- Marcadas como `integracion`. Se saltan si la API no responde en `GPS_BASE_URL`. La suite normal corre sin la API.
- Casos:
  - Bolsin 101 con `codigoComisionMedicaOrigen=CM-CBA-01`: devuelve `UbicacionBolsin` con latitud -31.4201 y longitud -64.1888.
  - Bolsines 120, 121, 123 y 124 (agregados al mock): devuelven las coordenadas esperadas.
  - Bolsines 111, 122, 125, 126 y 127 (no existen en la API): 404, el adaptador lanza `UbicacionNoDisponibleError`.
  - Bolsin 101 con codigo `CM-ROS-02` (no es su origen): 404, lanza `UbicacionNoDisponibleError`.
  - API key incorrecta: 401, se propaga como error de configuracion, no como A3.
- Las fechas se parsean sin zona horaria, tambien el caso sin segundos (`2026-03-07T12:30`).

Las pruebas de parseo (funciones puras) corren siempre, con respuestas de ejemplo copiadas de la API.

## 4. Plan de pruebas pytest

Ubicacion: `backend/tests/` (`pytest.ini` apunta a esa carpeta y se ejecuta desde la raiz). Las pruebas del gestor estan en `backend/tests/services/`. Fixtures en `conftest.py`: base SQLite en memoria, `registro_casos_uso` reseteado, fakes de GPS y correo, `TestClient` con la composicion de tests.

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
| A3 parcial | EB Cordoba 1, GPS fake lanza `UbicacionNoDisponibleError` para 111 | 111 en `sinUbicacion`, 101 con marcador. Sesion abierta. |
| A3 total | GPS fake lanza para todos (101 y 111) | `marcadores` vacio, todos en `sinUbicacion`. Sesion abierta (`test_a3_total_sin_ubicacion`). |
| A5 | `confirma: false` | `enviarMailGCM` no se llama. Correo fake sin envios. |
| Gestor no recorre lista | Inyeccion de una lista espia | El gestor solo usa los metodos del iterador. |

### 4.4 Endpoints (`tests/routes/test_seguimiento_bolsines.py`, `TestClient`)

| Caso | Entrada | Resultado esperado |
|---|---|---|
| POST sin JWT | Sin header | 401 |
| POST con usuario sin rol EB | JWT de un GCM | 403 |
| POST flujo principal | JWT de EB Cordoba 2 | 201 con `idCU` y `bolsines` |
| POST A1 | usuario dev EB Tucuman | 404 `codigo: SIN_BOLSINES_ENVIADOS` |
| POST A3 parcial | JWT de EB Cordoba 1 | 201, 111 (y en el seed 122) en `sinUbicacion` |
| POST A3 total | JWT de EB Cordoba 3 (seed) | 201, 125, 126 y 127 en `sinUbicacion`, `marcadores: []` |
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
3. **Iterator concreto:** abrir `backend/models/iterator/iterador_bolsin.py`. Mostrar `init(elementos, filtros)`, `elementoActual()` (llama a `comprobarFiltro()`) y `comprobarFiltro()`, con las llamadas a `esTuCMOrigen` y `sosEnviado`.
4. **Llamada desde el gestor:** abrir `backend/services/gestor_buscar_bolsines.py`. Mostrar `obtenerCodigoBolsinesEnviados()`: `crearIterador`, `primero`, `haFinalizado`, `elementoActual`, `getNumeroBolsin`, `siguiente`. Senalar que no hay `for` sobre la lista.
5. **Entidades:** `Bolsin.esTuCMOrigen` y `sosEnviado`, y la cadena hasta `Estado.esEnviado`.
6. **Boundary:** `backend/routes/seguimiento_bolsines.py`. Mostrar que solo traduce HTTP.
7. **Pruebas:** `pytest -k iterador -v` y luego `pytest -v`. Mostrar un caso de reutilizacion (CU 28).
8. **Flujo en vivo:** `docker compose up` con la API de la catedra corriendo. Login como EB Cordoba 1 y mostrar A3 parcial (111 y 122 en `sinUbicacion`). Despues EB Cordoba 3 y mostrar A3 total; EB Tucuman y mostrar A1.
9. **Persistencia:** abrir la base y mostrar el `CambioEstado` vigente de un bolsin.
10. **Decisiones:** `docs/99-decisiones-y-dudas.md`. Mencionar `CambioEstado` vs `CambioEstadoBolsin`, `primero`/`siguiente` que avanzan a un valido, y el centro del mapa pendiente.

Preguntas probables y respuesta corta:
- *Por que Iterator y no un loop?* Desacopla el gestor de la coleccion y deja el filtro reutilizable (CU 28).
- *¿Por qué `comprobarFiltro` dentro de `elementoActual`?* Así está en la secuencia de la Entrega 2: el iterador decide si el elemento cumple el filtro y devuelve `None` si no; el gestor no conoce el criterio.
- *Que pasa con varios workers?* El estado en memoria se pierde. Se documenta como limitacion.

## 6. Orden de implementacion

Estado: **pasos 1 a 17 completados**.

| # | Paso | Estado |
|---|---|---|
| 1 | Configuracion (`settings`, `database`) | Completado |
| 2 | Interfaces del iterador | Completado |
| 3 | `IteradorBolsin` en memoria | Completado |
| 4 | Entidades `Estado`, `ComisionMedica`, `Rol` | Completado |
| 5 | `CambioEstado` y `Bolsin` con relaciones | Completado |
| 6 | `Empleado` y `Usuario` (1 a 1) | Completado |
| 7 | `UbicacionBolsin` y errores del GPS | Completado |
| 8 | Adaptador GPS XTR-4500L | Completado |
| 9 | Fakes de GPS y correo | Completado |
| 10 | `GestorBuscarBolsines` y registro de casos de uso | Completado |
| 11 | `utils` de auth y seguridad | Completado |
| 12 | Schemas Pydantic | Completado |
| 13 | Rutas y `main.py` | Completado |
| 14 | Seed | Completado |
| 15 | Integracion real contra la API GPS | Completado (verificado contra la API de la catedra) |
| 16 | Frontend minimo | Completado |
| 17 | Revision final (pytest, compose, checklist) | Completado |

Pendientes y decisiones distintas: ver `docs/99-decisiones-y-dudas.md` (Microsoft Graph, centro por defecto del mapa, clave de Maps del frontend y tests de integracion real que requieren API + key).

## 7. Decisiones tomadas para esta fase

1. **Escenario A3 en la defensa:** A3 parcial con 111 y 122 (EB Cordoba 1); A3 total con 125-127 (EB Cordoba 3), como en `docs/08-datos-semilla.md`.
2. **Tests de integracion:** marcados como `integracion` y se saltan si la API no responde. No bloquean la suite normal.
3. **Frontend:** paso 16, despues del backend.
