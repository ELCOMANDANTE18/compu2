import argparse
from http.server import SimpleHTTPRequestHandler, HTTPServer
from io import BytesIO
from socketserver import ThreadingMixIn
from PIL import Image
import socket
import threading
import time

class ThreadingHTTPServerV6(ThreadingMixIn, HTTPServer):
    address_family = socket.AF_INET6

def procesar_imagen_entrada(archivo_imagen, factor_escala):
    try:
        bytes_imagen = archivo_imagen.read()
        imagen_pil = Image.open(BytesIO(bytes_imagen))

        print(f"Servidor: Recibida imagen del cliente. Dimensiones originales: {imagen_pil.size}")

        if imagen_pil.mode != 'L':
            imagen_gris = imagen_pil.convert('L')
        else:
            imagen_gris = imagen_pil

        with BytesIO() as salida:
            imagen_gris.save(salida, format='JPEG')
            imagen_final = salida.getvalue()

        return imagen_final

    except Exception as error:
        print(f"Error procesando la imagen: {error}")
        return None

def enviar_imagen_final(socket, imagen_bytes_final):
    try:
        socket.sendall(len(imagen_bytes_final).to_bytes(4, byteorder='big'))
        socket.sendall(imagen_bytes_final)
    except Exception as error:
        print(f"Error enviando la imagen procesada: {error}")

class ManejadorImagenes(SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            longitud_contenido = int(self.headers['Content-Length'])
            bytes_imagen = self.rfile.read(longitud_contenido)

            imagen_final = procesar_imagen_entrada(BytesIO(bytes_imagen), factor_escala=0.5)

            if imagen_final is None:
                self.send_response(500)
                self.end_headers()
                return

            print(f"Servidor: Enviando imagen al servidor de escalado...")

            with socket.create_connection(('localhost', 8000), timeout=5) as socket_conexion:
                enviar_imagen_final(socket_conexion, imagen_final)

                longitud_datos = int.from_bytes(socket_conexion.recv(4), byteorder='big')
                bytes_imagen_escalada = socket_conexion.recv(longitud_datos)

                print("Servidor: Recibida imagen escalada del servidor de escalado.")

            timestamp = int(time.time())
            nombre_archivo_escalada_principal = f"procesamiento_magico_{timestamp}.jpg"
            with open(nombre_archivo_escalada_principal, 'wb') as archivo:
                archivo.write(bytes_imagen_escalada)

            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            self.wfile.write(bytes_imagen_escalada)

            print(f"Servidor: Imagen procesada enviada al cliente y almacenada como {nombre_archivo_escalada_principal}.")

        except Exception as error:
            print(f"Error manejando la solicitud POST: {error}")

def iniciar_servidor(direccion_ip, puerto_escucha):
    manejador = ManejadorImagenes
    direccion = (direccion_ip, puerto_escucha)

    try:
        servidor_http = ThreadingHTTPServerV6 if ':' in direccion_ip else HTTPServer
        with servidor_http((direccion_ip, puerto_escucha), manejador) as servidor:
            print(f"Servidor escuchando en {direccion[0]}:{direccion[1]}")
            servidor.serve_forever()

    except KeyboardInterrupt:
        print('Deteniendo el servidor.')

def main():
    analizador = argparse.ArgumentParser(description='Procesamiento de imágenes')
    analizador.add_argument('-i', '--ip', required=True, help='Dirección de escucha')
    analizador.add_argument('-p', '--puerto', type=int, required=True, help='Puerto de escucha')
    argumentos = analizador.parse_args()

    try:
        iniciar_servidor(argumentos.ip, argumentos.puerto)
    except KeyboardInterrupt:
        print('Deteniendo el servidor.')

if __name__ == '__main__':
    main()