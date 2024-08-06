import os

def main():
    # Pipe para comunicación de padre a hijo
    parent_to_child_r, parent_to_child_w = os.pipe()
    # Pipe para comunicación de hijo a padre
    child_to_parent_r, child_to_parent_w = os.pipe()

    pid = os.fork()

    if pid > 0:  # Código del proceso padre
        # Cerrar extremos no usados
        os.close(parent_to_child_r)
        os.close(child_to_parent_w)

        # Escribir al hijo
        with os.fdopen(parent_to_child_w, 'w') as w:
            print('Padre escribe.')
            w.write("Hola hijo")

        # Leer del hijo
        with os.fdopen(child_to_parent_r) as r:
            print("Padre recibe:", r.read())

        # Esperar a que el hijo termine (puede ir en cualquier parte)
        os.wait()

    else:  # Código del proceso hijo
        # Cerrar extremos no usados
        os.close(parent_to_child_w)
        os.close(child_to_parent_r)

        # Leer del padre
        with os.fdopen(parent_to_child_r) as r:
            print("Hijo recibe:", r.read())

        # Escribir al padre
        with os.fdopen(child_to_parent_w, 'w') as w:
            print('hijo escribe.')
            w.write("Hola padre")

        # Salir del proceso hijo
        os._exit(0)

if __name__ == '__main__':
    main()
