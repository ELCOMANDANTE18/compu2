# src/storage_process.py
"""
Proceso de almacenamiento de recursos (IPC).
(Stub para Etapa 4)
"""

import logging
from multiprocessing import Pipe

def storage_process_worker(pipe_conn: Pipe):
    """
    Función que se ejecuta en un proceso separado para manejar archivos.
    """
    logging.info("Proceso de almacenamiento iniciado (STUB).")
    try:
        while True:
            request = pipe_conn.recv()
            if request.get("command") == "shutdown":
                break

            if request.get("command") == "upload":
                filename = request.get("filename")
                filedata_b64 = request.get("data")
                sala = request.get("sala")
                
                logging.info(f"Storage_Process: Recibido archivo '{filename}' para la sala '{sala}'...")
                # Aquí iría la lógica para:
                # 1. Decodificar base64
                # 2. Guardar el archivo en el filesystem (ej: 'uploads/sala/filename')
                # 3. Registrar los metadatos en la BD (usando db_manager)
                
                # Simulación
                response = {"status": "ok", "message": f"Archivo '{filename}' guardado."}
                pipe_conn.send(response)

    except EOFError:
        logging.info("Proceso de almacenamiento: Pipe cerrado.")
    finally:
        logging.info("Proceso de almacenamiento terminado.")
        pipe_conn.close()