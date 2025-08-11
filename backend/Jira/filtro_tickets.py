#Filtro Tickets.py
import re
from .jira_client import JiraClient

# Instancia global del cliente de Jira para realizar búsquedas
jira_client = JiraClient()

# Filtra y retorna los tickets abiertos según los estados definidos como abiertos en Jira
async def filtrar_tickets_abiertos():
    """
    Obtiene tickets abiertos según los estados definidos como abiertos.
    Utiliza una lista de estados considerados como abiertos y construye una consulta JQL para Jira.
    Retorna los resultados formateados o un mensaje si no hay tickets abiertos.
    """
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
    # Construye la consulta JQL para los estados abiertos
    estados_jql = ', '.join(f'"{estado}"' for estado in estados_abiertos)
    jql = f'status in ({estados_jql})'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return "No se encontraron tickets abiertos."
    return jira_client.format_search_results(search_data, formato_total=True)

# Filtra tickets por un estado específico, aceptando variantes y plurales
async def filtrar_tickets_por_estado(estado: str):
    """
    Obtiene tickets por un estado específico, aceptando variantes y plurales.
    Permite buscar usando sinónimos o formas alternativas del estado.
    Si el estado no es válido, sugiere los posibles valores aceptados.
    """
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
    # Busca el estado real a partir de los sinónimos
    for estado_valido, variantes in sinonimos_estados.items():
        if any(var in estado_normalizado for var in variantes):
            estado_real = estado_valido
            break
    if not estado_real:
        sugerencias = ', '.join(sinonimos_estados.keys())
        return f"Estado '{estado}' no válido. Usa uno de: {sugerencias}"
    # Construye la consulta JQL para el estado encontrado
    jql = f'status = "{estado_real}"'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return f"No se encontraron tickets con estado '{estado_real}'."
    return jira_client.format_search_results(search_data, formato_total=True)

# Filtra y retorna los tickets en estado cerrado, resuelto o cancelado
async def filtrar_tickets_cerrados():
    """
    Obtiene tickets en estado cerrado, resuelto o cancelado.
    Construye una consulta JQL para estos estados y retorna los resultados formateados o un mensaje si no hay tickets cerrados.
    """
    estados_cierre = ["cerrado", "resuelto", "cancelado"]
    # Construye la consulta JQL para los estados de cierre
    estados_jql = ', '.join(f'"{estado}"' for estado in estados_cierre)
    jql = f'status in ({estados_jql})'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return "No se encontraron tickets cerrados."
    return jira_client.format_search_results(search_data, formato_total=True)

# Filtra y retorna los tickets en estado 'Pendiente'
async def filtrar_tickets_pendientes():
    """
    Obtiene solo los tickets en estado 'Pendiente'.
    """
    estados_pendientes = ["Pendiente"]
    estados_jql = ', '.join(f'"{estado}"' for estado in estados_pendientes)
    jql = f'status in ({estados_jql})'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return "No se encontraron tickets pendientes."
    return jira_client.format_search_results(search_data, formato_total=True) 

# Filtra y retorna los tickets en estado 'En progreso'
async def filtrar_tickets_en_progreso():
    """
    Obtiene solo los tickets en estado 'En progreso'.
    """
    estados_en_progreso = ["En progreso"]
    estados_jql = ', '.join(f'"{estado}"' for estado in estados_en_progreso)
    jql = f'status in ({estados_jql})'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return "No se encontraron tickets en progreso."
    return jira_client.format_search_results(search_data, formato_total=True) 

# Filtra y retorna los tickets en estado 'Atendido'
async def filtrar_tickets_atendidos():
    """
    Obtiene solo los tickets en estado 'Atendido'.
    """
    estados_atendidos = ["Atendido"]
    estados_jql = ', '.join(f'"{estado}"' for estado in estados_atendidos)
    jql = f'status in ({estados_jql})'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return "No se encontraron tickets atendidos."
    return jira_client.format_search_results(search_data, formato_total=True) 

# Filtra y retorna los tickets en estado 'Escalado'
async def filtrar_tickets_escalados():
    """
    Obtiene solo los tickets en estado 'Escalado'.
    """
    estados_escalados = ["Escalado"]
    estados_jql = ', '.join(f'"{estado}"' for estado in estados_escalados)
    jql = f'status in ({estados_jql})'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return "No se encontraron tickets escalados."
    return jira_client.format_search_results(search_data, formato_total=True) 

# Filtra y retorna los tickets en estado 'Esperando soporte'
async def filtrar_tickets_esperando_soporte():
    """
    Obtiene solo los tickets en estado 'Esperando soporte'.
    """
    estados_esperando_soporte = ["Esperando soporte"]
    estados_jql = ', '.join(f'"{estado}"' for estado in estados_esperando_soporte)
    jql = f'status in ({estados_jql})'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return "No se encontraron tickets esperando soporte."
    return jira_client.format_search_results(search_data, formato_total=True) 

# Filtra y retorna los tickets en estado 'Esperando por cliente'
async def filtrar_tickets_esperando_por_cliente():
    """
    Obtiene solo los tickets en estado 'Esperando por cliente'.
    """
    estados_esperando_por_cliente = ["Esperando por cliente"]
    estados_jql = ', '.join(f'"{estado}"' for estado in estados_esperando_por_cliente)
    jql = f'status in ({estados_jql})'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return "No se encontraron tickets esperando por cliente."
    return jira_client.format_search_results(search_data, formato_total=True) 

# Filtra y retorna los tickets por prioridad específica (del 1 al 5)
async def filtrar_tickets_por_prioridad(prioridad: str):
    """
    Obtiene tickets por una prioridad específica (del 1 al 5), aceptando variantes como 'prioridad 1', 'p1', '1', etc.
    Si la prioridad no es válida, sugiere los posibles valores aceptados.
    """
    sinonimos_prioridad = {
        "1": ["1", "p1", "prioridad 1", "alta", "muy alta"],
        "2": ["2", "p2", "prioridad 2"],
        "3": ["3", "p3", "prioridad 3", "media"],
        "4": ["4", "p4", "prioridad 4", "baja"],
        "5": ["5", "p5", "prioridad 5", "muy baja"]
    }
    prioridad_normalizada = prioridad.strip().lower()
    prioridad_real = None
    for valor, variantes in sinonimos_prioridad.items():
        if any(var in prioridad_normalizada for var in variantes):
            prioridad_real = valor
            break
    if not prioridad_real:
        sugerencias = ', '.join([f'Prioridad {k}' for k in sinonimos_prioridad.keys()])
        return f"Prioridad '{prioridad}' no válida. Usa uno de: {sugerencias}"
    jql = f'priority = "{prioridad_real}"'
    search_data = await jira_client.search_issues(jql)
    if not search_data:
        return f"No se encontraron tickets con prioridad '{prioridad_real}'."
    return jira_client.format_search_results(search_data, formato_total=True) 

async def obtener_top_5_asignados():
    """
    Obtiene las 5 personas con mayor cantidad de tickets asignados.
    Utiliza una consulta JQL para obtener todos los tickets asignados y luego
    cuenta y ordena por cantidad de tickets por asignado.
    Retorna un ranking formateado de los top 5 asignados.
    """
    try:
        # Consulta JQL para obtener todos los tickets que tienen asignado
        # Usamos ORDER BY created DESC para obtener una muestra más representativa
        # que incluya tickets recientes y evite sesgos por orden alfabético
        jql = 'assignee IS NOT EMPTY ORDER BY created DESC'
        search_data = await jira_client.search_issues(jql, max_results=1000)
        
        if not search_data:
            return "No se encontraron tickets asignados. Error: No se pudo obtener datos de Jira."
        
        if "issues" not in search_data:
            return "No se encontraron tickets asignados. Error: Formato de respuesta inesperado de Jira."
        
        issues = search_data["issues"]
        
        # Si no hay tickets con assignee IS NOT EMPTY, probar con una consulta más amplia
        if not issues:
            jql_alt = 'ORDER BY created DESC'
            search_data_alt = await jira_client.search_issues(jql_alt, max_results=1000)
            
            if search_data_alt and "issues" in search_data_alt:
                issues = search_data_alt["issues"]
            else:
                return "No se encontraron tickets en el sistema."
        
        # Contar tickets por asignado
        asignados_count = {}
        tickets_sin_asignar = 0
        
        for issue in issues:
            fields = issue.get("fields", {})
            assignee = fields.get("assignee")
            
            if assignee:
                assignee_name = assignee.get("displayName", "Sin nombre")
                asignados_count[assignee_name] = asignados_count.get(assignee_name, 0) + 1
            else:
                tickets_sin_asignar += 1
        
        if not asignados_count:
            return "No se encontraron tickets asignados. Todos los tickets están sin asignar."
        
        # Ordenar por cantidad de tickets (descendente) y tomar los top 5
        sorted_asignados = sorted(asignados_count.items(), key=lambda x: x[1], reverse=True)
        top_5 = sorted_asignados[:5]
        
        # Formatear resultado
        result = "**Top 5 personas con mayor cantidad de tickets asignados:**\n\n"
        for i, (assignee_name, count) in enumerate(top_5, 1):
            result += f"{i}. **{assignee_name}**: {count} tickets\n"
        
        # Agregar información adicional
        total_asignados = len(asignados_count)
        total_tickets = sum(asignados_count.values())
        result += f"\n**Resumen:**\n"
        result += f"- Total de personas con tickets asignados: {total_asignados}\n"
        result += f"- Total de tickets asignados: {total_tickets}\n"
        result += f"- Tickets sin asignar: {tickets_sin_asignar}\n"
        
        return result
        
    except Exception as e:
        return f"Error obteniendo el ranking de asignados: {str(e)}" 

    
    
    