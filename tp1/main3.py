from PIL import Image
import multiprocessing as mp
import numpy as np
import random
from scipy.ndimage import gaussian_filter, sobel, median_filter, uniform_filter, laplace, prewitt, maximum_filter, minimum_filter
import time
import os
import signal
import sys

from app_fifo import escritor_fifo, lector_fifo

def cargar_imagen(ruta_imagen):
    imagen = Image.open(ruta_imagen)
    return imagen

def dividir_imagen(imagen, n):
    imagen_np = np.array(imagen)
    partes = np.array_split(imagen_np, n, axis=0)
    return partes

def aplicar_filtro(parte_imagen):
    filtros = [
        lambda img: gaussian_filter(img, sigma=2), # Desenfoque gaussiano
        lambda img: sobel(img, axis=-1), # Filtro de borde Sobel
        lambda img: median_filter(img, size=3), # Filtro de mediana
        lambda img: uniform_filter(img, size=3), # Filtro uniforme
        lambda img: laplace(img), # Filtro Laplaciano
        lambda img: prewitt(img, axis=-1), # Filtro Prewitt
        lambda img: maximum_filter(img, size=3), # Filtro máximo
        lambda img: minimum_filter(img, size=3) # Filtro mínimo
    ]
    
    filtro_seleccionado = random.choice(filtros)
    parte_filtrada = filtro_seleccionado(parte_imagen)
    
    return parte_filtrada

def procesar_parte(parte, conn):
    resultado = aplicar_filtro(parte)
    conn.send(resultado)
    conn.close()

def proceso_coordinador(pipes, n, fifo_name):
    try:
        resultados = [pipes[i][0].recv() for i in range(n)]
        for i in range(n):
            pipes[i][0].close()
        escritor_fifo(fifo_name, resultados)
    except (KeyboardInterrupt, SystemExit):
        print("Proceso coordinador interrumpido. Terminando de manera controlada.")
        sys.exit(0)

def crear_procesos_y_procesar(fifo_name, partes):
    n = len(partes)
    pipes = [mp.Pipe() for _ in range(n)]
    procesos = [mp.Process(target=procesar_parte, args=(partes[i], pipes[i][1])) for i in range(n)]
    proceso_coord = mp.Process(target=proceso_coordinador, args=(pipes, n, fifo_name))
    
    for proceso in procesos:
        proceso.start()
    
    proceso_coord.start()
    
    try:
        for proceso in procesos:
            proceso.join()
        
        proceso_coord.join()
    except (KeyboardInterrupt, SystemExit):
        print("Interrupción recibida. Terminando subprocesos de manera controlada.")
        for proceso in procesos:
            proceso.terminate()
        proceso_coord.terminate()
        sys.exit(0)

def guardar_imagen(partes, ruta_salida):
    imagen_completa = np.vstack(partes)
    imagen_final = Image.fromarray(np.uint8(imagen_completa))
    imagen_final.save(ruta_salida)

def proceso_principal(fifo_name, start_time, image_output):
    try:
        partes_editadas = lector_fifo(fifo_name)
        guardar_imagen(partes_editadas, image_output)
        total_time = time.time() - start_time
        print(f'Tiempo total: {total_time}')
    except (KeyboardInterrupt, SystemExit):
        print("Interrupción en el proceso principal. Terminando de manera controlada.")
        sys.exit(0)

def manejador_senal(sig, frame):
    print(f'Señal {sig} recibida. Terminando el programa de manera controlada.')
    sys.exit(0)

if __name__ == "__main__":
    # Configurar el manejador de señal para SIGINT y SIGTSTP
    signal.signal(signal.SIGINT, manejador_senal)
    # signal.signal(signal.SIGTSTP, manejador_senal)
    
    start_time = time.time()
    image_name = 'imagen.jpg'
    image_output = 'imagen_con_filtros.jpg'
    fifo_name = 'imagen_fifo'

    # Crear FIFO si no existe
    if not os.path.exists(fifo_name):
        os.mkfifo(fifo_name)

    imagen = cargar_imagen(image_name)
    partes = dividir_imagen(imagen, 4)
    
    principal = mp.Process(target=proceso_principal, args=(fifo_name, start_time, image_output))
    secundario = mp.Process(target=crear_procesos_y_procesar, args=(fifo_name, partes))
    
    # Inicia el proceso que leerá de la FIFO (lector)
    principal.start()
    # time.sleep(3)
    # Inicia el proceso que escribirá en la FIFO (escritor)
    secundario.start()

    try:
        # Espera que ambos procesos terminen
        secundario.join()
        principal.join()
    except (KeyboardInterrupt, SystemExit):
        print("Interrupción en el proceso principal. Terminando todos los procesos de manera controlada.")
        principal.terminate()
        secundario.terminate()
        sys.exit(0)
