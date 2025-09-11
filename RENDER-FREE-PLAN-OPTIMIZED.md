# 🔥 CONFIGURACIÓN OPTIMIZADA RENDER FREE PLAN

## 📊 Límites del Plan Gratuito Render:
- **750 horas/mes**: ~25 días de actividad
- **512MB RAM**: Limitada
- **0.1 CPU**: Compartida
- **Sleep después de 15 min**: Sin tráfico
- **Build time**: 20 minutos máximo

## ⚙️ OPTIMIZACIONES APLICADAS:

### **1. Requirements Mínimos**
```bash
# Solo paquetes esenciales
nextcord>=2.6.0  # Core Discord
psutil>=5.9.0    # Keep-Alive system
aiohttp>=3.9.0   # HTTP server
python-dotenv    # Variables de entorno
```

### **2. Keep-Alive Inteligente**
```python
# Ping cada 10 minutos para evitar sleep
# Consumo mínimo de CPU
# Auto-limpieza de memoria
# Compatible sin psutil si falla
```

### **3. Deshabilitar Música**
```env
MUSIC_DISABLED=true  # Ahorra 200MB+ RAM
```

### **4. Variables de Entorno Render**
```env
DISCORD_TOKEN=tu_token
MUSIC_DISABLED=true
PORT=10000
RENDER_EXTERNAL_HOSTNAME=tu-app.onrender.com
```

## 🚀 DEPLOY STEPS:

### **1. Crear Service en Render**
```
Type: Web Service
Repo: tu-repo-github
Branch: main
Runtime: Python 3
Build Command: pip install -r requirements-render.txt
Start Command: python bot.py
```

### **2. Environment Variables**
```
DISCORD_TOKEN = tu_token_discord
MUSIC_DISABLED = true
PORT = 10000
```

### **3. Health Check URL**
```
https://tu-app.onrender.com/health
```

## 📈 RESULTADOS ESPERADOS:

### **✅ Con Keep-Alive:**
- ✅ **24/7 activo** (hasta límite mensual)
- ✅ **Auto-ping** cada 10 minutos
- ✅ **HTTP health checks**
- ✅ **Uso eficiente de recursos**

### **⚠️ Limitaciones del Plan Gratuito:**
- ❌ **Música NO funciona** (Error 4006)
- ⏰ **~25 días/mes** máximo uptime
- 💾 **512MB RAM** límite estricto
- 🔄 **Restart** si excede recursos

## 🎯 PARA 24/7 COMPLETO:

### **Opción 1: Render Paid ($7/mes)**
```
- ✅ Uptime ilimitado
- ✅ 512MB RAM garantizada
- ✅ Música NO funciona (limitación IP)
```

### **Opción 2: Oracle Cloud Free**
```
- ✅ Gratis permanente
- ✅ 1GB RAM siempre activo
- ✅ Música funciona perfectamente
- ✅ IP dedicada
```

## 📋 CHECKLIST RENDER:

- [ ] **Bot deployado** en Render
- [ ] **Environment variables** configuradas
- [ ] **Keep-alive** funcionando
- [ ] **Health check** respondiendo
- [ ] **Logs** sin errores
- [ ] **24/7** dentro del límite mensual

## ⚡ COMANDOS DE MONITOREO:

```bash
# Ver uptime
curl https://tu-app.onrender.com/status

# Health check
curl https://tu-app.onrender.com/health

# Ping manual
curl https://tu-app.onrender.com/ping
```

**🎉 Con esta configuración tendrás ~25 días de uptime gratis mensual en Render!**