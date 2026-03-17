# Arquitectura del Sistema — RealtyEdit

## Diagrama de Nodos y Conectividad

```mermaid
flowchart TD
    CLI["🖥️ **CLIENTE** cli\nclient.py\n─────────────────\n--image foto.jpg\n--type watermark\n--location 'Mendoza'\n--property-type 'Casa'\n--condition 'Venta'"]

    SRV["⚙️ **SERVIDOR TCP** server.py\n─────────────────\nEscucha puerto 9000\nasyncio I/O no bloqueante"]

    H1["👶 Proceso Hijo #1\ncliente 1"]
    H2["👶 Proceso Hijo #2\ncliente 2"]
    HN["👶 Proceso Hijo #N\ncliente N"]

    DISP["📬 **DISPATCHER** dispatcher.py\n─────────────────\nLee del pipe read_fd\nEncola en Celery\nRegistra en SQLite"]

    WA["🔧 Worker A\nwatermark"]
    WB["🔧 Worker B\ntemplate"]
    WN["🔧 Worker N\nwatermark / template"]

    REDIS[("🗄️ **REDIS**\nbroker + result backend")]
    DB[("💾 **SQLite**\nhistorial de jobs")]

    CLI -->|"TCP Socket\nimagen + JSON\npuerto 9000"| SRV

    SRV -->|"fork()"| H1
    SRV -->|"fork()"| H2
    SRV -->|"fork()"| HN

    H1 -->|"os.pipe() write_fd"| DISP
    H2 -->|"os.pipe() write_fd"| DISP
    HN -->|"os.pipe() write_fd"| DISP

    DISP -->|"Celery task .delay()"| REDIS
    DISP -->|"INSERT job PENDING"| DB

    REDIS -->|"toma tarea"| WA
    REDIS -->|"toma tarea"| WB
    REDIS -->|"toma tarea"| WN

    WA -->|"result backend"| REDIS
    WB -->|"result backend"| REDIS
    WN -->|"result backend"| REDIS

    WA -->|"UPDATE DONE"| DB
    WB -->|"UPDATE DONE"| DB
    WN -->|"UPDATE DONE"| DB

    REDIS -->|"imagen procesada"| H1
    REDIS -->|"imagen procesada"| H2
    REDIS -->|"imagen procesada"| HN

    H1 -->|"TCP Socket resultado"| CLI
```

---

## Flujo de una Solicitud (Sequence Diagram)

```mermaid
sequenceDiagram
    actor Usuario
    participant CLI as Cliente CLI
    participant SRV as Servidor TCP
    participant HIJO as Proceso Hijo
    participant DISP as Dispatcher
    participant REDIS as Redis
    participant WORKER as Worker Celery
    participant DB as SQLite

    Usuario->>CLI: python client.py --image foto.jpg --type watermark
    CLI->>CLI: argparse — valida argumentos
    CLI->>SRV: TCP connect() puerto 9000
    SRV->>HIJO: fork()
    HIJO-->>SRV: proceso hijo creado
    CLI->>HIJO: send(imagen bytes + JSON metadata)
    Note over HIJO: asyncio — lee payload sin bloquear
    HIJO->>DISP: os.pipe() write_fd — escribe trabajo
    DISP->>DB: INSERT job status=PENDING
    DISP->>REDIS: process_image.delay(job_id, ...)
    Note over REDIS: encola tarea Celery
    REDIS->>WORKER: entrega tarea
    WORKER->>DB: UPDATE status=PROCESSING
    Note over WORKER: Pillow — aplica watermark o template
    WORKER->>DB: UPDATE status=DONE
    WORKER->>REDIS: guarda resultado (result backend)
    HIJO->>REDIS: result.get(job_id) — espera resultado
    REDIS-->>HIJO: imagen procesada (bytes)
    HIJO->>CLI: TCP send(imagen procesada)
    CLI->>CLI: guarda imagen en disco
    CLI-->>Usuario: Imagen guardada como output_foto.jpg
```

---

## Mecanismos de IPC — Vista Simplificada

```mermaid
flowchart LR
    subgraph Proceso_Padre["Proceso Padre (server.py)"]
        SRV["Servidor TCP\npuerto 9000"]
    end

    subgraph Proceso_Hijo["Proceso Hijo (fork)"]
        ASYNC["asyncio\nI/O no bloqueante"]
        PIPE_W["os.pipe()\nwrite_fd"]
    end

    subgraph Dispatcher["Proceso Dispatcher"]
        PIPE_R["os.pipe()\nread_fd"]
        CELERY_SEND["Celery\n.delay()"]
    end

    subgraph Workers["Workers Celery (paralelos)"]
        W1["Worker 1\nPillow"]
        W2["Worker 2\nPillow"]
    end

    CLI(["Cliente TCP"]) -->|TCP| SRV
    SRV -->|fork| ASYNC
    ASYNC --> PIPE_W
    PIPE_W -->|IPC| PIPE_R
    PIPE_R --> CELERY_SEND
    CELERY_SEND -->|Redis| W1
    CELERY_SEND -->|Redis| W2
    W1 -->|result backend| ASYNC
    W2 -->|result backend| ASYNC
    ASYNC -->|TCP| CLI
```

---

## Mecanismos Concurrentes y de Sincronización

| Mecanismo | Dónde se usa | Por qué |
|-----------|-------------|---------|
| `fork()` | Servidor por cada cliente | Manejo concurrente de múltiples clientes de forma aislada |
| `os.pipe()` | Proceso hijo → Dispatcher | IPC unidireccional para pasar el trabajo entre procesos |
| `asyncio` | Proceso hijo al leer del socket | I/O asíncrono para no bloquear esperando el payload |
| `Celery + Redis` | Dispatcher → Workers | Cola de tareas distribuida para paralelismo en el procesamiento |
| `Redis result backend` | Workers → Proceso hijo | Notificación del resultado procesado |
| `argparse` | Cliente CLI | Parseo y validación de argumentos de línea de comandos |