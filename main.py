# Importaciones de FastAPI y utilidades
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import json
import re
from jira_client import JiraClient

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
OLLAMA_URL = os.getenv("OLLAMA_URL", "https://5aaf5f3a9d6b.ngrok-free.app")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")

# Inicializar cliente de Jira
jira_client = JiraClient()

# Endpoint principal que sirve el frontend (index.html)
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)
    
# Función para detectar si un mensaje es una consulta de Jira y extraer información relevante
def detect_jira_query(mensaje: str) -> tuple[bool, str, str]:
    """Detecta si el mensaje es una consulta de Jira y extrae información"""
    # Patrones mejorados para detectar consultas de Jira
    patterns = {
        # Detecta frases como "ticket sd-123", "issue sd-123", "jira sd-123", etc.
        'ticket': r'(?:ticket|issue|jira|tarea|problema)\s+(sd-\d{3})',

        # Detecta frases como "proyecto ABC" o "project ABC" (donde ABC es la clave del proyecto)
        'project': r'(?:proyecto|project)\s+([A-Z]+)',#ESTA PENDIENTE

        # Detecta frases como "proyecto sd-123" para obtener el proyecto al que pertenece un ticket
        'project_of_ticket': r'(?:proyecto|project)\s+(sd-\d{3})',#PENDIENTE

        # Detecta búsquedas generales como "buscar algo en jira", "search algo", "encontrar algo", "listar algo"
        'search': r'(?:buscar|search|encontrar|listar)\s+(.+?)(?:\s+en\s+jira)?$',

        # Detecta preguntas sobre el estado de un ticket, por ejemplo "estado sd-123" o "sd-123 estado"
        'status': r'(?:estado|status)\s+(sd-\d{3})|(sd-\d{3})\s+(?:estado|status)',

        # Detecta preguntas sobre el asignado de un ticket, por ejemplo "asignado sd-123" o "sd-123 asignado"
        'assignee': r'(?:asignado|assignee|asignación)\s+(sd-\d{3})|(sd-\d{3})\s+(?:asignado|assignee|asignación)',

        # Detecta preguntas sobre la prioridad de un ticket, por ejemplo "prioridad sd-123" o "sd-123 prioridad"
        'priority': r'(?:prioridad|priority)\s+(sd-\d{3})|(sd-\d{3})\s+(?:prioridad|priority)',

        # Detecta preguntas sobre el resumen de un ticket, por ejemplo "resumen sd-123" o "sd-123 resumen"
        'summary': r'(?:resumen|summary)\s+(sd-\d{3})|(sd-\d{3})\s+(?:resumen|summary)',

        # Detecta preguntas sobre el historial de cambios de un ticket, por ejemplo "historial de cambios sd-123"
        'changelog': r'(?:historial de cambios|changelog)\s+(sd-\d{3})|(sd-\d{3})\s+(?:historial de cambios|changelog)',

        # Patrón simple para detectar cualquier código de ticket tipo sd-123 aunque no haya palabra clave
        'simple_ticket': r'\b(sd-\d{3})\b'
    }
    
    # Primero buscar patrones específicos
    for query_type, pattern in patterns.items():
        if query_type != 'simple_ticket':  # Saltar el patrón simple por ahora
            match = re.search(pattern, mensaje, re.IGNORECASE)
            if match:
                # El valor puede estar en el grupo 1 o 2 dependiendo del orden
                value = match.group(1) if match.group(1) else match.group(2)
                print(f"DEBUG: Detectado patrón '{query_type}' con valor '{value}'")
                return True, query_type, value
    
    # Si no se encontró patrón específico, buscar códigos de ticket simples
    simple_match = re.search(patterns['simple_ticket'], mensaje, re.IGNORECASE)
    if simple_match:
        ticket_code = simple_match.group(1)
        print(f"DEBUG: Detectado código de ticket simple: '{ticket_code}'")
        return True, 'ticket', ticket_code
    
    print(f"DEBUG: No se detectó consulta de Jira en: '{mensaje}'")
    return False, "", ""

# Función para obtener información de Jira según el tipo de consulta detectada
async def get_jira_info(query_type: str, query_value: str) -> str:
    """Obtiene información de Jira según el tipo de consulta"""
    try:
        # Si la consulta es sobre un ticket específico, obtener información del ticket
        if query_type == 'ticket':
            issue_data = await jira_client.get_issue(query_value)
            if issue_data is None:
                return "No se encontró información del ticket"
            return jira_client.format_issue_info(issue_data)
        
        # Si la consulta es sobre un proyecto, obtener información del proyecto
        elif query_type == 'project':
            project_data = await jira_client.get_project(query_value)
            if project_data:
                return f"**Proyecto: {project_data.get('name', 'N/A')}**\n- Clave: {project_data.get('key', 'N/A')}\n- Descripción: {project_data.get('description', 'Sin descripción')}"
            return "No se encontró información del proyecto"
        
        # Si la consulta es sobre el proyecto al que pertenece un ticket, obtener el proyecto desde el ticket
        elif query_type == 'project_of_ticket':
            issue_data = await jira_client.get_issue(query_value)
            if issue_data:
                project = issue_data.get('fields', {}).get('project', {})
                project_key = project.get('key', 'N/A')
                project_name = project.get('name', 'N/A')
                return f"El ticket {query_value} pertenece al proyecto: {project_name} (clave: {project_key})"
            return f"No se encontró información del ticket {query_value}"
        
        elif query_type == 'search':
            search_data = await jira_client.search_issues(query_value)
            if search_data is None:
                return "No se encontraron resultados en la búsqueda"
            return jira_client.format_search_results(search_data)
        #Si la consulta es sobre el estado de un ticket, obtener estado
        elif query_type == 'status':
            issue_data = await jira_client.get_issue(query_value)
            if issue_data:
                status = issue_data.get('fields', {}).get('status', {}).get('name', 'N/A')
                return f"**Estado del ticket {query_value}**: {status}"
            return f"No se encontró información del ticket {query_value}"
        #Si la consulta es sobre el asignado de un ticket, obtener asignado
        elif query_type == 'assignee':
            issue_data = await jira_client.get_issue(query_value)
            if issue_data:
                assignee = issue_data.get('fields', {}).get('assignee', {}).get('displayName', 'Sin asignar')
                return f"**Asignado del ticket {query_value}**: {assignee}"
            return f"No se encontró información del ticket {query_value}"
        #Si la consulta es sobre la prioridad de un ticket, obtener prioridad
        elif query_type == 'priority':
            issue_data = await jira_client.get_issue(query_value)
            if issue_data:
                priority = issue_data.get('fields', {}).get('priority', {}).get('name', 'N/A')
                return f"**Prioridad del ticket {query_value}**: {priority}"
            return f"No se encontró información del ticket {query_value}"
        #Si la consulta es sobre el resumen de un ticket, obtener resumen
        elif query_type == 'summary':
            issue_data = await jira_client.get_issue(query_value)
            if issue_data:
                summary = issue_data.get('fields', {}).get('summary', 'N/A')
                return f"**Resumen del ticket {query_value}**: {summary}"
            return f"No se encontró información del ticket {query_value}"
        #Si la consulta es sobre el historial de cambios de un ticket, obtener historial de cambios
        elif query_type == 'changelog':
            issue_data = await jira_client.get_issue(query_value, expand='changelog')
            if issue_data and 'changelog' in issue_data:
                histories = issue_data['changelog'].get('histories', [])
                if not histories:
                    return f"El ticket {query_value} no tiene historial de cambios."
                # Formatear historial de cambios de manera simple
                changelog_str = f"Historial de cambios para {query_value}:\n"
                for h in histories:
                    author = h.get('author', {}).get('displayName', 'Desconocido')
                    created = h.get('created', 'N/A')
                    items = h.get('items', [])
                    for item in items:
                        field = item.get('field', 'N/A')
                        fromString = item.get('fromString', 'N/A')
                        toString = item.get('toString', 'N/A')
                        changelog_str += f"- {created} por {author}: {field} cambió de '{fromString}' a '{toString}'\n"
                return changelog_str
            return f"No se encontró historial de cambios para el ticket {query_value}"
        
        return "Tipo de consulta no reconocido"
    
    except Exception as e:
        return f"Error consultando Jira: {str(e)}"

# Endpoint principal de chat que recibe mensajes y responde usando Ollama y Jira
@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    mensaje = data.get("mensaje", "")
    if not mensaje:
        return JSONResponse({"error": "Mensaje vacío"}, status_code=400)
    
    # Detectar si es una consulta de Jira
    is_jira_query, query_type, query_value = detect_jira_query(mensaje)
    
    print(f"DEBUG: is_jira_query={is_jira_query}, query_type={query_type}, query_value={query_value}")
    
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
        # Consulta normal sin Jira
        prompt = mensaje
    
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
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload,
                timeout=300.0  # 5 minutos de timeout
            )
            
            if response.status_code != 200:
                return JSONResponse(
                    {"error": f"Error al conectar con Ollama: {response.status_code}"}, 
                    status_code=500
                )
            
            response_data = response.json()
            respuesta = response_data.get("message", {}).get("content", "Sin respuesta")
            
            return {"respuesta": respuesta}
            
    except httpx.TimeoutException:
        return JSONResponse({"error": "Timeout: Ollama tardó más de 5 minutos en responder"}, status_code=500)
    except Exception as e:
        return JSONResponse({"error": f"Error de conexión: {str(e)}"}, status_code=500)

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

# Servir archivos estáticos (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static") 

