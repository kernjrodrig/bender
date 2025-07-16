# Bender IA - Chatbot con Integración Jira

Un chatbot inteligente que integra con Jira y utiliza Ollama para procesamiento de lenguaje natural.

## 🚀 Despliegue Rápido

### Opción 1: Script Automático (Recomendado)
```bash
cd /home/javo/Documents/bot_guzdan
./deploy.sh
```

### Opción 2: Comandos Manuales
```bash
# Construir imagen
podman build -t bender-ia:latest .

# Ejecutar contenedor con restart automático
podman run -d \
    --name bender-ia \
    --restart unless-stopped \
    -p 8000:8000 \
    -e OLLAMA_URL=http://https://5aaf5f3a9d6b.ngrok-free.app \
    -e MODEL_NAME=llama3 \
    --health-cmd="curl -f http://localhost:8000/ || exit 1" \
    --health-interval=30s \
    --health-timeout=10s \
    --health-retries=3 \
    --health-start-period=40s \
    --memory=1g \
    bender-ia:latest
```

## 🔧 Gestión del Contenedor

### Comandos Útiles
```bash
# Ver logs en tiempo real
podman logs -f bender-ia

# Ver estado del contenedor
podman ps

# Reiniciar contenedor
podman restart bender-ia

# Detener contenedor
podman stop bender-ia

# Eliminar contenedor
podman rm -f bender-ia
```

## 🛠️ Solución de Problemas

### Error: "Refreshing container... acquiring lock"
Este error indica que hay un contenedor anterior que no se cerró correctamente.

**Solución:**
```bash
# Limpiar contenedores antiguos
podman rm -f bender-ia 2>/dev/null || true
podman system prune -f

# Reconstruir y ejecutar
./deploy.sh
```

### Error: Contenedor se cierra inesperadamente
El contenedor ahora tiene configuración robusta con:
- **Restart automático**: `--restart unless-stopped`
- **Health checks**: Verificación cada 30 segundos
- **Logging mejorado**: Logs rotativos
- **Manejo de señales**: Shutdown elegante

### Error: No se puede conectar a Ollama
Verificar que Ollama esté ejecutándose en la IP correcta:
```bash
# Verificar conectividad
curl http://192.168.10.14:11434/api/tags

# Si no responde, actualizar la URL en el contenedor
podman stop bender-ia
podman run -d --name bender-ia --restart unless-stopped -p 8000:8000 \
    -e OLLAMA_URL=http://NUEVA_IP:11434 \
    -e MODEL_NAME=llama3 \
    bender-ia:latest
```

## 📊 Monitoreo

### Health Check
El contenedor incluye health checks automáticos:
- **Intervalo**: 30 segundos
- **Timeout**: 10 segundos
- **Reintentos**: 3
- **Período inicial**: 40 segundos

### Logs
Los logs se rotan automáticamente:
- **Tamaño máximo**: 10MB por archivo
- **Archivos máximos**: 3 archivos

## 🔄 Reinicio Automático

El contenedor se reiniciará automáticamente en los siguientes casos:
- **Fallo de la aplicación**: Restart inmediato
- **Reinicio del sistema**: Restart automático
- **Error de health check**: Restart después de 3 fallos

## 🌐 Acceso

- **URL**: http://localhost:8000
- **API Chat**: POST /chat
- **API Models**: GET /models

## 📝 Variables de Entorno

| Variable | Valor por Defecto | Descripción |
|----------|-------------------|-------------|
| `OLLAMA_URL` | `http://192.168.10.14:11434` | URL del servidor Ollama |
| `MODEL_NAME` | `llama3` | Modelo de lenguaje a usar |

## 🏗️ Arquitectura

- **Backend**: FastAPI con Python 3.11
- **Frontend**: HTML/JavaScript estático
- **IA**: Ollama con modelo Llama3
- **Integración**: Jira API v3
- **Contenedor**: Podman con configuración robusta 