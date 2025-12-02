# src/server.py
"""
Servidor principal del Sistema de Coordinación para Equipos de Estudio (SCEE).
Utiliza asyncio para manejar múltiples clientes concurrentes.
Etapa 2: Autenticación (IPC + DB) y Login obligatorio.
"""

import asyncio
import logging
import multiprocessing
from .config import HOST, PORT, MESSAGE_DELIMITER
from . import protocol
from . import db_manager
from . import auth_process

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='[SERVER] %(asctime)s - %(message)s')

# --- ESTA ES LA LÍNEA CLAVE ---
# Definimos 'log' para usarlo en todo el módulo.
log = logging.getLogger(__name__)
# -----------------------------

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # self.clients ahora es un diccionario donde la clave es el objeto 'writer'
        # y el valor es un dict con el estado y datos del usuario.
        # self.clients[writer] = {"addr": addr, "state": "connecting", "user": None}
        self.clients = {}
        
        # --- Configuración de IPC para Autenticación ---
        # Ahora 'log.info' está definido y funciona
        log.info("Iniciando pipe IPC para autenticación...")
        # parent_conn es para el Server, child_conn es para el Proceso
        self.auth_pipe_parent, auth_pipe_child = multiprocessing.Pipe()
        
        # Iniciar el proceso de autenticación
        self.auth_proc = multiprocessing.Process(
            target=auth_process.auth_process_worker,
            args=(auth_pipe_child,)
        )
        self.auth_proc.start()
        log.info(f"Proceso de autenticación iniciado (PID: {self.auth_proc.pid}).")


    async def authenticate(self, writer: asyncio.StreamWriter, login_message: dict):
        """
        Maneja la lógica de autenticación usando el proceso IPC.
        """
        addr = writer.get_extra_info('peername')
        user = login_message.get("user")
        pwd = login_message.get("password")

        if not user or not pwd:
            response_bytes = protocol.create_message("login_fail", message="Usuario y clave requeridos.")
            writer.write(response_bytes)
            await writer.drain()
            return

        # Las llamadas a pipe (send/recv) son bloqueantes.
        # Las ejecutamos en un hilo separado para no bloquear el loop de asyncio.
        loop = asyncio.get_running_loop()
        request = {"command": "auth", "user": user, "password": pwd}
        
        try:
            # 1. Enviar la solicitud (bloqueante)
            await loop.run_in_executor(None, self.auth_pipe_parent.send, request)
            # 2. Recibir la respuesta (bloqueante)
            response = await loop.run_in_executor(None, self.auth_pipe_parent.recv)

            # Procesar la respuesta
            if response.get("status") == "ok":
                user_data = response.get("user_data", {})
                log.info(f"Login exitoso para {user} desde {addr}.")
                # Actualizar el estado del cliente
                self.clients[writer] = {
                    "addr": addr,
                    "state": "authenticated",
                    "user": user_data
                }
                response_bytes = protocol.create_message("login_success", user=user_data)
                writer.write(response_bytes)
                await writer.drain()
            else:
                log.warn(f"Login fallido para {user} desde {addr}: {response.get('message')}")
                response_bytes = protocol.create_message("login_fail", message=response.get("message"))
                writer.write(response_bytes)
                await writer.drain()

        except Exception as e:
            log.error(f"Error durante la autenticación IPC para {user}: {e}")
            try:
                response_bytes = protocol.create_message("login_fail", message="Error interno del servidor.")
                writer.write(response_bytes)
                await writer.drain()
            except ConnectionError:
                pass # El cliente ya se desconectó


    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Corrutina para manejar la conexión de un cliente individual.
        """
        addr = writer.get_extra_info('peername')
        # Corregido: usar 'log' en lugar de 'logging'
        log.info(f"Nuevo cliente conectado (en espera de login): {addr}")
        # Registrar al cliente con estado 'connecting'
        self.clients[writer] = {"addr": addr, "state": "connecting", "user": None}

        try:
            while True:
                data_bytes = await reader.readuntil(MESSAGE_DELIMITER)
                if not data_bytes:
                    break

                message = protocol.parse_message(data_bytes)
                if not message:
                    continue

                client_state = self.clients[writer]
                action = message.get("action")
                
                # --- Lógica de Estado ---
                
                if client_state["state"] == "connecting":
                    if action == "login":
                        await self.authenticate(writer, message)
                    else:
                        # Rechazar cualquier otra acción si no está logueado
                        response_bytes = protocol.create_message("error", message="Debes iniciar sesión primero.")
                        writer.write(response_bytes)
                        await writer.drain()
                
                elif client_state["state"] == "authenticated":
                    # El cliente está logueado
                    if action == "message":
                        await self.broadcast(message, sender_writer=writer)
                    # (Aquí irán 'join_room', 'upload_file', etc. en futuras etapas)
                    else:
                        response_bytes = protocol.create_message("error", message=f"Acción '{action}' desconocida o no permitida.")
                        writer.write(response_bytes)
                        await writer.drain()

        except asyncio.IncompleteReadError:
            # Corregido: usar 'log' en lugar de 'logging'
            log.warning(f"Cliente {addr} desconectado (conexión cerrada).")
        except ConnectionResetError:
            # Corregido: usar 'log' en lugar de 'logging'
            log.warning(f"Cliente {addr} desconectado (conexión reseteada).")
        except Exception as e:
            # Corregido: usar 'log' en lugar de 'logging'
            log.error(f"Error inesperado con el cliente {addr}: {e}")
        finally:
            # Limpiar la conexión
            if writer in self.clients:
                user_info = self.clients[writer].get('user')
                username = user_info.get('username') if user_info else 'Desconocido'
                # Corregido: usar 'log' en lugar de 'logging'
                log.info(f"Cliente {username} ({addr}) desconectado.")
                del self.clients[writer]
                
            writer.close()
            await writer.wait_closed()
            # Corregido: usar 'log' en lugar de 'logging'
            log.info(f"Conexión con {addr} cerrada formalmente.")

    async def broadcast(self, message: dict, sender_writer=None):
        """
        Envía un mensaje a todos los clientes AUTENTICADOS.
        """
        if message.get("action") != "message":
            return

        sender_state = self.clients.get(sender_writer)
        if not sender_state or not sender_state.get("user"):
            # Corregido: usar 'log' en lugar de 'logging'
            log.warn("Intento de broadcast de un usuario no autenticado.")
            return

        content = message.get("content", "")
        username = sender_state["user"].get("username", "Anónimo")
        
        broadcast_msg_bytes = protocol.create_message(
            "broadcast",
            sender=username,
            content=content
        )

        if not broadcast_msg_bytes:
            return

        log.info(f"Broadcasting de {username}: {content}")
        
        for writer, client_state in list(self.clients.items()):
            # Enviar solo a clientes autenticados y que no sean el remitente
            if client_state["state"] == "authenticated" and writer != sender_writer:
                try:
                    writer.write(broadcast_msg_bytes)
                    await writer.drain()
                except ConnectionError:
                    # Corregido: usar 'log' en lugar de 'logging'
                    log.warning(f"Error al enviar a {client_state['addr']}, puede estar desconectándose.")


    async def start(self):
        """
        Prepara la BD y luego inicia el servidor.
        """
        # 1. Inicializar la Base de Datos
        await db_manager.init_db()
        
        # 2. Iniciar el servidor TCP
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )

        addr = server.sockets[0].getsockname()
        # Corregido: usar 'log' en lugar de 'logging'
        log.info(f"Servidor SCEE (Etapa 2) escuchando en {addr}")

        async with server:
            await server.serve_forever()

    def stop(self):
        """
        Detiene los procesos hijos (IPC) limpiamente.
        """
        # Corregido: usar 'log' en lugar de 'logging'
        log.info("Deteniendo el servidor y los procesos hijos...")
        try:
            # Enviar señal de apagado al proceso de autenticación
            self.auth_pipe_parent.send({"command": "shutdown"})
        except Exception as e:
            # Corregido: usar 'log' en lugar de 'logging'
            log.error(f"Error al enviar señal de shutdown a auth_process: {e}")
        
        # Esperar a que el proceso termine
        self.auth_proc.join(timeout=3)
        
        # Si sigue vivo, forzarlo
        if self.auth_proc.is_alive():
            # Corregido: usar 'log' en lugar de 'logging'
            log.warn("El proceso de autenticación no terminó, forzando terminación.")
            self.auth_proc.terminate()
            
        self.auth_pipe_parent.close()
        # Corregido: usar 'log' en lugar de 'logging'
        log.info("Proceso de autenticación detenido.")


if __name__ == "__main__":
    
    print("Iniciando servidor (Etapa 2)...")
    server = Server(HOST, PORT)
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        # Corregido: usar 'log' en lugar de 'logging'
        log.info("Servidor detenido por el usuario.")
    finally:
        server.stop()