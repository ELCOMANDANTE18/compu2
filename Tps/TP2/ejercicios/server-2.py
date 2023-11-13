from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
import io
import cv2
import numpy as np

class ResizeRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        image_data = self.rfile.read(content_length)
        scale_factor = float(self.headers['Scale-Factor'])
        
        try:
            # Convertir los datos binarios a una matriz de imagen utilizando OpenCV
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            # Redimensionar la imagen
            resized_image = cv2.resize(image, (0, 0), fx=scale_factor, fy=scale_factor)

            # Convertir la imagen redimensionada a datos binarios
            _, resized_image_data = cv2.imencode('.jpg', resized_image)

            # Enviar la imagen redimensionada de vuelta al servidor principal
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(resized_image_data)))
            self.end_headers()
            self.wfile.write(resized_image_data.tobytes())
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")

def run_resize_server(port):
    handler = ResizeRequestHandler
    with HTTPServer(('', port), handler) as httpd:
        print(f"Servidor de redimensionamiento escuchando en el puerto {port}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_resize_server(7501)
