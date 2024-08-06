import multiprocessing
import os
import time

def worker():
    print(f'Worker PID: {os.getpid()} is starting...')
    time.sleep(2)
    print(f'Worker PID: {os.getpid()} is finishing...')

if __name__ == "__main__":
    print(f'Main process PID: {os.getpid()}')
    
    # Crear el proceso hijo
    p = multiprocessing.Process(target=worker)
    p.start()
    
    # Esperar a que el proceso hijo termine sin recogerlo
    time.sleep(3)
    print(f'Main process PID: {os.getpid()} is finished sleeping.')

    # En este punto, el proceso hijo debe ser un proceso zombie
    while True:
        time.sleep(1)
        print(f'Main process PID: {os.getpid()} is still running. Check for zombie process.')

# Nota: No estamos usando p.join() intencionalmente para dejar el proceso hijo en estado zombie.
