# 🤖 DaBot v2 - Guía de Uso Local

## 🚀 **INICIO RÁPIDO**

### 1. **Ejecutar el Bot**
```bash
# Opción 1: Launcher automático (RECOMENDADO)
.\LAUNCH_BOT.bat

# Opción 2: Manual
python bot.py
```

### 2. **Acceder al Dashboard**
- **Dashboard Local:** Abre `local_dashboard.html` en tu navegador
- **API Direct:** `http://localhost:8080/api`
- **Dashboard Web:** `http://localhost:8080` (si configurado)

## ⚙️ **CONFIGURACIÓN INICIAL EN DISCORD**

### 🔧 **Configurar Canales**
```
/config_canales
```
- **📝 Logs:** moderación, mensajes, voz, entradas/salidas, roles, canales
- **🔔 Notificaciones:** nivel, warnings, bienvenida, despedida, anuncios
- **⚙️ Características:** tickets, sugerencias, reportes, música, comandos

### 📈 **Sistema de Niveles**
```
/level_config          # Configurar sistema de niveles
/level @usuario        # Ver nivel de un usuario
/leaderboard          # Ver ranking del servidor
```

### 📋 **Ver Configuración**
```
/ver_configuracion    # Ver todos los canales configurados
```

## 🎯 **COMANDOS ESPECÍFICOS POR CANAL**

### 📝 **Logs Específicos**
```
/canal_logs tipo:Moderación canal:#mod-logs
/canal_logs tipo:Mensajes canal:#message-logs
/canal_logs tipo:Voz canal:#voice-logs
```

### 🔔 **Notificaciones Específicas**
```
/canal_notificaciones tipo:"Subida de Nivel" canal:#level-ups
/canal_notificaciones tipo:Warnings canal:#warnings
/canal_notificaciones tipo:Bienvenida canal:#welcome
```

## 🛠️ **FUNCIONALIDADES COMPLETAS**

### 🛡️ **Moderación**
- `/ban @usuario razón` - Banear usuario
- `/kick @usuario razón` - Expulsar usuario
- `/warn @usuario razón` - Dar warning
- `/clear cantidad` - Limpiar mensajes
- `/anti_spam configurar` - Configurar anti-spam

### 🎮 **Entretenimiento**
- `/chiste` - Chiste aleatorio
- `/8ball pregunta` - Bola mágica 8
- `/coinflip` - Lanzar moneda
- `/dice caras` - Lanzar dados

### 🎵 **Música**
- `/play url/nombre` - Reproducir música
- `/pause` - Pausar música
- `/resume` - Reanudar música
- `/skip` - Saltar canción
- `/queue` - Ver cola
- `/stop` - Detener música

### 💰 **Economía**
- `/balance` - Ver dinero
- `/daily` - Reclamar diario
- `/blackjack cantidad` - Jugar blackjack
- `/slots cantidad` - Máquinas tragaperras
- `/roulette cantidad color` - Ruleta

### 🎫 **Tickets**
- `/ticket_setup` - Configurar sistema de tickets
- `/ticket_close` - Cerrar ticket

### 🔊 **VoiceMaster**
- `/voicemaster_setup` - Configurar VoiceMaster
- Botones automáticos en canales de voz

## 📊 **DASHBOARD WEB LOCAL**

### 🌐 **Acceso**
1. **Abrir:** `local_dashboard.html`
2. **Login:** Automático (modo local)
3. **Navegación:** Enlaces directos a cada sección

### 📋 **Secciones Disponibles**
- **Dashboard Principal:** Estadísticas generales
- **Gestión de Tickets:** Ver y gestionar tickets
- **API Status:** Estado de la API del bot

## 💾 **ARCHIVOS Y DATOS**

### 📁 **Estructura de Datos**
```
data/
├── warnings.json           # Warnings de usuarios
├── anti_spam_config.json  # Configuración anti-spam
├── economy.json           # Datos de economía
├── levels.json           # Datos de niveles
├── tickets.json          # Datos de tickets
├── voicemaster.json      # Configuración VoiceMaster
├── channel_config.json   # Configuración de canales
└── log_config.json       # Configuración de logs
```

### 📝 **Logs del Sistema**
```
logs/
└── bot.log              # Logs del bot
```

## 🔧 **TROUBLESHOOTING**

### ❌ **Bot no inicia**
1. Verificar que `DISCORD_TOKEN` está en `.env`
2. Ejecutar `pip install -r requirements.txt`
3. Revisar `logs/bot.log` para errores

### 🌐 **Dashboard no carga**
1. Verificar que el bot está corriendo
2. Ir a `http://localhost:8080`
3. Abrir `local_dashboard.html` directamente

### ⚙️ **Comandos no responden**
1. Verificar permisos del bot en Discord
2. Usar `/config_canales` para configurar canales
3. Verificar que el bot tiene permisos en el canal

### 📝 **Logs no aparecen**
1. Configurar canales con `/config_canales`
2. Verificar permisos del bot para escribir en canales
3. Usar `/ver_configuracion` para verificar

## 🎯 **MEJORES PRÁCTICAS**

### 🔒 **Permisos**
- **Bot:** Administrador (para todas las funciones)
- **Usuarios:** Configurar roles apropiados
- **Canales:** Permisos específicos por tipo de log

### 📢 **Canales Recomendados**
```
#mod-logs        → Logs de moderación
#message-logs    → Logs de mensajes
#voice-logs      → Logs de voz
#member-logs     → Entradas/salidas
#level-ups       → Subidas de nivel
#warnings        → Avisos de warnings
#welcome         → Bienvenidas
#tickets         → Crear tickets
#bot-commands    → Comandos exclusivos
```

### 📈 **Sistema de Niveles**
- **XP por mensaje:** 15-25 (aleatorio)
- **Cooldown:** 60 segundos
- **Cálculo:** nivel = √(xp / 100)
- **Roles automáticos:** Configurables

### 🎫 **Tickets**
- **Configurar primero** con `/ticket_setup`
- **Permisos:** Staff para gestionar
- **Categorías:** Crear categoría específica

## 📞 **SOPORTE**

### 🐛 **Reportar Bugs**
1. Revisar `logs/bot.log`
2. Documentar pasos para reproducir
3. Incluir configuración utilizada

### 💡 **Sugerencias**
- Modificar archivos en `modules/`
- Agregar nuevos comandos
- Personalizar embeds y mensajes

### 🔄 **Actualizaciones**
- Descargar nueva versión
- Conservar carpetas `data/` y `logs/`
- Ejecutar `pip install -r requirements.txt`

---

## 🎉 **¡Tu bot está listo para usar!**

Ejecuta `LAUNCH_BOT.bat` y configura los canales con `/config_canales` en Discord.
