# Entidades del sistema

## Cliente (`cliente.py`)
- Parsea argumentos CLI: --imagen, --perfil (portal/instagram), --host, --puerto.
- Establece conexión TCP con el servidor via socket asyncio.
- Serializa y envía la imagen en bytes junto con el perfil solicitado.
- Recibe la imagen procesada y la guarda localmente con sufijo del perfil.

## Servidor (`servidor.py`)
- Escucha conexiones entrantes en un puerto configurable via CLI.
- Acepta múltiples clientes de forma concurrente usando asyncio (un 
  coroutine por cliente, no un thread).
- Por cada imagen recibida, crea un job y lo coloca en la cola de tareas.
- Espera el resultado del worker correspondiente y lo devuelve al cliente.
- Registra cada trabajo en la base de datos (estado, timestamps).

## Cola de tareas (`multiprocessing.Queue`)
- Canal de IPC entre el servidor y los workers.
- Cada item contiene: imagen en bytes, perfil solicitado, ID de job.
- Desacopla la recepción de imágenes del procesamiento, permitiendo que 
  el servidor no se bloquee esperando que termine el worker.

## Workers (`worker.py`)
- Procesos independientes (multiprocessing.Process) que consumen jobs 
  de la cola de forma continua.
- Worker portal: aplica marca de agua con logo de la inmobiliaria y 
  redimensiona a las medidas estándar del portal web.
- Worker instagram: aplica plantilla con texto superpuesto (precio, 
  dirección, habitaciones) y realiza crop cuadrado.
- Al terminar, colocan la imagen procesada en una cola de resultados 
  para que el servidor la devuelva al cliente.

## Base de datos (`SQLite`)
- Guarda historial de trabajos: cliente origen, perfil solicitado, 
  fecha/hora, estado (pendiente / procesando / listo / error).