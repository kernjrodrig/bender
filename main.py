from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
import re
from jira_client import JiraClient

app = FastAPI()

# Permitir CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = os.getenv("OLLAMA_URL", "https://5aaf5f3a9d6b.ngrok-free.app")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")

# Inicializar cliente de Jira
jira_client = JiraClient()

def detect_jira_query(mensaje: str) -> tuple[bool, str, str]:
    """Detecta si el mensaje es una consulta de Jira y extrae información"""
    mensaje_lower = mensaje.lower()
    
    # Patrones mejorados para detectar consultas de Jira
    patterns = {
        'ticket': r'(?:ticket|issue|jira|tarea|problema)\s+([A-Z]+-\d+)',
        'project': r'(?:proyecto|project)\s+([A-Z]+)',
        'search': r'(?:buscar|search|encontrar|listar)\s+(.+?)(?:\s+en\s+jira)?$',
        'status': r'(?:estado|status)\s+([A-Z]+-\d+)',
        'assignee': r'(?:asignado|assignee)\s+([A-Z]+-\d+)',
        # Patrón simple para detectar códigos de ticket sin palabras clave
        'simple_ticket': r'\b([A-Z]+-\d+)\b'
    }
    
    # Primero buscar patrones específicos
    for query_type, pattern in patterns.items():
        if query_type != 'simple_ticket':  # Saltar el patrón simple por ahora
            match = re.search(pattern, mensaje_lower)
            if match:
                print(f"DEBUG: Detectado patrón '{query_type}' con valor '{match.group(1)}'")
                return True, query_type, match.group(1)
    
    # Si no se encontró patrón específico, buscar códigos de ticket simples
    simple_match = re.search(patterns['simple_ticket'], mensaje.upper())
    if simple_match:
        ticket_code = simple_match.group(1)
        print(f"DEBUG: Detectado código de ticket simple: '{ticket_code}'")
        return True, 'ticket', ticket_code
    
    print(f"DEBUG: No se detectó consulta de Jira en: '{mensaje}'")
    return False, "", ""

async def get_jira_info(query_type: str, query_value: str) -> str:
    """Obtiene información de Jira según el tipo de consulta"""
    try:
        if query_type == 'ticket':
            issue_data = await jira_client.get_issue(query_value)
            if issue_data:
                return jira_client.format_issue_info(issue_data)
            else:
                return f"No se encontró información del ticket {query_value}"
        
        elif query_type == 'project':
            project_data = await jira_client.get_project(query_value)
            if project_data:
                return f"**Proyecto: {project_data.get('name', 'N/A')}**\n- Clave: {project_data.get('key', 'N/A')}\n- Descripción: {project_data.get('description', 'Sin descripción')}"
            return "No se encontró información del proyecto"
        
        elif query_type == 'search':
            search_data = await jira_client.search_issues(query_value)
            if search_data:
                return jira_client.format_search_results(search_data)
            else:
                return "No se encontraron resultados para la búsqueda"
        
        elif query_type == 'status':
            issue_data = await jira_client.get_issue(query_value)
            if issue_data:
                status = issue_data.get('fields', {}).get('status', {}).get('name', 'N/A')
                return f"**Estado del ticket {query_value}**: {status}"
            return f"No se encontró información del ticket {query_value}"
        
        elif query_type == 'assignee':
            issue_data = await jira_client.get_issue(query_value)
            if issue_data:
                assignee = issue_data.get('fields', {}).get('assignee', {}).get('displayName', 'Sin asignar')
                return f"**Asignado del ticket {query_value}**: {assignee}"
            return f"No se encontró información del ticket {query_value}"
        
        return "Tipo de consulta no reconocido"
    
    except Exception as e:
        return f"Error consultando Jira: {str(e)}"

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    mensaje = data.get("mensaje", "")
    if not mensaje:
        return JSONResponse({"error": "Mensaje vacío"}, status_code=400)
    
    # Detectar si es una consulta de Jira
    is_jira_query, query_type, query_value = detect_jira_query(mensaje)
    
    print(f"DEBUG: is_jira_query={is_jira_query}, query_type={query_type}, query_value={query_value}")
    print(f"DEBUG: MODEL_NAME configurado: {MODEL_NAME}")
    
    if is_jira_query:
        print(f"DEBUG: Consultando Jira - tipo: {query_type}, valor: {query_value}")
        # Obtener información de Jira
        jira_info = await get_jira_info(query_type, query_value)
        print(f"DEBUG: Información de Jira obtenida: {jira_info[:200]}...")
        
        # Crear prompt para Ollama con contexto de Jira
        prompt = f"""
        Como asistente experto en Jira, analiza la siguiente información y responde de manera útil y clara:

        Consulta del usuario: {mensaje}
        
        Información de Jira obtenida:
        {jira_info}
        
        Por favor, proporciona una respuesta útil basada en esta información. Si hay errores o falta información, explícalo claramente.
        """
    else:
        # Consulta normal sin Jira, pide respuesta breve y concreta
        prompt = (
            f"Responde de forma breve, concreta y amable. "
            f"Si el mensaje es solo un saludo como 'hola', responde únicamente: "
            f"¡Hola! ¿En qué puedo ayudarte? 😊\n\n"
            f"Mensaje del usuario: {mensaje}"
        )
    
    # Preparar payload para Ollama API
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False
    }
    
    print(f"DEBUG: Enviando payload a Ollama: {payload}")
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"DEBUG: Conectando a {OLLAMA_URL}/api/chat")
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload,
                timeout=300.0  # 5 minutos de timeout
            )
            
            print(f"DEBUG: Status code de Ollama: {response.status_code}")
            print(f"DEBUG: Respuesta de Ollama: {response.text[:500]}...")
            
            if response.status_code != 200:
                return JSONResponse(
                    {"error": f"Error al conectar con Ollama: {response.status_code} - {response.text}"}, 
                    status_code=500
                )
            
            response_data = response.json()
            respuesta = response_data.get("message", {}).get("content", "Sin respuesta")
            
            return {"respuesta": respuesta}
            
    except httpx.TimeoutException:
        print("DEBUG: Timeout en la conexión con Ollama")
        return JSONResponse({"error": "Timeout: Ollama tardó más de 5 minutos en responder"}, status_code=500)
    except Exception as e:
        print(f"DEBUG: Excepción en chat: {str(e)}")
        return JSONResponse({"error": f"Error de conexión: {str(e)}"}, status_code=500)

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

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(
        content=open("static/index.html").read(),
        status_code=200
    )

# Servir archivos estáticos (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static") 
