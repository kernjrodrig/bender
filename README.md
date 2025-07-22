# Bender IA - Chatbot con Integración Jira

Un chatbot inteligente que integra con Jira y utiliza Ollama para procesamiento de lenguaje natural.

## 🚀 Despliegue Completo con Podman y Docker Compose

### **Requisitos previos**
- Tener instalado Podman y podman-compose (o Docker y docker-compose).
- Clonar este repositorio y ubicarse en la raíz del proyecto.

### **1. Sistema de Configuración Centralizada**

El proyecto usa un sistema de configuración centralizada que permite cambiar la URL de Ollama y otras configuraciones desde un solo lugar.

#### **Archivos de Configuración:**
- **`config.py`**: Configuración principal del proyecto
- **`docker.env`**: Variables de entorno para Docker
- **`generate_config.py`**: Script para generar archivos de configuración

#### **Comandos de Configuración:**
```bash
# Mostrar configuración actual
python generate_config.py show

# Generar archivo docker.env
python generate_config.py docker

# Generar archivo .env.example
python generate_config.py env

# Generar configuración de Nginx
python generate_config.py nginx

# Generar todos los archivos
python generate_config.py all
```

#### **Para cambiar la URL de Ollama:**
1. Edita `config.py` con la nueva URL
2. Ejecuta: `python generate_config.py docker`
3. Reinicia los servicios: `podman-compose down && podman-compose up -d`

### **2. Configura tus variables de entorno**

El archivo `docker-compose.yml` ahora usa `docker.env` para las variables de entorno. Si necesitas cambiar:
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
Verificar que Ollama esté ejecutándose en la URL correcta:
```bash
# Verificar conectividad
curl https://c510f9a99a12.ngrok-free.app/api/tags

# Si no responde, actualizar la URL usando el sistema centralizado:
# 1. Editar config.py con la nueva URL
# 2. python generate_config.py docker
# 3. podman-compose down && podman-compose up -d
```

### Error: Problemas con la configuración centralizada
Si hay problemas con el sistema de configuración:

```bash
# Verificar que config.py existe y es válido
python -c "from config import OLLAMA_URL; print(OLLAMA_URL)"

# Regenerar todos los archivos de configuración
python generate_config.py all

# Verificar que docker.env se generó correctamente
cat docker.env
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
| `OLLAMA_URL` | `https://5a15b4672e26.ngrok-free.app` | URL del servidor Ollama |
| `MODEL_NAME` | `llama3` | Modelo de lenguaje a usar |
| `FRONTEND_URL` | `http://localhost:5173` | URL del frontend |
| `OLLAMA_TIMEOUT` | `300` | Timeout en segundos |
| `CORS_ORIGINS` | `*` | Orígenes permitidos para CORS |
| `DEBUG_MODE` | `true` | Modo debug activado |
| `ENABLE_TELEGRAM_BOT` | `false` | Activa o desactiva el bot de Telegram |

## 🔧 Sistema de Configuración

### **Archivos de Configuración**

- **`config.py`**: Configuración principal centralizada
- **`docker.env`**: Variables de entorno para Docker
- **`generate_config.py`**: Script de generación automática
- **`CONFIGURACION.md`**: Documentación detallada

### **Procedimiento para Cambiar Configuración**

1. **Editar configuración principal:**
   ```bash
   # Editar config.py con la nueva URL
   nano config.py
   ```

2. **Generar archivos actualizados:**
   ```bash
   # Generar docker.env con nueva configuración
   python generate_config.py docker
   
   # O generar todos los archivos
   python generate_config.py all
   ```

3. **Reiniciar servicios:**
   ```bash
   # Detener servicios
   podman-compose down
   
   # Levantar con nueva configuración
   podman-compose up -d
   ```

4. **Verificar cambios:**
   ```bash
   # Ver configuración actual
   python generate_config.py show
   
   # Ver logs
   podman-compose logs -f
   ```

### **Comandos Útiles del Sistema**

```bash
# Ver configuración actual
python generate_config.py show

# Generar archivos de configuración
python generate_config.py docker    # Solo docker.env
python generate_config.py env       # Solo .env.example
python generate_config.py nginx     # Solo nginx-bender.conf
python generate_config.py all       # Todos los archivos

# Verificar que la aplicación funciona
curl http://localhost:8000/models
```

## 🏗️ Arquitectura

- **Backend**: FastAPI con Python 3.11
- **Frontend**: React + nginx
- **IA**: Ollama con modelo Llama3
- **Integración**: Jira API v3
- **Contenedor**: Podman con configuración robusta
- **Configuración**: Sistema centralizado con `config.py`

## 📚 Documentación Adicional

- **`CONFIGURACION.md`**: Documentación detallada del sistema de configuración
- **`generate_config.py`**: Script para generar archivos de configuración
- **`config.py`**: Configuración principal del proyecto
- **`docker.env`**: Variables de entorno para Docker 
