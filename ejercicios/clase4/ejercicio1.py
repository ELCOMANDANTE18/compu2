#PIPES
#Escribir un programa en Python que comunique dos procesos. 
#El proceso padre deberá leer un archivo de texto y enviar cada línea del archivo al proceso hijo a través de un pipe. 
#El proceso hijo deberá recibir las líneas del archivo y, por cada una de ellas, contar la cantidad de palabras 
#que contiene y mostrar ese número.
#2- Verificar si es posible que dos procesos hijos (o nieto) lean el PIPE del padre.
#3- Verificar si el PIPE sigue existiendo cuendo el padre muere (termina el proceso), cuando el hijo muere [o cuendo mueren ambos]
#$ ls -l /proc/[pid]/fd/

#!/usr/bin/python3

import argparse
import os

parser = argparse.ArgumentParser(description = 'Padre lee texto, hijo devuelve palabras por linea')

parser.add_argument('file', help = 'Archivo que se lee')

args = parser.parse_args()

lectura, escritura = os.pipe()

pid = os.fork()

if pid > 0:
    os.close(lectura)
    with open(args.file) as f:
        for linea in f:
            os.write(escritura, linea.encode())
    os.close(escritura)

else:
    os.close(escritura)
    datos = os.read(lectura, 1024)
    texto = datos.decode()
    linea = texto.split('\n')

    cantidad_de_palabras = 0
    fila = 1
    
    for escritura in linea:
        cantidad_de_palabras = len(escritura.split())
        print('En la fila', fila, 'hay', cantidad_de_palabras, 'palabras, que son:', [escritura])
        fila += 1