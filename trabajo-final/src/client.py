# src/client.py
"""
Cliente CLI interactivo para el sistema SCEE.
Usa asyncio para manejar la entrada del usuario (stdin) y los
mensajes del servidor (socket) de forma concurrente.
"""

import asyncio
import sys
import logging
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
                if message.get("action") == "broadcast":
                    sender = message.get("sender", "Sistema")
                    content = message.get("content", "")
                    # Imprime el mensaje y vuelve a mostrar el prompt "> "
                    print(f"\r[{sender}]: {content}\nTu > ", end="")
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

async def send_to_server(writer: asyncio.StreamWriter, username: str):
    """
    Lee la entrada del usuario (stdin) de forma asíncrona y la envía al servidor.
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

            # Etapa 1: Enviamos un mensaje de chat simple
            message_bytes = protocol.create_message(
                "message",
                username=username,
                content=message_content
            )
            
            if message_bytes:
                writer.write(message_bytes)
                await writer.drain()

        except Exception as e:
            logging.error(f"Error al enviar mensaje: {e}")
            break

    writer.close()
    await writer.wait_closed()
    logging.info("Saliendo del sender...")

async def main_client():
    """
    Función principal del cliente.
    """
    print("--- Cliente SCEE ---")
    username = input("Ingresa tu nombre de usuario: ")
    
    logging.info(f"Conectando a {HOST}:{PORT} como '{username}'...")
    
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        logging.info("¡Conectado exitosamente!")
        print("Escribe tus mensajes y presiona Enter. Escribe 'quit' para salir.")
        print("Tu > ", end="") # Prompt inicial

        # Ejecutamos las dos tareas concurrentemente
        # listen_task: escucha al servidor
        # send_task: escucha al usuario (stdin)
        listen_task = asyncio.create_task(listen_to_server(reader))
        send_task = asyncio.create_task(send_to_server(writer, username))

        # Esperamos a que cualquiera de las dos tareas termine
        # (por ejemplo, si el servidor se cae o el usuario escribe 'quit')
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