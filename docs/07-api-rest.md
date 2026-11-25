# 07 - API REST del CU 36

Endpoints FastAPI que implementan los pasos del CU 36 sin alterar la logica del gestor (`GestorBuscarBolsines`). `routes/` solo traduce HTTP a llamadas del gestor y del gestor a schemas (AGENTS.md §4).

`{idCU}` es el identificador UUID4 del caso de uso en curso (registro en memoria, `backend/services/registro_casos_uso.py`).

## 1. Endpoints

| Metodo | Ruta | Pasos CU | Metodo del gestor | Request | Response | Codigos HTTP |
|---|---|---|---|---|---|---|
| POST | `/seguimiento-bolsines` | 2 a 9 | `opcionSeguirBolsines()` | sin body | `SeguimientoCreadoResponse` (201) o `SinBolsinesResponse` (200) | 201, 200, 401, 403 |
| POST | `/seguimiento-bolsines/{idCU}/seleccion` | 10 | `tomarSeleccionBolsin(numeroBolsin)` | `SeleccionBolsinRequest` | `SeleccionBolsinResponse` | 200, 401, 403, 404, 422 |
| POST | `/seguimiento-bolsines/{idCU}/confirmacion-correo` | 11 a 13 | `tomarConfirmacionEnvioCorreo(confirma)` | `ConfirmacionCorreoRequest` | `ConfirmacionCorreoResponse` | 200, 401, 403, 404, 422, 502 |
| DELETE | `/seguimiento-bolsines/{idCU}` | A4 | `cancelar()` | ninguno | ninguno | 204, 401, 403, 404 |

Notas:
- `401`: sin JWT valido (`user_dependency`).
- `403`: el `Empleado` del usuario no tiene rol Encargado de Bolsines.
- `404`: `idCU` inexistente o vencido por TTL.
- `422`: validacion de schema (por ejemplo `numeroBolsin <= 0`).
- `502`: fallo del servidor de correo. La sesion queda abierta para reintentar.

## 2. Schemas (`backend/schemas/seguimiento.py`)

| Schema | Campos |
|---|---|
| `BolsinSeguimientoOut` | `numeroBolsin: int`, `numeroPrecinto: str \| None`, `codigoCMDestino: str` |
| `CoordenadaOut` | `latitud: float`, `longitud: float` |
| `MarcadorOut` | `numeroBolsin: int`, `latitud: float`, `longitud: float`, `fechaHoraUltimaActualizacion: datetime` |
| `MapaBolsinesOut` | `centro: CoordenadaOut`, `zoom: int`, `marcadores: list[MarcadorOut]` |
| `SinUbicacionOut` | `numeroBolsin: int`, `motivo: str` |
| `SeguimientoCreadoResponse` | `idCU: UUID`, `codigoCM: str`, `bolsines: list[BolsinSeguimientoOut]`, `mapa: MapaBolsinesOut`, `sinUbicacion: list[SinUbicacionOut]` |
| `SinBolsinesResponse` | `idCU: None`, `codigoCM: str`, `estado: Literal["SIN_BOLSINES"]` |
| `SeleccionBolsinRequest` | `numeroBolsin: int` (> 0) |
| `SeleccionBolsinResponse` | `idCU: UUID`, `bolsin: BolsinSeguimientoOut`, `ubicacion: MarcadorOut`, `requiereConfirmacionCorreo: bool` |
| `ConfirmacionCorreoRequest` | `confirma: bool` |
| `ConfirmacionCorreoResponse` | `estado: Literal["FINALIZADO"]`, `notificado: bool`, `destinatarioEnmascarado: str \| None` |
| `ErrorResponse` | `codigo: str`, `detalle: str` |

`destinatarioEnmascarado` muestra solo parte del mail (por ejemplo `g***@dominio.gob`). La direccion completa no sale de la API.

Los schemas solo validan y serializan. `MapaBolsinesOut` lo arma `integrations/google_maps` (ver `docs/06-integraciones.md` §3).

## 3. Usuario logueado y rol

- Se usa `user_dependency` (JWT, `backend/utils/auth.py`), igual que en el resto de la API.
- `Usuario` llega a `Empleado` por `idUser` (relacion 1 a 1).
- La validacion de rol se hace en `routes`: si el `Empleado` no es Encargado de Bolsines, responde `403`. Requiere el metodo `Rol.esEncargadoBolsines()`, ademas de `esGCM()`.
- Login real: endpoint de `routes/auth.py` (la ruta exacta se fija al implementar). El seed (`backend/data/seed.py`) crea un `Usuario` con su `Empleado` y rol Encargado de Bolsines. No hay token fijo ni bypass de autenticacion.

## 4. Mapeo de flujos alternativos a respuestas

| Alternativo | Endpoint | Respuesta | Efecto |
|---|---|---|---|
| A1: no hay bolsines Enviados de la CM | POST `/seguimiento-bolsines` | 200 `SinBolsinesResponse` | El gestor lanza `SinBolsinesEnviadosError` y el route la traduce a 200. No hay GPS, mapa ni correo. |
| A2: precinto sin resultado | (ninguno) | - | El filtro por precinto se hace en el frontend sobre `bolsines` y `marcadores`. Sin llamada al backend. |
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

POST `/seguimiento-bolsines`, response 200 (`SinBolsinesResponse`):
```json
{ "idCU": null, "codigoCM": "CM-CBA-01", "estado": "SIN_BOLSINES" }
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
