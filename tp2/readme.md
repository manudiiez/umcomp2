## Requerimientos

Para ejecutar este proyecto necesitas instalar las siguientes bibliotecas de Python:

- `asyncio`: Librería incluida en Python para operaciones asíncronas.
- `opencv-python`: Para el procesamiento de imágenes.
- `pickle`: Para la serialización de datos (incluida por defecto en Python).

## Ejecución del Proyecto

### 1. Ejecutar el Servidor de Escalado

```bash
python3 -m scale_server.server
```
Este servidor se ejecuta en el puerto 9999 de forma predeterminada.

### 2. Ejecutar el Servidor Asíncrono
```bash
python3 -m async_server.server -i 127.0.0.1 -p 8080
```

### 3. Ejecutar el Cliente
Una vez que ambos servidores están corriendo, puedes ejecutar el cliente para enviar una imagen:

```bash
python3 -m client.client -f imagen_xs.jpg -i 127.0.0.1 -p 8080 -s 0.5
```

## Imágenes de Prueba

En el repositorio se incluyen dos imágenes: una muy grande y otra pequeña. Estas imágenes están disponibles para realizar pruebas del funcionamiento del sistema.

```bash
python3 -m client.client -f imagen_xs.jpg -i 127.0.0.1 -p 8080 -s 0.5
```
```bash
python3 -m client.client -f imagen_xl.jpg -i 127.0.0.1 -p 8080 -s 0.2
```