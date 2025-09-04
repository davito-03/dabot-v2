# 🚀 Guía de Despliegue Completa - Da Bot v2

## 📋 Resumen del Sistema

- **Bot de Discord**: Desplegado en Render.com con PostgreSQL
- **Dashboard Web**: Desplegado en davito.es/dabot via FTP (Hostalia)
- **Comunicación**: API REST entre dashboard y bot
- **Autenticación**: Discord OAuth2 con JWT

## 🔧 Paso 1: Configuración de Discord Developer Portal

### A. Crear Aplicación de Discord
1. Ir a https://discord.com/developers/applications
2. Click "New Application"
3. Nombre: "Da Bot v2"
4. Guardar

### B. Configurar Bot
1. Ir a sección "Bot"
2. Click "Add Bot"
3. **Copiar Bot Token** (lo necesitarás después)
4. Habilitar intents:
   - ✅ Message Content Intent
   - ✅ Server Members Intent
   - ✅ Presence Intent

### C. Configurar OAuth2
1. Ir a sección "OAuth2" → "General"
2. Añadir Redirect URI: `https://davito.es/dabot/auth`
3. **Copiar Client ID y Client Secret**

### D. Generar URL de Invitación
1. Ir a "OAuth2" → "URL Generator"
2. Scopes: `bot` + `applications.commands`
3. Permissions: `Administrator` (o permisos específicos)
4. **Copiar URL generada**

## 🗄️ Paso 2: Despliegue en Render.com

### A. Preparar Repositorio
1. Subir código a GitHub
2. Asegurar que estos archivos estén en la raíz:
   - `render.yaml`
   - `requirements.txt`
   - `bot.py`
   - `Dockerfile`

### B. Crear Servicios en Render
1. Ir a https://dashboard.render.com
2. Click "New" → "Blueprint"
3. Conectar repositorio de GitHub
4. Render creará automáticamente:
   - PostgreSQL Database
   - Web Service (Bot)

### C. Configurar Variables de Entorno
En tu Web Service → Environment:

```env
DISCORD_TOKEN=tu_bot_token_de_discord
DISCORD_CLIENT_ID=tu_client_id_de_discord
DISCORD_CLIENT_SECRET=tu_client_secret_de_discord
JWT_SECRET=tu_secreto_jwt_super_largo_y_seguro
DATABASE_URL=postgresql://... (se autocompleta)
WEB_HOST=0.0.0.0
WEB_PORT=10000
LOG_LEVEL=INFO
```

### D. Verificar Despliegue
1. Esperar que el servicio se despliegue
2. Verificar logs: debe mostrar "Bot is ready"
3. Probar API: `https://tu-app.onrender.com/api/ping`
4. **Copiar URL de tu app** (la necesitarás para el dashboard)

## 🌐 Paso 3: Configurar Dashboard Web

### A. Actualizar URLs en JavaScript

**Archivo: `dashboard-web/js/api.js` (línea 14)**
```javascript
this.baseURL = 'https://TU-APP.onrender.com/api'; // ← Cambiar aquí
```

**Archivo: `dashboard-web/js/auth.js` (línea 16)**
```javascript
this.redirectUri = 'https://davito.es/dabot/auth'; // ← Ya está correcto
```

### B. Estructura de Archivos para FTP
```
dashboard-web/
├── index.html
├── dashboard.html
├── tickets.html
├── css/
│   ├── style.css
│   └── dashboard.css
├── js/
│   ├── auth.js
│   ├── api.js
│   ├── dashboard.js
│   ├── tickets.js
│   └── utils.js
└── assets/
    └── images/
        └── logo.png
```

## 📁 Paso 4: Subir Dashboard a Hostalia

### A. Conectar por FTP
- **Host**: ftp.hostalia.com (o el que te proporcionen)
- **Usuario**: tu_usuario_hostalia
- **Contraseña**: tu_contraseña_hostalia
- **Puerto**: 21

### B. Navegación FTP
1. Conectar al FTP
2. Ir a `/public_html/`
3. Crear carpeta `dabot` si no existe
4. Entrar en `/public_html/dabot/`

### C. Subir Archivos
1. Subir todos los archivos de `dashboard-web/`
2. Mantener estructura de carpetas:
   ```
   /public_html/dabot/
   ├── index.html
   ├── dashboard.html
   ├── tickets.html
   ├── css/
   ├── js/
   └── assets/
   ```

### D. Verificar Subida
- Acceder a: https://davito.es/dabot
- Debe cargar la página principal

## ✅ Paso 5: Verificación Final

### A. Test del Bot
1. Usar URL de invitación para añadir bot a servidor
2. Probar comandos básicos: `/ping`, `/help`
3. Verificar que responde correctamente

### B. Test de la API
```bash
# Probar endpoints básicos
curl https://tu-app.onrender.com/api/ping
curl https://tu-app.onrender.com/api/bot/stats
```

### C. Test del Dashboard
1. Ir a https://davito.es/dabot
2. Click "Iniciar Sesión"
3. Autorizar con Discord
4. Debe redirigir al dashboard
5. Seleccionar servidor y verificar datos

### D. Test de Tickets
1. En Discord: crear ticket con `/ticket create test`
2. En dashboard: ir a sección Tickets
3. Verificar que aparece el ticket
4. Probar responder desde dashboard

## 🔧 Configuración Adicional

### A. Comandos del Bot
Los comandos se registran automáticamente. Principales:

**Moderación:**
- `/warn <usuario> <razón>`
- `/ban <usuario> <razón>`
- `/kick <usuario> <razón>`

**Tickets:**
- `/ticket create <asunto>`
- `/ticket close`

**Economía:**
- `/balance`
- `/work`
- `/daily`

**Música:**
- `/play <canción>`
- `/queue`
- `/skip`

### B. Configuración por Servidor
Cada servidor puede configurar:
- Canal de logs
- Roles de moderador
- Sistema de economía
- Canal para VoiceMaster
- Categoría de tickets

## 🆘 Solución de Problemas

### Bot No Responde
1. Verificar logs en Render Dashboard
2. Comprobar variables de entorno
3. Verificar permisos del bot en servidor
4. Reiniciar servicio si es necesario

### Dashboard No Carga
1. Verificar archivos en FTP
2. Comprobar URL de API en `api.js`
3. Verificar CORS en el bot
4. Limpiar caché del navegador

### Error de Autenticación
1. Verificar Redirect URI en Discord
2. Comprobar Client ID/Secret
3. Verificar JWT_SECRET
4. Probar en modo incógnito

### Tickets No Aparecen
1. Verificar conexión bot-dashboard
2. Comprobar permisos de canales
3. Revisar logs de errores
4. Verificar configuración de tickets

## 📊 Monitoreo

### A. Render.com
- Ver logs en tiempo real
- Monitorear uso de recursos
- Verificar uptime

### B. Dashboard Web
- Estadísticas del bot
- Número de servidores
- Comandos ejecutados
- Tickets activos

### C. Base de Datos
- PostgreSQL gestionado por Render
- Backups automáticos
- Monitoreo de conexiones

## 🔄 Mantenimiento

### Actualizar Bot
1. Hacer cambios en código
2. Push a GitHub
3. Render redespliega automáticamente

### Actualizar Dashboard
1. Modificar archivos localmente
2. Re-subir por FTP
3. Limpiar caché si es necesario

### Monitoreo Regular
- Verificar logs diariamente
- Comprobar estadísticas
- Revisar tickets pendientes
- Actualizar dependencias periódicamente

---

## 📞 URLs Importantes

- **Bot Dashboard**: https://dashboard.render.com
- **Dashboard Web**: https://davito.es/dabot
- **Discord Developer**: https://discord.com/developers/applications
- **API Bot**: https://tu-app.onrender.com/api

## 🎯 Estado Final

Cuando todo esté configurado correctamente:

✅ Bot online en Discord
✅ API funcionando en Render
✅ Dashboard accesible en davito.es/dabot
✅ Autenticación Discord funcionando
✅ Tickets sincronizados
✅ Estadísticas en tiempo real

**¡Da Bot v2 estará completamente operativo!** 🎮
