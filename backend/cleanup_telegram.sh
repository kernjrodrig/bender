#!/bin/bash

echo "🧹 Limpiando procesos duplicados del bot de Telegram..."

# Buscar y terminar todos los procesos de telegram_bot.py
PIDS=$(pgrep -f "telegram_bot.py")

if [ -n "$PIDS" ]; then
    echo "📱 Procesos encontrados: $PIDS"
    echo "🛑 Terminando procesos..."
    
    for pid in $PIDS; do
        echo "   - Terminando PID: $pid"
        kill -TERM "$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
    done
    
    # Esperar un momento para que se cierren
    sleep 3
    
    # Verificar si quedaron procesos
    REMAINING=$(pgrep -f "telegram_bot.py")
    if [ -n "$REMAINING" ]; then
        echo "⚠️  Algunos procesos persisten, forzando cierre..."
        pkill -KILL -f "telegram_bot.py"
    fi
    
    echo "✅ Limpieza completada"
else
    echo "✅ No se encontraron procesos del bot de Telegram"
fi

# También limpiar procesos de Python que puedan estar colgados
PYTHON_PIDS=$(pgrep -f "python.*telegram")
if [ -n "$PYTHON_PIDS" ]; then
    echo "🐍 Limpiando procesos Python relacionados..."
    pkill -f "python.*telegram"
fi

echo "✨ Limpieza finalizada" 