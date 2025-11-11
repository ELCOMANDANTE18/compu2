# src/auth_process.py
"""
Proceso de autenticación (IPC).
(Stub para Etapa 2)
"""

import logging
from multiprocessing import Pipe
from . import db_manager # (Eventualmente usará db_manager)

def auth_process_worker(pipe_conn: Pipe):
    """
    Función que se ejecuta en un proceso separado para manejar la autenticación.
    Escucha pedidos (usuario, clave) desde el pipe y responde.
    """
    logging.info("Proceso de autenticación iniciado (STUB).")
    try:
        while True:
            # Bloquea hasta recibir un mensaje del servidor principal
            request = pipe_conn.recv() 
            if request.get("command") == "shutdown":
                break
                
            if request.get("command") == "auth":
                user = request.get("user")
                pwd = request.get("password")
                
                # Aquí se llamaría a la lógica de BD (que es async,
                # pero este proceso puede tener su propio loop si es necesario,
                # o simplemente usar una conexión de BD sincrónica)
                logging.info(f"Auth_Process: Verificando {user}...")
                
                # Simulación (la lógica real usaría db_manager)
                if user.startswith("profe") and pwd == "123":
                    response = {"status": "ok", "rol": "profesor", "username": user}
                elif user.startswith("alumno") and pwd == "123":
                    response = {"status": "ok", "rol": "alumno", "username": user}
                else:
                    response = {"status": "error", "message": "Credenciales inválidas"}
                
                pipe_conn.send(response)

    except EOFError:
        logging.info("Proceso de autenticación: Pipe cerrado.")
    finally:
        logging.info("Proceso de autenticación terminado.")
        pipe_conn.close()