# 06 - Integraciones (CU 36)

Fuentes: ERS v1.2, CU 36 (Observacion 1 sobre GPS Tracker) y requerimientos no funcionales 5, 6 y 7. Regla de `AGENTS.md` §4 y §8: las integraciones viven solo en `backend/integrations/` y el gestor depende solo de interfaces.

Estado de esta version:
- Seccion 1 (GPS): completa, segun la API simulada de la catedra (repositorio `LiberaeMentis/dsi-api-bolsines`).
- Secciones 2 a 6: definidas.

## 1. GPS Tracker (API simulada de la catedra)

Fuente: repositorio `LiberaeMentis/dsi-api-bolsines` (Spring Boot, datos en memoria, sin base). Contacto de la catedra: Ing. Sol Vega.

Estado: **completo**. La seccion 1.3 detalla lo que la API valida y devuelve.

### 1.1 Interfaz comun

`InterfazGPSTracker` (`backend/integrations/gps_tracker/interfaz_gps_tracker.py`) es una clase abstracta. Devuelve siempre la misma forma normalizada, sin importar el modelo de dispositivo:

```
InterfazGPSTracker (ABC)
  + getBolsinLocation(numeroBolsin: int, codigoCM: str): UbicacionBolsin   # una consulta por bolsin, firma del diagrama
```

Decision: la interfaz consulta **un bolsin por llamada**. El gestor recorre los bolsines Enviados y llama una vez por cada uno (paso 7 del CU, `docs/05-vista-dinamica.md`). Asi A3 se maneja por bolsin, sin lote. Se descarta `obtenerUbicaciones` por lote.

`UbicacionBolsin` (`backend/models/ubicacion_bolsin.py`, value object, no es tabla):

| Campo | Tipo Python |
|---|---|
| `numeroBolsin` | `int` |
| `latitud` | `float` |
| `longitud` | `float` |
| `fechaHoraUltimaActualizacion` | `datetime` |

Cada adaptador convierte el formato de su modelo a `UbicacionBolsin`. El gestor nunca ve JSON, CSV ni listas anidadas.

### 1.2 Modelo usado y adaptadores

La API expone los tres modelos de la ERS. Cada uno tiene su propia API key (header `X-API-Key`). Con una key de otro modelo responde 401.

**Modelo usado en el CU 36: XTR-4500L.** Es el de la Entrega 2 y el del diagrama de secuencia. Los adaptadores de NavTrack y GeoPulse existen en la API, pero el CU no los usa. Se implementan solo si el equipo los necesita.

| Modelo | Adaptador | Endpoint | Parametros | Header | Formato de respuesta |
|---|---|---|---|---|---|
| XTR-4500L (**usado**) | `gps_tracker_xtr4500l.py` | `GET /api/xtr-4500l/getBolsinLocation` | `numeroBolsin` (int), `codigoComisionMedicaOrigen` (str) | `X-API-Key: sk_xtr_...` | JSON: `{"items":[{numeroBolsin, latitud, longitud, fechaHoraUltimaActualizacion}]}` |
| NavTrack QX-7A | `gps_tracker_navtrack_qx7a.py` | `GET /api/navtrack-qx-7a/retrieveTrackingData` | `numeroBolsin` (int), `codigoComisionMedicaDestino` (str) | `X-API-Key: sk_nav_...` | Texto plano CSV: `101,-31.4201,-64.1888,2026-03-07T12:30` |
| GeoPulse MTR-900 | `gps_tracker_geopulse_mtr900.py` | `GET /api/geopulse-mtr-900/fetchCargoPositions` | `numeroBolsin` (int) | `X-API-Key: sk_geo_...` | Lista de listas: `[[101, -31.4201, -64.1888, "2026-03-07T12:30:00"]]` |

**Seleccion del modelo:** `GPS_MODELO` en `backend/config/settings.py`, valores `XTR-4500L` (default), `NAVTRACK-QX7A`, `GEOPULSE-MTR900`. `backend/config/composicion.py` elige el adaptador. Ningun otro modulo lee `GPS_MODELO`.

**Parseo:** cada adaptador tiene una funcion de parseo pura (sin red). La del XTR-4500L toma `items[0]` y valida que venga exactamente un item. Las fechas de la API vienen **sin zona horaria** (`2026-03-07T12:30:00`, o `2026-03-07T12:30` si los segundos son cero, porque la API usa `LocalDateTime.toString()`). Se parsean con `datetime.fromisoformat`, que acepta ambas formas.

**Base URL:** `GPS_BASE_URL`, default `http://localhost:8080`.

### 1.3 Comportamiento de la API (verificado en el repositorio)

| Situacion | HTTP | Cuerpo | Como lo trata el adaptador |
|---|---|---|---|
| OK | 200 | segun modelo | Parsea y devuelve `UbicacionBolsin`. |
| API key invalida o de otro modelo | 401 | `API_KEY_INVALIDA` | Error de configuracion. Se propaga como error del sistema, no como A3. |
| Parametro faltante o invalido | 400 | error JSON | Error de integracion. No deberia ocurrir con parametros validados. |
| Bolsin inexistente (no esta en la API) | 404 | error JSON | `UbicacionNoDisponibleError` para ese bolsin (**A3**). |
| Codigo de CM no coincide con el bolsin | 404 | error JSON | `UbicacionNoDisponibleError` para ese bolsin (**A3**). |

Consecuencia: la API no responde "sin ubicacion" con 200. Responde 404. El adaptador traduce 404 a A3.

Validacion de codigo: la API compara `codigoComisionMedicaOrigen` con el origen del bolsin (sin distinguir mayusculas). Por eso el adaptador envia el codigo de la CM del usuario logueado, y el bolsin solo tiene ubicacion si esa CM es su origen. Esto coincide con el filtro del CU 36.

### 1.4 Datos de la API y del set de datos

La API tiene 10 bolsines fijos (101 a 110). El set de datos (`docs/08-datos-semilla.md`) usa 101, 102, 103, 104 y 110 con origen y destino iguales a la API. El 111 no existe en la API, y es el caso A3 de la defensa.

## 2. Manejo de errores (A3)

Excepciones propias en `backend/integrations/gps_tracker/errores.py`:

```
class UbicacionNoDisponibleError(Exception)   # A3
    numeroBolsin: int
    motivo: str

class ErrorIntegracionGPS(Exception)          # 400/401/5xx o respuesta invalida
    motivo: str
```

Reglas:
- Un adaptador lanza `UbicacionNoDisponibleError` cuando recibe 404 (bolsin inexistente o codigo de CM que no coincide), que es el A3 del CU 36.
- Error de red o respuesta 5xx: tambien se traduce a `UbicacionNoDisponibleError` para ese bolsin (transitorio).
- 400 (parametro invalido), 401 (API key invalida) y respuesta con formato invalido: `ErrorIntegracionGPS`, que **no** es A3. El gestor no ve excepciones HTTP.
- El gestor captura `UbicacionNoDisponibleError` por bolsin, registra el bolsin como sin ubicacion y sigue con el resto. `ErrorIntegracionGPS` no se captura por bolsin: es un error de configuracion/integracion. Si ninguno tiene ubicacion, la sesion queda abierta con `marcadores` vacios y todos los bolsines en `sinUbicacion` (ver `docs/05-vista-dinamica.md` §5 y `docs/07-api-rest.md` §4).
- `routes` no captura esta excepcion: solo ve el resultado del gestor.

## 3. Google Maps

El backend no dibuja mapas. `InterfazGoogleMaps` (`backend/integrations/google_maps/interfaz_google_maps.py`) prepara los datos y el frontend renderiza.

`obtenerMapa(ubicaciones: UbicacionBolsin[]) -> MapaBolsines`, donde `MapaBolsines` es un schema de salida (`backend/schemas/seguimiento.py`):

```
MapaBolsines
  centro: { latitud: float, longitud: float }   # promedio de los marcadores, o centro por defecto si no hay
  zoom: int                                     # valor fijo por defecto
  marcadores: [
    { numeroBolsin: int, latitud: float, longitud: float, fechaHoraUltimaActualizacion: datetime }
  ]
```

Reparto de responsabilidades:
- **Backend (`integrations/google_maps`):** calcula centro y zoom por defecto, arma los marcadores y los devuelve en la respuesta HTTP del CU 36. No llama a la API de Google Maps en el servidor.
- **Frontend (`frontend/src/`):** renderiza el mapa con la libreria de Google Maps (ERS, requerimiento 7). Usa una clave de la API de Maps en `VITE_GOOGLE_MAPS_API_KEY`. Esa clave es publica por naturaleza del navegador: se restringe por dominio (`localhost:3020`).
- El filtro por numero de precinto o CM destino (paso 6 del CU) lo hace el frontend sobre `marcadores`, o pide otra consulta. No se implementa en el backend en esta entrega.

Ventaja: `InterfazGoogleMaps` es una implementacion simple y testeable sin red. La integracion real con la libreria queda en el frontend.

## 4. Notificacion por mail (CU 31)

Interfaz `InterfazCorreo` (`backend/integrations/correo/interfaz_correo.py`):

```
InterfazCorreo (ABC)
  + enviarMail(destinatario: str, asunto: str, cuerpo: str): void
```

Implementaciones:

| Implementacion | Archivo | Estado |
|---|---|---|
| Simulada por log/archivo | `correo/correo_simulado.py` | **Implementada.** Escribe el mensaje en el log de la aplicacion y, si `CORREO_ARCHIVO` esta definida, lo agrega a ese archivo. |
| Microsoft Graph (Outlook) | `correo/outlook_graph.py` | **No implementada.** Documentada: usaria la API de Microsoft Graph (ERS, requerimiento 5) con las credenciales `CORREO_TENANT_ID`, `CORREO_CLIENT_ID`, `CORREO_CLIENT_SECRET`. No se escribe codigo hasta tener credenciales. |
| Fake para tests | `correo/correo_fake.py` | Implementada. Guarda los envios en una lista para aserciones. |

Seleccion: `CORREO_MODO` en `settings.py` (`simulado` por defecto; `graph` cuando exista la implementacion).

Contenido del mail (CU 31): numero de bolsin, fecha y hora de ultima actualizacion, coordenadas. Lo arma el caso de uso de notificacion; la interfaz solo recibe texto.

## 5. Mocks en tests

| Dependencia | En tests | Como |
|---|---|---|
| GPS Tracker | `gps_tracker_fake.py` | Devuelve `UbicacionBolsin` predefinidas o lanza `UbicacionNoDisponibleError` para simular A3. |
| Google Maps | Se usa la implementacion real (es pura, sin red). | No hay mock necesario. |
| Correo | `correo_fake.py` | Acumula envios. Los tests verifican destinatario y contenido, y que A5 no envie nada. |
| Adaptadores GPS (parseo) | Funciones puras | Tests con cadenas de ejemplo, sin red. Las llamadas HTTP se prueban con `httpx.MockTransport` cuando exista la guia. |

`backend/tests/conftest.py` arma el gestor con los fakes mediante `config/composicion.py`, en lugar de los adaptadores reales. Un test nunca llama a la red ni envia mail real.

## 6. Configuracion

Todas las variables se leen en `backend/config/settings.py` y se cargan desde `.env` (ver `.env.example`). Ningun modulo lee `os.environ` directamente.

| Variable | Uso | Default |
|---|---|---|
| `GPS_MODELO` | Modelo de dispositivo: `XTR-4500L`, `NAVTRACK-QX7A`, `GEOPULSE-MTR900` | `XTR-4500L` |
| `GPS_BASE_URL` | URL base de la API GPS | `http://localhost:8080` |
| `GPS_API_KEY_XTR4500L` | API key del XTR-4500L (header `X-API-Key`) | vacio en el repo. Valor en `.env`. |
| `GPS_API_KEY_NAVTRACK` | API key del NavTrack QX-7A | vacio. Solo si se usa ese modelo. |
| `GPS_API_KEY_GEOPULSE` | API key del GeoPulse MTR-900 | vacio. Solo si se usa ese modelo. |
| `CORREO_MODO` | `simulado` o `graph` | `simulado` |
| `CORREO_ARCHIVO` | Archivo donde el correo simulado guarda los mensajes | vacio (solo log) |
| `CORREO_TENANT_ID`, `CORREO_CLIENT_ID`, `CORREO_CLIENT_SECRET` | Credenciales de Microsoft Graph | vacio. Solo si `CORREO_MODO=graph`. |
| `VITE_GOOGLE_MAPS_API_KEY` (frontend) | Clave de la API de Maps para el navegador | vacio. Restringida por dominio. |

Ver `.env.example` (variables del backend). La clave de Maps va en `frontend/.env`, no en el de la raiz.

## 7. Pendientes

1. Confirmar con el equipo si el CU 36 usa solo XTR-4500L (asi esta definido) o si conviene implementar tambien NavTrack y GeoPulse.
2. Credenciales de Microsoft Graph, si el equipo decide implementarlo.
3. Centro del mapa cuando no hay marcadores (`docs/07-api-rest.md` §5.3): valor por defecto a definir.
