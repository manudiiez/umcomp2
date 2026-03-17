# Funcionalidades por Entidad

## Cliente (`cliente.py`)

- Parsear argumentos por línea de comandos con `argparse`:
  - `--host`: dirección IP del servidor (default: `localhost`)
  - `--port`: puerto del servidor (default: `9000`)
  - `--file`: ruta de la imagen a enviar (obligatorio)
  - `--tipo`: tipo de procesamiento, `portal` o `instagram` (obligatorio)
  - `--precio`: precio de la propiedad (requerido para `instagram`)
  - `--direccion`: dirección de la propiedad (requerido para `instagram`)
  - `--ambientes`: cantidad de ambientes (requerido para `instagram`)
- Conectarse al servidor mediante un socket TCP.
- Serializar y enviar un encabezado JSON con la metadata de la propiedad.
- Enviar el contenido binario de la imagen.
- Recibir y mostrar la respuesta del servidor (job_id o ruta de imagen procesada).

## Servidor (`servidor.py`)

- Escuchar conexiones entrantes en un puerto TCP usando `asyncio`.
- Aceptar múltiples clientes de forma concurrente y no bloqueante.
- Recibir el encabezado JSON y el contenido binario de cada imagen.
- Guardar la imagen recibida en un directorio temporal (`/tmp/uploads/`).
- Publicar una tarea de procesamiento en la cola Celery/Redis con la metadata y ruta de la imagen.
- Devolver al cliente el `job_id` asignado a su tarea.
- Comunicarse con el proceso notificador mediante una `multiprocessing.Queue` (IPC).
- Notificar al cliente cuando su imagen ha sido procesada (si mantiene la conexión abierta).

## Workers Celery (`tasks.py`)

- Consumir tareas de la cola Redis.
- Para tipo `portal`:
  - Abrir la imagen con Pillow.
  - Superponer el logo de la inmobiliaria como marca de agua semitransparente.
  - Guardar la imagen procesada en `/outputs/portal/`.
- Para tipo `instagram`:
  - Abrir la imagen con Pillow.
  - Aplicar una plantilla visual (marco, colores de la inmobiliaria).
  - Insertar texto con precio, dirección y cantidad de ambientes.
  - Guardar la imagen procesada en `/outputs/instagram/`.
- Registrar en la base de datos SQLite: job_id, tipo, ruta de salida, timestamp, estado.
- Comunicar el resultado al proceso notificador del servidor.

## Proceso Notificador (`notificador.py`)

- Ejecutarse como proceso separado usando `multiprocessing.Process`.
- Escuchar resultados completados provenientes de los workers.
- Comunicar al servidor principal el resultado de cada job mediante una `multiprocessing.Queue`.

## Base de Datos (SQLite)

- Tabla `jobs`: almacena `job_id`, `tipo`, `archivo_entrada`, `archivo_salida`, `estado`, `timestamp`.
- Permite consultar el historial de imágenes procesadas.

## Broker de tareas (Redis)

- Actúa como intermediario entre el servidor y los workers Celery.
- Gestiona la cola de tareas pendientes y los resultados.