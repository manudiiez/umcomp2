from PIL import Image
import multiprocessing as mp
import numpy as np
import random
from scipy.ndimage import gaussian_filter, sobel, median_filter, uniform_filter, laplace, prewitt, maximum_filter, minimum_filter
import time
import os
import signal
import sys

def cargar_imagen(ruta_imagen):
    imagen = Image.open(ruta_imagen)  # Carga la imagen desde la ruta especificada
    return imagen

def dividir_imagen(imagen, n):
    imagen_np = np.array(imagen)  # Convierte la imagen a un array de numpy
    partes = np.array_split(imagen_np, n, axis=0)  # Divide la imagen en n partes a lo largo del eje vertical
    return partes

def aplicar_filtro(parte_imagen):
    filtros = [
        lambda img: gaussian_filter(img, sigma=2),  # Desenfoque gaussiano
        lambda img: sobel(img, axis=-1),  # Filtro de borde Sobel
        lambda img: median_filter(img, size=3),  # Filtro de mediana
        lambda img: uniform_filter(img, size=3),  # Filtro uniforme
        lambda img: laplace(img),  # Filtro Laplaciano
        lambda img: prewitt(img, axis=-1),  # Filtro Prewitt
        lambda img: maximum_filter(img, size=3),  # Filtro máximo
        lambda img: minimum_filter(img, size=3)  # Filtro mínimo
    ]
    
    filtro_seleccionado = random.choice(filtros)  # Selecciona un filtro aleatorio
    parte_filtrada = filtro_seleccionado(parte_imagen)  # Aplica el filtro seleccionado a la parte de la imagen
    
    return parte_filtrada

def procesar_parte(parte, shared_memory, shape, index, conn):
    resultado = aplicar_filtro(parte)  # Aplica un filtro a la parte de la imagen
    shared_array = np.frombuffer(shared_memory.get_obj()).reshape(shape)  # Obtiene la memoria compartida como un array numpy
    shared_array[index:index+parte.shape[0], :, :] = resultado  # Guarda la parte filtrada en la memoria compartida
    conn.send('done')  # Envía una señal de que el proceso ha terminado
    conn.close()  # Cierra la conexión del pipe

def proceso_coordinador(pipes, event, n):
    try:
        for i in range(n):
            pipes[i][0].recv()  # Espera la señal de que cada proceso ha terminado
            pipes[i][0].close()  # Cierra la conexión del pipe

        event.set()  # Señala que el procesamiento ha terminado
    except (KeyboardInterrupt, SystemExit):
        print("Proceso coordinador interrumpido. Terminando de manera controlada.")
        sys.exit(0)

def crear_procesos_y_procesar(shared_memory, shape, partes, event):
    n = len(partes)  # Número de partes en que se dividió la imagen
    pipes = [mp.Pipe() for _ in range(n)]  # Crea un pipe para cada proceso secundario
    procesos = [
        mp.Process(target=procesar_parte, args=(partes[i], shared_memory, shape, sum(part.shape[0] for part in partes[:i]), pipes[i][1]))
        for i in range(n)
    ]  # Crea un proceso para cada parte de la imagen
    proceso_coord = mp.Process(target=proceso_coordinador, args=(pipes, event, n))  # Crea el proceso coordinador
    
    for proceso in procesos:
        proceso.start()  # Inicia cada proceso secundario
    
    proceso_coord.start()  # Inicia el proceso coordinador
    
    try:
        for proceso in procesos:
            proceso.join()  # Espera a que cada proceso secundario termine

        proceso_coord.join()  # Espera a que el proceso coordinador termine
    except (KeyboardInterrupt, SystemExit):
        print("Interrupción recibida. Terminando subprocesos de manera controlada.")
        for proceso in procesos:
            proceso.terminate()  # Termina cada proceso secundario
        proceso_coord.terminate()  # Termina el proceso coordinador
        sys.exit(0)

def guardar_imagen(shared_memory, shape, ruta_salida):
    imagen_completa = np.frombuffer(shared_memory.get_obj()).reshape(shape)  # Obtiene la imagen completa desde la memoria compartida
    print(imagen_completa)
    imagen_final = Image.fromarray(np.uint8(imagen_completa))  # Convierte el array numpy en una imagen PIL
    imagen_final.save(ruta_salida)  # Guarda la imagen en la ruta especificada

def proceso_principal(shared_memory, shape, start_time, image_output, event):
    try:
        event.wait()  # Espera hasta que el evento indique que el procesamiento ha terminado
        print(shared_memory)
        guardar_imagen(shared_memory, shape, image_output)  # Guarda la imagen final procesada
        total_time = time.time() - start_time  # Calcula el tiempo total de procesamiento
        print(f'Tiempo total: {total_time}')  # Imprime el tiempo total
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
    
    start_time = time.time()  # Marca el tiempo de inicio
    image_name = 'tp1/imagen.jpg'  # Nombre del archivo de imagen de entrada
    image_output = 'tp1/imagen_con_filtros.jpg'  # Nombre del archivo de imagen de salida

    imagen = cargar_imagen(image_name)  # Carga la imagen desde el archivo
    partes = dividir_imagen(imagen, 4)  # Divide la imagen en 4 partes
    
    shape = (sum(part.shape[0] for part in partes), partes[0].shape[1], partes[0].shape[2])  # Calcula la forma de la imagen completa
    shared_memory = mp.Array('d', int(np.prod(shape)))  # Crea un array de memoria compartida
    event = mp.Event()  # Crea un evento para sincronización
    
    principal = mp.Process(target=proceso_principal, args=(shared_memory, shape, start_time, image_output, event))  # Crea el proceso principal
    secundario = mp.Process(target=crear_procesos_y_procesar, args=(shared_memory, shape, partes, event))  # Crea el proceso secundario
    
    # Inicia el proceso que guardará la imagen final
    principal.start()
    # time.sleep(3)
    # Inicia el proceso que aplicará los filtros
    secundario.start()

    try:
        # Espera que ambos procesos terminen
        secundario.join()
        principal.join()
    except (KeyboardInterrupt, SystemExit):
        print("Interrupción en el proceso principal. Terminando todos los procesos de manera controlada.")
        principal.terminate()  # Termina el proceso principal
        secundario.terminate()  # Termina el proceso secundario
        sys.exit(0)
