#!/usr/bin/env bash
# LeadForge — instalación de cero.
# Uso: bash setup.sh

set -e

cd "$(dirname "$0")"

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╭───────────────────────────────────────╮${NC}"
echo -e "${CYAN}│   LeadForge — setup                   │${NC}"
echo -e "${CYAN}╰───────────────────────────────────────╯${NC}"
echo

# 1. Comprobar Python 3.10+
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}✗ python3 no está instalado.${NC}"
    echo "  Instala Python 3.10 o superior y vuelve a ejecutar este script."
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo -e "${RED}✗ Se necesita Python 3.10+; tienes $PY_VERSION.${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $PY_VERSION OK"

# 2. Crear venv si no existe
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}→${NC} Creando entorno virtual en .venv/ ..."
    python3 -m venv .venv
else
    echo -e "${GREEN}✓${NC} .venv ya existe"
fi

PIP=".venv/bin/pip"
PY=".venv/bin/python"

# 3. Instalar dependencias
echo -e "${YELLOW}→${NC} Instalando dependencias (puede tardar 1-2 min) ..."
"$PIP" install --upgrade pip --quiet
"$PIP" install -r requirements.txt --quiet
echo -e "${GREEN}✓${NC} Dependencias instaladas"

# 4. Copiar .env.example a .env si no existe
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env creado desde .env.example"
    NEEDS_KEYS=1
else
    echo -e "${GREEN}✓${NC} .env ya existe (no lo toco)"
    NEEDS_KEYS=0
fi

echo
echo -e "${CYAN}╭───────────────────────────────────────╮${NC}"
echo -e "${CYAN}│   Listo                               │${NC}"
echo -e "${CYAN}╰───────────────────────────────────────╯${NC}"
echo

if [ "$NEEDS_KEYS" -eq 1 ]; then
    echo -e "${YELLOW}Siguiente paso:${NC} edita ${CYAN}.env${NC} y pega tus API keys."
    echo "  Guía paso a paso: docs/CONFIGURACION_APIS.md"
    echo
fi

echo -e "Prueba tu primera prospección:"
echo -e "  ${CYAN}.venv/bin/python -m src.prospeccion --query \"fisioterapeuta\" --location \"Madrid, España\" --max-results 20${NC}"
echo
echo -e "El CSV aparecerá en ${CYAN}output/${NC}."
