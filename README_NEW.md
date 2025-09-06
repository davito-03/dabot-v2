# 🤖 DaBot v2 - Bot de Discord Multipropósito

Un bot completo para Discord con sistema de tickets avanzado, música, moderación, economía y mucho más.

## 🚀 Inicio Rápido

### Lanzadores Disponibles

1. **`LANZAR_CON_DASHBOARD.bat`** ⭐ **RECOMENDADO**
   - Lanzador principal con dashboard integrado
   - Verifica Python e instala dependencias automáticamente
   - Inicia el bot con servidor web en http://localhost:8080
   - Incluye dashboard para gestión de tickets y warnings

2. **`INICIAR_BOT.bat`** 
   - Lanzador completo con verificaciones detalladas
   - Incluye ASCII art y configuración paso a paso
   - Ideal para primera configuración
   - Crea archivo .env automáticamente

3. **`INSTALAR_DEPENDENCIAS.bat`**
   - Solo instala las dependencias necesarias
   - Útil si tienes problemas de instalación
   - Instala paquetes uno por uno para mejor diagnóstico

### Configuración Inicial

1. **Clona o descarga** este repositorio
2. **Obtén un token de Discord**:
   - Ve a https://discord.com/developers/applications
   - Crea una nueva aplicación
   - Ve a "Bot" y copia el token
3. **Ejecuta** `LANZAR_CON_DASHBOARD.bat`
4. **Configura el token** en el archivo `.env` que se crea automáticamente

## 📋 Funcionalidades

### 🎵 Sistema de Música
- Reproduce música de YouTube
- Cola de reproducción avanzada
- Control de volumen
- Comandos: `/play`, `/skip`, `/stop`, `/queue`, `/volume`, `/disconnect`

### 🎫 Sistema de Tickets Avanzado
- **5 categorías**: soporte, reporte, sugerencia, apelación, otro
- **3 niveles de prioridad**: baja, media, alta
- Panel interactivo con botones
- Asignación de staff
- Transcripciones automáticas
- Configuración con `/ticket_setup`

### 📊 Dashboard Web
- **Panel principal**: http://localhost:8080/dashboard-web/tickets-dashboard.html
- Gestión de tickets en tiempo real
- Estadísticas visuales
- Filtros y búsqueda avanzada
- Gestión de warnings

### ⚡ Moderación
- `/ban`, `/kick`, `/warn`, `/clear`
- Sistema de warnings persistente
- Anti-spam automático
- Logs de moderación

### 💰 Economía
- Sistema de monedas virtuales
- Casino con minijuegos
- Recompensas diarias
- Tienda virtual
- Transferencias entre usuarios

### 🎮 Entretenimiento
- Juegos de dados
- 8-ball mágico
- Preguntas y respuestas
- Sistema de niveles y XP

### 🔊 VoiceMaster
- Canales de voz dinámicos
- Control de usuarios
- Configuración personalizada

## 🔧 Comandos Principales

### Música
```
/play [canción]     - Reproducir música de YouTube
/skip               - Saltar canción actual
/stop               - Parar reproducción
/queue              - Ver cola de reproducción
/volume [1-100]     - Cambiar volumen
/disconnect         - Desconectar del canal
```

### Tickets
```
/ticket_setup       - Configurar sistema de tickets
[Panel interactivo] - Crear tickets por categoría
```

### Moderación
```
/ban [usuario] [razón]      - Banear usuario
/kick [usuario] [razón]     - Expulsar usuario
/warn [usuario] [razón]     - Advertir usuario
/clear [cantidad]           - Limpiar mensajes
/warnings [usuario]         - Ver advertencias
```

### Economía
```
/balance            - Ver dinero
/daily              - Recompensa diaria
/casino             - Juegos de casino
/shop               - Tienda virtual
/transfer           - Transferir dinero
```

## 🌐 Dashboard Web

### Acceso
- **Principal**: http://localhost:8080/dashboard-web/tickets-dashboard.html
- **API**: http://localhost:8080/api/status
- **Gestión**: http://localhost:8080/dashboard-web/management.html

### Características
- ✅ Gestión de tickets en tiempo real
- ✅ Estadísticas por categoría y prioridad
- ✅ Filtros y búsqueda avanzada
- ✅ Gestión de warnings con detalles
- ✅ Configuración de canales y roles
- ✅ Interfaz responsive y moderna

## 📁 Estructura del Proyecto

```
dabot v2/
├── bot.py                          # Bot principal
├── requirements.txt                # Dependencias
├── LANZAR_CON_DASHBOARD.bat       # Lanzador principal ⭐
├── INICIAR_BOT.bat                # Lanzador con configuración
├── INSTALAR_DEPENDENCIAS.bat      # Instalador de dependencias
├── modules/
│   ├── music.py                   # Sistema de música
│   ├── advanced_tickets.py       # Tickets avanzados
│   ├── web_api.py                # API REST
│   ├── moderation.py             # Moderación
│   ├── economy.py                # Economía
│   ├── entertainment.py          # Entretenimiento
│   └── voicemaster.py           # VoiceMaster
├── dashboard-web/
│   ├── tickets-dashboard.html    # Dashboard principal
│   └── management.html           # Dashboard de gestión
└── data/                         # Datos del bot
```

## 🔗 API REST

### Endpoints Disponibles

#### Tickets
- `GET /api/guilds/{guild_id}/tickets` - Listar tickets
- `GET /api/guilds/{guild_id}/tickets/stats` - Estadísticas
- `POST /api/tickets/{ticket_id}/close` - Cerrar ticket
- `POST /api/tickets/{ticket_id}/assign` - Asignar staff

#### Warnings
- `GET /api/guilds/{guild_id}/warnings` - Listar warnings
- `POST /api/warnings/{guild_id}/{user_id}/add` - Agregar warning
- `DELETE /api/warnings/{guild_id}/{user_id}/{warning_id}` - Remover warning

#### General
- `GET /api/status` - Estado del bot
- `GET /api/guilds` - Servidores del usuario

## 🛠️ Requisitos del Sistema

- **Python 3.8+**
- **FFmpeg** (para música)
- **Conexión a Internet**
- **Token de Discord Bot**

### Dependencias Principales
- `nextcord` - Librería de Discord
- `yt-dlp` - Descarga de YouTube
- `PyNaCl` - Audio de Discord
- `aiohttp` - Servidor web
- `PyJWT` - Autenticación

## 🎯 Configuración Avanzada

### Variables de Entorno (.env)
```env
DISCORD_TOKEN=tu_token_aqui
WEB_PORT=8080
WEB_HOST=localhost
JWT_SECRET=tu_secreto_jwt
```

### Configuración de Tickets
1. Ejecuta `/ticket_setup` en tu servidor
2. Selecciona el canal donde aparecerá el panel
3. Configura la categoría para los tickets
4. Asigna el rol de staff

## 🐛 Solución de Problemas

### El bot no se conecta
- Verifica que el token en `.env` sea correcto
- Asegúrate de que el bot tenga permisos en tu servidor

### La música no funciona
- Instala FFmpeg en tu sistema
- Verifica que el bot esté en un canal de voz

### El dashboard no carga
- Verifica que el puerto 8080 esté libre
- Accede a http://localhost:8080/api/status para probar la API

## 🎉 Estado del Proyecto

✅ **COMPLETAMENTE FUNCIONAL**
- ✅ Bot conectándose correctamente
- ✅ Todos los sistemas operativos
- ✅ Dashboard web accesible
- ✅ API REST funcionando
- ✅ Música con YouTube integration
- ✅ Sistema de tickets multi-categoría
- ✅ Moderación y economía completas

## 📞 Soporte

Si tienes problemas:
1. Verifica que Python 3.8+ esté instalado
2. Ejecuta `INSTALAR_DEPENDENCIAS.bat` si hay errores de librerías
3. Revisa el archivo `bot.log` para errores detallados
4. Asegúrate de que el token de Discord sea válido

---

**¡El bot está listo para usar en producción!** 🚀
