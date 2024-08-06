from multiprocessing import Process, Lock
import time

def simple_lock_example(lock, i):
    lock.acquire()
    try:
        print(f'Proceso {i} accediendo a la sección crítica')
        time.sleep(1)
    finally:
        lock.release()

if __name__ == '__main__':
    lock = Lock()
    for num in range(5):
        Process(target=simple_lock_example, args=(lock, num)).start()
