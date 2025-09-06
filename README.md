# 🤖 DaBot v2 - Bot Multipropósito Definitivo

¡El bot de Discord más completo y avanzado! DaBot v2 incluye todas las funcionalidades de MEE6, La Cabra 2.0, VoiceMaster, ProBot, Dyno y Disboard, ¡y mucho más!

## 🌟 **Características Principales**

### 🎵 **Sistema de Música Avanzado**
- Reproducción desde YouTube con yt-dlp
- Cola de reproducción inteligente
- Control de volumen y salto de canciones
- Comandos: `/play`, `/skip`, `/stop`, `/queue`, `/volume`, `/disconnect`

### 🎫 **Sistema de Tickets Avanzado**
- **5 Categorías**: Soporte, Reporte, Sugerencia, Apelación, Otro
- **3 Niveles de Prioridad**: Baja, Media, Alta
- Panel interactivo con botones
- Asignación de staff automática
- Transcripciones de conversaciones
- Dashboard web para gestión

### 📊 **Sistema de Niveles y XP**
- XP por mensajes con cooldown inteligente
- Roles automáticos por nivel
- Tarjetas de nivel personalizadas
- Ranking del servidor
- Multiplicadores por roles
- Comandos: `/nivel`, `/ranking`, `/configurar-niveles`

### 🛡️ **AutoMod Inteligente**
- **Anti-Spam**: Detección de mensajes duplicados
- **Anti-Links**: Bloqueo de enlaces no autorizados
- **Anti-Invites**: Bloqueo de invitaciones de Discord
- **Anti-Caps**: Control de mayúsculas excesivas
- **Anti-Mentions**: Límite de menciones por mensaje
- Configuración por servidor
- Logs automáticos

### ⚠️ **Sistema de Moderación**
- Comando `/avisar` (en español) para warnings
- `/avisos` para ver historial de usuario
- `/quitar-aviso` para remover avisos específicos
- `/limpiar-avisos` para limpiar historial
- Ban, kick, timeout con confirmación
- Limpieza de mensajes avanzada

### 👋 **Sistema de Bienvenidas y Despedidas**
- Tarjetas de bienvenida personalizadas
- Mensajes configurables
- AutoRole para nuevos miembros
- DM de bienvenida opcional
- Comandos: `/configurar-bienvenida`, `/canal-bienvenida`, `/autorole`

### 🎮 **Interacciones y Diversión**
- **Animales**: `/gato`, `/perro`, `/zorro`, `/pato`
- **Interacciones**: `/abrazar`, `/besar`, `/abofetear`, `/acariciar`, `/acurrucar`, `/tocar`, `/morder`, `/bonk`
- Menú interactivo con `/interact`
- GIFs animados de waifu.pics
- Textos aleatorios personalizados

### 🎤 **VoiceMaster Pro**
- Canales de voz dinámicos
- Control total del propietario
- Límites de usuarios personalizables
- Configuración avanzada

### 💰 **Sistema de Economía**
- Monedas y banco
- Trabajos diarios
- Tienda de roles
- Apuestas y minijuegos
- Transferencias entre usuarios

### 📈 **Dashboard Web Completo**
- **Panel Principal**: http://localhost:8080/dashboard-web/tickets-dashboard.html
- **Gestión Avanzada**: http://localhost:8080/dashboard-web/management.html
- Estadísticas en tiempo real
- Gestión de tickets desde web
- Configuración de canales y roles
- Filtros y búsqueda avanzada

### 📡 **API REST Completa**
- Endpoints para todas las funcionalidades
- Autenticación JWT
- CORS configurado
- Documentación automática
- Base: http://localhost:8080/api/

## 🚀 **Instalación y Uso**

### 1. **Instalación Automática**
```bash
# Ejecutar el instalador
INSTALAR_DEPENDENCIAS.bat
```

### 2. **Configuración**
```bash
# Configurar el bot
INICIAR_BOT.bat
```

### 3. **Ejecución con Dashboard**
```bash
# Iniciar bot + dashboard web
LANZAR_CON_DASHBOARD.bat
```

## 📋 **Comandos Completos**

### 🎵 **Música**
- `/play <canción>` - Reproducir música de YouTube
- `/skip` - Saltar canción actual
- `/stop` - Parar reproducción
- `/queue` - Ver cola de reproducción
- `/volume <nivel>` - Ajustar volumen (1-100)
- `/disconnect` - Desconectar del canal de voz

### 🎫 **Tickets**
- Panel automático en canal configurado
- 5 categorías con prioridades
- Gestión desde dashboard web

### 📊 **Niveles**
- `/nivel [usuario]` - Ver nivel y progreso
- `/ranking [página]` - Ranking del servidor
- `/configurar-niveles` - Configurar sistema

### ⚠️ **Moderación**
- `/avisar <usuario> <razón>` - Dar aviso
- `/avisos <usuario>` - Ver avisos del usuario
- `/quitar-aviso <usuario> <id>` - Quitar aviso específico
- `/limpiar-avisos <usuario>` - Limpiar todos los avisos
- `/ban <usuario> [razón]` - Banear usuario
- `/kick <usuario> [razón]` - Expulsar usuario
- `/timeout <usuario> <tiempo> [razón]` - Timeout temporal
- `/clear <cantidad>` - Limpiar mensajes

### 🛡️ **AutoMod**
- `/automod` - Panel de configuración
- Activar/desactivar módulos específicos
- Configurar límites y excepciones

### 👋 **Bienvenidas**
- `/configurar-bienvenida` - Panel de configuración
- `/canal-bienvenida <canal>` - Establecer canal
- `/canal-despedida <canal>` - Canal de despedidas
- `/autorole <rol>` - Rol automático

### 🎮 **Diversión**
- `/gato` - Imagen aleatoria de gato
- `/perro` - Imagen aleatoria de perro
- `/zorro` - Imagen aleatoria de zorro
- `/pato` - Imagen aleatoria de pato
- `/abrazar <usuario>` - Abrazar a alguien
- `/besar <usuario>` - Besar a alguien
- `/abofetear <usuario>` - Abofetear a alguien
- `/acariciar <usuario>` - Acariciar a alguien
- `/interact <usuario>` - Menú de interacciones

### 🎤 **VoiceMaster**
- `/vmpanel` - Panel de configuración
- Creación automática de canales
- Control del propietario

### 💰 **Economía**
- `/balance [usuario]` - Ver dinero
- `/work` - Trabajar (cada 4 horas)
- `/daily` - Bonificación diaria
- `/shop` - Tienda de roles
- `/transfer <usuario> <cantidad>` - Transferir dinero

## 🔧 **Configuración Avanzada**

### Variables de Entorno (.env)
```env
DISCORD_TOKEN=tu_token_aqui
GUILD_ID=id_del_servidor
API_SECRET_KEY=clave_secreta_api
```

### Permisos Necesarios
- Administrar servidor
- Gestionar roles
- Gestionar canales
- Enviar mensajes
- Gestionar mensajes
- Conectar a voz
- Hablar en voz
- Usar comandos de aplicación

## 🌐 **Dashboard Web**

### URLs Principales
- **Dashboard Principal**: http://localhost:8080/dashboard-web/tickets-dashboard.html
- **Gestión Completa**: http://localhost:8080/dashboard-web/management.html
- **API Status**: http://localhost:8080/api/status

### Funcionalidades Web
- ✅ Gestión de tickets en tiempo real
- ✅ Estadísticas avanzadas
- ✅ Configuración de canales
- ✅ Gestión de warnings
- ✅ Filtros y búsqueda
- ✅ Responsive design
- ✅ Actualizaciones automáticas

## 📦 **Dependencias**

### Principales
- `nextcord` - Biblioteca de Discord
- `yt-dlp` - Descarga de YouTube
- `PyNaCl` - Audio de voz
- `ffmpeg-python` - Procesamiento de audio
- `aiohttp` - Servidor web
- `Pillow` - Procesamiento de imágenes
- `PyJWT` - Autenticación
- `cryptography` - Seguridad

### Instalación Manual
```bash
pip install nextcord yt-dlp PyNaCl ffmpeg-python aiohttp Pillow PyJWT cryptography python-dotenv
```

## 🆚 **Comparación con Otros Bots**

| Funcionalidad | DaBot v2 | MEE6 | Dyno | ProBot | La Cabra |
|---------------|----------|------|------|--------|----------|
| **Música** | ✅ Gratis | 💰 Premium | ✅ Limitada | ❌ No | ✅ Básica |
| **Tickets** | ✅ 5 Categorías | 💰 Premium | ✅ Básico | ✅ Básico | ❌ No |
| **Niveles** | ✅ Tarjetas Custom | ✅ Básico | ✅ Básico | ✅ Básico | ✅ Avanzado |
| **AutoMod** | ✅ Completo | ✅ Básico | ✅ Avanzado | ✅ Básico | ✅ Básico |
| **Dashboard** | ✅ Completo | 💰 Premium | ✅ Limitado | ✅ Básico | ❌ No |
| **Interacciones** | ✅ 20+ Comandos | ❌ No | ❌ No | ❌ No | ✅ Básicas |
| **VoiceMaster** | ✅ Incluido | ❌ No | ❌ No | ❌ No | ❌ No |
| **API** | ✅ REST Completa | 💰 Premium | ❌ No | ❌ No | ❌ No |
| **Costo** | ✅ **GRATIS** | 💰 $5/mes | 💰 $3/mes | 💰 $2/mes | ✅ Gratis |

## 🎯 **Ventajas Únicas**

### 🔥 **Todo en Uno**
- Reemplaza 6+ bots populares
- Funcionalidades premium gratis
- Dashboard web incluido
- API REST completa

### 🚀 **Rendimiento**
- Un solo bot vs múltiples
- Menos latencia
- Mayor estabilidad
- Configuración unificada

### 💡 **Innovación**
- Sistema de tickets más avanzado
- Interacciones únicas
- Dashboard responsive
- Comandos en español

### 🛠️ **Personalización**
- Código abierto
- Modificable
- Hosting propio
- Sin límites

## 📞 **Soporte y Desarrollo**

### 🔧 **Desarrollado por davito**
- Bot profesional
- Actualizaciones constantes
- Soporte técnico
- Funcionalidades a medida

### 📋 **Versiones**
- **v2.0**: Versión actual completa
- **v1.0**: Versión básica anterior
- **v2.1**: Próximas mejoras

### 🐛 **Reportar Bugs**
- GitHub Issues
- Discord directo
- Logs automáticos
- Corrección rápida

## 🎉 **¡Comienza Ahora!**

1. **Descarga** el bot
2. **Ejecuta** `INSTALAR_DEPENDENCIAS.bat`
3. **Configura** con `INICIAR_BOT.bat`
4. **Lanza** con `LANZAR_CON_DASHBOARD.bat`
5. **Disfruta** de todas las funcionalidades

---

### 🌟 **DaBot v2 - El único bot que necesitas** 🌟

*Reemplaza MEE6, Dyno, ProBot, VoiceMaster y más con una sola solución completa y gratuita.*
