# BENDER - AI Assistant con Jira

Este proyecto es un chatbot inteligente inspirado en Bender de Futurama, desarrollado en Python (FastAPI) que se conecta a Ollama y Jira, ofreciendo una interfaz web minimalista y moderna para consultar información de tickets y proyectos.

## Requisitos
- Podman (o Docker)
- Acceso a un servidor Ollama en `http://192.168.10.14:11434`
- Token de API de Jira (ya configurado)

## Funcionalidades

### Chat con IA
- Conversación normal con Llama 3
- Análisis y explicación de información

### Consultas Jira
- **Ticket específico**: `"ticket PROJ-123"`
- **Estado de ticket**: `"estado PROJ-123"`
- **Asignado**: `"asignado PROJ-123"`
- **Información de proyecto**: `"proyecto PROJ"`
- **Búsqueda**: `"buscar bug en PROJ"`

## Construcción y ejecución

1. Construir la imagen:

```sh
podman build -t bender-ai .
```

2. Ejecutar el contenedor:

```sh
podman run -d -p 8000:8000 --name bender-ai bender-ai
```

3. Accede a la interfaz web:

Abre tu navegador en [http://localhost:8000](http://localhost:8000)

## Personalización

- **URL de Ollama**: Cambia la variable de entorno `OLLAMA_URL`:
```sh
podman run -d -p 8000:8000 -e OLLAMA_URL="http://TU_IP:11434" --name bender-ai bender-ai
```

- **Modelo específico**: Cambia la variable de entorno `MODEL_NAME`:
```sh
podman run -d -p 8000:8000 -e MODEL_NAME="llama3:8b" --name bender-ai bender-ai
```

- **Configuración Jira**: Modifica las variables de entorno:
```sh
podman run -d -p 8000:8000 \
  -e JIRA_URL="https://tu-dominio.atlassian.net" \
  -e JIRA_EMAIL="tu-email@dominio.com" \
  -e JIRA_API_TOKEN="tu-token" \
  --name bender-ai bender-ai
```

## Endpoints adicionales

- `GET /models` - Lista los modelos disponibles en Ollama
- `POST /chat` - Envía mensajes al modelo configurado (con integración Jira)

## Variables de entorno

- `OLLAMA_URL`: URL del servidor Ollama (default: `http://192.168.10.14:11434`)
- `MODEL_NAME`: Nombre del modelo a usar (default: `llama3`)
- `JIRA_URL`: URL de tu instancia de Jira
- `JIRA_EMAIL`: Email de tu cuenta de Jira
- `JIRA_API_TOKEN`: Token de API de Jira (ya configurado) 