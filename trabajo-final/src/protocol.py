# src/protocol.py
"""
Define el protocolo de comunicación basado en JSON.
Incluye funciones para serializar y deserializar mensajes.
"""

import json
import logging
from .config import MESSAGE_DELIMITER

def create_message(action: str, **kwargs) -> bytes:
    """
    Crea un mensaje JSON serializado y listo para enviar por el socket.
    Añade un delimitador de nueva línea.
    """
    message = {"action": action}
    message.update(kwargs)
    try:
        json_message = json.dumps(message)
        # Añadimos el delimitador para que el servidor sepa dónde termina el mensaje
        return json_message.encode('utf-8') + MESSAGE_DELIMITER
    except TypeError as e:
        logging.error(f"Error al serializar el mensaje: {e} - Data: {message}")
        return b''

def parse_message(data_bytes: bytes) -> dict | None:
    """
    Parsea un mensaje JSON (bytes) recibido del socket.
    Espera que el delimitador ya haya sido manejado por el reader.
    """
    try:
        # Quitamos el delimitador y decodificamos
        data_str = data_bytes.strip().decode('utf-8')
        if not data_str:
            return None
        return json.loads(data_str)
    except json.JSONDecodeError:
        logging.warning(f"Mensaje JSON mal formado recibido: {data_bytes}")
        return None
    except UnicodeDecodeError:
        logging.warning(f"Error de decodificación de mensaje: {data_bytes}")
        return None