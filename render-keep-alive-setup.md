# 🔄 Configuración de Keep-Alive para Render

## 🚨 Problema: Render apaga servicios por inactividad

### **Plan Free**: Se apaga después de 15 minutos sin tráfico HTTP
### **Plan Paid**: Puede entrar en sleep mode en horarios de baja actividad

## ✅ Solución Implementada: Sistema Keep-Alive Completo

### 🔧 1. **Sistema Interno** (Automático)

El bot ahora incluye:
- **Servidor HTTP interno** en puerto 8080
- **Pings internos** cada 5 minutos  
- **Auto-ping externo** cada 10 minutos
- **Health checks** con métricas completas
- **Interfaz web** para monitoreo

### 🌐 2. **Endpoints Disponibles**

```
https://tu-app.onrender.com/          # Página principal con estado
https://tu-app.onrender.com/health    # Health check JSON
https://tu-app.onrender.com/ping      # Ping simple  
https://tu-app.onrender.com/status    # Estado detallado
https://tu-app.onrender.com/uptime    # Tiempo activo
```

### 📊 3. **Configuración en Render**

#### **Variables de Entorno Requeridas:**
```env
PORT=8080
RENDER_EXTERNAL_HOSTNAME=tu-app.onrender.com
KEEP_ALIVE_ENABLED=true
```

#### **Configuración del Servicio:**
- **Type**: Web Service ⚠️ (NO Background Worker)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`
- **Port**: 8080 (automático)

### 🎯 4. **Monitoreo Externo (Recomendado)**

#### **Opción A: UptimeRobot (Gratuito)**
1. Crear cuenta en [UptimeRobot](https://uptimerobot.com)
2. Agregar monitor HTTP(s):
   - **URL**: `https://tu-app.onrender.com/health`
   - **Intervalo**: 5 minutos
   - **Timeout**: 30 segundos

#### **Opción B: Ping-o-Matic (Gratuito)**
1. Registrar en [Ping-o-Matic](https://pingomatic.com)
2. URL: `https://tu-app.onrender.com/ping`
3. Intervalo: 10 minutos

#### **Opción C: StatusCake (Gratuito)**
1. Crear cuenta en [StatusCake](https://statuscake.com)
2. Monitor tipo: HTTP
3. URL: `https://tu-app.onrender.com/health`

### 🛠️ 5. **Script Manual** (Opcional)

Para ping desde tu propia máquina:
```bash
chmod +x external-ping.sh
./external-ping.sh
```

### 📋 6. **Verificación del Sistema**

#### **Paso 1: Verificar Endpoints**
Después del deploy, verificar que respondan:
```bash
curl https://tu-app.onrender.com/health
curl https://tu-app.onrender.com/ping
```

#### **Paso 2: Verificar Logs**
En Render Dashboard → Logs, buscar:
```
✅ Sistema Keep-Alive iniciado exitosamente
🌐 Servidor HTTP iniciado en 0.0.0.0:8080
💓 Ping interno #1 - Bot activo
```

#### **Paso 3: Verificar Estado**
Visitar: `https://tu-app.onrender.com/`
Debe mostrar página con estado del bot.

### ⚡ 7. **Configuración Automática**

El sistema detecta automáticamente:
- ✅ **Render**: Activa keep-alive automático
- ✅ **Puerto**: Usa variable PORT o 8080 por defecto
- ✅ **URL externa**: Detecta RENDER_EXTERNAL_HOSTNAME
- ✅ **Logs**: Información detallada en consola

### 🚨 8. **Limitaciones de Render Plan FREE**

⚠️ **Importante**: El plan gratuito tiene límites:
- **750 horas/mes**: ~31 días de uptime máximo
- **Suspensión después de límite**: Se apaga hasta el siguiente mes
- **Cold starts**: Puede tardar hasta 30 segundos en responder

### 💰 9. **Recomendación: Upgrade a Plan Paid**

Para **uptime 24/7 garantizado**:
- **Starter Plan ($7/mes)**: Uptime completo sin límites
- **Sin cold starts**: Respuesta inmediata
- **Recursos garantizados**: Mejor rendimiento

### 🎯 10. **Resultado Esperado**

Con esta configuración:
- ✅ **Bot activo 24/7** (dentro de límites del plan)
- ✅ **No se apaga por inactividad**
- ✅ **Monitoreo automático** con métricas
- ✅ **Recuperación automática** en caso de errores
- ✅ **Interfaz web** para verificar estado

### 📞 11. **Troubleshooting**

#### **Bot se sigue apagando:**
1. Verificar que el servicio sea **Web Service** (no Background Worker)
2. Verificar variable `PORT=8080`
3. Configurar monitor externo (UptimeRobot)
4. Revisar límites del plan gratuito

#### **Endpoints no responden:**
1. Verificar logs de Render para errores
2. Verificar variable `RENDER_EXTERNAL_HOSTNAME`
3. Probar endpoints localmente primero

#### **Health check falla:**
1. Verificar que el bot se conectó correctamente a Discord
2. Revisar permisos del bot en servidores
3. Verificar token de Discord válido

### 🏁 12. **Checklist Final**

- [ ] Servicio configurado como **Web Service**
- [ ] Variable `PORT=8080` configurada
- [ ] Bot desplegado y logs muestran Keep-Alive activo
- [ ] Endpoints `/health` y `/ping` responden
- [ ] Monitor externo configurado (UptimeRobot recomendado)
- [ ] Página principal muestra estado "ONLINE"
- [ ] Considerar upgrade a plan paid para uptime completo
