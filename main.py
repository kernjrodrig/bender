# Importaciones de FastAPI y utilidades
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
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

# Endpoint principal que redirige al nuevo frontend
@app.get("/", response_class=HTMLResponse)
async def index():
    return RedirectResponse(url="http://localhost:5173")
    
# Reemplaza detect_jira_query por una nueva función que detecta múltiples consultas

def detect_jira_queries(mensaje: str) -> list[tuple[str, list]]:
    """Detecta todas las consultas de Jira en el mensaje y extrae información relevante (soporta múltiples tipos y tickets)"""
    patterns = {
        'ticket': r'(?:ticket|issue|jira|tarea|problema)\s+((?:sd-\d{3}(?:,?\s*)?)+)',
        'project': r'(?:proyecto|project)\s+([A-Z]+)',
        'project_of_ticket': r'(?:proyecto|project)\s+((?:sd-\d{3}(?:,?\s*)?)+)',
        'search': r'(?:buscar|search|encontrar|listar)\s+(.+?)(?:\s+en\s+jira)?$',
        'status': r'(?:estado|status)\s+((?:sd-\d{3}(?:,?\s*)?)+)|((?:sd-\d{3}(?:,?\s*)?)+)\s+(?:estado|status)',
        'assignee': r'(?:asignado|assignee|asignación)\s+((?:sd-\d{3}(?:,?\s*)?)+)|((?:sd-\d{3}(?:,?\s*)?)+)\s+(?:asignado|assignee|asignación)',
        'priority': r'(?:prioridad|priority)\s+((?:sd-\d{3}(?:,?\s*)?)+)|((?:sd-\d{3}(?:,?\s*)?)+)\s+(?:prioridad|priority)',
        'summary': r'(?:resumen|summary|resumir)\s+((?:sd-\d{3}(?:,?\s*)?)+)|((?:sd-\d{3}(?:,?\s*)?)+)\s+(?:resumen|summary)',
        'changelog': r'(?:historial de cambios|changelog|historial)\s+((?:sd-\d{3}(?:,?\s*)?)+)|((?:sd-\d{3}(?:,?\s*)?)+)\s+(?:historial de cambios|changelog)',
        'simple_ticket': r'\b(sd-\d{3})\b'
    }
    results = []
    for query_type, pattern in patterns.items():
        if query_type != 'simple_ticket':
            for match in re.finditer(pattern, mensaje, re.IGNORECASE):
                value = match.group(1) if match.group(1) else (match.group(2) if len(match.groups()) > 1 else None)
                if value:
                    tickets = re.findall(r'sd-\d{3}', value, re.IGNORECASE)
                    if tickets:
                        results.append((query_type, tickets))
    # Si no se encontró ningún patrón, buscar tickets simples
    if not results:
        simple_matches = re.findall(patterns['simple_ticket'], mensaje, re.IGNORECASE)
        if simple_matches:
            results.append(('ticket', simple_matches))
    return results

# Función para obtener información de Jira según el tipo de consulta detectada
async def get_jira_info(query_type: str, query_value) -> str:
    """Obtiene información de Jira según el tipo de consulta. Soporta múltiples tickets."""
    try:
        print(f"DEBUG: get_jira_info iniciado - tipo: {query_type}, valor: {query_value}")
        # Si la consulta es sobre uno o varios tickets
        if query_type in ['ticket', 'status', 'assignee', 'priority', 'summary', 'changelog', 'project_of_ticket']:
            # Si es una lista, procesar cada ticket
            if isinstance(query_value, list):
                results = []
                for ticket in query_value:
                    if query_type == 'ticket':
                        issue_data = await jira_client.get_issue(ticket)
                        if issue_data is None:
                            results.append(f"Ticket {ticket}: No se encontró información")
                        else:
                            results.append(jira_client.format_issue_info(issue_data))
                    elif query_type == 'status':
                        issue_data = await jira_client.get_issue(ticket)
                        if issue_data:
                            status = issue_data.get('fields', {}).get('status', {}).get('name', 'N/A')
                            results.append(f"Ticket {ticket}: Estado: {status}")
                        else:
                            results.append(f"Ticket {ticket}: No se encontró información")
                    elif query_type == 'assignee':
                        issue_data = await jira_client.get_issue(ticket)
                        if issue_data:
                            assignee = issue_data.get('fields', {}).get('assignee', {}).get('displayName', 'Sin asignar')
                            results.append(f"Ticket {ticket}: Asignado: {assignee}")
                        else:
                            results.append(f"Ticket {ticket}: No se encontró información")
                    elif query_type == 'priority':
                        issue_data = await jira_client.get_issue(ticket)
                        if issue_data:
                            priority = issue_data.get('fields', {}).get('priority', {}).get('name', 'N/A')
                            results.append(f"Ticket {ticket}: Prioridad: {priority}")
                        else:
                            results.append(f"Ticket {ticket}: No se encontró información")
                    elif query_type == 'summary':
                        issue_data = await jira_client.get_issue(ticket)
                        if issue_data:
                            summary = issue_data.get('fields', {}).get('summary', 'N/A')
                            results.append(f"Ticket {ticket}: Resumen: {summary}")
                        else:
                            results.append(f"Ticket {ticket}: No se encontró información")
                    elif query_type == 'changelog':
                        issue_data = await jira_client.get_issue(ticket, expand='changelog')
                        if issue_data and 'changelog' in issue_data:
                            histories = issue_data['changelog'].get('histories', [])
                            if not histories:
                                results.append(f"Ticket {ticket}: No tiene historial de cambios.")
                            else:
                                changelog_str = f"Ticket {ticket}:\n"
                                for h in histories:
                                    author = h.get('author', {}).get('displayName', 'Desconocido')
                                    created = h.get('created', 'N/A')
                                    items = h.get('items', [])
                                    for item in items:
                                        field = item.get('field', 'N/A')
                                        fromString = item.get('fromString', 'N/A')
                                        toString = item.get('toString', 'N/A')
                                        changelog_str += f"- {created} por {author}: {field} cambió de '{fromString}' a '{toString}'\n"
                                results.append(changelog_str)
                        else:
                            results.append(f"Ticket {ticket}: No se encontró historial de cambios")
                    elif query_type == 'project_of_ticket':
                        issue_data = await jira_client.get_issue(ticket)
                        if issue_data:
                            project = issue_data.get('fields', {}).get('project', {})
                            project_key = project.get('key', 'N/A')
                            project_name = project.get('name', 'N/A')
                            results.append(f"Ticket {ticket}: Proyecto: {project_name} (clave: {project_key})")
                        else:
                            results.append(f"Ticket {ticket}: No se encontró información del ticket")
                return '\n'.join(results)
            # Si no es lista, procesar como antes
            else:
                ticket = query_value
                # (Lógica igual que antes para un solo ticket)
                if query_type == 'ticket':
                    issue_data = await jira_client.get_issue(ticket)
                    if issue_data is None:
                        return "No se encontró información del ticket"
                    return jira_client.format_issue_info(issue_data)
                elif query_type == 'status':
                    issue_data = await jira_client.get_issue(ticket)
                    if issue_data:
                        status = issue_data.get('fields', {}).get('status', {}).get('name', 'N/A')
                        return f"**Estado del ticket {ticket}**: {status}"
                    return f"No se encontró información del ticket {ticket}"
                elif query_type == 'assignee':
                    issue_data = await jira_client.get_issue(ticket)
                    if issue_data:
                        assignee = issue_data.get('fields', {}).get('assignee', {}).get('displayName', 'Sin asignar')
                        return f"**Asignado del ticket {ticket}**: {assignee}"
                    return f"No se encontró información del ticket {ticket}"
                elif query_type == 'priority':
                    issue_data = await jira_client.get_issue(ticket)
                    if issue_data:
                        priority = issue_data.get('fields', {}).get('priority', {}).get('name', 'N/A')
                        return f"**Prioridad del ticket {ticket}**: {priority}"
                    return f"No se encontró información del ticket {ticket}"
                elif query_type == 'summary':
                    issue_data = await jira_client.get_issue(ticket)
                    if issue_data:
                        summary = issue_data.get('fields', {}).get('summary', 'N/A')
                        return f"**Resumen del ticket {ticket}**: {summary}"
                    return f"No se encontró información del ticket {ticket}"
                elif query_type == 'changelog':
                    issue_data = await jira_client.get_issue(ticket, expand='changelog')
                    if issue_data and 'changelog' in issue_data:
                        histories = issue_data['changelog'].get('histories', [])
                        if not histories:
                            return f"El ticket {ticket} no tiene historial de cambios."
                        changelog_str = f"Historial de cambios para {ticket}:\n"
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
                    return f"No se encontró historial de cambios para el ticket {ticket}"
                elif query_type == 'project_of_ticket':
                    issue_data = await jira_client.get_issue(ticket)
                    if issue_data:
                        project = issue_data.get('fields', {}).get('project', {})
                        project_key = project.get('key', 'N/A')
                        project_name = project.get('name', 'N/A')
                        return f"El ticket {ticket} pertenece al proyecto: {project_name} (clave: {project_key})"
                    return f"No se encontró información del ticket {ticket}"
        # Si la consulta es sobre un proyecto, obtener información del proyecto
        elif query_type == 'project':
            project_data = await jira_client.get_project(query_value)
            if project_data:
                return f"**Proyecto: {project_data.get('name', 'N/A')}**\n- Clave: {project_data.get('key', 'N/A')}\n- Descripción: {project_data.get('description', 'Sin descripción')}"
            return "No se encontró información del proyecto"
        # Si la consulta es una búsqueda general
        elif query_type == 'search':
            search_data = await jira_client.search_issues(query_value)
            if search_data is None:
                return "No se encontraron resultados en la búsqueda"
            return jira_client.format_search_results(search_data)
        return "Tipo de consulta no reconocido"
    except Exception as e:
        error_msg = f"Error consultando Jira: {str(e)}"
        print(f"DEBUG: {error_msg}")
        return error_msg

# Modificar el endpoint /chat para soportar múltiples consultas Jira
@app.post("/chat")
async def chat(request: Request):
    try:
        print("DEBUG: Iniciando endpoint /chat")
        data = await request.json()
        mensaje = data.get("mensaje", "")
        if not mensaje:
            return JSONResponse({"error": "Mensaje vacío"}, status_code=400)
        
        print(f"DEBUG: Mensaje recibido: {mensaje}")
        
        # Detectar todas las consultas de Jira
        jira_queries = detect_jira_queries(mensaje)
        print(f"DEBUG: jira_queries detectadas: {jira_queries}")
        
        # Revisar si hay al menos una consulta de tipo 'summary'
        has_summary = any(q[0] == 'summary' for q in jira_queries)
        
        if jira_queries and has_summary:
            # Obtener la información completa de todos los tickets de tipo summary
            summary_tickets = []
            for query_type, tickets in jira_queries:
                if query_type == 'summary':
                    summary_tickets.extend(tickets)
            # Eliminar duplicados
            summary_tickets = list(set(summary_tickets))
            # Obtener la info completa de cada ticket
            ticket_infos = []
            for ticket in summary_tickets:
                issue_data = await jira_client.get_issue(ticket)
                if issue_data is None:
                    ticket_infos.append(f"Ticket {ticket}: No se encontró información")
                else:
                    ticket_infos.append(jira_client.format_issue_info(issue_data))
            # Unir toda la info
            all_info = "\n\n".join(ticket_infos)
            resumen_prompt = f"Por favor, haz un resumen general de la siguiente información de tickets de Jira. Si hay errores o falta información, explícalo claramente.\n\n{all_info}"
            prompt = resumen_prompt
        elif jira_queries:
            jira_infos = []
            for query_type, tickets in jira_queries:
                print(f"DEBUG: Consultando Jira - tipo: {query_type}, tickets: {tickets}")
                info = await get_jira_info(query_type, tickets)
                jira_infos.append(info)
            jira_info = "\n".join(jira_infos)
            prompt = f"""
            Como asistente experto en Jira, analiza la siguiente información y responde de manera útil y clara:

            Consulta del usuario: {mensaje}
            
            Información de Jira obtenida:
            {jira_info}
            
            Por favor, proporciona una respuesta útil basada en esta información. Si hay errores o falta información, explícalo claramente.
            """
        else:
            prompt = mensaje
        
        print(f"DEBUG: Prompt preparado para Ollama: {prompt[:100]}...")
        
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
        
        print(f"DEBUG: Conectando a Ollama en {OLLAMA_URL}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload,
                timeout=300.0  # Aumentar timeout a 5 minutos
            )
            
            print(f"DEBUG: Respuesta de Ollama - Status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"Error al conectar con Ollama: {response.status_code}"
                print(f"DEBUG: {error_msg}")
                return JSONResponse({"error": error_msg}, status_code=500)
            
            response_data = response.json()
            respuesta = response_data.get("message", {}).get("content", "Sin respuesta")
            
            print(f"DEBUG: Respuesta final: {respuesta[:100]}...")
            return {"respuesta": respuesta}
            
    except httpx.TimeoutException as e:
        error_msg = f"Timeout: Ollama tardó más de 5 minutos en responder: {str(e)}"
        print(f"DEBUG: {error_msg}")
        return JSONResponse({"error": error_msg}, status_code=500)
    except Exception as e:
        error_msg = f"Error de conexión: {str(e)}"
        print(f"DEBUG: {error_msg}")
        return JSONResponse({"error": error_msg}, status_code=500)

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