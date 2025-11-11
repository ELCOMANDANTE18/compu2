# src/db_manager.py
"""
Módulo para el manejo asíncrono de la base de datos (Etapa 2+).
Usará aiosqlite o asyncpg.
"""

import logging
from .config import DB_TYPE, DB_NAME

async def init_db():
    """
    Inicializa la base de datos y crea las tablas si no existen.
    (Stub para Etapa 2)
    """
    logging.info(f"Inicializando base de datos ({DB_TYPE})... (STUB)")
    # Aquí iría la lógica con aiosqlite/asyncpg
    # Ejemplo con aiosqlite:
    # async with aiosqlite.connect(DB_NAME) as db:
    #     await db.execute("CREATE TABLE IF NOT EXISTS ...")
    #     await db.commit()
    print("Gestor de BD (stub) - Listo.")

async def verify_user(username, password):
    """
    Verifica las credenciales del usuario en la BD.
    (Stub para Etapa 2)
    """
    logging.info(f"Verificando usuario {username}... (STUB)")
    # Simulación:
    if username == "profe" and password == "1234":
        return {"id": 1, "username": "profe", "rol": "profesor"}
    if username == "alumno" and password == "1234":
        return {"id": 2, "username": "alumno", "rol": "alumno"}
    return None