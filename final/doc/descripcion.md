# Descripción de la Aplicación

# RealtyEdit — Sistema de Edición de Imágenes para Inmobiliaria

## Descripción de la Aplicación

RealtyEdit es una aplicación cliente-servidor para procesamiento automático de imágenes inmobiliarias. El cliente envía imágenes junto con metadatos de la propiedad (ubicación, tipo, condición) y el tipo de edición deseada. El servidor recibe las solicitudes de múltiples clientes de forma concurrente, encola los trabajos de procesamiento y los distribuye entre workers especializados que realizan la edición.

Se soportan dos tipos de edición:

- **Portal** (`watermark`): Se aplica una marca de agua centrada sobre la imagen.
- **Instagram** (`template`): Se superpone una plantilla visual y se escriben sobre la imagen los datos de la propiedad (ubicación, tipo y condición).

El flujo general es: el cliente envía la imagen + parámetros → el servidor la recibe y encola el trabajo → un worker toma el trabajo y procesa la imagen → el resultado se devuelve al cliente.

---

## Descripción Técnica Detallada

### El cliente hace:
- Parseo de argumentos por línea de comandos (`argparse`): ruta de imagen, tipo de edición (`watermark` o `template`), y metadatos de la propiedad.
- Conexión al servidor vía TCP socket.
- Envío de la imagen (binario) + metadatos (JSON) al servidor.
- Espera y recepción de la imagen procesada.
- Guardado del resultado en disco.

### El servidor hace:
- Escucha conexiones entrantes en un socket TCP.
- Por cada cliente que se conecta, spawnea un proceso hijo (via `fork`) para atender esa conexión de forma concurrente.
- El proceso hijo recibe la imagen y la encola a través de un Pipe IPC hacia el proceso Dispatcher.
- Usa I/O asíncrono (`asyncio` o `select`) para no bloquear mientras espera datos del cliente.

### El Dispatcher hace:
- Recibe trabajos del socket server via Pipe (IPC).
- Los encola en una `Queue` de Celery (broker Redis).
- Actúa como intermediario desacoplando la recepción de la ejecución.

### Los Workers (Celery) hacen:
- Toman tareas de la cola de Celery.
- Ejecutan el procesamiento de imagen:
  - `watermark`: Usa Pillow para componer la marca de agua centrada.
  - `template`: Usa Pillow para superponer la plantilla y escribir los textos con los datos de la propiedad.
- Guardan el resultado y notifican al servidor.

### El servidor responde:
- Una vez procesada la imagen, el proceso hijo envía el resultado de vuelta al cliente por el socket TCP.

---

## Uso de Cada Herramienta de la Materia

| Requisito                          | Implementación en RealtyEdit                                                  |
|------------------------------------|-------------------------------------------------------------------------------|
| Sockets con clientes múltiples     | Servidor TCP con `fork()` por cada cliente entrante                           |
| IPC                                | `Pipe` (os.pipe) entre proceso hijo del servidor y el Dispatcher              |
| Asincronismo de I/O                | `asyncio` o `select()` en el servidor para leer datos sin bloquear            |
| Cola de tareas distribuidas        | Celery + Redis broker para encolar y distribuir trabajos a los workers        |
| Parseo de argumentos CLI           | `argparse` en el cliente: `--image`, `--type`, `--location`, `--property-type`, `--condition` |

### Opcionales incorporados:
- **Docker**: Contenedor para el servidor + workers + Redis.
- **Base de datos (SQLite/PostgreSQL)**: Registro del historial de imágenes procesadas (cliente, tipo, timestamp, path resultado).
- **Celery**: Workers distribuidos para el procesamiento paralelo de imágenes.