import os
import time

fifo_name = 'clase5/myfifo'

if not os.path.exists(fifo_name):
    print('Creando FIFO')
    os.mkfifo(fifo_name)

print('Abriendo FIFO para escribir')
with open(fifo_name, "w") as fifo:
    data_to_write = "Hola, mundo desde el archivo FIFO"
    print(f'Escribiendo en FIFO: {data_to_write}')
    fifo.write(f"{data_to_write}\n")
    fifo.write("FIN\n")
    print('Fin')
