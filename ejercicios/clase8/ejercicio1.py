# 1 - Considerando el programa noblock.py, realizar un programa que lance 10 procesos hijos que intenten encontrar el nonce
# para un No-Bloque con una dificultad dada. El hijo que lo encuentre primero debe comunicarse con el padre. 
# Realizar todo utilizando multiprocessing

######################

import argparse
import multiprocessing


parser = argparse.ArgumentParser(description = 'Segmento de memoria compartida.')
parser.add_argument('-f', '--file', help='Ruta del archivo', required = True)
args = parser.parse_args()
