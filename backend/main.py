# Importaciones de FastAPI y utilidades
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
import re
import time
from Jira.jira_tipo_consulta import detect_jira_queries, get_jira_info
from Jira.Jira_chat import router as chat_router
from Jira.filtro_tickets import obtener_top_5_asignados

# Inicialización de la aplicación FastAPI.
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

# Configuración de variables de entorno

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://192.168.10.80:8089")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama-3-8b-instruct")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Endpoint principal que redirige al frontend configurado
@app.get("/", response_class=HTMLResponse)
async def index():
    return RedirectResponse(url=FRONTEND_URL)
    
# Eliminar el endpoint /chat de aquí

# Endpoint para listar modelos disponibles en LMStudio
@app.get("/models")
async def list_models():
    """Endpoint para listar modelos disponibles en LMStudio"""
    try:
        # LMStudio no tiene endpoint /api/tags, devolvemos información básica
        return {
            "message": "LMStudio no expone lista de modelos via API",
            "url": OLLAMA_URL,
            "available_endpoints": ["/api/chat"],
            "note": "Los modelos se configuran directamente en la interfaz de LMStudio"
        }
    except Exception as e:
        return JSONResponse({"error": f"Error: {str(e)}"}, status_code=500)

# Endpoint para obtener las 5 personas con mayor cantidad de tickets asignados
@app.get("/top-assignees")
async def get_top_assignees():
    """Endpoint para obtener las 5 personas con mayor cantidad de tickets asignados"""
    try:
        result = await obtener_top_5_asignados()
        return JSONResponse({"result": result})
    except Exception as e:
        return JSONResponse({"error": f"Error: {str(e)}"}, status_code=500)

# Endpoint de prueba para verificar conectividad con LMStudio
@app.get("/test-lmstudio")
async def test_lmstudio():
    """Endpoint para probar la conectividad con LMStudio"""
    try:
        async with httpx.AsyncClient() as client:
            # Probar endpoint de chat de LMStudio (formato OpenAI)
            test_payload = {
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hola, responde solo 'OK' si me escuchas."
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7,
                "stream": False
            }
            
            response = await client.post(
                f"{OLLAMA_URL}/v1/chat/completions",
                json=test_payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return JSONResponse({
                    "status": "success",
                    "message": "Conexión exitosa con LMStudio",
                    "url": OLLAMA_URL,
                    "model": MODEL_NAME,
                    "test_response": response_data.get("message", {}).get("content", "Sin respuesta")[:100],
                    "note": "LMStudio está funcionando correctamente"
                })
            else:
                return JSONResponse({
                    "status": "error",
                    "message": f"Error al conectar con LMStudio: {response.status_code}",
                    "url": OLLAMA_URL,
                    "response_text": response.text
                }, status_code=500)
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error de conexión: {str(e)}",
            "url": OLLAMA_URL
        }, status_code=500)

# Endpoint para Open WebUI (formato OpenAI API)
@app.post("/v1/chat/completions")
async def openai_chat_completions(request: Request):
    """Endpoint compatible con OpenAI API para Open WebUI"""
    try:
        body = await request.json()
        
        # Extraer mensajes del request
        messages = body.get("messages", [])
        model = body.get("model", MODEL_NAME)
        max_tokens = body.get("max_tokens", 1000)
        temperature = body.get("temperature", 0.7)
        
        # Construir prompt para Jira
        if messages:
            last_message = messages[-1]["content"]
            prompt = f"Eres un asistente experto en Jira llamado Bender que SIEMPRE responde en español. El usuario te pregunta: {last_message}\n\nIMPORTANTE: Responde ÚNICAMENTE en español."
        else:
            prompt = "Hola, soy Bender, tu asistente de Jira. ¿En qué puedo ayudarte?"
        
        # Preparar payload para LMStudio
        lmstudio_payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        # Conectar a LMStudio
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/v1/chat/completions",
                json=lmstudio_payload,
                timeout=120.0
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # Devolver en formato OpenAI
                return {
                    "id": "chatcmpl-" + str(hash(str(time.time()))),
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response_data.get("choices", [{}])[0].get("message", {}).get("content", "Sin respuesta")
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                }
            else:
                return JSONResponse(
                    {"error": f"Error de LMStudio: {response.status_code}"}, 
                    status_code=500
                )
                
    except Exception as e:
        return JSONResponse(
            {"error": f"Error interno: {str(e)}"}, 
            status_code=500
        )

# Endpoint para listar modelos (formato OpenAI)
@app.get("/v1/models")
async def openai_models():
    """Endpoint compatible con OpenAI API para listar modelos"""
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_NAME,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "bender-ai"
            }
        ]
    }

# El frontend ahora está en http://localhost:5173 
app.include_router(chat_router) 
