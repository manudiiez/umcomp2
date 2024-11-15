import cv2
import asyncio

def procesar_imagen(imagen_bytes):
    # Convertir la imagen a escala de grises usando OpenCV
    imagen_gris = cv2.cvtColor(imagen_bytes, cv2.COLOR_BGR2GRAY)
    return imagen_gris

async def convertir_a_grises(imagen_bytes):
    loop = asyncio.get_event_loop()
    imagen = await loop.run_in_executor(None, procesar_imagen, imagen_bytes)
    return imagen
