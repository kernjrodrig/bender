# Integración con LMStudio

## Configuración

Este backend ahora está configurado para trabajar con **LMStudio** en lugar de Ollama.

### Variables de Entorno

- `OLLAMA_URL`: URL del servidor LMStudio (por defecto: `http://192.168.10.80:8089`)
- `MODEL_NAME`: Nombre del modelo a usar (por defecto: `llama3`)

### Endpoints Disponibles

#### `/test-lmstudio`
Endpoint de prueba para verificar la conectividad con LMStudio.

**GET** `/test-lmstudio`

Respuesta exitosa:
```json
{
  "status": "success",
  "message": "Conexión exitosa con LMStudio",
  "url": "http://192.168.10.80:8089",
  "models": [...]
}
```

#### `/models`
Lista los modelos disponibles en LMStudio.

**GET** `/models`

#### `/chat`
Endpoint principal de chat que utiliza LMStudio para generar respuestas.

**POST** `/chat`

Body:
```json
{
  "mensaje": "Consulta del usuario"
}
```

## Pruebas

### Script de Prueba
Ejecuta el script de prueba para verificar la conectividad:

```bash
cd backend
python test_lmstudio.py
```

### Verificación Manual
1. Asegúrate de que LMStudio esté ejecutándose en `http://192.168.10.80:8089`
2. Verifica que el modelo `llama3` esté disponible
3. Prueba el endpoint `/test-lmstudio`

## Docker

### Variables en docker-compose.yml
```yaml
environment:
  - OLLAMA_URL=http://192.168.10.80:8089
  - MODEL_NAME=llama3
```

### Reconstruir y ejecutar
```bash
docker-compose down
docker-compose up --build
```

## Diferencias con Ollama

- **URL**: Cambió de ngrok a IP local
- **Timeout**: Reducido de 5 minutos a 2 minutos
- **Mensajes de error**: Actualizados para reflejar LMStudio

## Troubleshooting

### Error de Conexión
- Verifica que LMStudio esté ejecutándose
- Confirma la IP y puerto en la configuración
- Asegúrate de que no haya firewall bloqueando la conexión

### Timeout
- El timeout está configurado en 2 minutos
- Si es muy lento, considera ajustar el timeout en `Jira_chat.py`

### Modelo No Encontrado
- Verifica que el modelo `llama3` esté disponible en LMStudio
- Usa el endpoint `/models` para listar modelos disponibles 