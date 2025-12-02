# 🧠 Sistema de Coordinación para Equipos de Estudio (SCEE)

Proyecto cliente-servidor concurrente diseñado para facilitar la comunicación y la gestión de recursos entre alumnos y profesores.

## 🎯 Objetivo

Desarrollar un sistema escalable y seguro que permita el intercambio de mensajes y la coordinación de recursos dentro de equipos de estudio. En esta primera etapa, el objetivo es proporcionar un chat por broadcast para validar la comunicación básica entre clientes y servidor.

## 🚩 Estado del proyecto — Etapa 1

Actualmente la aplicación ofrece un chat por broadcast básico:

- **Servidor**: Implementado con `asyncio` (TCP) y capaz de atender múltiples clientes simultáneamente.
- **Cliente**: Aplicación CLI basada en `asyncio` que gestiona entrada por stdin y socket de red.
- **Protocolo**: Mensajes en formato JSON definidos en `src/protocol.py`.
- **Tecnologías**: Python 3.10+, `asyncio`. Preparado para integrar `aiosqlite` en fases posteriores.

---

## 🚀 Guía rápida — Cómo ejecutar (Etapa 1)

1) Crear y activar entorno virtual (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
# .\.venv\Scripts\Activate.ps1  # Windows PowerShell
```

2) Instalar dependencias:

```bash
pip install -r requirements.txt
```

3) Iniciar el servidor (desde la raíz del proyecto):

```bash
python -m src.server
```

4) Iniciar uno o más clientes en terminales separadas:

```bash
python -m src.client
```

Cuando se inicia, el cliente solicita un nombre de usuario; los mensajes se reenvían (broadcast) a todos los clientes conectados.

---

## 🔧 Estructura del proyecto (resumen)

- `src/server.py`: Lógica del servidor.
- `src/client.py`: Lógica del cliente CLI.
- `src/protocol.py`: Formato JSON del protocolo de mensajes.
- `src/auth_process.py`: (planificado) proceso de autenticación.
- `requirements.txt`: dependencias del proyecto.

---

## 🧭 Próximos pasos (Etapa 2 y roadmap)

En las siguientes fases se planea:

- Integrar `aiosqlite` para persistencia de datos (usuarios, mensajes, etc.).
- Añadir un proceso de autenticación separado (`auth_process.py`) y comunicación IPC con el servidor (por ejemplo, `multiprocessing.Pipe`).
- Forzar login en el flujo de cliente/servidor (acción `login`).
- Implementar medidas de seguridad y validación de datos.

---

## 🤝 Contribuciones

Si quieres contribuir: abre un issue con tu propuesta o envía PRs con cambios. Incluye pruebas y una breve descripción del objetivo del cambio.

---

## 📝 Licencia

Revisa el archivo de licencia del repositorio o consulta al autor del proyecto para más detalles.

---

Si deseas, puedo añadir secciones adicionales como ejemplos de mensajes JSON del protocolo, un diagrama de arquitectura o un script de inicio rápido (make / scripts). Indica qué prefieres y lo implemento.