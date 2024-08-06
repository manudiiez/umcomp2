from PIL import Image
import multiprocessing as mp
import numpy as np
import random
from scipy.ndimage import gaussian_filter, sobel, median_filter, uniform_filter, laplace, prewitt, maximum_filter, minimum_filter
import time


def cargar_imagen(ruta_imagen):
    """
    Carga una imagen desde el disco.

    Args:
    ruta_imagen (str): Ruta al archivo de imagen.

    Returns:
    Image: Objeto de imagen cargado.
    """
    imagen = Image.open(ruta_imagen)
    return imagen


def dividir_imagen(imagen, n):
    """
    Divide una imagen en n partes iguales.

    Args:
    imagen (Image): Objeto de imagen cargado.
    n (int): Número de partes en las que se va a dividir la imagen.

    Returns:
    list: Lista de partes de la imagen como arrays de numpy.
    """
    imagen_np = np.array(imagen)
    partes = np.array_split(imagen_np, n, axis=0)
    return partes

def crear_procesos_y_procesar(partes):
    
    """
    Crea un proceso para cada parte de la imagen y aplica un filtro en paralelo.

    Args:
    partes (list): Lista de arrays de numpy que representan partes de la imagen.

    Returns:
    list: Lista de arrays de numpy con las partes filtradas de la imagen.
    """
    n = len(partes)
    pipes = [mp.Pipe() for _ in range(n)]
    procesos = [mp.Process(target=procesar_parte, args=(partes[i], pipes[i][1])) for i in range(n)]
    
    # Iniciar todos los procesos
    for proceso in procesos:
        proceso.start()
    
    # Recibir los resultados
    resultados = [pipes[i][0].recv() for i in range(n)]
    
    # Esperar a que todos los procesos terminen
    for proceso in procesos:
        proceso.join()
    
    return resultados

def procesar_parte(parte, conn):
    """
    Aplica un filtro a una parte de la imagen y envía el resultado de vuelta al proceso coordinador.

    Args:
    parte (numpy.ndarray): Array de numpy que representa la parte de la imagen.
    conn (multiprocessing.Connection): Conexión para enviar el resultado al proceso coordinador.
    """
    resultado = aplicar_filtro(parte)
    conn.send(resultado)
    conn.close()

def aplicar_filtro(parte_imagen):
    """
    Aplica un filtro de desenfoque gaussiano a una parte de la imagen.

    Args:
    parte_imagen (numpy.ndarray): Array de numpy que representa la parte de la imagen.

    Returns:
    numpy.ndarray: Parte de la imagen con el filtro aplicado.
    """
    filtros = [
        lambda img: gaussian_filter(img, sigma=2),      # Desenfoque gaussiano
        lambda img: sobel(img, axis=-1),                # Filtro de borde Sobel
        lambda img: median_filter(img, size=3),         # Filtro de mediana
        lambda img: uniform_filter(img, size=3),        # Filtro uniforme
        lambda img: laplace(img),                       # Filtro Laplaciano
        lambda img: prewitt(img, axis=-1),              # Filtro Prewitt
        lambda img: maximum_filter(img, size=3),        # Filtro máximo
        lambda img: minimum_filter(img, size=3)         # Filtro mínimo
    ]
    
    # Seleccionar un filtro aleatorio
    filtro_seleccionado = random.choice(filtros)
    
    # Aplicar el filtro seleccionado a la parte de la imagen
    parte_filtrada = filtro_seleccionado(parte_imagen)
    
    return parte_filtrada

def guardar_imagen(partes, ruta_salida):
    """
    Guarda una parte de la imagen filtrada en el disco.

    Args:
    parte_filtrada (numpy.ndarray): Array de numpy que representa la parte filtrada de la imagen.
    ruta_salida (str): Ruta donde se guardará la parte filtrada de la imagen.
    """
    imagen_completa = np.vstack(partes)
    # Convertir el array de numpy de vuelta a un objeto de imagen de Pillow
    imagen_final = Image.fromarray(np.uint8(imagen_completa))

    # Guardar la imagen filtrada en el disco
    imagen_final.save(ruta_salida)



if __name__ == "__main__":
    start_time = time.time()
    imagen = cargar_imagen('imagen.jpg')
    partes = dividir_imagen(imagen, 4)
    partes_filtradas = crear_procesos_y_procesar(partes)
    guardar_imagen(partes_filtradas, 'imagen_con_filtros.jpg')
    total_time = time.time() - start_time
    print(f'Tiempo total: {total_time}')

    