from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx
import os
from jira_tipo_consulta import detect_jira_queries, get_jira_info
from filtro_tickets import (
    filtrar_tickets_abiertos,
    filtrar_tickets_urgentes,
    filtrar_tickets_asignados_a,
    filtrar_tickets_sin_asignar,
    filtrar_tickets_por_estado,
    filtrar_tickets_cerrados
)
import re

router = APIRouter()

OLLAMA_URL = os.getenv("OLLAMA_URL", "https://5a15b4672e26.ngrok-free.app")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")

@router.post("/chat")
async def chat(request: Request):
    try:
        print("DEBUG: Iniciando endpoint /chat")
        data = await request.json()
        mensaje = data.get("mensaje", "")
        if not mensaje:
            return JSONResponse({"error": "Mensaje vacío"}, status_code=400)
        
        print(f"DEBUG: Mensaje recibido: {mensaje}")

        # --- Detección de filtros especiales ---
        mensaje_lower = mensaje.lower()
        filtro_resultado = None
        if re.search(r"tickets?\s+abiertos?", mensaje_lower):
            filtro_resultado = await filtrar_tickets_abiertos()
        elif re.search(r"tickets?\s+urgentes?", mensaje_lower):
            filtro_resultado = await filtrar_tickets_urgentes()
        elif re.search(r"tickets?\s+sin\s+asignar", mensaje_lower):
            filtro_resultado = await filtrar_tickets_sin_asignar()
        elif re.search(r"tickets?\s+cerrados?", mensaje_lower):
            filtro_resultado = await filtrar_tickets_cerrados()
        else:
            # Buscar por estado específico (en progreso, pendiente, atendido, etc.)
            match_estado = re.search(r"tickets?\s+en\s+([\w\s]+)", mensaje_lower)
            if match_estado:
                estado = match_estado.group(1).strip()
                filtro_resultado = await filtrar_tickets_por_estado(estado)
            else:
                # Buscar "tickets asignados a <persona>"
                match = re.search(r"tickets?\s+asignados?\s+a\s+([\w.\-@]+)", mensaje_lower)
                if match:
                    persona = match.group(1)
                    filtro_resultado = await filtrar_tickets_asignados_a(persona)

        if filtro_resultado:
            prompt = f"Consulta del usuario: {mensaje}\n\nResultados de Jira:\n{filtro_resultado}\n\nPor favor, responde de manera útil y clara sobre estos tickets."
        else:
            # Detectar todas las consultas de Jira
            jira_queries = detect_jira_queries(mensaje)
            print(f"DEBUG: jira_queries detectadas: {jira_queries}")
            # Revisar si hay al menos una consulta de tipo 'summary'
            has_summary = any(q[0] == 'summary' for q in jira_queries)
            if jira_queries and has_summary:
                summary_tickets = []
                for query_type, tickets in jira_queries:
                    if query_type == 'summary':
                        summary_tickets.extend(tickets)
                summary_tickets = list(set(summary_tickets))
                ticket_infos = []
                for ticket in summary_tickets:
                    issue_data = await get_jira_info('ticket', ticket)
                    if issue_data is None:
                        ticket_infos.append(f"Ticket {ticket}: No se encontró información")
                    else:
                        ticket_infos.append(issue_data)
                all_info = "\n\n".join(ticket_infos)
                resumen_prompt = f"Por favor, haz un resumen general de la siguiente información de tickets de Jira.\n\n{all_info}"
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
                timeout=300.0
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