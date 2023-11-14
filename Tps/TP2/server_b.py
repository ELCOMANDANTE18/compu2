import argparse
import socket
from PIL import Image
from io import BytesIO
import threading

def redimensionar_imagen(imagen, factor_redimension):
    nueva_dimension = tuple(int(dim * factor_redimension) for dim in imagen.size)
    imagen_redimensionada = imagen.resize(nueva_dimension, Image.ANTIALIAS)
    return imagen_redimensionada

def manejar_cliente_redimension(socket_cliente, factor_redimension):
    try:
        longitud_datos = int.from_bytes(socket_cliente.recv(4), byteorder='big')
        imagen_bytes = socket_cliente.recv(longitud_datos)

        imagen_pillow = Image.open(BytesIO(imagen_bytes))
        
        print(f"Servidor: Recibida imagen del servidor principal. Dimensiones: {imagen_pillow.size}")

        imagen_redimensionada = redimensionar_imagen(imagen_pillow, factor_redimension)

        print(f"Servidor: Dimensiones después de redimensionar: {imagen_redimensionada.size}")

        with BytesIO() as output:
            imagen_redimensionada.save(output, format='JPEG')
            imagen_bytes_redimensionada = output.getvalue()

        enviar_imagen_redimensionada(socket_cliente, imagen_bytes_redimensionada)
    except Exception as e:
        print(f"Error manejando el cliente de redimension: {e}")
    finally:
        socket_cliente.close()

def enviar_imagen_redimensionada(sock, imagen_bytes_redimensionada):
    try:
        longitud_datos = len(imagen_bytes_redimensionada)
        sock.sendall(longitud_datos.to_bytes(4, byteorder='big'))
        sock.sendall(imagen_bytes_redimensionada)
        print("Servidor: Imagen redimensionada enviada al servidor principal.")

    except BrokenPipeError:
        print("La conexión fue cerrada por el otro extremo.")
    except Exception as e:
        print(f"Error al enviar la imagen redimensionada: {e}")
    finally:
        sock.close()

def servidor_redimension(ip, puerto, factor_redimension):
    socket_servidor = socket.socket(socket.AF_INET6 if ':' in ip else socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_servidor.bind((ip, puerto))
    except socket.error:
        print("Error al vincular el socket.")
        return

    socket_servidor.listen(5)
    print(f"Servidor escuchando en {ip}:{puerto}")

    try:
        while True:
            socket_cliente, direccion = socket_servidor.accept()
            print(f"Conexión aceptada desde {direccion[0]}:{direccion[1]}")

            threading.Thread(target=manejar_cliente_redimension, args=(socket_cliente, factor_redimension)).start()
    except KeyboardInterrupt:
        print('Deteniendo el servidor.')
    finally:
        socket_servidor.close()

def main():
    analizador = argparse.ArgumentParser(description='Servidor de Redimension')
    analizador.add_argument('-i', '--ip', required=True, help='Dirección de escucha')
    analizador.add_argument('-p', '--puerto', type=int, required=True, help='Puerto de escucha')
    analizador.add_argument('-s', '--escala', type=float, required=True, help='Factor de redimension')
    argumentos = analizador.parse_args()

    try:
        servidor_redimension(argumentos.ip, argumentos.puerto, argumentos.escala)
    except KeyboardInterrupt:
        print('Deteniendo el servidor.')

if __name__ == '__main__':
    main()
    
    