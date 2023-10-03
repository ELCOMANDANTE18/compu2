#FIFOS
#1- Escribir un programa que realice la multiplicación de dos matrices de 2x2. 
#Cada elemento deberá calcularse en un proceso distinto devolviendo el resultado en una fifo indicando el indice del elemento. 
#El padre deberá leer en el fifo y mostrar el resultado final.

#!/usr/bin/python3

#python3 ejercicio01_A.py -m1 1 2 3 4 -m2 1 2 3 4

import argparse
import os

parser = argparse.ArgumentParser(description = 'Multiplicacion de dos matrices 2x2')

parser.add_argument('-m1', nargs=4, type=int, metavar=('a', 'b', 'c', 'd'), help = 'matriz 1 en orden a b c d')
parser.add_argument('-m2', nargs=4, type=int, metavar=('e', 'f', 'g', 'h'), help = 'matriz 2 en orden e f g h')

args = parser.parse_args()

matriz1 = args.m1
matriz2 = args.m2

fifo_01 = '/tmp/fifo_01'
fifo_02 = '/tmp/fifo_02'
fifo_03 = '/tmp/fifo_03'
fifo_04 = '/tmp/fifo_04'

def child_01():
    fifo = open(fifo_01, 'w')
    calculo_01 = str(matriz1[0]*matriz2[0]+matriz1[1]*matriz2[2])
    fifo.write(calculo_01)
    fifo.close()

def child_02():
    fifo = open(fifo_02, 'w')
    calculo_02 = str(matriz1[0]*matriz2[0]+matriz1[1]*matriz2[3])
    fifo.write(calculo_02)
    fifo.close()

def child_03():
    fifo = open(fifo_03, 'w')
    calculo_03 = str(matriz1[2]*matriz2[0]+matriz1[3]*matriz2[2])
    fifo.write(calculo_03)
    fifo.close()

def child_04():
    fifo = open(fifo_04, 'w')
    calculo_04 = str(matriz1[2]*matriz2[1]+matriz1[3]*matriz2[3])
    fifo.write(calculo_04)
    fifo.close()

def parent():
    fifo_in_01 = open(fifo_01, 'r')
    fifo_in_02 = open(fifo_02, 'r')
    fifo_in_03 = open(fifo_03, 'r')
    fifo_in_04 = open(fifo_04, 'r')

    pos1 = fifo_in_01.readline().rstrip()
    pos2 = fifo_in_02.readline().rstrip()
    pos3 = fifo_in_03.readline().rstrip()
    pos4 = fifo_in_04.readline().rstrip()

    fifo_in_01.close()
    fifo_in_02.close()
    fifo_in_03.close()
    fifo_in_04.close()

    mat = [[pos1,pos2],[pos3,pos4]]

    for i in mat:
        print(i)

if not os.path.exists(fifo_01):
    os.mkfifo(fifo_01)
if not os.path.exists(fifo_02):
    os.mkfifo(fifo_02)
if not os.path.exists(fifo_03):
    os.mkfifo(fifo_03)
if not os.path.exists(fifo_04):
    os.mkfifo(fifo_04)

pid = os.fork()

if pid > 0:
    parent()

else:
    child_01()
    child_02()
    child_03()
    child_04()