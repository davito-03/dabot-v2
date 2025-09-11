#!/bin/bash
# render-music-check.sh - Script para verificar y manejar música en Render

echo "🎵 Verificando compatibilidad de música en Render..."

# Verificar si estamos en Render
if [ "$RENDER" = "true" ] || [ ! -z "$RENDER_SERVICE_ID" ]; then
    echo "⚠️  Render detectado - Configurando para limitaciones de voz"
    
    # Establecer variable de entorno para deshabilitar música automáticamente
    export MUSIC_DISABLED=true
    echo "🚫 Música deshabilitada automáticamente en Render"
    
    # Verificar FFmpeg
    if command -v ffmpeg &> /dev/null; then
        echo "✅ FFmpeg encontrado, pero funcionalidad de voz limitada"
    else
        echo "❌ FFmpeg no encontrado - instalando..."
        apt-get update -qq
        apt-get install -y ffmpeg libopus-dev > /dev/null 2>&1
        
        if command -v ffmpeg &> /dev/null; then
            echo "✅ FFmpeg instalado exitosamente"
        else
            echo "❌ Error instalando FFmpeg"
        fi
    fi
    
    echo ""
    echo "📋 Resumen de configuración:"
    echo "   • Entorno: Render"
    echo "   • Música: Deshabilitada (limitaciones conocidas)"
    echo "   • FFmpeg: $(command -v ffmpeg > /dev/null && echo "Instalado" || echo "No disponible")"
    echo "   • Solución: Usar /voice-enable para intentar reactivar"
    echo ""
    
else
    echo "✅ Entorno local detectado - funcionalidad completa disponible"
fi

echo "🚀 Iniciando bot..."
