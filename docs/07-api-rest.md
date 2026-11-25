# 07 - API REST del CU 36

Endpoints FastAPI que implementan los pasos del CU 36 sin alterar la logica del gestor (`GestorBuscarBolsines`). `routes/` solo traduce HTTP a llamadas del gestor y del gestor a schemas (AGENTS.md §4).

`{idCU}` es el identificador UUID4 del caso de uso en curso (registro en memoria, `backend/services/registro_casos_uso.py`).

## 1. Endpoints

| Metodo | Ruta | Pasos CU | Metodo del gestor | Request | Response | Codigos HTTP |
|---|---|---|---|---|---|---|
| POST | `/seguimiento-bolsines` | 2 a 9 | `opcionSeguirBolsines()` | sin body | `SeguimientoCreadoResponse` (201) | 201, 403, 404 |
| POST | `/seguimiento-bolsines/{idCU}/seleccion` | 10 | `tomarSeleccionBolsin(numeroBolsin)` | `SeleccionBolsinRequest` | `SeleccionBolsinResponse` | 200, 403, 404, 422 |
| POST | `/seguimiento-bolsines/{idCU}/confirmacion-correo` | 11 a 13 | `tomarConfirmacionEnvioCorreo(confirma)` | `ConfirmacionCorreoRequest` | `ConfirmacionCorreoResponse` | 200, 403, 404, 422, 502 |
| DELETE | `/seguimiento-bolsines/{idCU}` | A4 | `cancelar()` | ninguno | ninguno | 204, 403, 404 |

Notas:
- `403`: el `Empleado` del usuario de desarrollo no tiene rol Encargado de Bolsines (`ROL_INSUFICIENTE`).
- `404`: A1 (`SIN_BOLSINES_ENVIADOS`) o `idCU` inexistente/vencido (`CASO_USO_NO_ENCONTRADO`).
- `422`: validacion de schema (`SOLICITUD_INVALIDA`) o bolsin fuera de los enviados (`BOLSIN_FUERA_DE_ENVIADOS`).
- `502`: fallo del servidor de correo (`CORREO_NO_ENVIADO`). La sesion queda abierta para reintentar.

## 2. Schemas (`backend/schemas/seguimiento.py`)

| Schema | Campos |
|---|---|
| `BolsinSeguimientoOut` | `numeroBolsin: int`, `numeroPrecinto: str \| None`, `codigoCMDestino: str` |
| `CoordenadaOut` | `latitud: float`, `longitud: float` |
| `MarcadorOut` | `numeroBolsin: int`, `latitud: float`, `longitud: float`, `fechaHoraUltimaActualizacion: datetime` |
| `MapaBolsinesOut` | `centro: CoordenadaOut`, `zoom: int`, `marcadores: list[MarcadorOut]` |
| `SinUbicacionOut` | `numeroBolsin: int`, `motivo: str` |
| `SeguimientoCreadoResponse` | `idCU: UUID`, `codigoCM: str`, `bolsines: list[BolsinSeguimientoOut]`, `mapa: MapaBolsinesOut`, `sinUbicacion: list[SinUbicacionOut]` |
| `SeleccionBolsinRequest` | `numeroBolsin: int` (> 0) |
| `SeleccionBolsinResponse` | `idCU: UUID`, `bolsin: BolsinSeguimientoOut`, `ubicacion: MarcadorOut`, `requiereConfirmacionCorreo: bool` |
| `ConfirmacionCorreoRequest` | `confirma: bool` |
| `ConfirmacionCorreoResponse` | `estado: Literal["FINALIZADO"]`, `notificado: bool`, `destinatarioEnmascarado: str \| None` |
| `ErrorResponse` | `codigo: str`, `mensaje: str` |

`destinatarioEnmascarado` muestra solo parte del mail (por ejemplo `g***@dominio.gob`). La direccion completa no sale de la API.

Los schemas solo validan y serializan. `MapaBolsinesOut` lo arma `integrations/google_maps` (ver `docs/06-integraciones.md` §3).

## 3. Usuario logueado y rol

- Las rutas de seguimiento usan la dependencia de **usuario de desarrollo** (`usuario_dev_dependency`), que carga el `Usuario` de `settings.USUARIO_DEV` con su `Empleado`, `Rol` y `ComisionMedica`.
- El login JWT (`routes/auth.py`: token, refresh, logout) sigue disponible para el resto de la API.
- La validacion de rol se hace en `routes`: si el `Empleado` no es Encargado de Bolsines, responde `403` con `{codigo: "ROL_INSUFICIENTE", mensaje}`.
- `GET /auth/me` devuelve `{id, mail, nombre, apellido, rol, codigoCM}` del usuario de desarrollo.

## 4. Mapeo de flujos alternativos a respuestas

| Alternativo | Endpoint | Respuesta | Efecto |
|---|---|---|---|
| A1: no hay bolsines Enviados de la CM | POST `/seguimiento-bolsines` | 404 `{codigo: "SIN_BOLSINES_ENVIADOS", mensaje}` | El gestor lanza `SinBolsinesEnviadosError` y el route la traduce a 404. No hay GPS, mapa ni correo. |
| A2: precinto sin resultado | (ninguno) | - | `GestorBuscarBolsines.filtrarPorPrecinto` devuelve lista vacia y agrega advertencia; el frontend informa. |
| A3: GPS no informa ubicacion de un bolsin | POST `/seguimiento-bolsines` | 201, el bolsin aparece en `sinUbicacion` y no en `marcadores` | El gestor sigue con el resto. Si ninguno tiene ubicacion, `marcadores` es `[]`, todos los bolsines van en `sinUbicacion` y la sesion queda abierta. El EB puede seleccionar otro bolsin o cancelar. |
| A4: EB cancela | DELETE `/seguimiento-bolsines/{idCU}` | 204 | El gestor se elimina del registro en memoria. No se envia correo. |
| A5: EB no confirma el correo | POST `.../confirmacion-correo` con `confirma: false` | 200, `notificado: false` | No se llama a `enviarMailGCM`. La sesion se cierra. |

## 5. Ejemplos JSON

### 5.1 Flujo principal

**Paso 1, POST `/seguimiento-bolsines`** (sin body, header `Authorization: Bearer <jwt>`)

Response 201 (usuario EB Córdoba 1, escenario de `08-datos-semilla.md` §7):
```json
{
  "idCU": "3f2a9c1e-7b4d-4e8a-9f10-2c5d6e7a8b90",
  "codigoCM": "CM-CBA-01",
  "bolsines": [
    { "numeroBolsin": 101, "numeroPrecinto": "P-0101", "codigoCMDestino": "CM-ROS-02" },
    { "numeroBolsin": 111, "numeroPrecinto": "P-0111", "codigoCMDestino": "CM-MDZ-03" }
  ],
  "mapa": {
    "centro": { "latitud": -31.4201, "longitud": -64.1888 },
    "zoom": 6,
    "marcadores": [
      { "numeroBolsin": 101, "latitud": -31.4201, "longitud": -64.1888, "fechaHoraUltimaActualizacion": "2026-03-07T12:30:00" }
    ]
  },
  "sinUbicacion": [ { "numeroBolsin": 111, "motivo": "El GPS no informo ubicacion" } ]
}
```

**Paso 2, POST `/seguimiento-bolsines/{idCU}/seleccion`**

Request:
```json
{ "numeroBolsin": 101 }
```

Response 200:
```json
{
  "idCU": "3f2a9c1e-7b4d-4e8a-9f10-2c5d6e7a8b90",
  "bolsin": { "numeroBolsin": 101, "numeroPrecinto": "P-0101", "codigoCMDestino": "CM-ROS-02" },
  "ubicacion": { "numeroBolsin": 101, "latitud": -31.4201, "longitud": -64.1888, "fechaHoraUltimaActualizacion": "2026-03-07T12:30:00" },
  "requiereConfirmacionCorreo": true
}
```

**Paso 3, POST `/seguimiento-bolsines/{idCU}/confirmacion-correo`**

Request:
```json
{ "confirma": true }
```

Response 200:
```json
{ "estado": "FINALIZADO", "notificado": true, "destinatarioEnmascarado": "g***@example.test" }
```

### 5.2 A1: sin bolsines Enviados

POST `/seguimiento-bolsines`, response 404:
```json
{ "codigo": "SIN_BOLSINES_ENVIADOS", "mensaje": "No hay bolsines Enviados para la CM CM-CBA-01" }
```

No hay sesion abierta, ni GPS, mapa o correo.

### 5.3 A3: GPS sin ubicacion para un bolsin

POST `/seguimiento-bolsines`, response 201 (fragmento; es el caso de la defensa: 101 con ubicacion y 111 sin ubicacion):

```json
{
  "idCU": "3f2a9c1e-7b4d-4e8a-9f10-2c5d6e7a8b90",
  "codigoCM": "CM-CBA-01",
  "bolsines": [
    { "numeroBolsin": 101, "numeroPrecinto": "P-0101", "codigoCMDestino": "CM-ROS-02" },
    { "numeroBolsin": 111, "numeroPrecinto": "P-0111", "codigoCMDestino": "CM-MDZ-03" }
  ],
  "mapa": {
    "centro": { "latitud": -31.4201, "longitud": -64.1888 },
    "zoom": 6,
    "marcadores": [
      { "numeroBolsin": 101, "latitud": -31.4201, "longitud": -64.1888, "fechaHoraUltimaActualizacion": "2026-03-07T12:30:00" }
    ]
  },
  "sinUbicacion": [ { "numeroBolsin": 111, "motivo": "El GPS no informo ubicacion" } ]
}
```

Si ningun bolsin tuviera ubicacion, `marcadores` seria `[]` y todos irian a `sinUbicacion`. En ese caso el `centro` toma el valor por defecto del backend (`docs/06-integraciones.md` §7).

### 5.4 A5: EB no confirma el correo

POST `.../confirmacion-correo`, request:
```json
{ "confirma": false }
```

Response 200:
```json
{ "estado": "FINALIZADO", "notificado": false, "destinatarioEnmascarado": null }
```

### 5.5 Error: caso de uso inexistente o vencido

Response 404 (cualquier endpoint con `{idCU}`):
```json
{ "codigo": "CASO_USO_NO_ENCONTRADO", "detalle": "El caso de uso no existe o vencio." }
```
