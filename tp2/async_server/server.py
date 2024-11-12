import asyncio
import socket
import argparse
from .functions import convertir_a_grises
import pickle


async def manejar_cliente(reader, writer):
    data = b""
    while True:
        packet = await reader.read(4096)
        if not packet:
            break
        data += packet

    if not data:
        writer.close()
        await writer.wait_closed()
        return

    recibido = pickle.loads(data)
    imagen = recibido['imagen']
    factor_escala = recibido['factor_escala']
    imagen_gris = await convertir_a_grises(imagen)
    data = pickle.dumps({'imagen': imagen_gris, 'factor_escala': factor_escala})

    # Conectar con el segundo servidor para reducir el tamaño
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(("localhost", 9999))
        except ConnectionRefusedError:
            print("Error: No se pudo conectar al servidor de escalado en localhost:9999. Asegúrese de que el servidor de escalado esté en funcionamiento.")
            # Enviar mensaje de error al cliente
            mensaje_error = "Error: No se pudo conectar al servidor de escalado."
            writer.write(mensaje_error.encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return
        s.sendall(data)
        s.shutdown(socket.SHUT_WR)

        # Recibir la imagen reducida
        imagen_reducida = b""
        while True:
            packet = s.recv(4096)
            if not packet:
                break
            imagen_reducida += packet

    # Enviar la imagen reducida de vuelta al cliente original
    writer.write(imagen_reducida)
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def iniciar_servidor(ip, port):
    server = await asyncio.start_server(manejar_cliente, ip, port, family=socket.AF_UNSPEC)
    addr = server.sockets[0].getsockname()
    print(f'Servidor corriendo en {addr}')

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            print("Servidor detenido.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Tp2 - procesa imágenes | Servidor para convertir a escala de grises")
    parser.add_argument('-i', '--ip', type=str, required=True, help='Dirección IP para escuchar')
    parser.add_argument('-p', '--port', type=int, required=True, help='Puerto para escuchar')
    args = parser.parse_args()
    asyncio.run(iniciar_servidor(args.ip, args.port))
