"""
Se pueden ver los procesos con ps lf.
Para ver los procesos padre se pueden ver con ps ps
"""


import os
import sys
import time

print('SOY EL PADRE (PID: %d)' % os.getpid())
print('fork --------------------------------')
try:
  ret = os.fork()
except OSError:
  print('ERROR AL CREAR EL HIJO')
  


if ret > 0:
  print('SOY EL PADRE (PID: %d )' % os.getpid())
  # Cuando bash ejecuta algo como este programa, se queda esperando el exit status del hijo. Si el padre no espera (os.wait()) no se devolverá el prompt por que bash no busca el exist status del hijo.
  ret = os.wait()
  print(ret)
  print('FIN DEL PADRE')
  
elif ret == 0:
  print('SOY EL HIJO (PID: %d -- PPID: %d)' % (os.getpid(), os.getppid()))
  
#  time.sleep(2)
  os.execlp('python3', 'python3', 'clase3/hijo/hijo.py')
  
  print('DA IGUAL LO QUE SE EJECUTE EN ESTE PUNTO PORQUE EXEC MODIFICA EL BINARIO ACTUAL')