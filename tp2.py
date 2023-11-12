import argparse
import os
import http.server
import socketserver
import socket
import cgi
import shutil
import base64
from multiprocessing import Process, Pipe

try:
    from PIL import Image
except ImportError:
    print("Error: Error al importar Pillow. \nInstale Pillow en su equipo y luego vuelva a iniciar el servidor.\nComando: pip install Pillow")
    exit()

class HandlerManual(http.server.BaseHTTPRequestHandler):
    def image_grey_conversion(self, image_path, conn):
        with Image.open(image_path) as img:
            converted_img = img.convert('L')
            grayscale_image_path = "grayscale_image.jpg"
            converted_img.save(grayscale_image_path)
            conn.send(grayscale_image_path)

    def child_process(self, image_path, conn):
        p = Process(target=self.image_grey_conversion, args=(image_path, conn))
        p.start()
        p.join()

    def do_GET(self):
        if self.path == "/download":
            with open("grayscale_image.jpg", 'rb') as f:
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.send_header("Content-Disposition", "attachment; filename=grayscale_image.jpg")
                self.end_headers()
                shutil.copyfileobj(f, self.wfile)
            
            os.remove("grayscale_image.jpg")
        else:
            if self.path == "/index" or self.path == "/":
                file_path = os.path.join(os.path.dirname(__file__), "index.html")
                self.serve_html(file_path)
            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write('Not Found'.encode())



    def do_POST(self):
        content_type, _ = cgi.parse_header(self.headers.get('content-type'))

        if content_type == 'multipart/form-data':
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
            if "file" in form and form["file"].file:
                try:
                    parent_conn, child_conn = Pipe()
                    with open("uploaded_image.jpg", 'wb') as f:
                        shutil.copyfileobj(form["file"].file, f)
                    
                    try:
                        with Image.open("uploaded_image.jpg") as img:
                            pass
                    except:
                        os.remove("uploaded_image.jpg")
                        self.send_response(302)
                        self.send_header('Location', '/index')
                        self.end_headers()
                        return

                    self.child_process("uploaded_image.jpg", child_conn)
                    transformed_image_path = parent_conn.recv()

                    if transformed_image_path:
                        self.serve_transformed_image(transformed_image_path)
                        return
                except Exception as e:
                    self.send_response(302)
                    self.send_header('Location', '/index')
                    self.end_headers()
                    return

            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write('Error al cargar la imagen'.encode())
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write('Solicitud no válida'.encode())



    def serve_html(self, file_path):
        with open(file_path, "rb") as f:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f.read())

    def serve_transformed_image(self, image_path):
        with open(image_path, 'rb') as f:
            encoded_image = base64.b64encode(f.read()).decode('utf-8')

        with open("transformed_image.html", "r") as html_file:
            html = html_file.read().replace("{{encoded_image}}", encoded_image)

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

        os.remove("uploaded_image.jpg")

def main():
    parser = argparse.ArgumentParser(description='Simple HTTP Server with argparse')
    parser.add_argument('-i', '--ip', required=True, help='Listening address')
    parser.add_argument('-p', '--port', required=True, type=int, help='Listening port')
    args = parser.parse_args()

    ip_type = socket.AF_INET if ':' not in args.ip else socket.AF_INET6
    server_address = (args.ip, args.port)

    socketserver.ThreadingTCPServer.address_family = ip_type
    socketserver.ThreadingTCPServer.allow_reuse_address = True

    my_http_handler = HandlerManual
    http = socketserver.ThreadingTCPServer(server_address, my_http_handler)

    print(f"Ejecutando servidor en el enlace {args.ip}, puerto {args.port}")
    http.serve_forever()

if __name__ == "__main__":
    main()  