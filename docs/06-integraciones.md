# 06 - Integraciones (CU 36)

Fuentes: ERS v1.2, CU 36 (Observacion 1 sobre GPS Tracker) y requerimientos no funcionales 5, 6 y 7. Regla de `AGENTS.md` §4 y §8: las integraciones viven solo en `backend/integrations/` y el gestor depende solo de interfaces.

Estado de esta version:
- Seccion 1 (adaptadores GPS): **pendiente**. La guia de la API simulada de la catedra (`docs/referencias/api-gps-guia.md`) no existe en el repo. No se definen endpoints ni formatos de respuesta sin esa guia. Se completa cuando el equipo la copie.
- Secciones 2 a 6: definidas.

## 1. GPS Tracker (pendiente de la guia de la catedra)

### 1.1 Interfaz comun

`InterfazGPSTracker` (`backend/integrations/gps_tracker/interfaz_gps_tracker.py`) es una clase abstracta. Su metodo devuelve siempre la misma forma normalizada, sin importar el modelo de dispositivo:

```
InterfazGPSTracker (ABC)
  + obtenerUbicaciones(codigosBolsin: int[], codigoCM: str): UbicacionBolsin[]
```

`UbicacionBolsin` (`backend/models/ubicacion_bolsin.py`, value object, no es tabla):

| Campo | Tipo Python |
|---|---|
| `numeroBolsin` | `int` |
| `latitud` | `float` |
| `longitud` | `float` |
| `fechaHoraUltimaActualizacion` | `datetime` |

Cada adaptador convierte el formato de su modelo a `UbicacionBolsin`. El gestor nunca ve JSON, CSV ni matrices.

Nota: el diagrama de diseno (`docs/04-vista-estatica.md`) muestra `getBolsinLocation(numeroBolsin, codigoCM)` en la interfaz. Esa firma es la del endpoint del XTR-4500L. Para respetar el diagrama, la interfaz publica se llama `getBolsinLocation` y se consulta por bolsin; `obtenerUbicaciones` queda como nombre de la version normalizada por lote. Pendiente de confirmar con la guia y el equipo.

### 1.2 Adaptadores por modelo (ERS, Obs. 1)

Firmas segun la ERS. Los formatos de respuesta y las rutas HTTP se completan con la guia de la catedra.

| Modelo | Adaptador | Endpoint (ERS) | Entrada (ERS) | Salida (ERS) |
|---|---|---|---|---|
| XTR-4500L | `gps_tracker_xtr4500l.py` | `getBolsinLocation()` | API key, numero de bolsin (int), codigo CM origen (str) | JSON en cadena: por cada item, numero, latitud, longitud, fecha/hora de ultima actualizacion |
| NavTrack QX-7A | `gps_tracker_navtrack_qx7a.py` | `retrieveTrackingData()` | API key, numero de bolsin (int), codigo CM destino (str) | Un solo String con items separados por comas |
| GeoPulse MTR-900 | `gps_tracker_geopulse_mtr900.py` | `fetchCargoPositions()` | API key, numero de bolsin (int) | Matriz |

**Cual se usa contra la API de la catedra:** pendiente. La ERS describe tres modelos, pero la API simulada puede exponer solo uno. Se confirma con la guia.

**Seleccion del modelo:** variable `GPS_MODELO` en `backend/config/settings.py` (valores `XTR-4500L`, `NAVTRACK-QX7A`, `GEOPULSE-MTR900`). `backend/config/composicion.py` elige el adaptador segun esa variable. Ningun otro modulo lee `GPS_MODELO`.

**Parseo:** cada adaptador tiene su funcion de parseo pura (sin red), probada con respuestas de ejemplo. Los formatos se documentaran aca cuando se conozcan.

## 2. Manejo de errores (A3)

Excepcion propia en `backend/integrations/gps_tracker/errores.py`:

```
class UbicacionNoDisponibleError(Exception)
    numeroBolsin: int
    motivo: str
```

Reglas:
- Un adaptador lanza `UbicacionNoDisponibleError` cuando el GPS no informa ubicacion para un bolsin (A3 del CU 36), o cuando la respuesta es invalida.
- Error de red o autenticacion: tambien se traduce a `UbicacionNoDisponibleError` para ese bolsin, con el motivo correspondiente. El gestor no ve excepciones HTTP.
- El gestor captura `UbicacionNoDisponibleError` por bolsin, registra el bolsin como sin ubicacion y sigue con el resto. Si ninguno tiene ubicacion, informa a la pantalla y termina el CU (ver `docs/05-vista-dinamica.md` §5, A3).
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
| `GPS_MODELO` | Modelo de dispositivo: `XTR-4500L`, `NAVTRACK-QX7A`, `GEOPULSE-MTR900` | `XTR-4500L` (pendiente de confirmar) |
| `GPS_BASE_URL` | URL base de la API GPS | vacio (pendiente de la guia) |
| `GPS_API_KEY` | API key identificatoria | vacio. Nunca en el repo. |
| `CORREO_MODO` | `simulado` o `graph` | `simulado` |
| `CORREO_ARCHIVO` | Archivo donde el correo simulado guarda los mensajes | vacio (solo log) |
| `CORREO_TENANT_ID`, `CORREO_CLIENT_ID`, `CORREO_CLIENT_SECRET` | Credenciales de Microsoft Graph | vacio. Solo si `CORREO_MODO=graph`. |
| `VITE_GOOGLE_MAPS_API_KEY` (frontend) | Clave de la API de Maps para el navegador | vacio. Restringida por dominio. |

Ver `.env.example` (variables del backend). La clave de Maps va en `frontend/.env`, no en el de la raiz.

## 7. Pendientes

1. Copiar la guia de la API simulada de la catedra en `docs/referencias/api-gps-guia.md`. Con ella se completa la seccion 1 (rutas, formatos y modelo real).
2. Definir el nombre definitivo del metodo de la interfaz GPS (`getBolsinLocation` por bolsin u `obtenerUbicaciones` por lote).
3. Credenciales de Microsoft Graph, si el equipo decide implementarlo.
