# 00 - Contexto del TP Bolsines

Grupo 7 - 3K7 - PPAI 2026 (UTN FRC, Diseno de Sistemas de Informacion).

## 1. Dominio (resumen)

Un organismo controlador (sede central en CABA) envia documentacion fisica entre Comisiones Medicas (CM): CMJ (jurisdiccionales, mas de 80) y la CMC (central, en CABA). El envio se hace en **bolsines** (bolsas de tela con precinto) junto con **remitos**.

- **Documentacion:** se registra con tipo de documento, fecha de pase, CM origen, asunto y archivos. Tiene numero secuencial unico generado por el sistema.
- **Remito:** agrupa documentacion dirigida a **una sola CM destino**. Se genera un remito por cada CM destino.
- **Bolsin:** contiene remitos de **una unica CM destino**. Datos: fecha, CM origen, CM destino, peso (gramos), nro. de precinto, remitos que contiene y numero secuencial unico.
- **Precinto:** dispositivo numerado que cierra el bolsin. Si se reabre para modificarlo, se coloca un precinto nuevo y se actualiza el nro. en el sistema.
- **Encargado de Bolsines (EB):** responsable de armar, cerrar, retirar, recibir y seguir los bolsines.
- **Gerente de CM (GCM):** recibe notificaciones y genera reportes.

### Estados (Entrega 1, maquina de estados de Bolsin)

Creado -> Cerrado -> Enviado -> Recibido. Desde Creado o Cerrado puede pasar a De baja. Cerrado puede reabrirse a Creado.

Estados de Remito y Documentacion (ERS): Creado / Registrada, En bolsin saliente, En bolsin enviado, Recibido y aceptado (parcial), Cancelado, etc.

Para el CU 36 solo importa el estado **Enviado** del bolsin.

## 2. Caso de uso 36: Consultar seguimiento de bolsines

**Actor principal:** Encargado de Bolsines (EB).
**Actores secundarios:** GPS Tracker, Servidor Google Maps.
**Objetivo:** consultar en un mapa la ubicacion de los bolsines en movimiento entre CM.
**Prioridad:** Alta. **Complejidad:** Mediana. **Tipo:** Concreto.

### Flujo principal

1. EB selecciona la opcion para consultar la ubicacion de uno o varios bolsines.
2. Sistema busca y muestra la CM del usuario logueado.
3. Sistema busca los bolsines en estado **Enviado** cuya CM origen es la CM del usuario logueado.
4. Sistema solicita al GPS Tracker los datos de localizacion de los bolsines.
5. Sistema recibe del GPS Tracker la localizacion de cada bolsin.
6. Sistema muestra sobre un mapa la posicion de los bolsines, con opcion de seleccionar un bolsin del mapa o filtrar por nro. de precinto o CM destino.
7. EB selecciona un bolsin del mapa.
8. Sistema consulta si desea enviar un correo al Gerente de CM destino con la ubicacion.
9. EB confirma el envio del correo.
10. Sistema busca el correo del GCM destino.
11. Sistema incluye el CU 31 "Notificar ubicacion de bolsin" (numero de bolsin, fecha y hora de ultima actualizacion, coordenadas). Fin del caso de uso.

### Flujos alternativos

- **A1:** No se encuentran bolsines en estado Enviado.
- **A2:** No se encuentra bolsin con el nro. de precinto ingresado.
- **A3:** El GPS Tracker no pudo informar la ubicacion del bolsin.
- **A4:** El EB cancela la ejecucion del caso de uso.
- **A5:** El EB no selecciona la opcion de enviar correo electronico.

### Modelo de GPS (ERS, Obs. 1)

Hay tres modelos posibles, pero la Entrega 2 y el diagrama de secuencia usan **XTR-4500L**, con endpoint `getBolsinLocation()`: recibe API Key, nro. de bolsin (entero) y codigo de CM origen (String); devuelve un JSON en texto con numero, latitud, longitud y fecha/hora de ultima actualizacion.

## 3. Alcance de implementacion

- Patron **Iterator** (Gamma) para la busqueda de bolsines Enviados de la CM del usuario logueado (`IAgregado`, `IIterador`, `IteradorBolsin`, `GestorBuscarBolsines`).
- Entidades: `Bolsin`, `CambioEstado`, `Estado`, con sus metodos de negocio.
- Integracion real con la API del GPS Tracker (detras de `backend/integrations/`).
- Notificacion por correo al GCM destino (detras de `backend/integrations/`).
- Visualizacion en mapa: el backend devuelve `MapaBolsines` (centro, zoom y marcadores) en la respuesta del CU 36. El frontend renderiza el mapa con la libreria de Google Maps (`VITE_GOOGLE_MAPS_API_KEY`). El backend no llama a la API de Google Maps.

## 4. Entregables del TP (Entrega 2 y siguientes)

1. **Identificacion del patron implementado:** descripcion del problema, intencion, justificacion y tabla de participantes (rol, clase, responsabilidad).
2. **Vista estatica de la realizacion del CU:** diagrama de clases de diseno con tipos de datos, retornos, parametros y visibilidad (publica/privada) de la estructura resultante del patron.
3. **Vista dinamica de la realizacion del CU:** diagrama de secuencia de la parte rediseñada por el Iterator (el resto se mantiene igual que en analisis).
4. **Detalles de implementacion:** codigo en `backend/` (`index.py`, `models/`, `services/`, `routes/`, `utils/`, `integrations/`, etc.) siguiendo `AGENTS.md`, y en `frontend/`.
5. **Criterios de correccion:**
   - Iterator visible y usado por el gestor.
   - Filtro (CM origen y estado Enviado) dentro de `comprobarFiltro()`.
   - Logica de negocio en `models`/`services`; `routes` sin logica.
   - Nombres coincidentes con los diagramas.
   - Alternativos A1..A5 cubiertos por pruebas.
   - Pruebas pytest pasando.
6. **Integracion con la API real del GPS Tracker:** adaptador en `backend/integrations/`, configuracion por variables de entorno, prueba con fake para CI.

## 5. Documentos fuente

Estan en `docs/referencias/`:
- Modelo de dominio V1.1
- Descripcion del caso V1.1
- ERS V1.2
- Entrega 1 (analisis)
- Entrega 2 (diseno)

Inconsistencias y decisiones: ver `docs/99-decisiones-y-dudas.md`.
