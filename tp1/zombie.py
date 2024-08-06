import multiprocessing as mp
import os
import time

def worker():
    print(f'Worker PID: {os.getpid()} is starting...')
    try:
        while True:
            time.sleep(1)  # Mantener el proceso activo
    except KeyboardInterrupt:
        print(f'Worker PID: {os.getpid()} is terminating...')

if __name__ == "__main__":
    print(f'Main process PID: {os.getpid()}')

    num_workers = 4  # Número de procesos a crear
    processes = []

    for _ in range(num_workers):
        p = mp.Process(target=worker)
        p.start()
        print(f'Started worker with PID: {p.pid}')
        processes.append(p)
    
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("Main process received interrupt. Terminating workers...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()
        print("All workers terminated.")
