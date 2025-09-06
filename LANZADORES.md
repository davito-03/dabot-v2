# 🚀 Lanzadores de DaBot v2

## 📁 Lanzadores Disponibles

### 1. `LANZAR_CON_DASHBOARD.bat` ⭐ **PRINCIPAL**
**¿Cuándo usar?** Para uso normal del bot con dashboard web

**Características:**
- ✅ Lanzador principal recomendado
- ✅ Verifica automáticamente Python
- ✅ Instala dependencias si es necesario
- ✅ Inicia bot + servidor web + dashboard
- ✅ Interfaz limpia y informativa
- ✅ Manejo de errores mejorado

**Dashboard incluido:**
- 📊 http://localhost:8080/dashboard-web/tickets-dashboard.html
- 🔧 http://localhost:8080/api/status

---

### 2. `INICIAR_BOT.bat` 
**¿Cuándo usar?** Para primera configuración o diagnóstico

**Características:**
- ✅ ASCII art del bot
- ✅ Verificaciones detalladas paso a paso
- ✅ Crea archivo .env automáticamente
- ✅ Abre notepad para configurar token
- ✅ Ideal para usuarios nuevos
- ✅ Información detallada de estado

**Incluye:**
- 🔧 Configuración automática de .env
- 📋 Verificación de archivos necesarios
- 📁 Creación de carpetas (data, logs)
- 🎨 Interfaz visual atractiva

---

### 3. `INSTALAR_DEPENDENCIAS.bat`
**¿Cuándo usar?** Solo para instalar dependencias

**Características:**
- ✅ Instalación paso a paso de cada paquete
- ✅ Diagnóstico de errores específicos
- ✅ Progreso visual con numeración
- ✅ Útil para solucionar problemas de instalación
- ✅ No inicia el bot, solo instala

**Paquetes instalados:**
- nextcord 2.6.0
- yt-dlp (YouTube)
- PyNaCl (Audio Discord)
- ffmpeg-python
- python-dotenv
- aiohttp (Servidor web)
- PyJWT (Autenticación)
- cryptography

---

## 🗑️ Lanzadores Eliminados

Los siguientes lanzadores fueron eliminados por ser redundantes:

- ❌ `START_BOT_SIMPLE.bat` - Duplicado de INICIAR_BOT.bat
- ❌ `LAUNCH_BOT.bat` - Funcionalidad similar al principal
- ❌ `start_local.bat` - Muy básico, sin verificaciones
- ❌ `install.bat` - Menos específico que INSTALAR_DEPENDENCIAS.bat

---

## 📋 Guía de Uso

### Primera vez usando el bot:
1. **Ejecutar**: `INICIAR_BOT.bat`
2. **Configurar**: Token en el archivo .env
3. **Usar**: `LANZAR_CON_DASHBOARD.bat` para uso diario

### Si hay problemas de dependencias:
1. **Ejecutar**: `INSTALAR_DEPENDENCIAS.bat`
2. **Verificar**: Los errores específicos
3. **Intentar**: `LANZAR_CON_DASHBOARD.bat` de nuevo

### Para uso normal:
1. **Ejecutar**: `LANZAR_CON_DASHBOARD.bat`
2. **Acceder**: http://localhost:8080
3. **Disfrutar**: Todas las funcionalidades del bot

---

## 🎯 Recomendaciones

- 🏆 **Para uso diario**: `LANZAR_CON_DASHBOARD.bat`
- 🔧 **Para configuración**: `INICIAR_BOT.bat`
- 🛠️ **Para problemas**: `INSTALAR_DEPENDENCIAS.bat`

---

## ✅ Estado Actual

**Lanzadores activos:** 3
**Lanzadores eliminados:** 4
**Estado:** ✅ Optimizado y funcional

¡Todos los lanzadores están listos para usar! 🚀
