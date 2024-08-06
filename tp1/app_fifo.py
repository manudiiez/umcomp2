import pickle
import time

def escritor_fifo(fifo_name, array_data):

    with open(fifo_name, "wb") as fifo:
        # Serializa los datos del array con pickle
        pickle.dump(array_data, fifo)


def lector_fifo(fifo_name):
    with open(fifo_name, "rb") as fifo:
        # Deserializa los datos del array con pickle
        array_data = pickle.load(fifo)
    return array_data   

