# 08 - Datos semilla (CU 36)

Set de datos que permite demostrar el flujo principal y los alternativos A1 a A5 en la defensa. Los numeros de bolsin, los codigos de CM y las ubicaciones coinciden con la API simulada del GPS de la catedra (repositorio `LiberaeMentis/dsi-api-bolsines`, datos precargados en `InMemoryBolsinRepository.init()`).

El script `backend/data/seed.py` se implementa en una tarea posterior. Este documento define el contenido y el procedimiento.

## 1. Estados

Nombres de la Entrega 1 (maquina de estados de Bolsin). La descripcion toma el texto de la ERS.

| id | nombre | descripcion |
|---|---|---|
| 1 | Creado | Bolsin armado, sin precinto |
| 2 | Cerrado | Cerrado con precinto, pendiente de retiro |
| 3 | Enviado | Retirado por el correo, en transito |
| 4 | Recibido | Recibido en CM destino (ERS: "Recibido en CM destino") |
| 5 | De baja | Dado de baja |

Solo `Enviado` importa para el CU 36 (`Estado.esEnviado()` compara `nombre == "Enviado"`).

## 2. Roles

`Rol.nombre` debe coincidir exactamente, porque `esGCM()` y `esEncargadoBolsines()` comparan por nombre.

| id | nombre |
|---|---|
| 1 | Encargado de Bolsines |
| 2 | Gerente de Comisión Médica |
| 3 | Encargado de Documentación |
| 4 | Parametrizador del sistema |

## 3. Comisiones Médicas

Codigos iguales a los de la API del GPS. Son 6 CM: 5 CMJ y la CMC.

| codigo | nombre | Tipo |
|---|---|---|
| CM-CBA-01 | Comisión Médica Córdoba | CMJ |
| CM-CBA-02 | Comisión Médica Córdoba 2 | CMJ |
| CM-ROS-02 | Comisión Médica Rosario | CMJ |
| CM-MDZ-03 | Comisión Médica Mendoza | CMJ |
| CM-TUC-01 | Comisión Médica Tucumán | CMJ |
| CM-BA-01 | Comisión Médica Central | CMC (CABA) |

`CM-BA-01` se toma como CMC. Es un supuesto a partir del codigo, registrado en §8.

## 4. Empleados y usuarios

Cada `Empleado` tiene un `Usuario` (relacion 1 a 1, `idUser` unico). El correo del GCM vive en `Usuario.mail`. Dominio `example.test`, reservado para pruebas.

| Empleado | CM | Rol | mail (`Usuario.mail`) | Uso en la defensa |
|---|---|---|---|---|
| EB Córdoba 1 | CM-CBA-01 | Encargado de Bolsines | eb.cba01@example.test | Principal (con A3) |
| EB Córdoba 2 | CM-CBA-02 | Encargado de Bolsines | eb.cba02@example.test | Principal limpio |
| EB Tucumán | CM-TUC-01 | Encargado de Bolsines | eb.tuc01@example.test | A1 |
| GCM Córdoba | CM-CBA-01 | Gerente de Comisión Médica | gcm.cba-01@example.test | Destino de correo |
| GCM Córdoba 2 | CM-CBA-02 | Gerente de Comisión Médica | gcm.cba-02@example.test | Destino de correo |
| GCM Rosario | CM-ROS-02 | Gerente de Comisión Médica | gcm.ros-02@example.test | Destino de correo |
| GCM Mendoza | CM-MDZ-03 | Gerente de Comisión Médica | gcm.mdz-03@example.test | Destino de correo |
| GCM Tucumán | CM-TUC-01 | Gerente de Comisión Médica | gcm.tuc-01@example.test | Destino de correo |
| GCM CABA | CM-BA-01 | Gerente de Comisión Médica | gcm.ba-01@example.test | Destino de correo |

Contrasenas: no van en el codigo ni en este documento. El seed las toma de la variable `SEED_PASSWORD_DEV` (en `.env`) y guarda solo el hash (pwdlib/argon2).

El caso de uso necesita el GCM de la CM destino del bolsin seleccionado. Por eso hay un GCM por cada CM.

### Sesion

El seed no crea filas en `RefreshToken`. La sesion se crea en el login (`POST` de `routes/auth.py`). Para la defensa se inicia sesion con uno de los usuarios de la tabla.

## 5. Bolsines

Precinto `null` mientras el bolsin esta en `Creado`. Peso en gramos. La columna "En la API" indica si el numero existe en la API simulada y, si existe, si el origen y destino coinciden con la API.

| numeroBolsin | Origen → Destino | Estado actual | numeroPrecinto | peso | En la API | Rol en la defensa |
|---|---|---|---|---|---|---|
| 101 | CM-CBA-01 → CM-ROS-02 | Enviado | P-0101 | 4200 | Si, coincide | Principal, con ubicacion |
| 110 | CM-CBA-02 → CM-ROS-02 | Enviado | P-0110 | 3800 | Si, coincide | Principal limpio |
| 111 | CM-CBA-01 → CM-MDZ-03 | Enviado | P-0111 | 2950 | No (404) | **A3**: sin ubicacion |
| 102 | CM-ROS-02 → CM-MDZ-03 | Enviado | P-0102 | 1500 | Si, coincide | Enviado de otra CM, excluido |
| 103 | CM-MDZ-03 → CM-BA-01 | Enviado | P-0103 | 2100 | Si, coincide | Enviado de otra CM, excluido |
| 104 | CM-BA-01 → CM-CBA-01 | Enviado | P-0104 | 900 | Si, coincide | Enviado de la CMC, excluido |
| 114 | CM-CBA-01 → CM-BA-01 | Cerrado | P-0114 | 2600 | No | Cerrado, excluido |
| 113 | CM-CBA-01 → CM-ROS-02 | Creado | null | 1200 | No | Creado, excluido |
| 115 | CM-CBA-01 → CM-MDZ-03 | Recibido | P-0115 | 1800 | No | Recibido, excluido |
| 117 | CM-TUC-01 → CM-CBA-01 | De baja | null | 500 | No | De baja, excluido |
| 118 | CM-CBA-01 → CM-TUC-01 | De baja | null | 800 | No | De baja, excluido |
| 116 | CM-TUC-01 → CM-BA-01 | Creado | null | 700 | No | Sin Enviados de Tucumán (A1) |

Notas:
- Los numeros 105 a 109 de la API no se cargan. El 105 sale de CM-TUC-01 y, si se cargara como Enviado, rompería A1.
- Los bolsines 101, 102, 103, 104 y 110 tienen origen y destino iguales a la API. Si no coincidieran, la API responderia 404 y el sistema lo tomaria como A3 por error.
- El numero 111 no existe en la API. Es el unico caso de A3 de la defensa.
- Los numeros 112 y 119 en adelante quedan libres.

### Ubicaciones de referencia (API simulada)

| numeroBolsin | latitud | longitud | fechaHoraUltimaActualizacion |
|---|---|---|---|
| 101 | -31.4201 | -64.1888 | 2026-03-07T12:30:00 |
| 110 | -31.4167 | -64.1833 | 2026-03-07T12:52:09 |

Las ubicaciones no se guardan en la base. Las devuelve la API en cada consulta.

## 6. Historial de CambioEstado

Cada bolsin tiene una fila de `CambioEstado` por estado recorrido. Solo una fila por bolsin tiene `fechaHoraFin` nula (cambio actual). El cambio actual es el unico que cuenta para `sosActual()` y `sosEnviado()`.

Fechas en 2026.

| Bolsin | Cadena (estado, fechaHoraInicio → fechaHoraFin) |
|---|---|
| 101, 102, 103, 104, 110, 111 | Creado (20/11 09:00 → 20/11 17:30), Cerrado (20/11 17:30 → 21/11 08:05), Enviado (21/11 08:05 → actual) |
| 114 | Creado (20/11 09:00 → 20/11 17:30), Cerrado (20/11 17:30 → actual) |
| 115 | Creado (20/11 09:00 → 20/11 17:30), Cerrado (20/11 17:30 → 21/11 08:05), Enviado (21/11 08:05 → 22/11 10:00), Recibido (22/11 10:00 → actual) |
| 113 | Creado (24/11 09:00 → actual) |
| 116 | Creado (24/11 10:00 → actual) |
| 117 | Creado (19/11 09:00 → 19/11 12:00), De baja (19/11 12:00 → actual) |
| 118 | Creado (22/11 09:00 → 23/11 11:00), De baja (23/11 11:00 → actual) |

Regla de carga: `fechaHoraInicio` del cambio siguiente es igual a `fechaHoraFin` del anterior. El cambio actual tiene `fechaHoraFin` nula.

## 7. Escenarios para la defensa

| Escenario | Usuario | Accion | Resultado esperado |
|---|---|---|---|
| Principal | EB Córdoba 1 | Seguimiento completo | Enviados 101 y 111. Marcador para 101. 111 en `sinUbicacion` (A3). |
| Principal limpio | EB Córdoba 2 | Seguimiento completo, hasta el correo | Solo 110, con ubicacion. Correo a GCM Rosario. |
| A1 | EB Tucumán | Seguimiento | 404 `{codigo: "SIN_BOLSINES_ENVIADOS"}`. No hay Enviados de CM-TUC-01. |
| A2 | EB Córdoba 1 | Filtro por precinto `P-0111` en el frontend | Muestra solo 111. Sin llamada al backend. Con `P-9999`, sin resultados. |
| A3 | EB Córdoba 1 | Seleccionar 111 | Sin marcador. La sesion queda abierta. |
| A4 | Cualquiera | DELETE del caso de uso | 204. No se envia correo. |
| A5 | Cualquiera | Confirmacion con `confirma: false` | 200, `notificado: false`. No se llama a `enviarMailGCM`. |
| Filtro de exclusion | EB Córdoba 1 | Seguimiento | No aparecen 102, 103, 104 (Enviados de otras CM) ni 113, 114, 115, 117, 118 (otros estados). |

## 8. Decisiones y supuestos

1. **EB Córdoba 2 con el bolsin 110.** Aprobado. Da un escenario principal completo sin A3.
2. **Nombre de CM-CBA-02:** "Comisión Médica Córdoba 2". Aprobado, sujeto a cambio por el equipo.
3. **CM-BA-01 como CMC:** supuesto a partir del codigo, aprobado.
4. **Emails y contrasenas:** dominio `example.test`, contrasena en `.env` (`SEED_PASSWORD_DEV`). Aprobado.

## 9. Procedimiento de carga (`backend/data/seed.py`)

1. Crear el esquema con `create_all` sobre la base de `DATABASE_URL`.
2. Si ya hay filas en `Estado`, no hacer nada (idempotente). Con `--reset`, borrar y recargar. Solo para desarrollo.
3. Insertar en este orden: `Estado`, `Rol`, `ComisionMedica`, `Usuario` (con hash de `SEED_PASSWORD_DEV`), `Empleado`, `Bolsin`, `CambioEstado`. Los bolsines referencian las CM por codigo, que el script resuelve a id.
4. Verificaciones al final:
   - Un solo `CambioEstado` con `fechaHoraFin` nula por bolsin.
   - Origen y destino de 101, 102, 103, 104 y 110 iguales a la API.
   - 111 no tiene equivalente en la API (escenario A3).
5. Ejecucion: `docker compose exec backend python -m data.seed`, o localmente desde la raiz con `PYTHONPATH=backend python -m data.seed`.
