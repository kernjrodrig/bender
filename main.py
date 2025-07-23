# Importaciones de FastAPI y utilidades
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
import re
from jira_tipo_consulta import detect_jira_queries, get_jira_info
from Jira_chat import router as chat_router

# Inicialización de la aplicación FastAPI
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("¡La aplicación FastAPI ha iniciado dentro del contenedor!")

# Permitir CORS para desarrollo (acepta peticiones de cualquier origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de variables de entorno para Ollama

OLLAMA_URL = os.getenv("OLLAMA_URL", "https://7524977226f5.ngrok-free.app")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
# Eliminar la inicialización de JiraClient y las funciones detect_jira_queries y get_jira_info
# Endpoint principal que redirige al nuevo frontend
@app.get("/", response_class=HTMLResponse)
async def index():
    return RedirectResponse(url="http://localhost:5173")
    
# Eliminar el endpoint /chat de aquí

# Endpoint para listar modelos disponibles en Ollama
@app.get("/models")
async def list_models():
    """Endpoint para listar modelos disponibles en Ollama"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                return response.json()
            else:
                return JSONResponse({"error": "No se pudieron obtener los modelos"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": f"Error: {str(e)}"}, status_code=500)

# El frontend ahora está en http://localhost:5173 
app.include_router(chat_router) 
