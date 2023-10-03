#!/usr/bin/env
#Ejercicio 2:

#Escribir un programa en Python que acepta dos argumentos de línea de comando: una cadena de texto, un número entero. 
#El programa debe imprimir una repetición de la cadena de texto tantas veces como el número entero.
import argparse

def programa2():
    parser = argparse.ArgumentParser("Ingresa una cadena de texto y un número")
    parser.add_argument("secuencia",help="La secuencia escrita se repetira tanta veces")
    parser.add_argument("var1",metavar="N",type=int,help="Ingresa la cantidad de veces que quieres que se repita el texto")
    args = parser.parse_args()
    print((args.secuencia + " " )*args.var1)

programa2()
