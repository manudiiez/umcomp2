import os
import time

fifo_name = 'clase5/myfifo'

print('Abriendo FIFO para leer')
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
