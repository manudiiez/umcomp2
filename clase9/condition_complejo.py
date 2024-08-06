from multiprocessing import Process, Condition, Lock
import time

class SharedConditionResource:
    def __init__(self, condition):
        self.condition = condition
        self.value = 0

    def wait_for_update(self, process_id):
        with self.condition:
            print(f'Proceso {process_id} esperando actualización')
            self.condition.wait()
            print(f'Proceso {process_id} detectó actualización: {self.value}')

    def update_resource(self, value):
        with self.condition:
            self.value = value
            print(f'Recurso actualizado a: {self.value}')
            self.condition.notify_all()

def complex_condition_example(resource, i):
    if i == 0:
        for val in range(1, 4):
            time.sleep(2)
            resource.update_resource(val)
    else:
        resource.wait_for_update(i)

if __name__ == '__main__':
    condition = Condition(Lock())
    shared_resource = SharedConditionResource(condition)
    processes = [Process(target=complex_condition_example, args=(shared_resource, i)) for i in range(5)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
