# src/auth_process.py
"""
Proceso de autenticación (IPC).
Recibe pedidos de autenticación desde el servidor principal vía Pipe
y los verifica contra la base de datos usando db_manager.
"""

import logging
import asyncio
from multiprocessing.connection import Connection
from . import db_manager

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def auth_process_worker(pipe_conn: Connection):
    """
    Función que se ejecuta en un proceso separado para manejar la autenticación.
    Escucha pedidos (usuario, clave) desde el pipe y responde.
    """
    log.info("Proceso de autenticación iniciado.")
    # Creamos un loop de asyncio para este proceso
    # loop = asyncio.get_event_loop()

    try:
        while True:
            # Bloquea hasta recibir un mensaje del servidor principal
            request = pipe_conn.recv()
            if request.get("command") == "shutdown":
                log.info("Comando 'shutdown' recibido.")
                break
                
            if request.get("command") == "auth":
                user = request.get("user")
                pwd = request.get("password")
                
                log.info(f"Auth_Process: Verificando {user}...")
                
                try:
                    # Ejecutamos la corrutina de verificación de BD
                    # en un nuevo loop de asyncio para este proceso.
                    user_data = asyncio.run(db_manager.verify_user(user, pwd))
                    
                    if user_data:
                        response = {"status": "ok", "user_data": user_data}
                    else:
                        response = {"status": "error", "message": "Credenciales inválidas"}
                
                except Exception as e:
                    log.error(f"Error en el worker de autenticación durante verify_user: {e}")
                    response = {"status": "error", "message": "Error interno del servidor"}
                
                pipe_conn.send(response)

    except EOFError:
        log.info("Proceso de autenticación: Pipe cerrado (normal al apagar).")
    except Exception as e:
        log.error(f"Error inesperado en auth_process_worker: {e}")
    finally:
        log.info("Proceso de autenticación terminado.")
        pipe_conn.close()