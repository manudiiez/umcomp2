# Funcionalidades por Entidad — RealtyEdit

## 1. Cliente (`client.py`)

**Propósito:** Interfaz de línea de comandos que permite al usuario enviar una imagen al servidor para su procesamiento.

**Funcionalidades:**
- Parsear argumentos de línea de comandos con `argparse`:
  - `--image` : ruta a la imagen de entrada (obligatorio)
  - `--type` : tipo de edición, `watermark` o `template` (obligatorio)
  - `--location` : ubicación de la propiedad, ej. `"Mendoza, Argentina"` (requerido para `template`)
  - `--property-type` : tipo de propiedad, ej. `"Casa"`, `"Departamento"` (requerido para `template`)
  - `--condition` : condición, `"Venta"` o `"Alquiler"` (requerido para `template`)
  - `--output` : ruta de salida para la imagen procesada (opcional, default: `output_<nombre_original>`)
  - `--host` : IP del servidor (default: `localhost`)
  - `--port` : puerto del servidor (default: `9000`)
- Validar que los argumentos requeridos para cada tipo de edición estén presentes.
- Leer la imagen del disco en modo binario.
- Construir el payload: imagen (bytes) + metadatos (JSON).
- Establecer conexión TCP al servidor.
- Enviar el payload.
- Esperar y recibir la imagen procesada.
- Guardar la imagen procesada en disco.
- Mostrar mensajes de estado al usuario.

**Ejemplo de uso:**
```bash
# Marca de agua para portal
python client.py --image foto_casa.jpg --type watermark

# Overlay para Instagram
python client.py --image foto_depto.jpg --type template \
  --location "Godoy Cruz, Mendoza" \
  --property-type "Departamento" \
  --condition "Alquiler"
```

---

## 2. Servidor TCP (`server.py`)

**Propósito:** Punto de entrada del sistema. Acepta conexiones de múltiples clientes de forma concurrente.

**Funcionalidades:**
- Crear y bindear un socket TCP al puerto configurado.
- Escuchar conexiones entrantes.
- Por cada nueva conexión, crear un proceso hijo con `fork()` para manejarla de forma aislada y concurrente.
- En el proceso hijo:
  - Usar I/O asíncrono (`asyncio` + `StreamReader`/`StreamWriter` o `select()`) para recibir el payload del cliente sin bloquear.
  - Escribir el trabajo recibido al Dispatcher a través del extremo de escritura de `os.pipe()`.
  - Esperar el resultado del procesamiento (via Redis result backend a través del job ID).
  - Enviar la imagen resultante de vuelta al cliente.
  - Cerrar la conexión.
- En el proceso padre:
  - Cerrar el descriptor de socket del hijo.
  - Hacer `waitpid` no bloqueante para limpiar procesos zombies.
- Loggear cada conexión entrante y su resultado.

---

## 3. Dispatcher (`dispatcher.py`)

**Propósito:** Proceso intermediario que desacopla la recepción del trabajo de su ejecución.

**Funcionalidades:**
- Leer continuamente del extremo de lectura del `os.pipe()`.
- Por cada trabajo recibido:
  - Deserializar el payload (imagen bytes + metadatos JSON).
  - Guardar la imagen temporalmente en disco (en `/tmp/realty_edit/`).
  - Registrar el trabajo en la base de datos SQLite con estado `PENDING`.
  - Enviar la tarea a Celery con `process_image.delay(job_id, image_path, job_type, metadata)`.
- Loggear la recepción y encolado de cada trabajo.

---

## 4. Workers Celery (`tasks.py`)

**Propósito:** Ejecutar el procesamiento de imagen de forma paralela y distribuida.

**Funcionalidades:**
- Definir las tareas Celery:
  - `process_image(job_id, image_path, job_type, metadata)`: función principal despachada por Celery.
- Según `job_type`:
  - `watermark`:
    - Abrir la imagen con Pillow.
    - Crear/cargar la imagen de marca de agua.
    - Centrar y componer la marca de agua sobre la imagen original con transparencia ajustable.
    - Guardar el resultado.
  - `template`:
    - Abrir la imagen con Pillow.
    - Cargar la plantilla visual (PNG con transparencia).
    - Superponer la plantilla sobre la imagen.
    - Escribir los textos con `ImageDraw` y `ImageFont`:
      - Ubicación de la propiedad.
      - Tipo de propiedad.
      - Condición (Venta/Alquiler).
    - Guardar el resultado.
- Actualizar el estado del job en la base de datos SQLite (`PROCESSING` → `DONE` o `ERROR`).
- Retornar la ruta de la imagen procesada.

---

## 5. Base de Datos (`db.py`)

**Propósito:** Persistir el historial de trabajos procesados.

**Funcionalidades:**
- Crear tabla `jobs` si no existe (SQLite, con `sqlite3`).
- Insertar nuevos registros con estado `PENDING`.
- Actualizar estado del job (`PENDING` → `PROCESSING` → `DONE`/`ERROR`).
- Registrar `completed_at` y `output_path` al finalizar.
- Proveer función de consulta por `job_id`.

**Esquema:**
```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    client_ip TEXT,
    job_type TEXT,          -- 'watermark' o 'template'
    location TEXT,
    property_type TEXT,
    condition TEXT,
    status TEXT,            -- PENDING | PROCESSING | DONE | ERROR
    created_at TIMESTAMP,
    completed_at TIMESTAMP,
    input_path TEXT,
    output_path TEXT
);
```

---

## 6. Módulo de Procesamiento de Imágenes (`image_processor.py`)

**Propósito:** Lógica de edición de imágenes, usada internamente por los workers.

**Funcionalidades:**
- `apply_watermark(image_path, output_path, watermark_path, opacity)`: compone la marca de agua centrada.
- `apply_template(image_path, output_path, template_path, metadata)`: superpone la plantilla y escribe los textos.
- Manejo de errores de imagen (formato no soportado, imagen corrupta).

---

## Resumen de Comunicación entre Entidades

```
Cliente ──TCP──► Servidor
                  └─fork()──► Proceso Hijo
                                └─os.pipe()──► Dispatcher
                                                └─Celery──► Worker A
                                                └─Celery──► Worker B
                                                └─Celery──► Worker N
                                                └─SQLite (registro)
                              Proceso Hijo ◄──Redis result──Worker
Cliente ◄──TCP── Proceso Hijo
```