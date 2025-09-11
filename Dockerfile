# Usar imagen oficial de Python 3.12
FROM python:3.12-slim

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Actualizar pip
RUN pip install --upgrade pip

# Copiar archivos de requirements
COPY requirements-render.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements-render.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p logs data

# Configurar permisos
RUN chmod +x /app

# Exponer puerto para web API
EXPOSE 8080

# Comando para ejecutar el bot
CMD ["python", "bot.py"]
