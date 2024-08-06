"""
El padre y el hijo tendrán el mismo PID ya que el hijo se ejecuta modificando el binario del padre. Reemplaza al padre.

"""


import os



print('SOY EL PADRE (PID: %d)' % os.getpid())
os.execlp('python3', 'python3', 'clase3/hijo/hijo.py')

print('DA IGUAL LO QUE SE EJECUTE EN ESTE PUNTO PORQUE EXEC MODIFICA EL BINARIO ACTUAL')