# src/client.py
"""
Cliente CLI interactivo para el sistema SCEE.
Etapa 2: Implementa flujo de Login.
"""

import asyncio
import sys
import logging
import getpass # Para ocultar la contraseña
from .config import HOST, PORT, MESSAGE_DELIMITER
from . import protocol

logging.basicConfig(level=logging.INFO, format='[CLIENT] %(asctime)s - %(message)s')

async def listen_to_server(reader: asyncio.StreamReader):
    """
    Escucha continuamente los mensajes del servidor y los imprime.
    """
    while True:
        try:
            data_bytes = await reader.readuntil(MESSAGE_DELIMITER)
            if not data_bytes:
                logging.warning("El servidor cerró la conexión (data vacía).")
                break
                
            message = protocol.parse_message(data_bytes)
            if message:
                # Manejo de mensajes recibidos
                action = message.get("action")
                if action == "broadcast":
                    sender = message.get("sender", "Sistema")
                    content = message.get("content", "")
                    # Imprime el mensaje y vuelve a mostrar el prompt "> "
                    print(f"\r[{sender}]: {content}\nTu > ", end="")
                elif action == "error":
                    # Errores enviados por el servidor
                    print(f"\r[ERROR Servidor]: {message.get('message', 'Error desconocido')}\nTu > ", end="")
                else:
                    # Otros mensajes del sistema
                    print(f"\r[Sistema]: {message}\nTu > ", end="")
            
        except asyncio.IncompleteReadError:
            logging.warning("Conexión perdida con el servidor.")
            break
        except Exception as e:
            logging.error(f"Error al leer del servidor: {e}")
            break
    logging.info("Saliendo del listener del servidor...")


async def send_to_server(writer: asyncio.StreamWriter):
    """
    Lee la entrada del usuario (stdin) de forma asíncrona y la envía al servidor.
    En Etapa 2, ya no necesita el 'username', el servidor lo sabe.
    """
    loop = asyncio.get_running_loop()
    
    while True:
        try:
            # Usamos run_in_executor para ejecutar el 'input' bloqueante
            # en un hilo separado, sin bloquear el loop de asyncio.
            # sys.stdin.readline() es una alternativa que captura el \n
            message_content = await loop.run_in_executor(
                None, 
                sys.stdin.readline
            )
            message_content = message_content.strip() # Quitar el \n

            if not message_content:
                continue

            if message_content.lower() == 'quit':
                logging.info("Desconectando...")
                break

            # Etapa 2: Solo enviamos la acción y el contenido.
            # El servidor sabe quiénes somos por nuestra conexión.
            message_bytes = protocol.create_message(
                "message",
                content=message_content
            )
            
            # --- BLOQUE CORREGIDO ---
            # El error estaba aquí. Este 'if' necesita 
            # el código indentado debajo de él.
            if message_bytes:
                writer.write(message_bytes)
                await writer.drain()
            # --- FIN BLOQUE CORREGIDO ---

        except Exception as e:
            logging.error(f"Error al enviar mensaje: {e}")
            break

    # Esta parte se ejecuta fuera del 'while True' cuando se rompe el loop
    writer.close()
    await writer.wait_closed()
    logging.info("Saliendo del sender...")

async def main_client():
    """
    Función principal del cliente.
    Implementa el flujo de login.
    """
    print("--- Cliente SCEE ---")
    username = input("Usuario: ")
    # Usamos getpass para que la contraseña no haga eco en la terminal
    password = getpass.getpass("Contraseña: ")
    
    logging.info(f"Conectando a {HOST}:{PORT} como '{username}'...")
    
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        logging.info("Conectado. Enviando credenciales...")

        # --- Flujo de Login ---
        login_msg_bytes = protocol.create_message("login", user=username, password=password)
        writer.write(login_msg_bytes)
        await writer.drain()

        # Esperar respuesta de login
        login_response_bytes = await reader.readuntil(MESSAGE_DELIMITER)
        login_response = protocol.parse_message(login_response_bytes)

        if login_response and login_response.get("action") == "login_success":
            user_data = login_response.get('user', {})
            logging.info(f"Login exitoso. Bienvenido {user_data.get('username')} (Rol: {user_data.get('rol')})")
        else:
            error_msg = login_response.get('message', 'Credenciales incorrectas')
            logging.error(f"Login fallido: {error_msg}")
            writer.close()
            await writer.wait_closed()
            return # Terminar el cliente
        # --- Fin Flujo de Login ---

        print("Escribe tus mensajes y presiona Enter. Escribe 'quit' para salir.")
        print("Tu > ", end="") # Prompt inicial

        # Ejecutamos las dos tareas concurrentemente
        listen_task = asyncio.create_task(listen_to_server(reader))
        # 'send_to_server' ya no necesita el username
        send_task = asyncio.create_task(send_to_server(writer))

        # Esperamos a que cualquiera de las dos tareas termine
        done, pending = await asyncio.wait(
            [listen_task, send_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancelamos las tareas pendientes para limpiar
        for task in pending:
            task.cancel()
        
    except ConnectionRefusedError:
        logging.error("No se pudo conectar al servidor. ¿Está corriendo?")
    except Exception as e:
        logging.error(f"Ocurrió un error: {e}")
    finally:
        logging.info("Cliente desconectado.")


if __name__ == "__main__":
    # Para correr el cliente:
    # python -m src.client
    try:
        asyncio.run(main_client())
    except KeyboardInterrupt:
        print("\nSaliendo...")