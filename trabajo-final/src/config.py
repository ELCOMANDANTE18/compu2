# src/config.py
"""
Configuración centralizada para el servidor y cliente SCEE.
"""

# Configuración del servidor
HOST = '127.0.0.1'
PORT = 8888

# Configuración de la base de datos (para Etapa 2+)
DB_TYPE = 'sqlite'  # O 'postgresql'
DB_NAME = 'scee.db'

# Tamaño del buffer para sockets
BUFFER_SIZE = 1024

# Delimitador de mensajes
# Usamos un terminador de línea para separar mensajes JSON en el stream TCP
MESSAGE_DELIMITER = b'\n'