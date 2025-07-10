import os
import httpx
from typing import Dict, List, Optional

class JiraClient:
    def __init__(self):
        self.base_url = os.getenv("JIRA_URL", "https://servicedeskguzdan.atlassian.net")
        self.api_token = os.getenv("JIRA_API_TOKEN", "ATATT3xFfGF0WYvVBIvD0E1vQjLC51Qm1LHbaC6zJLyIqC852CNFb3f4ojMGNCZ7I_fHzaPhKDqqWeI_P1YYWbDYwYFMHNk9G0s6rLlDQrUqmCRpPalxvI4r0xfMG9qd2kMJ38054bKW92WiKwfPjrjBfSig1ctLcihTlbBWaSqSJdx_kCtThZY=5BEA5AC6")
        self.email = os.getenv("JIRA_EMAIL", "javier.rodriguez@guzdan.com")
        
    def _get_headers(self) -> Dict[str, str]:
        """Genera headers para autenticación con Jira"""
        import base64
        credentials = f"{self.email}:{self.api_token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def get_issue(self, issue_key: str) -> Optional[Dict]:
        """Obtiene información de un ticket específico"""
        try:
            print(f"DEBUG: Consultando Jira para issue: {issue_key}")
            print(f"DEBUG: URL: {self.base_url}/rest/api/3/issue/{issue_key}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/3/issue/{issue_key}",
                    headers=self._get_headers(),
                    timeout=30.0
                )
                
                print(f"DEBUG: Status code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"DEBUG: Respuesta exitosa para {issue_key}")
                    return data
                else:
                    print(f"DEBUG: Error HTTP {response.status_code} para {issue_key}")
                    print(f"DEBUG: Respuesta: {response.text}")
                    return None
        except Exception as e:
            print(f"DEBUG: Excepción obteniendo issue {issue_key}: {e}")
            return None
    
    async def search_issues(self, jql: str, max_results: int = 50) -> Optional[Dict]:
        """Busca tickets usando JQL"""
        try:
            payload = {
                "jql": jql,
                "maxResults": max_results,
                "fields": ["summary", "status", "assignee", "priority", "created", "updated"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/rest/api/3/search",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
        except Exception as e:
            print(f"Error buscando issues: {e}")
            return None
    
    async def get_project(self, project_key: str) -> Optional[Dict]:
        """Obtiene información de un proyecto"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/api/3/project/{project_key}",
                    headers=self._get_headers(),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
        except Exception as e:
            print(f"Error obteniendo proyecto {project_key}: {e}")
            return None
    
    def format_issue_info(self, issue_data: Dict) -> str:
        """Formatea la información del ticket para que sea legible"""
        if not issue_data:
            return "No se encontró información del ticket"
        
        fields = issue_data.get("fields", {})
        
        info = f"""
**Ticket: {issue_data.get('key', 'N/A')}**
- **Resumen**: {fields.get('summary', 'N/A')}
- **Estado**: {fields.get('status', {}).get('name', 'N/A')}
- **Prioridad**: {fields.get('priority', {}).get('name', 'N/A')}
- **Asignado**: {fields.get('assignee', {}).get('displayName', 'Sin asignar')}
- **Creado**: {fields.get('created', 'N/A')}
- **Actualizado**: {fields.get('updated', 'N/A')}
- **Descripción**: {fields.get('description', 'Sin descripción')}
"""
        return info.strip()
    
    def format_search_results(self, search_data: Dict) -> str:
        """Formatea los resultados de búsqueda"""
        if not search_data or "issues" not in search_data:
            return "No se encontraron tickets"
        
        issues = search_data["issues"]
        if not issues:
            return "No se encontraron tickets que coincidan con la búsqueda"
        
        result = f"**Encontrados {len(issues)} tickets:**\n\n"
        
        for issue in issues:
            fields = issue.get("fields", {})
            result += f"• **{issue.get('key')}**: {fields.get('summary', 'Sin resumen')} - {fields.get('status', {}).get('name', 'N/A')}\n"
        
        return result.strip() 