import asyncio
import argparse
from functions import procesar_imagen, convertir_a_grises

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

    imagen_gris = await convertir_a_grises(data)
    writer.write(imagen_gris)
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def iniciar_servidor(ip, port):
    server = await asyncio.start_server(manejar_cliente, ip, port)
    addr = server.sockets[0].getsockname()
    print(f'Servidor corriendo en {addr}')

    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            print("Servidor detenido.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Servidor de procesamiento de imágenes asíncrono con sockets")
    parser.add_argument('-i', '--ip', type=str, required=True, help='Dirección IP para escuchar')
    parser.add_argument('-p', '--port', type=int, required=True, help='Puerto para escuchar')
    args = parser.parse_args()

    asyncio.run(iniciar_servidor(args.ip, args.port))