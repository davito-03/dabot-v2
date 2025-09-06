#!/bin/bash
# Script de configuración rápida para DaBot v2

echo "🚀 CONFIGURADOR RÁPIDO DE DABOT V2"
echo "=================================="
echo ""

# Crear backup de configuración actual si existe
if [ -f "config.yaml" ]; then
    echo "💾 Creando backup de configuración actual..."
    cp config.yaml "config_backup_$(date +%Y%m%d_%H%M%S).yaml"
    echo "✅ Backup creado"
fi

echo ""
echo "📋 CONFIGURACIÓN BÁSICA"
echo "----------------------"

# Solicitar configuración básica
read -p "🌍 Idioma (es-ES/en-US): " language
language=${language:-es-ES}

read -p "🔧 Prefijo para comandos (!): " prefix
prefix=${prefix:-!}

read -p "👑 Tu ID de Discord: " owner_id

read -p "🎫 ID del canal de tickets: " ticket_channel

read -p "👋 ID del canal de bienvenidas: " welcome_channel

read -p "📝 ID del canal de logs: " log_channel

echo ""
echo "⚙️ Aplicando configuración..."

# Crear configuración personalizada usando sed (o similar)
sed -i "s/language: 'es-ES'/language: '$language'/g" config.yaml
sed -i "s/prefix: '!'/prefix: '$prefix'/g" config.yaml

if [ ! -z "$owner_id" ]; then
    sed -i "s/'600041740124160011': 100/'$owner_id': 100/g" config.yaml
fi

if [ ! -z "$ticket_channel" ]; then
    sed -i "s/channel_id: ''/channel_id: '$ticket_channel'/g" config.yaml
fi

if [ ! -z "$welcome_channel" ]; then
    sed -i "s/channel_id: ''/channel_id: '$welcome_channel'/g" config.yaml
fi

if [ ! -z "$log_channel" ]; then
    sed -i "s/moderation: ''/moderation: '$log_channel'/g" config.yaml
fi

echo "✅ Configuración aplicada"
echo ""
echo "🎯 MÓDULOS RECOMENDADOS"
echo "----------------------"
echo "✅ Habilitados por defecto:"
echo "   - Moderación (avisos, bans, automod)"
echo "   - Niveles (XP, ranking, tarjetas)"
echo "   - Interacciones (gato, perro, abrazos)"
echo "   - Bienvenidas (tarjetas personalizadas)"
echo "   - Dashboard web (puerto 8080)"
echo ""
echo "⚠️  Para personalizar más:"
echo "   1. Edita manualmente config.yaml"
echo "   2. Usa /config en Discord después de iniciar el bot"
echo "   3. Visita el dashboard en http://localhost:8080"
echo ""
echo "🚀 ¡Listo! Ejecuta el bot con:"
echo "   python bot.py"
