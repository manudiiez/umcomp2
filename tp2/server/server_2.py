# archivo: server_scaling.py

import socketserver
import cv2
import pickle
import os
import signal

class ScalingHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"Procesando solicitud en PID: {os.getpid()}")
        data = b""
        while True:
            packet = self.request.recv(4096)
            if not packet:
                break
            data += packet
        
        if not data:
            return

        recibido = pickle.loads(data)
        imagen = recibido['imagen']
        factor_escala = recibido['factor_escala']

        # Reducir el tamaño de la imagen
        nueva_imagen = cv2.resize(imagen, (0, 0), fx=factor_escala, fy=factor_escala)
        imagen_serializada = pickle.dumps(nueva_imagen)

        # Enviar la imagen reducida de vuelta
        self.request.sendall(imagen_serializada)

class ForkingTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass

def signal_handler(signal, frame):
    print("Servidor detenido de forma segura.")
    os._exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    with ForkingTCPServer(("localhost", 9999), ScalingHandler) as server:
        print("Servidor de escalado corriendo en el puerto 9999...")
        server.serve_forever()
