# Llamadas al sistema
mecanismo a través del cual los programas en el espacio de usuario solicitan servicios del kernel de Linux.

Llamada al Sistema	Descripción:
- fork(): Crea un nuevo proceso duplicando el proceso existente.
- exit(): Termina el proceso actual y libera los recursos asociados.
- wait(): Espera a que un proceso hijo termine y recoge su estado de salida.
- exec(): Reemplaza el programa actual en el proceso actual con uno nuevo.
- open(): Abre un archivo y devuelve un descriptor de archivo.
- read(): Lee datos de un descriptor de archivo en un búfer.
- write(): Escribe datos de un búfer a un descriptor de archivo.
- close(): Cierra un descriptor de archivo, liberando cualquier recurso asociado.
- pipe(): Crea un par de descriptores de archivo conectados entre sí para IPC.
- dup()	Duplica un descriptor de archivo, creando una copia del mismo.
- kill(): Envía una señal a un proceso o a un grupo de procesos.
- getpid(): Devuelve el PID (identificador de proceso) del proceso actual.
- getppid(): Devuelve el PID del proceso padre del proceso actual.
- chdir(): Cambia el directorio de trabajo actual del proceso.
- mkdir(): Crea un nuevo directorio.
- rmdir(): Elimina un directorio vacío.
- lseek(): Cambia la posición de lectura/escritura en un descriptor de archivo.
- mmap(): Mapea un archivo o dispositivo en memoria.
- munmap(): Desmapea un segmento de memoria.
- fork(): Crea un proceso hijo que es una copia del proceso padre.
- execve(): Ejecuta un programa, reemplazando el proceso actual con el nuevo programa.
- waitpid(): Espera por cambios en el estado de un proceso hijo específico.
- signal(): Establece el manejador de una señal.
- ioctl(): Controla un dispositivo.
- fstat(): Obtiene el estado de un archivo.
- stat(): Obtiene el estado de un archivo basado en su nombre.
- link(): Crea un nuevo enlace (una entrada de directorio
- adicional) para un archivo existente.
- unlink(): Elimina un enlace a un archivo, lo que puede resultar en la eliminación del archivo si era el último enlace.

### Fork
Basicamente crea un nuevo proceso duplicando el proceso existente, y a partir de donde se ejecuta todo continua pero en memorias distintas
### Exec 
Permite ejecutar archivos y consultas de cmd, pero cunado se ejecuta reemplaza el proceso actual

## Procesos zombies
Basicamente es un proceso hijo que temrina pero el proceso padre nunca espera la devolucion, por lo tanto queda ocupando memoeria al pedo.

# Pipe
Permite la comunicacion entre procesos sin la necesidad de un sistema de archivos

# Fifo
Archivo especial que se utilzia para la comunicacion entre procesos

# señales
Es una forma de comunicacion entre procesos
Aquí hay una explicación detallada para algunas señales particulares:

- SIGABRT: Genera un aborto del proceso, usualmente iniciado por la función abort() y produce un volcado de memoria.
- SIGALRM: Indica que un temporizador establecido por alarm() ha expirado y termina el proceso si no se maneja.
- SIGBUS: Indica un error de acceso a memoria, como un desalineamiento de direcciones, y genera un volcado de memoria.
- SIGCHLD: Ignorada por defecto, esta señal es enviada a un proceso cuando uno de sus procesos hijos se detiene o termina.
- SIGCONT: Señal para continuar ejecutando un proceso previamente detenido por SIGSTOP o SIGTSTP.
- SIGFPE: Indica una excepción de punto flotante, como la división por cero, y genera un volcado de memoria.
- SIGHUP: Señal enviada para indicar que el terminal del usuario se ha desconectado o que el proceso de control ha terminado, y por defecto termina el proceso.
- SIGKILL: Termina el proceso inmediatamente. Esta señal no puede ser capturada ni ignorada.
- SIGQUIT: Señal generada por una interrupción de teclado (como Ctrl+\) y genera un volcado de memoria.
- SIGSEGV: Indica un acceso inválido a la memoria y genera un volcado de memoria.
- SIGSTOP: Detiene el proceso. Esta señal no puede ser capturada ni ignorada.

# Memoria compartida
Es una forma de comunicar datos de forma directa sin utilizar un intermedio por lo que no se sobrecarga el kernel

# Multiprocesamiento
Técnica de programación que permite a una aplicación ejecutar múltiples procesos simultáneamente. 

# Lock
sincronización simple que permite asegurar que solo un proceso acceda a un recurso compartido a la vez.

# RLock
permite que un mismo proceso adquiera el lock varias veces. Necesita ser liberado el mismo número de veces que fue adquirido.

# Semaphore
variable de sincronización que controla el acceso a un recurso con un contador.

# BoundedSemaphore
es similar a un Semaphore, pero con la restricción adicional de que no permite incrementos por encima del valor inicial.

# Condition
Una Condition es una variable de sincronización avanzada que permite a los procesos esperar hasta que una condición específica se cumpla. Se utiliza junto con un Lock o RLock.forlLock


----
Punto 3: Comunicación y Sincronización
Recomendaciones:

Pipes: Usa multiprocessing.Pipe para la comunicación entre procesos.
Proceso coordinador: Crea un proceso coordinador que reciba los resultados parciales a través de las pipes y los combine.
Sincronización: Usa os.wait() para asegurarte de que todos los procesos hijos terminen antes de combinar los resultados.
Por qué:

multiprocessing.Pipe es fácil de usar para pasar datos entre procesos y permite una comunicación eficiente.
Un proceso coordinador centraliza la recolección y combinación de resultados, simplificando la lógica del programa.
os.wait() asegura que el proceso padre espera a que todos los procesos hijos terminen, evitando procesos zombis.
Punto 4: Manejo de Señales
Recomendaciones:

Señales (signal): Configura una señal como SIGINT para manejar interrupciones.
Manejador de señales: Implementa un manejador de señales en el proceso principal para capturar interrupciones y realizar limpieza adecuada.
Por qué:

Las señales permiten manejar eventos asíncronos como interrupciones del usuario (Ctrl+C), permitiendo una terminación controlada de los procesos.
Un manejador de señales asegura que los recursos se liberen correctamente y que los procesos hijos se terminen adecuadamente.
Punto 5: Uso de Memoria Compartida
Recomendaciones:

Memoria compartida: Usa multiprocessing.Array para crear un array compartido entre procesos.
Almacenamiento de resultados: Modifica los procesos hijos para almacenar los resultados parciales en la memoria compartida.
Combinación de resultados: Usa el proceso coordinador para leer los resultados de la memoria compartida y combinarlos en una imagen final.
Por qué:

multiprocessing.Array permite compartir datos entre procesos sin necesidad de comunicación explícita, lo que simplifica el intercambio de información.
Usar memoria compartida puede ser más eficiente que pasar grandes cantidades de datos a través de pipes.
