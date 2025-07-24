import re
from jira_client import JiraClient

jira_client = JiraClient()

def detect_jira_queries(mensaje: str) -> list[tuple[str, list]]:
    """Detecta todas las consultas de Jira en el mensaje y extrae información relevante (soporta múltiples tipos y tickets)"""
    patterns = {
        'ticket': r'(?:ticket|issue|jira|tarea|problema)\s+((?:sd-\d{1,3}(?:,?\s*)?)+)',
        'project': r'(?:proyecto|project)\s+([A-Z]+)',
        'project_of_ticket': r'(?:proyecto|project)\s+((?:sd-\d{1,3}(?:,?\s*)?)+)',
        'search': r'(?:buscar|search|encontrar|listar)\s+(.+?)(?:\s+en\s+jira)?$',
        'status': r'(?:estado|status)\s+((?:sd-\d{1,3}(?:,?\s*)?)+)|((?:sd-\d{1,3}(?:,?\s*)?)+)\s+(?:estado|status)',
        'assignee': r'(?:asignado|assignee|asignación)\s+((?:sd-\d{1,3}(?:,?\s*)?)+)|((?:sd-\d{1,3}(?:,?\s*)?)+)\s+(?:asignado|assignee|asignación)',
        'priority': r'(?:prioridad|priority)\s+((?:sd-\d{1,3}(?:,?\s*)?)+)|((?:sd-\d{1,3}(?:,?\s*)?)+)\s+(?:prioridad|priority)',
        'summary': r'(?:resumen|summary|resumir)\s+((?:sd-\d{1,3}(?:,?\s*)?)+)|((?:sd-\d{1,3}(?:,?\s*)?)+)\s+(?:resumen|summary)',
        'changelog': r'(?:historial de cambios|changelog|historial|cambios)\s+((?:sd-\d{1,3}(?:,?\s*)?)+)|((?:sd-\d{1,3}(?:,?\s*)?)+)\s+(?:historial de cambios|changelog)',
        'simple_ticket': r'\b(sd-\d{1,3})\b'
    }
    results = []
    for query_type, pattern in patterns.items():
        if query_type != 'simple_ticket':
            for match in re.finditer(pattern, mensaje, re.IGNORECASE):
                value = match.group(1) if match.group(1) else (match.group(2) if len(match.groups()) > 1 else None)
                if value:
                    tickets = re.findall(r'sd-\d{1,3}', value, re.IGNORECASE)
                    if tickets:
                        results.append((query_type, tickets))
    # Si no se encontró ningún patrón, buscar tickets simples
    if not results:
        simple_matches = re.findall(patterns['simple_ticket'], mensaje, re.IGNORECASE)
        if simple_matches:
            results.append(('ticket', simple_matches))
    return results

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