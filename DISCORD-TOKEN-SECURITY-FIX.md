# 🚨 DIAGNÓSTICO: Error 4006 en Railway

## 🔍 **Error 4006 significa:**
- **Token inválido o expirado**
- **Permisos insuficientes en Discord**
- **Bot no tiene permisos de voz**
- **Región del servidor problemática**

## ⚠️ **PRIMERA SOLUCIÓN: Regenerar Token**

Tu token está **públicamente visible** en `.env`. Debes:

### 1. **Regenerar Token en Discord**
```
1. Ir a https://discord.com/developers/applications
2. Seleccionar tu aplicación
3. Bot → Reset Token
4. COPIAR el nuevo token
5. Actualizar .env INMEDIATAMENTE
```

### 2. **Verificar Permisos del Bot**
```
Permisos REQUERIDOS en Discord:
✅ Connect (Conectar)
✅ Speak (Hablar)  
✅ Use Voice Activity (Usar actividad de voz)
✅ Send Messages (Enviar mensajes)
✅ Use Slash Commands (Usar comandos slash)
```

### 3. **URL de Invitación Correcta**
```
https://discord.com/api/oauth2/authorize?client_id=TU_CLIENT_ID&permissions=3147776&scope=bot%20applications.commands
```

## 🔧 **SOLUCIÓN TEMPORAL: Deshabilitar Música**

Mientras solucionas el token:

### En Railway Variables:
```env
MUSIC_DISABLED=true
```

## 🎯 **Checklist de Solución**

### ✅ **Paso 1: Token Seguro**
- [ ] Regenerar token en Discord Developer Portal
- [ ] Actualizar .env con nuevo token
- [ ] Actualizar variable en Railway
- [ ] **NUNCA** subir .env a GitHub

### ✅ **Paso 2: Permisos**
- [ ] Verificar permisos de voz en servidor Discord
- [ ] Bot tiene rol con permisos de voz
- [ ] Canal de voz permite al bot conectar

### ✅ **Paso 3: Configuración Railway**
```env
DISCORD_TOKEN=NUEVO_TOKEN_REGENERADO
MUSIC_DISABLED=false
```

## 🚨 **URGENTE: Seguridad**

Tu token actual está **comprometido** porque está visible en el código. DEBES:

1. **Regenerar INMEDIATAMENTE**
2. **Cambiar contraseñas** si es necesario
3. **Nunca** subir archivos .env a GitHub
4. **Usar variables de entorno** en Railway

## 📝 **Después de Regenerar Token**

```bash
# En Railway logs debería aparecer:
✅ Bot conectado exitosamente
✅ Módulo música cargado
🎵 Listo para reproducir música
```

## 🔒 **Seguridad .env**

Agregar a `.gitignore`:
```gitignore
.env
.env.local
.env.production
*.log
__pycache__/
```

**Error 4006 NO es problema de hosting - es problema de autenticación.**
