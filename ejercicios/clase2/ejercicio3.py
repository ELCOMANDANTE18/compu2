#Ejercicio 3:

#Escribir un programa en Python que acepte argumentos de línea de comando para leer un archivo de texto. 
#El programa debe contar el número de palabras y líneas del archivo e imprimirlas en la salida estándar. 
#Además el programa debe aceptar una opción para imprimir la longitud promedio de las palabras del archivo. 
#Esta última opción no debe ser obligatoria. Si hubiese errores deben guardarse el un archivo cuyo nombre será "errors.log" usando la redirección de la salida de error.
import argparse

def programa_3():
    parser =argparse.ArgumentParser()
    parser.add_argument("archivo",metavar="F",type=str,help="Ingresa el archivo en cuestión")
    args= parser.parse_args()
    
    try:
        with open(args.archivo,"r") as f:
            contenido = f.read()
            print(f"Cantidad de Lineas:{len(contenido)}")
            print(f"Cantidad de palabras:{len(contenido.splitlines())}")
    except Exception as e:
        with open("errors.log","a"):
          print("No se ha encontrado el archivo") 


programa_3()
