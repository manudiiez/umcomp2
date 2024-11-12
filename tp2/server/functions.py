import cv2
import numpy as np
import asyncio
import pickle

def procesar_imagen(imagen_bytes):
    # Deserializar la imagen usando pickle
    imagen = pickle.loads(imagen_bytes)

    # Convertir la imagen a escala de grises usando OpenCV
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Serializar la imagen procesada usando pickle
    return pickle.dumps(imagen_gris)

async def convertir_a_grises(imagen_bytes):
    loop = asyncio.get_event_loop()
    # Convertir la imagen a escala de grises en un subproceso para no bloquear el bucle de eventos
    imagen = await loop.run_in_executor(None, procesar_imagen, imagen_bytes)
    return imagen
