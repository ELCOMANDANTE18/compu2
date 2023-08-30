#!/usr/bin/python3
import socket
import threading

def worker_thread(connection):
    print("Inicializabdi hilo de trabajo...")

    while True:
        data = connection.recv(1024)
        if data.decode() == '\r\n':
            continue
        else:
            message = data.decode()
            print("Datos Recibidos: %s" % message)
            if message == "exit\r\n":
                reacion = "\nDespedida!\r\n".encode("utf-8")
                connection.send(reacion)
                print("El cliente cancelo el enlace.\r\n")
                connection.close()
                break
            else:
                response_msg = message.upper() + "\r\n"
                connection.send(response_msg.encode("utf-8"))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host_address = ""
listening_port = 50001

server_socket.bind((host_address, listening_port))
server_socket.listen(5)

while True:
    client_socket, client_address = server_socket.accept()

    print("Conectada a %s" % str(client_address))

    initial_msg = 'Se aprecia tu conexion/presencia' + "\r\n"
    client_socket.send(initial_msg.encode('ascii'))

    worker = threading.Thread(target=worker_thread, args=(client_socket,))
    worker.start()
    
    