# src/client.py
"""
Cliente CLI SCEE.
Etapa 3.5: Navegación completa (Login -> Menu Salas <-> Chat).
"""

import asyncio
import sys
import logging
import getpass
from .config import HOST, PORT, MESSAGE_DELIMITER
from . import protocol

logging.basicConfig(level=logging.INFO, format='%(message)s')

async def chat_listener(reader):
    """Escucha mensajes del servidor mientras se está en una sala."""
    while True:
        try:
            data = await reader.readuntil(MESSAGE_DELIMITER)
            msg = protocol.parse_message(data)
            if not msg: continue
            
            action = msg.get("action")
            
            if action == "broadcast":
                sender = msg.get("sender")
                content = msg.get("content")
                print(f"\r[{sender}]: {content}\nTu > ", end="")
            elif action == "leave_success":
                # Señal del servidor de que salimos correctamente
                print("\n<<< Has salido de la sala.")
                break
            elif action == "error":
                print(f"\r[ERROR]: {msg.get('message')}\nTu > ", end="")
                
        except asyncio.IncompleteReadError:
            print("\n[!] Desconectado del servidor.")
            break
        except asyncio.CancelledError:
            # Tarea cancelada (normal al salir)
            break

async def chat_sender(writer):
    """Envía mensajes y maneja el comando 'quit' local."""
    loop = asyncio.get_running_loop()
    while True:
        try:
            msg = await loop.run_in_executor(None, sys.stdin.readline)
            msg = msg.strip()
            
            if msg.lower() == "quit":
                # Enviar señal de salir al servidor
                writer.write(protocol.create_message("leave_room"))
                await writer.drain()
                break # Rompe el bucle de envío

            if msg:
                writer.write(protocol.create_message("message", content=msg))
                await writer.drain()
        except:
            break

async def start_chat_mode(reader, writer):
    """Maneja la sesión de chat activa."""
    print("Escribe mensajes. Escribe 'quit' para volver al menú de salas.\nTu > ", end="")
    
    listener_task = asyncio.create_task(chat_listener(reader))
    sender_task = asyncio.create_task(chat_sender(writer))
    
    # Esperamos a que cualquiera de las dos termine
    done, pending = await asyncio.wait(
        [sender_task, listener_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    # --- CORRECCIÓN DE CONCURRENCIA ---
    if sender_task in done:
        # Caso: El usuario escribió 'quit' y el sender terminó.
        # IMPORTANTE: No cancelar el listener todavía. Debemos esperar a recibir
        # el 'leave_success' del servidor para limpiar el buffer de red.
        # El listener se cerrará solo cuando llegue ese mensaje.
        await listener_task
    else:
        # Caso: El listener terminó primero (el servidor nos sacó o se cayó la conexión).
        # Aquí sí debemos cancelar el sender porque está esperando input del usuario.
        sender_task.cancel()
        try:
            await sender_task
        except asyncio.CancelledError:
            pass

async def select_room(reader, writer):
    """Muestra lista y permite elegir sala. Retorna True si entra, False si sale del app."""
    # 1. Pedir lista
    writer.write(protocol.create_message("get_rooms"))
    await writer.drain()
    
    # 2. Recibir lista
    try:
        data = await reader.readuntil(MESSAGE_DELIMITER)
        msg = protocol.parse_message(data)
    except:
        return False
    
    print("\n=== MENÚ DE SALAS ===")
    for room in msg.get("rooms", []):
        print(f"[{room['id']}] {room['nombre']}")
    print("---------------------")
    print("Escribe el ID para entrar, o 'quit' para cerrar el programa.")
    
    # 3. Elegir
    loop = asyncio.get_running_loop()
    while True:
        choice = await loop.run_in_executor(None, input, "Opción > ")
        choice = choice.strip()
        
        if choice.lower() == "quit":
            return False # Salir del programa

        writer.write(protocol.create_message("join", room_id=choice))
        await writer.drain()
        
        # 4. Confirmación
        data = await reader.readuntil(MESSAGE_DELIMITER)
        resp = protocol.parse_message(data)
        
        if resp.get("action") == "join_success":
            print(f"\n>>> Unido a {resp.get('room_name')}. Cargando historial...")
            for old_msg in resp.get("history", []):
                print(f"[{old_msg['username']}]: {old_msg['contenido']}")
            print("-" * 30)
            return True # Entró a sala
        else:
            print(f"Error: {resp.get('message')}")

async def main():
    print("--- SCEE Cliente v0.4 (Navegable) ---")
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
    except:
        print("No se pudo conectar al servidor.")
        return

    # --- LOGIN ---
    user = input("Usuario: ")
    pwd = getpass.getpass("Contraseña: ")
    writer.write(protocol.create_message("login", user=user, password=pwd))
    await writer.drain()
    
    data = await reader.readuntil(MESSAGE_DELIMITER)
    resp = protocol.parse_message(data)
    
    if resp.get("action") != "login_success":
        print("Login fallido.")
        writer.close()
        return
    
    print(f"Hola {resp['user']['username']}!")

    # --- BUCLE PRINCIPAL DE NAVEGACIÓN ---
    while True:
        # Intentar seleccionar sala
        ingreso_a_sala = await select_room(reader, writer)
        
        if ingreso_a_sala:
            # Si entró, iniciar modo chat
            await start_chat_mode(reader, writer)
            # Al volver de start_chat_mode, el bucle while se repite (vuelve al menú)
        else:
            # Si select_room devolvió False (usuario puso 'quit' en el menú)
            print("Cerrando sesión...")
            break

    writer.close()
    await writer.wait_closed()
    print("Adiós.")

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass