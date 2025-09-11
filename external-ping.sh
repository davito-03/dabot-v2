#!/bin/bash
# external-ping.sh - Script para hacer ping externo al bot en Render

# Configuración
BOT_URL="${RENDER_EXTERNAL_URL:-https://your-app.onrender.com}"
PING_INTERVAL=300  # 5 minutos
LOG_FILE="/tmp/ping.log"

echo "🌐 Iniciando sistema de ping externo para mantener activo el bot"
echo "📍 URL objetivo: $BOT_URL"
echo "⏰ Intervalo: $PING_INTERVAL segundos"
echo ""

# Función de ping
ping_bot() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Ping al endpoint de health
    local response=$(curl -s -w "%{http_code}" -o /dev/null "$BOT_URL/health" --max-time 30)
    
    if [ "$response" = "200" ]; then
        echo "[$timestamp] ✅ Ping exitoso - Bot activo (HTTP $response)"
        echo "[$timestamp] OK - $response" >> "$LOG_FILE"
    else
        echo "[$timestamp] ❌ Ping falló - HTTP $response"
        echo "[$timestamp] FAIL - $response" >> "$LOG_FILE"
        
        # Intentar ping simple si health falla
        local simple_response=$(curl -s -w "%{http_code}" -o /dev/null "$BOT_URL/ping" --max-time 30)
        if [ "$simple_response" = "200" ]; then
            echo "[$timestamp] ✅ Ping simple exitoso (HTTP $simple_response)"
            echo "[$timestamp] SIMPLE_OK - $simple_response" >> "$LOG_FILE"
        fi
    fi
}

# Loop principal
while true; do
    ping_bot
    sleep $PING_INTERVAL
done
