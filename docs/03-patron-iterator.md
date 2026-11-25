# 03 - Patron Iterator (CU 36)

## 1. Identificacion del patron implementado

**Descripcion del problema que se propone resolver, con breve justificacion.**

**Patron seleccionado:** Iterator (patron de comportamiento de Gamma).

**Intencion:** proporcionar una forma de acceder secuencialmente a los elementos de un objeto agregado sin exponer su representacion interna.

**Problema:** en el diseno de analisis del CU 36, `GestorBuscarBolsines` resuelve la busqueda de los bolsines en estado Enviado cuya CM origen es la CM del usuario logueado. Para eso recorre el mismo la coleccion de bolsines y consulta a cada uno `esTuCMOrigen()` y `sosEnviado()`. El gestor cumple dos roles a la vez: coordina el caso de uso y recorre y filtra datos.

**Justificacion:**

**1. Acceso a la coleccion**
- *Problema:* el gestor conoce como esta almacenada la coleccion de bolsines y como recorrerla.
- *Solucion:* el recorrido se delega en `IteradorBolsin`. El gestor solo usa `primero()`, `haFinalizado()`, `elementoActual()` y `siguiente()`, sin depender de la estructura interna de la coleccion.

**2. Responsabilidades del gestor**
- *Problema:* el gestor coordina el caso de uso y ademas recorre y filtra los bolsines.
- *Solucion:* el filtrado (CM origen igual a la CM del usuario logueado y estado Enviado) queda encapsulado en `comprobarFiltro()` del iterador. El gestor solo recibe los bolsines que cumplen el filtro.

**3. Reutilizacion del recorrido**
- *Problema:* otros casos de uso necesitan recorrer bolsines con otros criterios. Por ejemplo, el CU 28 (Registrar recepcion de bolsin) busca los bolsines enviados a la CM del usuario logueado, es decir, filtra por CM destino y no por CM origen.
- *Solucion:* el iterador recibe la coleccion y los filtros en `new(elementos, filtros)`, asi que el mismo recorrido puede reutilizarse cambiando solo los filtros.

**Nota:** en el CU 28 el filtro es por CM destino. `IteradorBolsin` lo resuelve con el mismo `comprobarFiltro()`, pasando filtros distintos. El CU 28 no se implementa en esta entrega.

## 2. Participantes

| Rol en el patron | Clase | Responsabilidad |
|---|---|---|
| Agregado | `IAgregado` (interfaz) | Declara `crearIterador()`. |
| Agregado concreto | `GestorBuscarBolsines` | Implementa `crearIterador()` y crea el `IteradorBolsin` con los bolsines y los filtros. |
| Iterador | `IIterador` (interfaz) | Declara `primero()`, `siguiente()`, `haFinalizado()`, `elementoActual()` y `comprobarFiltro()`. |
| Iterador concreto | `IteradorBolsin` | Recorre la coleccion de bolsines y devuelve los que cumplen el filtro. |

## 3. Antes / despues

**Antes (diseno de analisis, Entrega 1):** el gestor recorre y filtra.

```
GestorBuscarBolsines.obtenerBolsinesEnviados():
    bolsinesEnviados = []
    para cada bolsin en bolsines:
        si bolsin.esTuCMOrigen(codigoCMUsuario) y bolsin.sosEnviado():
            agregar bolsin a bolsinesEnviados
    devolver bolsinesEnviados
```

**Despues (diseno con Iterator, Entrega 2):** el gestor solo coordina. El recorrido y el filtro estan en el iterador.

```
GestorBuscarBolsines.obtenerCodigoBolsinesEnviados():
    iterador = crearIterador(bolsines, filtros=[codigoCMUsuario, ESTADO_ENVIADO])
    codigos = []
    iterador.primero()
    mientras no iterador.haFinalizado():
        codigos.agregar(iterador.elementoActual().getNumeroBolsin())
        iterador.siguiente()
    devolver codigos

IteradorBolsin.comprobarFiltro(filtros):
    devolver bolsin.esTuCMOrigen(filtros[0]) y bolsin.sosEnviado()
```

El gestor ya no llama a `esTuCMOrigen` ni a `sosEnviado`, y tampoco recorre la lista. Esa es la diferencia que hay que poder mostrar en la defensa.

## 4. Como se ve el patron en el codigo

| Participante | Archivo | Clase |
|---|---|---|
| Agregado | `backend/models/iterator/i_agregado.py` | `IAgregado` |
| Iterador | `backend/models/iterator/i_iterador.py` | `IIterador` |
| Iterador concreto | `backend/models/iterator/iterador_bolsin.py` | `IteradorBolsin` |
| Agregado concreto | `backend/services/gestor_buscar_bolsines.py` | `GestorBuscarBolsines` |

Relacion con las entidades: `IteradorBolsin` usa `Bolsin` (`backend/models/bolsin.py`) para llamar a `esTuCMOrigen()` y `sosEnviado()`. `Bolsin` no conoce al iterador.

Reglas que hacen visible el patron (`AGENTS.md` §6):
- `GestorBuscarBolsines` implementa `IAgregado` y expone `crearIterador()`.
- El gestor recorre solo con `primero()`, `haFinalizado()`, `elementoActual()` y `siguiente()`.
- El filtro vive en `comprobarFiltro()`, no en el gestor.
- No se agregan otros patrones que oculten al iterador (repositorios genericos, `Specification`, `Strategy` de filtros, fabricas adicionales).

### Guia de defensa oral (5 puntos)

1. **Senalar la interfaz del agregado:** mostrar `IAgregado` y decir que `GestorBuscarBolsines` la implementa con `crearIterador()`.
2. **Mostrar la creacion del iterador:** en el gestor, `crearIterador(bolsines, filtros)` devuelve un `IteradorBolsin`. Explicar que el gestor no sabe como esta almacenada la coleccion.
3. **Recorrer el bucle del gestor:** `primero()`, `haFinalizado()`, `elementoActual()`, `siguiente()`. Senalar que no hay un `for` sobre la lista.
4. **Mostrar `comprobarFiltro()`:** es el unico lugar donde estan `esTuCMOrigen()` y `sosEnviado()`. Explicar que los filtros se pasan en `new()`, y que por eso el CU 28 puede reutilizar el recorrido con otro criterio.
5. **Mostrar el resultado en la prueba:** `backend/tests/test_iterador_bolsin.py` verifica el filtro, y `backend/tests/test_gestor_buscar_bolsines.py` verifica que el gestor devuelve solo los codigos de bolsines Enviados de la CM del usuario logueado (flujo principal y alternativos A1 y A2).

---

**Notas:**
- El diagrama de clases de Entrega 2 declara `comprobarFiltro` en `IIterador` como publico. Se mantiene asi.
- `obtenerCodigoBolsinesEnviados()` devuelve codigos, segun la decision registrada. `crearIterador` recibe la coleccion de objetos `Bolsin`.
