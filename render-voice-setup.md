# 🎵 Configuración de Voz para Render

## ⚠️ Problema Identificado

El error `WebSocket closed with 4006` indica que Discord está rechazando la conexión de voz desde Render. Este es un problema común en proveedores de hosting.

## 🔧 Soluciones Implementadas

### 1. FFmpeg Optimizado
- Configuración específica para servidores remotos
- Detección automática de rutas FFmpeg
- Opciones de reconexión mejoradas

### 2. Manejo de Errores Robusto
- Reintentos automáticos de conexión
- Timeouts configurables
- Mensajes de error descriptivos

### 3. Detección de Entorno
- Identificación automática de Render
- Advertencias apropiadas
- Comando `/voice-info` para diagnóstico

## 📦 Instalación de FFmpeg en Render

### Opción 1: Buildpack (Recomendado)
```bash
# En la configuración de Render, agregar buildpack:
https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
```

### Opción 2: Dockerfile Personalizado
```dockerfile
FROM python:3.12-slim

# Instalar FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar código y dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

### Opción 3: Script de Setup
```bash
#!/bin/bash
# render-setup.sh
apt-get update
apt-get install -y ffmpeg
python bot.py
```

## 🚨 Limitaciones de Render

### Problemas Conocidos
1. **Conexiones UDP**: Render puede bloquear conexiones UDP necesarias para voz
2. **NAT/Firewall**: Restricciones de red que afectan Discord
3. **Latencia**: Mayor latencia puede causar timeouts
4. **Recursos**: Limitaciones de CPU/memoria en planes gratuitos

### Alternativas
1. **VPS Dedicado**: Mejor control sobre configuración
2. **Railway**: Mejor soporte para aplicaciones con voz
3. **Fly.io**: Más flexible para conexiones de red
4. **Servidor Local**: Funcionalidad completa garantizada

## 🔍 Diagnóstico

### Comandos de Prueba
```bash
# Verificar FFmpeg
ffmpeg -version

# Probar conectividad Discord
curl -I https://discord.com/api/gateway

# Verificar resolución DNS
nslookup discord.media
```

### Logs Importantes
```
ERROR:nextcord.voice_client:Failed to connect to voice... Retrying...
ConnectionClosed: Shard ID None WebSocket closed with 4006
```

## 🛠️ Pasos de Resolución

### 1. Verificar Buildpack
- Asegurar que el buildpack de FFmpeg está instalado
- Rebuilder la aplicación después de agregar buildpack

### 2. Configurar Variables de Entorno
```env
FFMPEG_PATH=/app/.heroku/vendor/ffmpeg/ffmpeg
LD_LIBRARY_PATH=/app/.heroku/vendor/ffmpeg/lib:$LD_LIBRARY_PATH
```

### 3. Actualizar Dependencias
```bash
pip install --upgrade nextcord yt-dlp
```

### 4. Probar Funcionalidad
- Usar `/voice-info` para verificar estado
- Intentar `/play` con URLs simples
- Revisar logs de Render

## 📞 Soporte

Si los problemas persisten:

1. **Logs Detallados**: Habilitar logging verbose
2. **Configuración Mínima**: Probar con configuración básica
3. **Proveedor Alternativo**: Considerar migración si es crítico
4. **Contacto Discord**: Reportar si es problema de la API

## 🎯 Resultado Esperado

Con estas mejoras:
- ✅ Mejor manejo de errores de conexión
- ✅ Mensajes informativos para usuarios
- ✅ Reintentos automáticos
- ✅ Detección de limitaciones del entorno
- ⚠️ Las limitaciones de Render pueden persistir

## 📋 Checklist Final

- [ ] Buildpack FFmpeg instalado
- [ ] Variables de entorno configuradas
- [ ] Código actualizado con mejoras
- [ ] Aplicación rebuildeada en Render
- [ ] Pruebas realizadas con `/voice-info`
- [ ] Documentación de limitaciones clara para usuarios
