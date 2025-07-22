import os

# Configuración de Ollama
OLLAMA_URL = os.getenv("OLLAMA_URL", "https://5a15b4672e26.ngrok-free.app")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")

# Configuración del frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Configuración de timeouts
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))  # 5 minutos en segundos

# Configuración de CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Configuración de Jira (si es necesario en el futuro)
JIRA_URL = os.getenv("JIRA_URL", "")
JIRA_USERNAME = os.getenv("JIRA_USERNAME", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

# Configuración de logging
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true" 