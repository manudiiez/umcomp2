import socket
import argparse
import cv2
import pickle
import time
import os
import ipaddress

def enviar_imagen(filepath, ip, port):
    start_time = time.time()
    if not os.path.exists(filepath):
        print(f"Error: La ruta de la imagen '{filepath}' no existe.")
        return
    imagen = cv2.imread(filepath)
    if imagen is None:
        print(f"Error: No se pudo leer la imagen en '{filepath}'. Verifique el archivo.")
        return
    imagen_serializada = pickle.dumps(imagen)
    # Determinar si la dirección IP es IPv4 o IPv6
    ip_version = ipaddress.ip_address(ip).version
    family = socket.AF_INET6 if ip_version == 6 else socket.AF_INET
    # Crear socket y conectar al servidor
    with socket.socket(family, socket.SOCK_STREAM) as s:
        try:
            s.connect((ip, port))
        except ConnectionRefusedError:
            print(f"Error: No se pudo conectar al servidor en {ip}:{port}. Asegúrese de que el servidor esté en funcionamiento.")
            return
        s.sendall(imagen_serializada)
        s.shutdown(socket.SHUT_WR) 
        
        
        data = b""
        while True:
            packet = s.recv(4096)
            if not packet:
                break
            data += packet

        if data.startswith(b"Error:"):
            print(data.decode())
            return
    
    imagen_procesada = pickle.loads(data)
    filename, ext = os.path.splitext(filepath)
    processed_filename = f"{filename}_procesada{ext}"
    cv2.imwrite(processed_filename, imagen_procesada)
    end_time = time.time()
    print(f"Tiempo para aplicar el filtro: {end_time - start_time:.2f} segundos")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Tp2 - procesa imágenes | Cliente para enviar imagen al servidor")
    parser.add_argument('-f', '--file', type=str, required=True, help='Ruta de la imagen a enviar')
    parser.add_argument('-i', '--ip', type=str, required=True, help='Dirección IP del servidor')
    parser.add_argument('-p', '--port', type=int, required=True, help='Puerto del servidor')
    args = parser.parse_args()
    enviar_imagen(args.file, args.ip, args.port)
