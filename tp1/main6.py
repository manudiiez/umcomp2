from PIL import Image
import multiprocessing as mp
import numpy as np
import getopt
import sys
from scipy.ndimage import gaussian_filter, sobel, median_filter, uniform_filter, laplace, prewitt, maximum_filter, minimum_filter
import time
import signal

def cargar_imagen(ruta_imagen):
    imagen = Image.open(ruta_imagen)  # Carga la imagen desde la ruta especificada
    return imagen

def dividir_imagen(imagen, n):
    imagen_np = np.array(imagen)  # Convierte la imagen a un array de numpy
    partes = np.array_split(imagen_np, n, axis=0)  # Divide la imagen en n partes a lo largo del eje vertical
    return partes

def aplicar_filtro(parte_imagen, filtro_seleccionado):
    filtros = {
        'gaussian': lambda img: gaussian_filter(img, sigma=2),  # Desenfoque gaussiano
        'sobel': lambda img: sobel(img, axis=-1),  # Filtro de borde Sobel
        'median': lambda img: median_filter(img, size=3),  # Filtro de mediana
        'uniform': lambda img: uniform_filter(img, size=3),  # Filtro uniforme
        'laplace': lambda img: laplace(img),  # Filtro Laplaciano
        'prewitt': lambda img: prewitt(img, axis=-1),  # Filtro Prewitt
        'maximum': lambda img: maximum_filter(img, size=3),  # Filtro máximo
        'minimum': lambda img: minimum_filter(img, size=3)  # Filtro mínimo
    }
    
    if filtro_seleccionado not in filtros:
        raise ValueError(f"Filtro no válido: {filtro_seleccionado}")

    parte_filtrada = filtros[filtro_seleccionado](parte_imagen)  # Aplica el filtro seleccionado a la parte de la imagen
    return parte_filtrada

def procesar_parte(parte, shared_memory, shape, index, conn, filtro_seleccionado):
    resultado = aplicar_filtro(parte, filtro_seleccionado)  # Aplica el filtro a la parte de la imagen
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
        event.set()
        sys.exit(0)

def crear_procesos_y_procesar(shared_memory, shape, partes, event, filtro_seleccionado):
    n = len(partes)  # Número de partes en que se dividió la imagen
    pipes = [mp.Pipe() for _ in range(n)]  # Crea un pipe para cada proceso secundario
    procesos = [
        mp.Process(target=procesar_parte, args=(partes[i], shared_memory, shape, sum(part.shape[0] for part in partes[:i]), pipes[i][1], filtro_seleccionado))
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
        print("Interrupción recibida. Terminando subprocesos y proceso coordinador de manera controlada.")
        event.set()
        for proceso in procesos:
            proceso.terminate()  # Termina cada proceso secundario
        proceso_coord.terminate()  # Termina el proceso coordinador
        sys.exit(0)

def guardar_imagen(shared_memory, shape, ruta_salida):
    imagen_completa = np.frombuffer(shared_memory.get_obj()).reshape(shape)  # Obtiene la imagen completa desde la memoria compartida
    imagen_final = Image.fromarray(np.uint8(imagen_completa))  # Convierte el array numpy en una imagen PIL
    imagen_final.save(ruta_salida)  # Guarda la imagen en la ruta especificada

def proceso_principal(shared_memory, shape, start_time, image_output, event):
    try:
        event.wait()  # Espera hasta que el evento indique que el procesamiento ha terminado
        guardar_imagen(shared_memory, shape, image_output)  # Guarda la imagen final procesada
        total_time = time.time() - start_time  # Calcula el tiempo total de procesamiento
        print(f'Tiempo total: {total_time}')  # Imprime el tiempo total
    except (KeyboardInterrupt, SystemExit):
        print("Interrupción en el proceso principal. Terminando de manera controlada. funcion proceso_principal")
        sys.exit(0)

def manejador_senal(sig, frame):
    print(f'Señal {sig} recibida. Terminando el programa de manera controlada.')
    raise SystemExit(0)

def mostrar_ayuda():
    print("Uso: python script.py -f <filtro> -n <partes>")
    print("Filtros disponibles: gaussian, sobel, median, uniform, laplace, prewitt, maximum, minimum")

if __name__ == "__main__":
    # Manejador de señales
    signal.signal(signal.SIGINT, manejador_senal)
    # signal.signal(signal.SIGTSTP, manejador_senal)

    # Obtener los argumentos de la línea de comandos
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:n:", ["filtro=", "partes="])
    except getopt.GetoptError as err:
        print(err)
        mostrar_ayuda()
        sys.exit(2)

    filtro_seleccionado = None
    num_partes = 4 
    max_procesos = mp.cpu_count() 
    for opt, arg in opts:
        if opt == '-h':
            mostrar_ayuda()
            sys.exit()
        elif opt in ("-f", "--filtro"):
            filtro_seleccionado = arg
        elif opt in ("-n", "--partes"):
            if arg.lower() == "max":
                num_partes = max_procesos
            else:
                num_partes = int(arg)
                if num_partes > max_procesos:
                    print(f"El número de partes especificado ({num_partes}) excede el número máximo de procesos que esta computadora puede manejar ({max_procesos}).")
                    sys.exit(2)

    if filtro_seleccionado is None:
        print("Debe especificar un filtro.")
        mostrar_ayuda()
        sys.exit(2)

    start_time = time.time() 

    # Datos iniciales
    image_name = 'tp1/imagen.jpg' 
    image_output = 'tp1/imagen_con_filtros.jpg' 
    imagen = cargar_imagen(image_name)
    partes = dividir_imagen(imagen, num_partes)
    
    # Calculo del tamaño de la memoria
    altura_total = 0
    for part in partes:
        altura_total += part.shape[0]

    ancho = partes[0].shape[1]
    profundidad = partes[0].shape[2]

    shape = (altura_total, ancho, profundidad) 

    # Creacion de la memoria compartida
    shared_memory = mp.Array('d', int(np.prod(shape)))  
    event = mp.Event()  # Crea un evento para sincronización

    # Creacion de los procesos
    principal = mp.Process(target=proceso_principal, args=(shared_memory, shape, start_time, image_output, event)) 
    secundario = mp.Process(target=crear_procesos_y_procesar, args=(shared_memory, shape, partes, event, filtro_seleccionado)) 
    
    # Inician los procesos
    principal.start()
    secundario.start()

    try:
        # Espera que ambos procesos terminen
        secundario.join()
        principal.join()
    except (KeyboardInterrupt, SystemExit):
        print("Interrupción en el proceso principal. Terminando todos los procesos de manera controlada.")
        event.set()
        principal.terminate()  # Termina el proceso principal
        secundario.terminate()  # Termina el proceso secundario
        sys.exit(0)
