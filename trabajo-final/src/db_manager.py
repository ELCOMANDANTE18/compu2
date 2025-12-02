# src/db_manager.py
"""
Módulo para el manejo asíncrono de la base de datos (Etapa 2).
Usará aiosqlite.
"""

import logging
import aiosqlite
from .config import DB_TYPE, DB_NAME

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def init_db():
    """
    Inicializa la base de datos y crea las tablas si no existen.
    Inserta datos de prueba.
    """
    log.info(f"Inicializando base de datos ({DB_TYPE}) en '{DB_NAME}'...")
    async with aiosqlite.connect(DB_NAME) as db:
        # Habilitar claves foráneas
        await db.execute("PRAGMA foreign_keys = ON;")

        # --- Tabla de Usuarios ---
        await db.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('profesor', 'alumno'))
        );
        """)

        # --- Tabla de Salas ---
        await db.execute("""
        CREATE TABLE IF NOT EXISTS salas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        );
        """)

        # --- Tabla de Mensajes (para Etapa 3) ---
        await db.execute("""
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contenido TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER NOT NULL,
            sala_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (sala_id) REFERENCES salas (id)
        );
        """)

        # --- Insertar datos de prueba (si no existen) ---
        try:
            await db.executemany(
                "INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
                [
                    ('profe', '123', 'profesor'), # Contraseña en texto plano (¡malo!)
                    ('alumno', '456', 'alumno')
                ]
            )
        except aiosqlite.IntegrityError:
            log.info("Usuarios de prueba ya existen.")

        try:
            await db.executemany(
                "INSERT INTO salas (nombre) VALUES (?)",
                [('General',), ('Física Cuántica',)]
            )
        except aiosqlite.IntegrityError:
            log.info("Salas de prueba ya existen.")

        await db.commit()
    log.info("Base de datos inicializada correctamente.")


async def verify_user(username, password) -> dict | None:
    """
    Verifica las credenciales del usuario en la BD.
    Devuelve los datos del usuario si es válido, o None si no.
    """
    log.info(f"Verificando usuario {username} en la BD...")
    async with aiosqlite.connect(DB_NAME) as db:
        # Configurar row_factory para obtener resultados como diccionarios
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            "SELECT * FROM usuarios WHERE username = ? AND password = ?",
            (username, password)
        )
        user_row = await cursor.fetchone()
        
        if user_row:
            log.info(f"Usuario {username} verificado con éxito.")
            return dict(user_row) # Convertir la Fila (Row) a un dict
            
    log.warn(f"Fallo la verificación para el usuario {username}.")
    return None