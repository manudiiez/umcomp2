import os

# Crear un pipe
r, w = os.pipe()

# Crear un proceso hijo
pid = os.fork()
if pid > 0:
    # Proceso padre
    os.close(r)  # Cerrar el extremo de lectura en el padre
    w = os.fdopen(w, 'w')
    print("Proceso padre escribiendo")
    w.write("Hola desde el padre")
    w.close()
    #este comando se saltea lo que sigue de codigo y va directo a que el hijo termine la comunicacion de procesos, y luego continua con el codigo.
    os.wait()
    print('al terminar')
else:
    # Proceso hijo
    os.close(w)  # Cerrar el extremo de escritura en el hijo
    r = os.fdopen(r)
    print("Proceso hijo leyendo")
    print(r.read())
    r.close()