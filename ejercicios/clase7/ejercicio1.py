# Memoria Compartida
# Etapa 1
# Escribir un programa que reciba por argumento la opción -f acompañada de un path_file
# El programa deberá crear un segmento de memoria compartida y generar dos hijos H1 y H2.

# H1 deberá leer desde sdtin lo que ingrese el usuario, línea por línea, enviando una señal USR1 al padre en cada línea leida.

# Una vez ingresada una línea, el proceso padre leerá la memoria compartida y mostrará la línea leida por pantalla
# y enviará una señal USR1 a H2.
# Al recibir la señal USR1, H2 leerá la línea desde la memoria compartida y la escribirá en mayúsculas en el archivo 
# recibido como argumento.
# Etapa 2
# Cuando el usuario introduzca "bye" en la terminal, H1 enviará al padre la señal USR2 y terminará.
# Al recibir la señal USR2, el padre, la enviará a H2 que también terminará.
# El padre esperará a ambos hijos y terminará también.

#!/usr/bin/python3

import argparse
import os
import multiprocessing
import signal

parser = argparse.ArgumentParser(description='Memoria Compartida')
parser.add_argument('-f', help='Ruta del archivo')  # dest='path_file'
args = parser.parse_args()

def child_01(shared_memory):
    while True:
        user_input = input('Ingrese palabras: ')
        if user_input == 'bye':
            shared_memory.put(None)  # Marca de finalización
            break
        else:
            os.kill(os.getppid(), signal.SIGUSR1)
            shared_memory.put(user_input)


def parent(shared_memory):
    while True:
        if not shared_memory.empty():
            read_memory = shared_memory.get()
            if read_memory is None:  # Marca de finalización
                break
            else:
                words = read_memory.split()
                print(words)


#def child_02():
    


if __name__ == '__main__':
    shared_memory = multiprocessing.Queue()
    pid = os.fork()

    if pid > 0:
        parent(shared_memory)
    else:
        child_01(shared_memory)









# def child_01(shared_memory):
#     while True:
#         user_input = input('Ingrese palabras: ')
#         if user_input == 'bye':
#             shared_memory.put(user_input)
#             os.kill(os.getppid(), signal.SIGUSR2)       # Envia la señal SIGUSR2 al proceso padre
#             signal.pause()                          
#             break
#         else:
#             shared_memory.put(user_input)

# #def child_02(shared_memory):


# def parent(shared_memory):
#     while True:
#         if not shared_memory.empty():
#             user_input = shared_memory.get()
#             may_user_input = user_input.upper()
#             for word in may_user_input.split('\n'):
#                 print(word)
#         else:
#             child_01(shared_memory)