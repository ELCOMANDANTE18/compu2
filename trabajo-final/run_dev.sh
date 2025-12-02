#!/bin/bash
# Script de instalación minimalista

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "Instalación completa. Para activar el entorno ejecuta: source .venv/bin/activate"