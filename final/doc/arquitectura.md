# Arquitectura del sistema

## Diagrama 
```mermaid
graph LR
    C1["Cliente 1\n--perfil portal"] -->|TCP socket| S
    C2["Cliente 2\n--perfil instagram"] -->|TCP socket| S
    CN["Cliente N"] -->|TCP socket| S

    S["Servidor\nasyncio"] -->|multiprocessing.Queue| Q["Cola de tareas\nIPC"]

    Q -->|job| WP["Worker portal\nMarca de agua + resize"]
    Q -->|job| WI["Worker instagram\nPlantilla + crop"]

    WP -->|imagen procesada| S
    WI -->|imagen procesada| S

    S -->|historial| DB["Base de datos\nSQLite"]
```

## Componentes y conectividad

```
[Cliente 1] ──┐
[Cliente 2] ──┤── TCP socket ──→ [Servidor asyncio] ──→ [Queue IPC] ──→ [Worker portal]
[Cliente N] ──┘                         ↑                               [Worker instagram]
                                        └─────── imagen procesada ───────────┘
                                        ↓
                                  [Base de datos SQLite]
```

## Mecanismos utilizados

| Mecanismo       | Dónde se usa                 | Por qué                                      |
| --------------- | ---------------------------- | -------------------------------------------- |
| asyncio         | Servidor: manejo de clientes | I/O bound, escala sin overhead de threads    |
| multiprocessing | Workers de procesamiento     | CPU bound, necesita paralelismo real         |
| Queue (IPC)     | Servidor → Workers           | Desacopla recepción de procesamiento         |
| TCP Sockets     | Cliente ↔ Servidor           | Comunicación confiable, orientada a conexión |
| SQLite          | Servidor → DB                | Historial liviano, sin dependencias extras   |
