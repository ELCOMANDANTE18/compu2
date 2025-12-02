# src/server.py
"""
Servidor principal SCEE.
Etapa 3.5: Soporte para Salas de Chat, Persistencia y Navegación (Salir de sala).
"""

import asyncio
import logging
import multiprocessing
from .config import HOST, PORT, MESSAGE_DELIMITER
from . import protocol
from . import db_manager
from . import auth_process

logging.basicConfig(level=logging.INFO, format='[SERVER] %(asctime)s - %(message)s')
log = logging.getLogger(__name__)

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # self.clients[writer] = {"addr":..., "state":..., "user":..., "room_id": None}
        self.clients = {}
        
        # IPC Autenticación
        log.info("Iniciando proceso de autenticación...")
        self.auth_pipe_parent, auth_pipe_child = multiprocessing.Pipe()
        self.auth_proc = multiprocessing.Process(
            target=auth_process.auth_process_worker,
            args=(auth_pipe_child,)
        )
        self.auth_proc.start()

    async def authenticate(self, writer, login_message):
        """Maneja el login vía IPC."""
        user = login_message.get("user")
        pwd = login_message.get("password")
        
        loop = asyncio.get_running_loop()
        request = {"command": "auth", "user": user, "password": pwd}
        
        try:
            await loop.run_in_executor(None, self.auth_pipe_parent.send, request)
            response = await loop.run_in_executor(None, self.auth_pipe_parent.recv)

            if response.get("status") == "ok":
                user_data = response.get("user_data", {})
                log.info(f"Login OK: {user}")
                # Estado pasa a 'authenticated', pero aún no tiene sala ('room_id': None)
                self.clients[writer] = {
                    "addr": writer.get_extra_info('peername'),
                    "state": "authenticated",
                    "user": user_data,
                    "room_id": None
                }
                writer.write(protocol.create_message("login_success", user=user_data))
            else:
                writer.write(protocol.create_message("login_fail", message="Credenciales inválidas"))
            await writer.drain()

        except Exception as e:
            log.error(f"Error Auth IPC: {e}")
            writer.close()

    async def send_room_list(self, writer):
        """Envía la lista de salas disponibles al cliente."""
        rooms = await db_manager.get_rooms()
        writer.write(protocol.create_message("room_list", rooms=rooms))
        await writer.drain()

    async def join_room(self, writer, message):
        """Une al usuario a una sala y envía el historial."""
        room_id = message.get("room_id")
        try:
            room_id = int(room_id)
        except (ValueError, TypeError):
            writer.write(protocol.create_message("error", message="ID de sala inválido"))
            return

        client_state = self.clients[writer]
        
        # Si ya estaba en una sala, avisar que salió primero (opcional, pero limpio)
        if client_state.get("room_id"):
             await self.leave_room(writer, None, notify_client=False)

        client_state["room_id"] = room_id
        client_state["state"] = "in_room"
        
        room_name = f"Sala {room_id}" 

        log.info(f"Usuario {client_state['user']['username']} unido a Sala {room_id}")
        
        # Obtener historial
        history = await db_manager.get_chat_history(room_id)
        
        writer.write(protocol.create_message("join_success", room_id=room_id, room_name=room_name, history=history))
        await writer.drain()

        # Avisar a otros en la sala
        await self.broadcast({
            "action": "message", 
            "content": f"--> {client_state['user']['username']} ha entrado a la sala."
        }, sender_writer=writer, system_msg=True)

    async def leave_room(self, writer, message, notify_client=True):
        """Saca al usuario de la sala actual y lo devuelve al estado 'authenticated'."""
        client_state = self.clients.get(writer)
        if not client_state or not client_state.get("room_id"):
            return

        old_room_id = client_state["room_id"]
        username = client_state['user']['username']
        
        # 1. Broadcast de despedida a la sala vieja
        await self.broadcast({
            "action": "message",
            "content": f"<-- {username} ha salido de la sala."
        }, sender_writer=writer, system_msg=True)

        log.info(f"Usuario {username} salió de Sala {old_room_id}")

        # 2. Resetear estado
        client_state["room_id"] = None
        client_state["state"] = "authenticated"

        # 3. Confirmar al cliente (solo si fue solicitado explícitamente)
        if notify_client:
            writer.write(protocol.create_message("leave_success"))
            await writer.drain()

    async def handle_message(self, writer, message):
        """Maneja el envío de mensajes de chat."""
        client_state = self.clients[writer]
        room_id = client_state.get("room_id")
        user_id = client_state["user"]["id"]
        content = message.get("content")

        if not room_id:
            return

        # 1. Guardar en BD (Persistencia)
        await db_manager.save_message(user_id, room_id, content)

        # 2. Broadcast a la sala
        await self.broadcast(message, sender_writer=writer)

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        self.clients[writer] = {"addr": addr, "state": "connecting", "user": None, "room_id": None}
        log.info(f"Conexión: {addr}")

        try:
            while True:
                data = await reader.readuntil(MESSAGE_DELIMITER)
                msg = protocol.parse_message(data)
                if not msg: continue

                action = msg.get("action")
                state = self.clients[writer]["state"]

                if state == "connecting":
                    if action == "login": await self.authenticate(writer, msg)
                    else: pass 
                
                elif state == "authenticated":
                    # Usuario logueado (en el lobby)
                    if action == "get_rooms": await self.send_room_list(writer)
                    elif action == "join": await self.join_room(writer, msg)
                    elif action == "login": pass 
                    else: writer.write(protocol.create_message("error", message="Debes unirte a una sala."))
                
                elif state == "in_room":
                    # Usuario chateando en sala
                    if action == "message": await self.handle_message(writer, msg)
                    elif action == "leave_room": await self.leave_room(writer, msg) # NUEVA ACCIÓN
                    elif action == "join": await self.join_room(writer, msg) 
                    elif action == "get_rooms": await self.send_room_list(writer)

        except Exception as e:
            log.warning(f"Error con cliente {addr}: {e}")
        finally:
            if writer in self.clients:
                del self.clients[writer]
            writer.close()
            await writer.wait_closed()

    async def broadcast(self, message, sender_writer, system_msg=False):
        """Envía mensaje solo a usuarios en la MISMA sala."""
        sender_state = self.clients.get(sender_writer)
        if not sender_state: return

        room_id = sender_state.get("room_id")
        # Si el usuario ya salió (room_id es None), no podemos hacer broadcast basado en él.
        # Pero en leave_room guardamos old_room antes de borrarlo, así que el broadcast
        # se hace antes de borrar el room_id.
        
        username = sender_state["user"]["username"] if not system_msg else "Sistema"
        
        out_msg = protocol.create_message("broadcast", sender=username, content=message.get("content"))

        for target_writer, state in self.clients.items():
            if state.get("room_id") == room_id:
                try:
                    target_writer.write(out_msg)
                    await target_writer.drain()
                except: pass

    async def start(self):
        await db_manager.init_db()
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        log.info(f"Servidor SCEE Etapa 3.5 en {self.host}:{self.port}")
        async with server: await server.serve_forever()

    def stop(self):
        self.auth_pipe_parent.send({"command": "shutdown"})
        self.auth_proc.join()

if __name__ == "__main__":
    srv = Server(HOST, PORT)
    try: asyncio.run(srv.start())
    except KeyboardInterrupt: pass
    finally: srv.stop()