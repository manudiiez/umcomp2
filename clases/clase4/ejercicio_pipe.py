import os

r,w = os.pipe()
pid = os.fork()

if pid > 0:
    print('Padre escribe.')
    os.write(w, "Hola hijo".encode())
    os.wait()
    print("Padre lee: " + os.read(r,100).decode())
    os.close(r)
    os.close(w)
    exit()
else:
    print("Hijo lee: " + os.read(r,100).decode())
    print("Hijo escribe.")
    os.write(w, "Chau papa".encode())
    os.close(r)
    os.close(w)
    exit()
    