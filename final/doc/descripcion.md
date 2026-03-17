# Descripción de la aplicación

Quiero armar una app cliente-servidor de procesamiento de imágenes orientada 
a una inmobiliaria. El cliente envía una imagen desde la línea de comandos 
indicando el perfil de destino (portal web o Instagram). El servidor recibe 
las conexiones de forma concurrente usando asyncio (I/O no bloqueante), 
encola cada imagen como un job, y workers especializados la procesan en 
paralelo según el perfil solicitado. Una vez procesada, el servidor devuelve 
la imagen al cliente que la envió.

- Se usa concurrencia en el servidor mediante asyncio para manejar múltiples 
  clientes simultáneos sin crear un thread por conexión, lo que permite 
  escalar a muchos usuarios (por ejemplo, múltiples inmobiliarias) sin 
  overhead excesivo.
- Se usa paralelismo en el procesamiento mediante workers como procesos 
  independientes (multiprocessing), ya que el procesamiento de imágenes 
  es CPU-intensivo y asyncio no es adecuado para ese tipo de carga.
- Las entidades servidor y workers se comunican de manera asincrónica 
  usando multiprocessing.Queue como mecanismo de IPC.
- El cliente parsea argumentos por línea de comandos (--imagen, --perfil, 
  --host, --puerto).