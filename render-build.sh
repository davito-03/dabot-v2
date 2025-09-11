#!/bin/bash
# render-build.sh - Script de construcción para Render con soporte FFmpeg

echo "🚀 Iniciando build para Render..."

# Actualizar repositorios
echo "📦 Actualizando repositorios..."
apt-get update -qq

# Instalar FFmpeg y dependencias
echo "🎵 Instalando FFmpeg..."
apt-get install -y \
    ffmpeg \
    libffi-dev \
    libnacl-dev \
    python3-dev \
    libopus-dev \
    libopus0 \
    > /dev/null 2>&1

# Verificar instalación de FFmpeg
echo "🔍 Verificando FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg instalado correctamente:"
    ffmpeg -version | head -n 1
else
    echo "❌ Error: FFmpeg no se instaló correctamente"
    exit 1
fi

# Instalar dependencias de Python
echo "🐍 Instalando dependencias de Python..."
pip install --no-cache-dir -r requirements.txt

echo "🎉 Build completado exitosamente!"
echo "🎵 El bot está listo para reproducir música!"
