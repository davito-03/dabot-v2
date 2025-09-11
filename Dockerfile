# Usar imagen base de Ubuntu con Python 3.12
FROM ubuntu:22.04

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Instalar Python 3.12 y dependencias del sistema
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.12 \
    python3.12-pip \
    python3.12-venv \
    python3.12-dev \
    ffmpeg \
    git \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    libnacl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Crear enlaces simbólicos para python y pip
RUN ln -s /usr/bin/python3.12 /usr/bin/python && \
    ln -s /usr/bin/python3.12 /usr/bin/python3

# Establecer directorio de trabajo
WORKDIR /app

# Actualizar pip
RUN python -m pip install --upgrade pip

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
