import os

def main():
    print("Inicio del programa (proceso padre).")

    pid = os.fork()

    if pid == 0:
        # Este código se ejecuta en el proceso hijo
        print("Hola, soy el proceso hijo.")
    else:
        # Este código se ejecuta en el proceso padre
        print(f"Hola, soy el proceso padre, y mi hijo tiene PID {pid}.")

    print("Fin del programa.")

if __name__ == "__main__":
    main()