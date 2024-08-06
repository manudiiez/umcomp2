import sys
import os
import time
import getopt

def run_task(task_type, duration):
    pid = os.fork()
    if pid == 0:
        # Código ejecutado por el proceso hijo
        print(f"Proceso hijo {os.getpid()} ejecutando tarea '{task_type}' durante {duration} segundos.")
        time.sleep(duration)
        print(f"Proceso hijo {os.getpid()} ha completado su tarea.")
        sys.exit(0)
    return pid

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "", ["task="])
    except getopt.GetoptError:
        print("Uso: main.py --task <type,duration> [--task <type,duration> ...]")
        sys.exit(2)

    tasks = []

    # Extraer las tareas de los argumentos
    for opt, arg in opts:
        if opt == "--task":
            task_details = arg.split(',')
            if len(task_details) != 2:
                continue
            tasks.append((task_details[0], int(task_details[1])))

    children = []
    start_time = time.time()

    # Iniciar cada tarea
    for task_type, duration in tasks:
        pid = run_task(task_type, duration)
        children.append(pid)

    # Esperar a que todos los hijos terminen
    for child in children:
        os.waitpid(child, 0)


    total_time = time.time() - start_time
    # Reporte final
    print(f"Se han completado todas las tareas. Total de tareas: {len(children)}.")
    print(f"Tiempo total transcurrido: {total_time:.2f} segundos.")

if __name__ == "__main__":
    main(sys.argv[1:])


# comando para ejecutar
# python3 main.py --task io,5 --task cpu,3

