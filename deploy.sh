#!/bin/bash

# Script de despliegue para Bender IA
set -e

CONTAINER_NAME="bender-ia"
IMAGE_NAME="bender-ia:latest"

echo "🚀 Desplegando Bender IA..."

# Función para limpiar contenedores antiguos
cleanup_old_containers() {
    echo "🧹 Limpiando contenedores antiguos..."
    
    # Detener y eliminar contenedor existente si existe
    if podman ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo "📴 Deteniendo contenedor existente..."
        podman stop ${CONTAINER_NAME} 2>/dev/null || true
        podman rm ${CONTAINER_NAME} 2>/dev/null || true
    fi
    
    # Eliminar imagen antigua si existe
    if podman images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${IMAGE_NAME}$"; then
        echo "🗑️  Eliminando imagen antigua..."
        podman rmi ${IMAGE_NAME} 2>/dev/null || true
    fi
}

# Función para construir la imagen
build_image() {
    echo "🔨 Construyendo imagen Docker..."
    podman build -t ${IMAGE_NAME} .
}

# Función para ejecutar el contenedor
run_container() {
    echo "🎯 Ejecutando contenedor..."
    podman run -d \
        --name ${CONTAINER_NAME} \
        --restart unless-stopped \
        -p 8000:8000 \
        -e OLLAMA_URL=http://192.168.10.14:11434 \
        -e MODEL_NAME=llama3 \
        --health-cmd="curl -f http://localhost:8000/ || exit 1" \
        --health-interval=30s \
        --health-timeout=10s \
        --health-retries=3 \
        --health-start-period=40s \
        --memory=1g \
        ${IMAGE_NAME}
}

# Función para verificar el estado
check_status() {
    echo "📊 Verificando estado del contenedor..."
    sleep 5
    
    if podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo "✅ Contenedor ejecutándose correctamente"
        echo "🌐 Aplicación disponible en: http://localhost:8000"
        
        # Mostrar logs
        echo "📋 Últimos logs:"
        podman logs --tail 10 ${CONTAINER_NAME}
    else
        echo "❌ Error: El contenedor no está ejecutándose"
        echo "📋 Logs de error:"
        podman logs ${CONTAINER_NAME} 2>/dev/null || echo "No se pueden obtener logs"
        exit 1
    fi
}

# Función para mostrar comandos útiles
show_commands() {
    echo ""
    echo "🔧 Comandos útiles:"
    echo "   Ver logs: podman logs -f ${CONTAINER_NAME}"
    echo "   Ver estado: podman ps"
    echo "   Detener: podman stop ${CONTAINER_NAME}"
    echo "   Reiniciar: podman restart ${CONTAINER_NAME}"
    echo "   Eliminar: podman rm -f ${CONTAINER_NAME}"
}

# Ejecutar el despliegue
cleanup_old_containers
build_image
run_container
check_status
show_commands

echo "🎉 Despliegue completado!" 