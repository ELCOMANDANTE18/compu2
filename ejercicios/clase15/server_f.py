#!/usr/bin/python3
import socket
import os
import sys
import signal

signal.signal(signal.SIGCHLD, signal.SIG_IGN)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host_address = ""
listening_port = 50002

server_socket.bind((host_address, listening_port))
server_socket.listen(5)

while True:
    client_socket, client_address = server_socket.accept()

    print("Connection from %s" % str(client_address))

    welcome_msg = "Thanks for connecting" + "\r\n"
    client_socket.send(welcome_msg.encode('ascii'))
    
    try:
        child_pid = os.fork()
        if not child_pid:
            while True:
                msg = client_socket.recv(1024)
                if not msg.decode():
                    break
                else:
                    data = msg.decode()
                    print("Recibido: %s" % data)
                    if data == "exit\r\n":
                        response = "\nHasta_luego\r\n".encode("utf-8")
                        client_socket.send(response)
                        client_socket.close()
                        print("Cliente %s ha cerrado la conexion\r\n" % str(client_address))
                        sys.exit(0)
                    else:
                        response_msg = data.upper() + "\r\n"
                        client_socket.send(response_msg.encode("utf-8"))
    except BrokenPipeError:
        print("El Cliente ha cerrado la conexion")

    client_socket.close()