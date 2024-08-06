import signal
import sys
import time

def manejador_senal(sig, frame):
    print("Señal SIGINT recibida. Terminando el programa de manera controlada.")
    # Aquí puedes realizar cualquier limpieza o cierre necesario
    sys.exit(0)

# Configurar el manejador de señal para SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, manejador_senal)

def tarea_larga():
    print("Tarea larga en progreso. Presiona Ctrl+C para interrumpir.")
    try:
        while True:
            print("Trabajando...")
            time.sleep(1)  # Simula trabajo prolongado
    except KeyboardInterrupt:
        print("Tarea interrumpida. Limpiando recursos...")

def main():
    print("Programa iniciado. Presiona Ctrl+C para interrumpir.")
    # time.sleep(3)
    tarea_larga()
    print("Programa terminado.")

if __name__ == "__main__":
    print('If name')
    # time.sleep(3)
    main()
