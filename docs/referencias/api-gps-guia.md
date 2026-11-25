# Guia de la API simulada del GPS Tracker

Elaborada por el equipo a partir del repositorio de la catedra **`LiberaeMentis/dsi-api-bolsines`**. No forma parte de los documentos originales de la catedra.

El repositorio es un backend mock en **Java 17 + Spring Boot** que simula tres modelos de GPS Tracker del dominio de Bolsines. No usa base de datos ni autenticacion real: solo valida una API key mock por modelo.

## 1. Requisitos y ejecucion

- Java 17.
- Sin base de datos.
- Sin autenticacion real (solo API key mock).

Levantar con Maven Wrapper:

```
./mvnw spring-boot:run
```

La API queda disponible en:

```
http://localhost:8080
```

Tambien se puede ejecutar la clase `GpsTrackerMockApplication` desde IntelliJ o la configuracion de VS Code.

## 2. Configuracion y API keys

Las claves estan publicadas en `src/main/resources/application.properties` del repositorio. Son valores mock de desarrollo.

- XTR-4500L: `sk_xtr_9F3a7C21bE6d4A10f2c8e5b7d913`
- NavTrack QX-7A: `sk_nav_7b61d9e4c3a2485fae10c77d5b2f`
- GeoPulse MTR-900: `sk_geo_f2d84a1c9e7345b8a6d1c3f0972e`
- Puerto: `8080` (`server.port=8080`)

Los endpoints de GPS requieren el header:

```
X-API-Key: <api key del modelo>
```

Si se envia una key incorrecta o de otro modelo, la API responde `401`.

En nuestro backend, la key se configura por variable de entorno `GPS_API_KEY` (en `.env`), nunca en el codigo. El modelo se elige con `GPS_MODELO` (`xtr4500l`, `navtrack`, `geopulse`).

## 3. Endpoints

| Metodo | Ruta | Parametros | Header | Salida |
|---|---|---|---|---|
| GET | `/health` | - | - | JSON `{"status":"ok"}` |
| GET | `/api/mock/bolsines` | - | - | Lista de bolsines mock |
| GET | `/api/mock/bolsines/{numeroBolsin}` | path `numeroBolsin` | - | Un bolsin mock |
| GET | `/api/xtr-4500l/getBolsinLocation` | `numeroBolsin`, `codigoComisionMedicaOrigen` | `X-API-Key` (XTR) | JSON |
| GET | `/api/navtrack-qx-7a/retrieveTrackingData` | `numeroBolsin`, `codigoComisionMedicaDestino` | `X-API-Key` (NavTrack) | Texto plano CSV |
| GET | `/api/geopulse-mtr-900/fetchCargoPositions` | `numeroBolsin` | `X-API-Key` (GeoPulse) | Matriz |

## 4. XTR-4500L

Modelo usado por el CU 36.

Request de ejemplo:

```
curl -H "X-API-Key: sk_xtr_9F3a7C21bE6d4A10f2c8e5b7d913" \
  "http://localhost:8080/api/xtr-4500l/getBolsinLocation?numeroBolsin=101&codigoComisionMedicaOrigen=CM-CBA-01"
```

Respuesta:

```json
{
  "items": [
    {
      "numeroBolsin": 101,
      "latitud": -31.4201,
      "longitud": -64.1888,
      "fechaHoraUltimaActualizacion": "2026-03-07T12:30:00"
    }
  ]
}
```

Notas:
- La API valida que `codigoComisionMedicaOrigen` coincida con el origen del bolsin.
- Devuelve un unico item; `fechaHoraUltimaActualizacion` no tiene zona horaria.
- Si el bolsin no existe o el codigo no coincide, responde `404`.

## 5. NavTrack QX-7A

Request de ejemplo:

```
curl -H "X-API-Key: sk_nav_7b61d9e4c3a2485fae10c77d5b2f" \
  "http://localhost:8080/api/navtrack-qx-7a/retrieveTrackingData?numeroBolsin=101&codigoComisionMedicaDestino=CM-ROS-02"
```

Respuesta (`Content-Type: text/plain`):

```
101,-31.4201,-64.1888,2026-03-07T12:30
```

Notas:
- La API valida que `codigoComisionMedicaDestino` coincida con el destino del bolsin.
- Devuelve un unico string con los campos separados por comas.
- La fecha puede venir sin segundos cuando son cero.

## 6. GeoPulse MTR-900

Request de ejemplo:

```
curl -H "X-API-Key: sk_geo_f2d84a1c9e7345b8a6d1c3f0972e" \
  "http://localhost:8080/api/geopulse-mtr-900/fetchCargoPositions?numeroBolsin=101"
```

Respuesta:

```
[[101, -31.4201, -64.1888, "2026-03-07T12:30:00"]]
```

Notas:
- No recibe codigo de CM y no lo valida.
- Devuelve una matriz (lista de listas).
- La fecha se devuelve como texto entre comillas.

## 7. Errores

Formato del cuerpo:

```json
{
  "error": "API_KEY_INVALIDA",
  "mensaje": "La API Key provista no es valida.",
  "status": 401,
  "timestamp": "2026-03-07T12:30:00"
}
```

Codigos implementados (`GlobalExceptionHandler`):

| HTTP | `error` | Cuando ocurre |
|---|---|---|
| 401 | `API_KEY_INVALIDA` | API key incorrecta o de otro modelo |
| 400 | `SOLICITUD_INVALIDA` | Parametro o header faltante o invalido |
| 404 | `BOLSIN_NO_ENCONTRADO` | Numero de bolsin inexistente |
| 404 | `CODIGO_COMISION_NO_COINCIDE` | El codigo de CM no coincide con el bolsin |
| 500 | `ERROR_INTERNO` | Error inesperado |

## 8. Datos mock precargados

Definidos en `InMemoryBolsinRepository.init()`. Son 10 bolsines fijos.

| numeroBolsin | Origen | Destino | Latitud | Longitud | fechaHoraUltimaActualizacion |
|---|---|---|---|---|---|
| 101 | CM-CBA-01 | CM-ROS-02 | -31.4201 | -64.1888 | 2026-03-07T12:30:00 |
| 102 | CM-ROS-02 | CM-MDZ-03 | -32.9468 | -60.6393 | 2026-03-07T12:32:15 |
| 103 | CM-MDZ-03 | CM-BA-01 | -32.8895 | -68.8458 | 2026-03-07T12:35:04 |
| 104 | CM-BA-01 | CM-CBA-01 | -34.6037 | -58.3816 | 2026-03-07T12:36:20 |
| 105 | CM-TUC-01 | CM-SLA-01 | -26.8083 | -65.2176 | 2026-03-07T12:40:31 |
| 106 | CM-SLA-01 | CM-JUJ-01 | -24.7829 | -65.4232 | 2026-03-07T12:43:18 |
| 107 | CM-NQN-01 | CM-MDQ-01 | -38.9516 | -68.0591 | 2026-03-07T12:45:46 |
| 108 | CM-MDQ-01 | CM-BA-01 | -38.0055 | -57.5426 | 2026-03-07T12:47:02 |
| 109 | CM-LPL-01 | CM-CBA-01 | -34.9215 | -57.9545 | 2026-03-07T12:49:27 |
| 110 | CM-CBA-02 | CM-ROS-02 | -31.4167 | -64.1833 | 2026-03-07T12:52:09 |

Cualquier otro numero (por ejemplo 111 o 999) responde `404 BOLSIN_NO_ENCONTRADO`. Ese comportamiento es el que usa el CU 36 para el alternativo A3.

## 9. Validaciones por modelo

| Modelo | Parametro de codigo | Valida contra |
|---|---|---|
| XTR-4500L | `codigoComisionMedicaOrigen` | CM origen del bolsin |
| NavTrack QX-7A | `codigoComisionMedicaDestino` | CM destino del bolsin |
| GeoPulse MTR-900 | (ninguno) | No valida |

La comparacion de codigos no distingue mayusculas y minusculas.

## 10. Como lo usa nuestro backend

- `InterfazGPSTracker` (async) con `getBolsinLocation(numeroBolsin, codigoCM)`.
- Adaptador usado: `GpsTrackerXtr4500l` (`GPS_MODELO=xtr4500l`), con `GPS_BASE_URL` y `GPS_API_KEY`.
- Normalizacion a `UbicacionBolsin` (`numeroBolsin`, `latitud`, `longitud`, `fechaHoraUltimaActualizacion`).
- Mapeo de errores:
  - `404` (bolsin inexistente o codigo que no coincide), error de red o `5xx` -> `UbicacionNoDisponibleError` (alternativo A3).
  - `400`/`401` o respuesta con formato invalido -> `ErrorIntegracionGPS` (no es A3).
- Fechas sin zona horaria: se parsean con `datetime.fromisoformat`.

## 11. Notas

- Es un mock para desarrollo y defensa; no usar en produccion.
- Los datos son fijos en memoria y se reinician al levantar la aplicacion.
- Las API keys son mock y estan publicadas en el repositorio de la catedra.
