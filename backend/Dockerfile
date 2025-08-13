FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements primero para aprovechar la caché de Docker
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Hacer los scripts de inicio ejecutables
RUN chmod +x start.sh

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exponer el puerto
EXPOSE 8000

# Health check para verificar que la aplicación esté funcionando
HEALTHCHECK --interval=50s --timeout=20s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Usar el script de inicio robusto
CMD ["./start.sh"] 