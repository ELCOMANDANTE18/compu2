#Realizar un programa que implemente fork junto con el parseo de argumentos. 
#Deberá realizar relizar un fork si -f aparece entre las opciones al ejecutar el programa. 
#El proceso padre deberá calcular la raiz cuadrada positiva de un numero y el hijo la raiz negativa.

#!/usr/bin/python3

import argparse
import os
import math

parser = argparse.ArgumentParser(description = 'Proceso padre calcula raiz cuadrada de un numero, proceso hijo la raiz negativa') 

parser.add_argument('-f', action='store_true', help = 'Si se proporsiona -f se realizara el fork')
parser.add_argument('--numero', help='Numero con el que se va a realizar la operacion', type=int)

args = parser.parse_args()

pid = os.fork()
    
if args.f:
    if pid > 0:
        number = args.numero
        raiz = math.sqrt(number)
        print('SOY PADRE (PID: %d -- PPID: %d)' % (os.getpid(), os.getppid()))
        print('La raíz cuadrada de', number, 'es', raiz)
    else:
        number = args.numero
        raiz_cubica = number**(1/3)
        print('SOY HIJO (PID: %d -- PPID: %d)' % (os.getpid(), os.getppid()))
        print("La raíz cúbica de", number, "es", raiz_cubica)
else:
    print('No le pasaste -f')