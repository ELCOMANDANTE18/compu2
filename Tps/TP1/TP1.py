#!/usr/bin/python3
#Programa que invierte el archivo de texto

import argparse
import os
import multiprocessing


def linea_de_proceso(linea, control):
#Invierte el orden de los caracteres de la línea y envía el resultado al proceso padre a través del pipe.
    linea_invertida = linea[::-1]
    control.send(linea_invertida)
    control.close()


def inversor():
    # Se establece las entrada de los argumentos
    parser = argparse.ArgumentParser(description='Se invierte el orden de las lineas que esta adentro del archivo')
    parser.add_argument('-f', 
                        '--file',
                         type=str, 
                         required=True, 
                         help='Especificar la ruta en cuestión de donde esta el archivo')
    args = parser.parse_args()

    # Se lee el archivo y se obtienen las líneas
    with open(args.file, 'r') as f:
        lines = f.readlines()

    # Crea un proceso para cada línea y envía la línea a través de un pipe.
    # Cada proceso invertirá la línea y enviará el resultado al proceso padre a través de un nuevo pipe.
    procesos = []
    for line in lines:
        parent_conn, child_conn = multiprocessing.Pipe()
        proceso = multiprocessing.Process(target=linea_de_proceso, args=(line.strip(), child_conn))
        procesos.append((proceso, parent_conn))
        proceso.start()

    # Espera a que todos los procesos terminen y recupera los resultados.
    linea_invertida = []
    for process, parent_conn in procesos:
        proceso.join()
        linea_invertida.append(parent_conn.recv())

    # Imprime los resultados invertidos.
    for line in linea_invertida:
        print(line)


if __name__ == '__main__':
    inversor()



