# Bender IA - Backend (Docker/Podman Compose)

Este repositorio levanta únicamente el backend (FastAPI) con `docker-compose.yml` en el puerto 8000. El frontend anterior fue retirado.

## Requisitos
- Docker + Docker Compose (o Podman + podman-compose)
- Puerto 8000 libre

## Variables de entorno
- `OLLAMA_URL` (por defecto: `http://192.168.10.80:8089`)
- `MODEL_NAME` (por defecto: `meta-llama-3-8b-instruct`)
- `FRONTEND_URL` (por defecto: `http://localhost:5173`) – usado por `GET /` para redirigir al frontend externo.

Puedes sobreescribirlas al ejecutar Compose:
```bash
OLLAMA_URL=http://TU_HOST:PUERTO MODEL_NAME=tu-modelo FRONTEND_URL=https://mi-front.ejemplo docker compose up -d --build
# o con Podman
OLLAMA_URL=http://TU_HOST:PUERTO MODEL_NAME=tu-modelo FRONTEND_URL=https://mi-front.ejemplo podman-compose up -d --build
```

## Levantar el backend
```bash
# Docker
docker compose up -d --build

# Podman
podman-compose up -d --build
```

Esto iniciará el contenedor `bender-ia` escuchando en `http://localhost:8000`.

## Verificar
```bash
# Salud (redirige al antiguo frontend; es normal si no existe)
curl -i http://localhost:8000/

# Modelos (informativo)
curl http://localhost:8000/models

# Probar conectividad con LMStudio/OpenAI-compatible
curl http://localhost:8000/test-lmstudio
```

## Endpoints principales
- `GET /` → redirección a `FRONTEND_URL` (por defecto `http://localhost:5173`)
- `GET /models`
- `GET /test-lmstudio`
- `POST /v1/chat/completions` (formato OpenAI)
- `GET /v1/models` (formato OpenAI)

Ejemplo de `POST /v1/chat/completions`:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "meta-llama-3-8b-instruct",
    "messages": [
      {"role": "user", "content": "Hola"}
    ],
    "max_tokens": 200,
    "temperature": 0.7
  }'
```

## Logs y administración
```bash
# Logs
docker compose logs -f bender-ia
# o
podman-compose logs -f bender-ia

# Estado
docker ps | grep bender-ia
podman ps | grep bender-ia

# Reiniciar / detener / eliminar
docker compose restart bender-ia
docker compose stop bender-ia
docker compose down
```

## Notas
- Si `test-lmstudio` falla, revisa que `OLLAMA_URL` apunte a tu servidor (LMStudio, Ollama o API OpenAI‑compatible) y que sea accesible desde el contenedor.
- El endpoint raíz (`/`) redirige a `http://localhost:5173`. Si no tienes frontend, usa los endpoints de API listados arriba.
