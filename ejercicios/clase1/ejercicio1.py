#!/usr/bin/env
#Ejercicio 1:
#Escribir un programa en Python que acepte un número de argumento entero positivo n. 
#Genere una lista de los n primeros números impares. 
#El programa debe imprimir la lista resultante en la salida estándar. 

import argparse

def programa1():
    parser = argparse.ArgumentParser(description="Ingresa algunos números.")
    parser.add_argument("var1",metavar="N",type=int,help="Ingresa valores Positivos")
    args = parser.parse_args()
    if args.var1 > 0:
        print([i for i in range(1,args.var1*2,2)])
    else:
        print("Ingresa un entero positivo")            

programa1()
