# 🚀 Guía Rápida de Deploy en Render

## ⚡ Opción Recomendada: Web Service (Sin Docker)

### 1. **Crear Nuevo Web Service**
1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Haz clic en **"New +"** → **"Web Service"**
3. Conecta tu repositorio: `https://github.com/davito-03/dabot-v2.git`

### 2. **Configuración del Servicio**
```
Name: dabot-v2
Runtime: Python 3
Build Command: pip install --upgrade pip && pip install -r requirements-render.txt  
Start Command: python bot.py
```

### 3. **Variables de Entorno Esenciales**
```
DISCORD_TOKEN=tu_token_aqui
WEB_PORT=10000
WEB_HOST=0.0.0.0
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 4. **Health Check**
```
Health Check Path: /health
```

---

## 🐳 Opción Alternativa: Docker

Si quieres usar Docker, asegúrate de que la configuración sea:

### **Configuración Docker en Render:**
```
Dockerfile Path: ./Dockerfile
Docker Context: ./
```

### **Puerto Exposado:**
```
Port: 8080 (desde el Dockerfile)
```

---

## 🔧 **Troubleshooting**

### **Error: nextcord 3.1.1 requires Python 3.12+**
✅ **Solucionado** - Ahora usamos:
- `runtime.txt`: python-3.12.5
- `requirements-render.txt`: nextcord==2.6.0

### **Error: python3.12-pip package not found**
✅ **Solucionado** - Dockerfile actualizado para usar imagen oficial de Python

### **Error: Health check failing**
✅ **Solucionado** - Bot incluye servidor web con endpoint `/health`

---

## 📊 **Verificar Deploy**

### **Logs Esperados:**
```
🚀 Iniciando DABOT V2...
🌐 Servidor web iniciado en 0.0.0.0:10000
✅ Bot conectado como: DaBot#1234
🔄 Comandos sincronizados
```

### **Health Check:**
Visita: `https://tu-app.onrender.com/health`
Debería retornar:
```json
{
  "status": "healthy",
  "service": "DaBot v2", 
  "timestamp": "2025-09-11T...",
  "version": "2.0.0"
}
```

---

## 🎯 **Configuración Recomendada Final**

### **Método Simple (Recomendado):**
- ✅ Web Service sin Docker
- ✅ Python 3.12.5 
- ✅ requirements-render.txt
- ✅ Health check en /health

### **Si prefieres Docker:**
- ✅ Dockerfile simplificado con python:3.12-slim
- ✅ Build context: ./ 
- ✅ Puerto 8080

---

## 🔄 **Re-Deploy Después de Errores**

1. **Auto-deploy está activado** - Los cambios se despliegan automáticamente
2. **Manual deploy**: Dashboard → Tu servicio → "Manual Deploy"
3. **Logs en tiempo real**: Dashboard → Tu servicio → "Logs"

---

¡Los cambios están subidos a GitHub y listos para deploy! 🎉
