#!/bin/bash

# Script de inicio robusto para la aplicación Bender
set -e

echo "🚀 Iniciando Bender IA..."

# Función para manejar señales de terminación
cleanup() {
    echo "📴 Recibida señal de terminación, cerrando aplicación..."
    # Enviar señal SIGTERM a todos los procesos
    if [ -n "$UVICORN_PID" ]; then
        kill -TERM "$UVICORN_PID" 2>/dev/null || true
        wait "$UVICORN_PID" 2>/dev/null || true
    fi
    if [ -n "$TELEGRAM_BOT_PID" ]; then
        kill -TERM "$TELEGRAM_BOT_PID" 2>/dev/null || true
        wait "$TELEGRAM_BOT_PID" 2>/dev/null || true
    fi
    echo "✅ Aplicación cerrada correctamente"
    exit 0
}

# Configurar manejadores de señales
trap cleanup SIGTERM SIGINT

# Verificar variables de entorno
echo "🔧 Configuración:"
echo "   - OLLAMA_URL: ${OLLAMA_URL:-https://5aaf5f3a9d6b.ngrok-free.app}"
echo "   - MODEL_NAME: ${MODEL_NAME:-llama3}"
echo "   - Puerto: 8000"

# Verificar conectividad con Ollama
echo "🔍 Verificando conectividad con Ollama..."
if curl -s --max-time 10 "${OLLAMA_URL:-https://5aaf5f3a9d6b.ngrok-free.app}/api/tags" > /dev/null; then
    echo "✅ Ollama está accesible"
else
    echo "⚠️  Advertencia: No se puede conectar a Ollama, pero continuando..."
fi

# Iniciar el bot de Telegram en segundo plano
echo "🤖 Iniciando bot de Telegram..."
python telegram_bot.py &
TELEGRAM_BOT_PID=$!

# Iniciar la aplicación con uvicorn
echo "🎯 Iniciando servidor uvicorn..."
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level info \
    --timeout-keep-alive 300 \
    --access-log \
    --use-colors &
UVICORN_PID=$!

# Esperar a que cualquiera de los procesos termine
wait $UVICORN_PID $TELEGRAM_BOT_PID 