🧠 Proyecto: Sistema de Coordinación para Equipos de Estudio (SCEE)

🎯 Objetivo General

Sistema cliente-servidor concurrente para comunicación y gestión de recursos entre alumnos y profesores.

🚩 Estado: ETAPA 1 - Chat Broadcast Básico

Esta versión implementa un chat por broadcast simple.

Servidor: asyncio TCP para múltiples clientes.

Cliente: asyncio CLI (maneja stdin y socket).

Protocolo: JSON (protocol.py).

Tecnologías: Python 3.10+, asyncio, aiosqlite (preparado).

🚀 Cómo Ejecutar (Etapa 1)

1. Preparar Entorno Virtual

# Crear entorno
python -m venv .venv
# Activar (macOS/Linux)
source .venv/bin/activate
# Activar (Windows PowerShell)
.\.venv\Scripts\Activate.ps1


2. Instalar Dependencias

pip install -r requirements.txt


3. Iniciar el Servidor

En una terminal (desde la raíz del proyecto):

python -m src.server


4. Iniciar Clientes

En dos o más terminales nuevas:

python -m src.client


Ingresa un nombre de usuario. Los mensajes se reenvían a todos.

🧭 Próximos Pasos (Etapa 2)

Implementar aiosqlite.

Crear proceso de autenticación (auth_process.py).

Comunicar servidor y autenticación vía IPC (multiprocessing.Pipe).

Requerir login (action: "login").