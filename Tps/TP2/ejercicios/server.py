import argparse
import cgi
from http.server import SimpleHTTPRequestHandler
from io import BytesIO
import requests
import socket
import multiprocessing
import uuid
import os
import socketserver
import threading
import cv2
import numpy as np

class ImageHandler:
    @staticmethod
    def process_image(image_data, scale_factor, queue):
        try:
            # Convertir los datos binarios a una matriz de imagen utilizando OpenCV
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)

            # Enviar la imagen al servidor de redimensionamiento
            resize_url = "http://localhost:7501"  # Cambiar si el servidor de redimensionamiento se ejecuta en otro host o puerto
            headers = {"Scale-Factor": str(scale_factor), "Content-Type": "image/jpeg"}
            _, resized_image_data = cv2.imencode('.jpg', image)
            
            print("Enviando datos...")
            response = requests.post(resize_url, data=resized_image_data.tobytes(), headers=headers)
            
            print("Datos recibidos.")
            
            # Obtener la imagen redimensionada del servidor de redimensionamiento
            resized_image_data = response.content

            # Colocar la imagen procesada en la cola
            queue.put(resized_image_data)
            print("Procesamiento terminado.")
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")

class MyRequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        content_type, pdict = cgi.parse_header(self.headers['content-type'])
        if content_type == 'multipart/form-data':
            form_data = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )

            if 'file' in form_data:
                file_item = form_data['file']
                image_data = file_item.file.read()

                # Obtener el factor de escala del formulario
                scale_factor = float(form_data.getvalue('scale_factor'))

                # Genera un nombre único para la imagen procesada
                filename = f"resized_image_{uuid.uuid4()}.jpg"

                # Crea una cola de comunicación para enviar la imagen al proceso hijo
                queue = multiprocessing.Queue()
                
                # Inicia el proceso hijo para procesar la imagen
                process = multiprocessing.Process(target=ImageHandler.process_image, args=(image_data, scale_factor, queue))
                process.start()

                # Bloquea el servidor HTTP hasta que se complete el procesamiento de la imagen
                process.join()

                # Obtiene la imagen procesada desde la cola
                resized_image_data = queue.get()

                print("Guardando imagen...")
                # Guarda la imagen en el sistema de archivos
                with open(filename, 'wb') as file:
                    file.write(resized_image_data)
                    print("Imagen guardada.")

                # Imprime el tamaño de la imagen recibida y el nombre del archivo guardado
                print(f"Imagen recibida. Tamaño: {len(image_data)} bytes. Guardada como: {filename}")

                # Envía la imagen procesada al cliente
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(f"Imagen recibida. Tamaño: {len(image_data)} bytes. Guardada como: {filename}".encode('utf-8'))

def run_server(ip, port, ipv6=False):
    address = "::" if ipv6 else ip
    handler = MyRequestHandler

    with socketserver.TCPServer((address, port), handler) as httpd:
        httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(f"Servidor HTTP escuchando en http://{address}:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor HTTP para procesar imágenes y redimensionarlas.")
    parser.add_argument("-i", "--ip", required=True, help="Dirección IP de escucha.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Número de puerto para escuchar.")
    parser.add_argument("--ipv6", action="store_true", help="Habilitar soporte para IPv6.")

    args = parser.parse_args()

    run_server(args.ip, args.port, args.ipv6)
