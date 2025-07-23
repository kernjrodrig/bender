#!/bin/bash

# Uso: ./cambiar_ollama_url.sh NUEVA_URL

NUEVA_URL="$1"

if [ -z "$NUEVA_URL" ]; then
  echo "Uso: $0 NUEVA_URL"
  exit 1
fi

# Cambia en docker-compose.yml
sed -i "s|OLLAMA_URL=.*|OLLAMA_URL=$NUEVA_URL|g" docker-compose.yml

# Cambia en main.py (os.getenv)
sed -i "s|os.getenv(\"OLLAMA_URL\", \".*\"|os.getenv(\"OLLAMA_URL\", \"$NUEVA_URL\"|g" main.py

# Cambia en start.sh
sed -i "s|OLLAMA_URL=.*|OLLAMA_URL=$NUEVA_URL|g" start.sh

echo "¡Listo! OLLAMA_URL actualizado a $NUEVA_URL en los tres archivos."