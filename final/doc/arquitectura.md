# Arquitectura del Sistema

## Diagrama general

```mermaid
flowchart TD
    C1["Cliente CLI\n--tipo portal --file casa.jpg"]
    C2["Cliente CLI\n--tipo instagram --file depto.jpg"]

    SRV["Servidor Principal\nasyncio.start_server()"]

    NOTIF["Proceso Notificador\nmultiprocessing.Process"]
    Q["multiprocessing.Queue\nIPC"]

    REDIS["Redis\nBroker Celery"]

    WA["Worker A\nCelery — tipo portal\nPillow: marca de agua"]
    WB["Worker B\nCelery — tipo instagram\nPillow: plantilla visual"]

    DB["SQLite\npropimager.db"]
    OUT["Disco\n/outputs/portal/\n/outputs/instagram/"]

    C1 -->|"Socket TCP\nJSON + bytes imagen"| SRV
    C2 -->|"Socket TCP\nJSON + bytes imagen"| SRV

    SRV -->|"celery.delay()"| REDIS
    REDIS --> WA
    REDIS --> WB

    WA -->|"resultado"| NOTIF
    WB -->|"resultado"| NOTIF
    NOTIF -->|"Queue.put()"| Q
    Q -->|"Queue.get()"| SRV
    SRV -->|"job_id / ruta lista"| C1
    SRV -->|"job_id / ruta lista"| C2

    WA --> OUT
    WB --> OUT
    WA --> DB
    WB --> DB
```

## Diagrama de secuencia

```mermaid
sequenceDiagram
    participant C as Cliente CLI
    participant S as Servidor (asyncio)
    participant R as Redis
    participant W as Worker Celery
    participant N as Notificador (multiprocessing)

    C->>S: Socket TCP — header JSON + bytes imagen
    S->>S: Guarda imagen en /tmp/uploads/
    S->>R: celery.delay(job_id, tipo, ruta, metadata)
    S-->>C: Responde job_id

    R->>W: Entrega tarea
    W->>W: Procesa imagen con Pillow
    W->>W: Guarda en /outputs/ y registra en SQLite
    W->>N: Publica resultado en Redis backend

    N->>N: Detecta job finalizado
    N->>S: Queue.put({job_id, ruta_salida})
    S->>C: Notifica imagen lista + ruta
```

## Nodos y mecanismos de IPC

| Nodo | Tecnología | Rol |
|---|---|---|
| Cliente CLI | `socket`, `argparse` | Envía imagen y metadata |
| Servidor principal | `asyncio` | Acepta N clientes concurrentes, encola tareas |
| Redis | Redis | Broker de tareas Celery |
| Workers | `Celery`, `Pillow` | Procesan imágenes en paralelo |
| Proceso Notificador | `multiprocessing.Process` | Detecta resultados y los pasa por IPC |
| `multiprocessing.Queue` | IPC | Comunicación notificador → servidor |
| Base de datos | SQLite | Persistencia de jobs y metadata |