
import socket

# Definir la dirección IP y el puerto del servidor
IP = 'localhost'
PORT = 7500

# Crear un objeto de socket y establecer una conexión con el servidor
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((IP, PORT))

# Enviar datos al servidor
mensaje = 'Hola, servidor!'
cliente.send(mensaje.encode())

# Recibir datos del servidor
datos = cliente.recv(1024)
print(datos.decode())

# Cerrar la conexión
cliente.close()
import socket
import argparse

def cliente(ip, puerto, archivo_imagen):
    try:
        # Conectar al servidor de escalado
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((ip, puerto))

            # Enviar nombre del archivo de imagen al servidor
            client_socket.sendall(archivo_imagen.encode())

            # Recibir la imagen procesada del servidor
            with open('imagen_procesada.jpg', 'wb') as f:
                data = client_socket.recv(1024)
                while data:
                    f.write(data)
                    data = client_socket.recv(1024)

            print('Imagen procesada recibida con éxito.')

    except Exception as e:
        print(f'Error en la comunicación con el servidor: {str(e)}')

def main():
    parser = argparse.ArgumentParser(description='Cliente para el servidor de escalado de imágenes')
    parser.add_argument('-i', '--ip', required=True, help='Dirección IP del servidor de escalado')
    parser.add_argument('-p', '--puerto', type=int, required=True, help='Puerto del servidor de escalado')
    parser.add_argument('-f', '--archivo', required=True, help='Nombre del archivo de imagen a procesar')
    args = parser.parse_args()

    cliente(args.ip, args.puerto, args.archivo)

if __name__ == '__main__':
    main()
