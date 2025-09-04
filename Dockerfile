# usar imagen de python 3.11
FROM python:3.11-slim

# establecer directorio de trabajo
WORKDIR /app

# instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# copiar archivos de requirements
COPY requirements.txt .

# instalar dependencias de python
RUN pip install --no-cache-dir -r requirements.txt

# copiar código fuente
COPY . .

# crear directorios necesarios
RUN mkdir -p logs data

# exponer puerto para web api
EXPOSE 8080

# comando para ejecutar el bot
CMD ["python", "bot.py"]
