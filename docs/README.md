# Documentacion del TP Bolsines (CU 36)

Sistema "Bolsines" - UTN FRC, Diseno de Sistemas de Informacion, PPAI 2026, grupo 3K7 (Grupo 7).

Este directorio reune el analisis, el diseno y el plan de implementacion del caso de uso **CU 36 "Consultar seguimiento de bolsines"**, resuelto con el patron **Iterator** (Gamma). Para las reglas permanentes del proyecto (stack, arquitectura, nombres y flujo de trabajo) ver `AGENTS.md` en la raiz.

## Indice

| Documento | Contenido |
|---|---|
| `00-contexto.md` | Dominio (bolsines, remitos, CM, estados), CU 36 completo (flujo y alternativos A1 a A5) y entregables del TP. |
| `01-arquitectura.md` | Diagrama de capas, clase -> carpeta/archivo, justificacion, estado del CU en HTTP, reglas de dependencias y arbol de archivos. |
| `02-modelo-datos.md` | Entidades del CU 36 con tipos, claves, relaciones y metodos; mapeo a SQLModel; diagrama ER; inconsistencias. |
| `03-patron-iterator.md` | Identificacion del patron: problema, justificacion, participantes, antes/despues y guia de defensa. |
| `04-vista-estatica.md` | Diagrama de clases de diseno (embebido), especificacion por clase (tipos y visibilidad) y decisiones. |
| `05-vista-dinamica.md` | Diagramas de secuencia de diseno: parte rediseñada por el Iterator y flujo completo; Entrega 1 vs Entrega 2; alternativos. |
| `06-integraciones.md` | GPS Tracker (API de la catedra), manejo de errores (A3), Google Maps, correo (CU 31), mocks y configuracion. |
| `07-api-rest.md` | Endpoints FastAPI del CU 36, schemas Pydantic, autenticacion, alternativos -> respuestas y ejemplos JSON. |
| `08-datos-semilla.md` | Set de datos para la defensa: estados, roles, CM, usuarios, bolsines, historial de estados y procedimiento de carga. |
| `09-implementacion-y-pruebas.md` | Detalles de implementacion, criterios -> evidencia, integracion GPS real, plan pytest, checklist y orden de implementacion. |
| `99-decisiones-y-dudas.md` | Bitacora de decisiones y dudas (fecha / duda / decision tomada). |
| `diagramas/clases-diseno.puml` | Diagrama de clases de diseno (PlantUML). |
| `diagramas/secuencia-cu36-iterator.puml` | Secuencia de la parte rediseñada por el Iterator. |
| `diagramas/secuencia-cu36-completo.puml` | Secuencia del flujo completo, con la porcion reemplazada marcada. |
| `referencias/` | Documentos fuente del TP (ERS, modelo de dominio, descripcion del caso, Entregas 1 y 2). Solo lectura. |

## Orden de lectura

Primera lectura (contexto y diseno):

1. `00-contexto.md`
2. `03-patron-iterator.md`
3. `04-vista-estatica.md`
4. `05-vista-dinamica.md`
5. `02-modelo-datos.md`

Implementacion:

6. `01-arquitectura.md`
7. `06-integraciones.md`
8. `07-api-rest.md`
9. `08-datos-semilla.md`
10. `09-implementacion-y-pruebas.md`

Consulta permanente: `99-decisiones-y-dudas.md` (toda duda resuelta o pendiente esta ahi).

## Resumen de diseno (10 lineas)

1. El CU 36 permite al Encargado de Bolsines ver en un mapa los bolsines **Enviados** de su Comision Medica y notificar su ubicacion al Gerente de la CM destino.
2. El backend es FastAPI (Python 3.12) con SQLModel sobre SQLite; el frontend es Vite + React + TypeScript.
3. La logica de negocio vive en `models` (entidades con metodos) y en `services` (`GestorBuscarBolsines`); `routes` solo traduce HTTP.
4. El patron **Iterator** separa el recorrido de la coleccion: `GestorBuscarBolsines` es el `IAgregado` y `IteradorBolsin` el `IIterador` concreto.
5. El filtro (CM origen del usuario logueado y estado Enviado) vive en `IteradorBolsin.comprobarFiltro()`; `primero()` y `siguiente()` avanzan hasta el proximo elemento valido.
6. La cadena de estado es `Bolsin.sosEnviado()` -> `CambioEstado.sosActual()` -> `CambioEstado.sosEnviado()` -> `Estado.esEnviado()`.
7. El GPS se consulta por bolsin a traves de `InterfazGPSTracker` (adaptador XTR-4500L); un 404 del GPS se traduce a `UbicacionNoDisponibleError` y al alternativo A3.
8. El backend devuelve `MapaBolsines` (centro, zoom, marcadores); el frontend dibuja el mapa con Google Maps.
9. El estado del caso de uso vive en memoria por `idCU` (`gestores_activos`), lo que exige un unico worker de uvicorn.
10. Los alternativos A1 (sin bolsines), A3 (GPS sin ubicacion), A4 (cancelar) y A5 (no enviar correo) estan cubiertos por el diseno, la API y el plan de pruebas.

## Ejecucion rapida

```
pytest                                  # desde la raiz; pytest.ini apunta a backend/
uvicorn main:app --app-dir backend --port 8020
docker compose up --build               # backend 8020 + frontend 3020
```
