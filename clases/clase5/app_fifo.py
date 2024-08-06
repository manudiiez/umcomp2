import os
import time
from multiprocessing import Process

fifo_name = 'clase5/myfifo'

def escritor_fifo():
    if not os.path.exists(fifo_name):
        print('Creando FIFO')
        os.mkfifo(fifo_name)

    print('Abriendo FIFO para escribir')
    with open(fifo_name, "w") as fifo:
        data_to_write = "Hola, mundo desde el archivo FIFO"
        print(f'Escribiendo en FIFO: {data_to_write}')
        fifo.write(f"{data_to_write}\n")
        fifo.write("FIN\n")
        print('Fin de escritura')

def lector_fifo():
    print('Abriendo FIFO para leer...')
    with open(fifo_name, "r") as fifo:
        while True:
            print('Leyendo desde FIFO...')
            line = fifo.readline().strip()
            if line:
                if line == "FIN":
                    print("No hay más datos. Terminando el lector.")
                    break
                print(f"Leído de la FIFO: {line}")
            else:
                time.sleep(1)
    print("FIFO cerrada.")

if __name__ == "__main__":
    lector = Process(target=lector_fifo)
    escritor = Process(target=escritor_fifo)

    # Inicia el lector primero
    lector.start()
    time.sleep(1)  # Asegura que el lector esté listo

    # Inicia el escritor después
    escritor.start()

    # Espera que ambos procesos terminen
    escritor.join()
    lector.join()
