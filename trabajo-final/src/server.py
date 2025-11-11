# src/server.py
"""
Servidor principal del Sistema de Coordinación para Equipos de Estudio (SCEE).
Utiliza asyncio para manejar múltiples clientes concurrentes.
Etapa 1: Infraestructura base (TCP Async + JSON) y broadcast de mensajes.
"""

import asyncio
import logging
from .config import HOST, PORT, MESSAGE_DELIMITER
from . import protocol

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='[SERVER] %(asctime)s - %(message)s')

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # Mantiene un registro de los clientes conectados
        # (writer, addr) -> username (cuando se implemente login)
        # Por ahora: (addr) -> writer
        self.clients = {}

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Corrutina para manejar la conexión de un cliente individual.
        """
        addr = writer.get_extra_info('peername')
        logging.info(f"Nuevo cliente conectado: {addr}")
        self.clients[addr] = writer

        try:
            while True:
                # Usamos readuntil para leer un mensaje completo terminado por el delimitador
                data_bytes = await reader.readuntil(MESSAGE_DELIMITER)

                if not data_bytes:
                    # Cliente desconectado (aunque readuntil debería lanzar IncompleteReadError)
                    break

                # Parsear el mensaje
                message = protocol.parse_message(data_bytes)
                if message:
                    logging.info(f"Mensaje recibido de {addr}: {message}")
                    # Etapa 1: Simplemente hacemos broadcast del mensaje a todos los demás
                    await self.broadcast(message, sender_addr=addr)

        except asyncio.IncompleteReadError:
            logging.warning(f"Cliente {addr} desconectado (conexión cerrada).")
        except ConnectionResetError:
            logging.warning(f"Cliente {addr} desconectado (conexión reseteada).")
        except Exception as e:
            logging.error(f"Error inesperado con el cliente {addr}: {e}")
        finally:
            # Limpiar la conexión
            if addr in self.clients:
                del self.clients[addr]
            writer.close()
            await writer.wait_closed()
            logging.info(f"Conexión con {addr} cerrada.")

    async def broadcast(self, message: dict, sender_addr=None):
        """
        Envía un mensaje a todos los clientes conectados, opcionalmente
        exceptuando al remitente.
        """
        # Por ahora, solo reenviamos el contenido del mensaje para el chat
        if message.get("action") == "message":
            content = message.get("content", "")
            username = message.get("username", "Anónimo")
            
            # Preparamos el mensaje de broadcast
            broadcast_msg_bytes = protocol.create_message(
                "broadcast",
                sender=username,
                content=content
            )

            if not broadcast_msg_bytes:
                return

            logging.info(f"Broadcasting: {broadcast_msg_bytes.decode().strip()}")
            
            # Usamos una lista temporal para evitar problemas si self.clients cambia
            for addr, writer in list(self.clients.items()):
                if addr != sender_addr:
                    try:
                        writer.write(broadcast_msg_bytes)
                        await writer.drain()
                    except ConnectionError:
                        logging.warning(f"Error al enviar a {addr}, puede estar desconectándose.")
                        # (handle_client se encargará de limpiarlo si falla)


    async def start(self):
        """
        Inicia el servidor.
        """
        server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )

        addr = server.sockets[0].getsockname()
        logging.info(f"Servidor SCEE escuchando en {addr}")

        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    # Este bloque solo se ejecuta si corres 'python -m src.server'
    # Asume que estás en el directorio 'final/'
    
    # Para que los imports relativos funcionen (from . import protocol)
    # es mejor correrlo como módulo desde el directorio raíz 'final/':
    # python -m src.server
    
    print("Iniciando servidor...")
    server = Server(HOST, PORT)
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logging.info("Servidor detenido por el usuario.")