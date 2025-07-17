#!/bin/bash

# Script de limpieza para Bender IA
set -e

CONTAINERS=(bender-ia bender-frontend)
IMAGES=(bender-ia:latest bender-frontend:latest)

echo "🧹 Limpiando contenedores antiguos..."
for c in "${CONTAINERS[@]}"; do
    if podman ps -a --format "{{.Names}}" | grep -q "^${c}$"; then
        echo "📴 Deteniendo y eliminando contenedor: $c"
        podman stop $c 2>/dev/null || true
        podman rm $c 2>/dev/null || true
    fi
done

echo "🗑️  Eliminando imágenes antiguas..."
for i in "${IMAGES[@]}"; do
    if podman images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${i}$"; then
        echo "🗑️  Eliminando imagen: $i"
        podman rmi $i 2>/dev/null || true
    fi
done

echo "✅ Limpieza completada." 
