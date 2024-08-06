import os, time

pid = os.fork()
start_time = time.time()
total_time = time.time() - start_time
if pid == 0:
  os.execlp("sleep", "sleep", "3")
time.sleep(5)
print('Finalizando el padre')
total_time = time.time() - start_time
print(f"Tiempo total transcurrido: {total_time:.2f} segundos.")