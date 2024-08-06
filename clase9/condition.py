from multiprocessing import Process, Condition, Lock
# Lock: Es como un bloqueo, ejemplo del baño
import time

def simple_condition_example(cond, i):
    with cond:
        print(f'Proceso {i} esperando la condición')
        cond.wait()
        print(f'Proceso {i} condición cumplida')

if __name__ == '__main__':
    condition = Condition(Lock())
    for num in range(5):
        Process(target=simple_condition_example, args=(condition, num)).start()

    time.sleep(2)
    with condition:
        print('Condición cumplida, notificando a todos')
        condition.notify_all()