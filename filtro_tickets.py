import re
from jira_client import JiraClient

jira_client = JiraClient()

async def filtrar_tickets_abiertos():
    """Obtiene tickets abiertos según los estados definidos como abiertos"""
    estados_abiertos = [
        "esperando por soporte",
        "esperando por cliente",
        "escalado",
        "en progreso",
        "pendiente",
        "atendido"
    ]
    estados_cerrados = [
        "cerrado",
        "resuelto",
        "cancelado"
    ]
    estados_jql = ', '.join(f'"{estado}"' for estado in estados_abiertos)
    jql = f'status in ({estados_jql})'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return "No se encontraron tickets abiertos."
    return jira_client.format_search_results(search_data)

async def filtrar_tickets_por_estado(estado: str):
    """Obtiene tickets por un estado específico, aceptando variantes y plurales"""
    sinonimos_estados = {
        "esperando por soporte": ["esperando por soporte", "espera soporte", "soporte", "esperando soporte"],
        "esperando por cliente": ["esperando por cliente", "espera cliente", "cliente", "esperando cliente"],
        "escalado": ["escalado", "escalados"],
        "en progreso": ["en progreso", "progreso", "en progreso"],
        "pendiente": ["pendiente", "pendientes"],
        "atendido": ["atendido", "atendidos"],
        "cerrado": ["cerrado", "cerrados"],
        "resuelto": ["resuelto", "resueltos"],
        "cancelado": ["cancelado", "cancelados"]
    }
    estado_normalizado = estado.strip().lower()
    estado_real = None
    for estado_valido, variantes in sinonimos_estados.items():
        if any(var in estado_normalizado for var in variantes):
            estado_real = estado_valido
            break
    if not estado_real:
        sugerencias = ', '.join(sinonimos_estados.keys())
        return f"Estado '{estado}' no válido. Usa uno de: {sugerencias}"
    jql = f'status = "{estado_real}"'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return f"No se encontraron tickets con estado '{estado_real}'."
    return jira_client.format_search_results(search_data)

async def filtrar_tickets_cerrados():
    """Obtiene tickets en estado cerrado, resuelto o cancelado"""
    estados_cierre = ["cerrado", "resuelto", "cancelado"]
    estados_jql = ', '.join(f'"{estado}"' for estado in estados_cierre)
    jql = f'status in ({estados_jql})'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return "No se encontraron tickets cerrados."
    return jira_client.format_search_results(search_data) 