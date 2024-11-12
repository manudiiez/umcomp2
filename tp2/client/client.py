import socket
import argparse
import cv2
import pickle
import time
import os


def enviar_imagen(filepath, ip, port):
    imagen = cv2.imread(filepath)
    imagen_serializada = pickle.dumps(imagen)
    
    # Crear socket y conectar al servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(imagen_serializada)
        s.shutdown(socket.SHUT_WR) 
        
        data = b""
        while True:
            packet = s.recv(4096)
            if not packet:
                break
            data += packet
    
    imagen_procesada = pickle.loads(data)
    filename, ext = os.path.splitext(filepath)
    processed_filename = f"{filename}_procesada{ext}"
    cv2.imwrite(processed_filename, imagen_procesada)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cliente para enviar imagen al servidor")
    parser.add_argument('-f', '--file', type=str, required=True, help='Ruta de la imagen a enviar')
    parser.add_argument('-i', '--ip', type=str, required=True, help='Dirección IP del servidor')
    parser.add_argument('-p', '--port', type=int, required=True, help='Puerto del servidor')
    args = parser.parse_args()
    start_time = time.time()
    enviar_imagen(args.file, args.ip, args.port)
    end_time = time.time()
    print(f"Tiempo para aplicar el filtro: {end_time - start_time:.2f} segundos")
