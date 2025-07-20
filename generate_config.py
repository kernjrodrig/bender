#!/usr/bin/env python3
"""
Script para generar archivos de configuración para diferentes servicios
usando la URL de Ollama centralizada desde config.py
"""

import os
import sys
from config import OLLAMA_URL, MODEL_NAME, FRONTEND_URL, OLLAMA_TIMEOUT

def generate_docker_env():
    """Genera el archivo docker.env con la configuración actual"""
    content = f"""# Variables de entorno para Docker y servicios externos
# URL de Ollama (actualizada)
OLLAMA_URL={OLLAMA_URL}

# Modelo de Ollama
MODEL_NAME={MODEL_NAME}

# Configuración del frontend
FRONTEND_URL={FRONTEND_URL}

# Configuración de timeouts
OLLAMA_TIMEOUT={OLLAMA_TIMEOUT}

# Configuración de CORS
CORS_ORIGINS=*

# Configuración de logging
DEBUG_MODE=true
"""
    
    with open('docker.env', 'w') as f:
        f.write(content)
    print(f"✅ Archivo docker.env generado con URL: {OLLAMA_URL}")

def generate_env_example():
    """Genera un archivo .env.example con la configuración actual"""
    content = f"""# Configuración de Ollama
OLLAMA_URL={OLLAMA_URL}
MODEL_NAME={MODEL_NAME}

# Configuración del frontend
FRONTEND_URL={FRONTEND_URL}

# Configuración de timeouts (en segundos)
OLLAMA_TIMEOUT={OLLAMA_TIMEOUT}

# Configuración de CORS (separar múltiples orígenes con comas)
CORS_ORIGINS=*

# Configuración de Jira (opcional)
JIRA_URL=
JIRA_USERNAME=
JIRA_API_TOKEN=

# Configuración de logging
DEBUG_MODE=true
"""
    
    with open('.env.example', 'w') as f:
        f.write(content)
    print(f"✅ Archivo .env.example generado con URL: {OLLAMA_URL}")

def generate_nginx_config():
    """Genera una configuración de ejemplo para Nginx"""
    content = f"""# Configuración de ejemplo para Nginx
# Coloca este archivo en /etc/nginx/sites-available/bender

server {{
    listen 80;
    server_name localhost;

    # Proxy para la API de FastAPI
    location /api/ {{
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    # Proxy para Ollama (si es necesario)
    location /ollama/ {{
        proxy_pass {OLLAMA_URL}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    # Frontend
    location / {{
        proxy_pass {FRONTEND_URL};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    
    with open('nginx-bender.conf', 'w') as f:
        f.write(content)
    print(f"✅ Archivo nginx-bender.conf generado")

def show_current_config():
    """Muestra la configuración actual"""
    print("🔧 Configuración actual:")
    print(f"   OLLAMA_URL: {OLLAMA_URL}")
    print(f"   MODEL_NAME: {MODEL_NAME}")
    print(f"   FRONTEND_URL: {FRONTEND_URL}")
    print(f"   OLLAMA_TIMEOUT: {OLLAMA_TIMEOUT} segundos")

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python generate_config.py [docker|env|nginx|all|show]")
        print("  docker: Genera docker.env")
        print("  env: Genera .env.example")
        print("  nginx: Genera nginx-bender.conf")
        print("  all: Genera todos los archivos")
        print("  show: Muestra la configuración actual")
        return

    command = sys.argv[1].lower()
    
    if command == "docker":
        generate_docker_env()
    elif command == "env":
        generate_env_example()
    elif command == "nginx":
        generate_nginx_config()
    elif command == "all":
        generate_docker_env()
        generate_env_example()
        generate_nginx_config()
    elif command == "show":
        show_current_config()
    else:
        print(f"Comando '{command}' no reconocido")
        print("Comandos disponibles: docker, env, nginx, all, show")

if __name__ == "__main__":
    main() 