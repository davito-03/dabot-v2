# Imagen optimizada para Render Free Plan
FROM python:3.12-slim

# Variables de entorno optimizadas
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema (mínimas para Render)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y

# Establecer directorio de trabajo
WORKDIR /app

# Actualizar pip y setuptools
RUN pip install --upgrade pip setuptools wheel

# Copiar requirements minimal primero para cache
COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Intentar instalar requirements completos, fallback a minimal
COPY requirements-render.txt .
RUN pip install --no-cache-dir -r requirements-render.txt || \
    (echo "Falling back to minimal requirements" && \
     pip install --no-cache-dir -r requirements-minimal.txt)

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs data

# Exponer puerto para web API
EXPOSE 8080

# Comando para ejecutar el bot
CMD ["python", "bot.py"]
