# Bender IA - Chatbot con Integración Jira

Un chatbot inteligente que integra con Jira y utiliza Ollama para procesamiento de lenguaje natural.

## 🚀 Despliegue Completo con Podman y Docker Compose

### **Requisitos previos**
- Tener instalado Podman y podman-compose (o Docker y docker-compose).
- Clonar este repositorio y ubicarse en la raíz del proyecto.

### **1. Configura tus variables de entorno**

Edita el archivo `docker-compose.yml` si necesitas cambiar:
- La URL de Ollama (`OLLAMA_URL`)
- El modelo (`MODEL_NAME`)
- Si quieres activar el bot de Telegram (`ENABLE_TELEGRAM_BOT=true` o `false`)

### **2. Construye las imágenes**

```bash
podman-compose build
```

### **3. Levanta los servicios**

```bash
podman-compose up -d
```

Esto levantará:
- **Backend** (FastAPI) en el puerto 8000
- **Frontend** (React + nginx) en el puerto 5173
- **Bot de Telegram** (opcional, según variable de entorno)

### **4. Accede a la aplicación**

- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Backend:** [http://localhost:8000](http://localhost:8000)

### **5. Logs y gestión**

```bash
# Ver logs de todos los servicios
podman-compose logs -f

# Detener los servicios
podman-compose down
```

## 🛠️ Solución de Problemas con Compose

- Si cambias variables de entorno, reconstruye el frontend:
  ```bash
  podman-compose build frontend
  podman-compose up -d frontend
  ```
- Si tienes errores de red, asegúrate de que los servicios estén en la misma red definida por Compose.
- Si el bot de Telegram no debe ejecutarse, pon `ENABLE_TELEGRAM_BOT=false` en el `docker-compose.yml`.

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
| `ENABLE_TELEGRAM_BOT` | `false` | Activa o desactiva el bot de Telegram |

## 🏗️ Arquitectura

- **Backend**: FastAPI con Python 3.11
- **Frontend**: React + nginx
- **IA**: Ollama con modelo Llama3
- **Integración**: Jira API v3
- **Contenedor**: Podman con configuración robusta 
