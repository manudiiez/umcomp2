import multiprocessing
import ctypes

def increment_array(shared_array, index, increment_value):
    # Incrementa el valor en la posición dada del array compartido
    shared_array[index] += increment_value
    print(f"Proceso {multiprocessing.current_process().name} incrementó el índice {index} a {shared_array[index]}")

if __name__ == "__main__":
    # Define el tamaño del array compartido y el tipo de dato (ctypes.c_int)
    array_size = 5
    SharedArray = multiprocessing.Array(ctypes.c_int, array_size)

    # Inicializa el array compartido con valores iniciales
    for i in range(array_size):
        SharedArray[i] = i

    # Imprime el array inicial
    print(f"Array inicial: {list(SharedArray)}")

    processes = []
    increment_value = 5

    # Crea y lanza múltiples procesos que incrementan los valores del array compartido
    for i in range(array_size):
        p = multiprocessing.Process(target=increment_array, args=(SharedArray, i, increment_value))
        processes.append(p)
        p.start()

    # Espera a que todos los procesos terminen
    for p in processes:
        p.join()

    # Imprime el array final
    print(f"Array final: {list(SharedArray)}")
