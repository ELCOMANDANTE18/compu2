# src/db_manager.py
"""
Módulo para el manejo asíncrono de la base de datos (Etapa 3).
Incluye manejo de salas y mensajes persistentes.
"""

import logging
import aiosqlite
from .config import DB_TYPE, DB_NAME

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def init_db():
    """
    Inicializa la base de datos, tablas y datos semilla.
    """
    log.info(f"Inicializando base de datos en '{DB_NAME}'...")
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("PRAGMA foreign_keys = ON;")

        # Tablas (Usuarios, Salas, Mensajes)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL CHECK(rol IN ('profesor', 'alumno'))
        );
        """)
        
        await db.execute("""
        CREATE TABLE IF NOT EXISTS salas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        );
        """)

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

        # Datos semilla
        try:
            await db.executemany(
                "INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
                [('profe', '123', 'profesor'), ('alumno', '456', 'alumno')]
            )
        except aiosqlite.IntegrityError:
            pass

        try:
            await db.executemany(
                "INSERT INTO salas (nombre) VALUES (?)",
                [('General',), ('Física I',), ('Matemática II',)]
            )
        except aiosqlite.IntegrityError:
            pass

        await db.commit()
    log.info("Base de datos lista.")

async def verify_user(username, password) -> dict | None:
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, username, rol FROM usuarios WHERE username = ? AND password = ?",
            (username, password)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

# --- NUEVAS FUNCIONES ETAPA 3 ---

async def get_rooms() -> list[dict]:
    """Obtiene la lista de todas las salas."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT id, nombre FROM salas")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def save_message(user_id: int, room_id: int, content: str):
    """Guarda un mensaje en la base de datos."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO mensajes (usuario_id, sala_id, contenido) VALUES (?, ?, ?)",
            (user_id, room_id, content)
        )
        await db.commit()

async def get_chat_history(room_id: int, limit=20) -> list[dict]:
    """Recupera los últimos mensajes de una sala."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        # Hacemos JOIN para traer el nombre del usuario
        query = """
            SELECT m.contenido, m.timestamp, u.username 
            FROM mensajes m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.sala_id = ?
            ORDER BY m.timestamp DESC
            LIMIT ?
        """
        cursor = await db.execute(query, (room_id, limit))
        rows = await cursor.fetchall()
        # Invertimos la lista para mostrar los más viejos arriba y nuevos abajo
        return [dict(row) for row in rows][::-1]