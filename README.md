# 🤖 DaBot v2 - Bot de Discord Completo y Avanzado

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/nextcord-3.1+-green.svg)](https://github.com/nextcord/nextcord)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Completado-brightgreen.svg)]()

**DaBot v2** es un bot de Discord completamente funcional y avanzado que incluye sistemas de moderación, entretenimiento, música con interfaz como FlaviBot, configuración automática de servidores, y mucho más. Perfecto para cualquier tipo de comunidad de Discord.

---

## 📋 Tabla de Contenidos

- [🚀 Características Principales](#-características-principales)
- [🆕 Nuevos Sistemas Integrados](#-nuevos-sistemas-integrados)
- [⚡ Instalación Rápida](#-instalación-rápida)
- [🎮 Comandos Disponibles](#-comandos-disponibles)
- [� Sistema de Música Avanzado](#-sistema-de-música-avanzado)
- [🛠️ Configuración Automática](#️-configuración-automática)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🔧 Configuración Manual](#-configuración-manual)
- [❓ FAQ y Solución de Problemas](#-faq-y-solución-de-problemas)
- [🤝 Contribuir](#-contribuir)

---

## 🚀 Características Principales

### ✨ **Funcionalidades Core**
- **🎭 Comandos de entretenimiento** - 8ball, bromas, abrazos, besos y más interacciones
- **🛡️ Sistema de moderación completo** - Ban, kick, timeout, warns con logs automáticos
- **🎵 Reproductor de música avanzado** - YouTube con interfaz de selección como FlaviBot
- **⏰ Tareas programadas** - Recordatorios y eventos automáticos
- **🔄 Mensajes persistentes** - Paneles que sobreviven reinicios del bot
- **🚀 Configuración automática completa** - Servidores listos en minutos

### 🛠️ **Sistemas Avanzados**
- **💾 Base de datos SQLite** - Persistencia de configuraciones y datos
- **📊 Sistema de logs automático** - Registro completo de moderación
- **🎫 Sistema de tickets interactivo** - Soporte con paneles y botones
- **🔊 VoiceMaster avanzado** - Canales temporales de voz personalizables
- **👋 Auto-roles y bienvenidas** - Automatización completa de nuevos miembros
- **✅ Panel de verificación** - Control de acceso al servidor con captcha
- **🔞 Comandos NSFW** - Configurables por servidor con restricciones

---

## 🆕 Nuevos Sistemas Integrados

### 📜 **Sistema de Reglas Automáticas**
- **4 plantillas de reglas** según tipo de servidor
- **Generación automática** de reglas personalizadas
- **Integración con moderación** para aplicación automática

### ⭐ **Sistema de Niveles Avanzado**
- **XP por mensajes y tiempo en voz** con multiplicadores
- **Selección de colores de rol** personalizable
- **Recompensas automáticas** por niveles alcanzados
- **Progresión de privilegios** desbloqueando funciones

### 🛡️ **Moderación Integrada**
- **Plantillas de permisos** automáticas por tipo de servidor
- **Roles de staff predefinidos** con permisos optimizados
- **Sistema de warns escalable** con acciones automáticas
- **Anti-spam y anti-raid** integrados

### 💥 **Comandos Destructivos Seguros**
- **Reset completo de servidor** con verificación de propietario
- **Respaldo automático** antes de operaciones destructivas
- **Confirmación múltiple** para prevenir accidentes
- **Restauración de configuraciones** desde respaldos

### 🚀 **Configuración Completa de Servidores**
4 plantillas profesionales de servidor:
1. **🎮 Comunidad de Streamer** - Para streamers y sus comunidades
2. **🎯 Servidor Gaming** - Para comunidades gaming y esports
3. **💻 Servidor de Desarrollo** - Para comunidades de programadores
4. **🌟 Comunidad General** - Para comunidades sociales y temáticas

Cada plantilla incluye:
- **📋 5-6 categorías organizadas** con permisos específicos
- **💬 20-25 canales especializados** optimizados para cada uso
- **👥 8-10 roles con jerarquía** y permisos balanceados
- **🔒 Configuraciones de seguridad** avanzadas
- **🤖 Integración automática** con todos los sistemas del bot

---

## ⚡ Instalación Rápida

### 🔧 **Instalación Automática**
1. **Descarga** el proyecto completo
2. **Ejecuta** `install.bat` (Windows) - ¡Instala TODO automáticamente!
3. **Configura** tu token en `.env`
4. **Ejecuta** `INICIAR.bat` o `python bot.py`

```bash
# O instalación manual
git clone https://github.com/davito-03/dabot-v2.git
cd dabot-v2
pip install -r requirements.txt
```

### 📝 **Configuración del Token**
Crea un archivo `.env` con:
```env
DISCORD_TOKEN=tu_token_aquí
```

### ✅ **Verificación**
Ejecuta `test_bot.py` para verificar que todo funciona correctamente.

---

## 🎮 Comandos Disponibles

### 🎭 **Entretenimiento**
```
/8ball <pregunta>          - Bola mágica 8 con predicciones
/broma [usuario]           - Broma divertida aleatoria
/abrazo <usuario>          - Dar un abrazo cariñoso
/beso <usuario>            - Dar un beso romántico
/palmadita <usuario>       - Dar palmaditas en la cabeza
/nsfw-menu                 - Panel NSFW (solo canales permitidos)
```

### 🛡️ **Moderación**
```
/ban <usuario> [razón] [tiempo]     - Banear usuario temporal o permanente
/kick <usuario> [razón]             - Expulsar usuario del servidor
/timeout <usuario> <tiempo> [razón] - Silenciar temporalmente
/warn <usuario> <razón>             - Advertir usuario con registro
/clear <cantidad>                   - Limpiar mensajes (máx 100)
/nick <usuario> <nuevo_nick>        - Cambiar nickname de usuario
```

### 🎵 **Música Avanzada**
```
/play <canción>           - Buscar y reproducir música de YouTube
/stop                     - Parar música y limpiar cola
/skip                     - Saltar canción actual
/queue                    - Ver cola de reproducción
/volume <nivel>           - Cambiar volumen (0-100)
/shuffle                  - Mezclar orden de la cola
/loop                     - Activar/desactivar repetición
/nowplaying              - Ver canción actual con controles
```

### ⏰ **Tareas Programadas**
```
/recordatorio <tiempo> <mensaje>           - Crear recordatorio personal
/evento <nombre> <fecha> <descripción>     - Crear evento del servidor
/agenda                                    - Ver eventos programados
```

### 🚀 **Configuración Automática**
```
/setup                    - Configuración básica automática
/servidor-completo        - Configuración completa (4 plantillas)
/reset-servidor          - Reset completo con verificación
/panels verify           - Verificar mensajes persistentes
/test all                - Probar todos los sistemas
```

---

## 🎵 Sistema de Música Avanzado

### 🔍 **Búsqueda Inteligente como FlaviBot**
- **Interfaz de selección** con hasta 5 resultados de YouTube
- **Vista previa** de duración, canal y título
- **Botones interactivos** para seleccionar la canción deseada
- **Búsqueda alternativa** si YouTube bloquea la búsqueda principal

### 🎛️ **Controles Avanzados**
- **Panel de control** con botones para play/pause, skip, stop
- **Control de volumen** visual con botones +/- 
- **Cola de reproducción** con navegación por páginas
- **Modo repetición** (canción, cola, desactivado)
- **Mezcla aleatoria** de la cola de reproducción

### 🔧 **Características Técnicas**
- **FFmpeg integrado** con instalación automática
- **Múltiples fuentes** de YouTube con respaldo
- **Gestión de errores** robusta con intentos alternativos
- **Optimización de calidad** automática según conexión
- **Soporte para listas** de reproducción de YouTube

### 🚫 **Solución a Problemas de YouTube**
- **Triple sistema de respaldo** para evitar bloqueos
- **Detección automática** de restricciones regionales
- **Fuentes alternativas** cuando YouTube no está disponible
- **Búsqueda por requests** como método de emergencia

---

## 🛠️ Configuración Automática

### � **Configuración Básica (`/setup`)**
- Canales básicos (general, logs, bienvenidas)
- Roles fundamentales (moderador, miembro)
- Configuraciones de seguridad estándar
- Integración con sistemas del bot

### 🚀 **Configuración Completa (`/servidor-completo`)**

#### **🎮 Plantilla: Comunidad de Streamer**
```
📋 Categorías: Información, Stream, Comunidad, Gaming, Privado
💬 Canales: 25 canales especializados para streamers
👥 Roles: Streamer, Moderador, Suscriptor, VIP, etc.
🔒 Permisos: Optimizados para streaming y comunidad
```

#### **🎯 Plantilla: Servidor Gaming**
```
📋 Categorías: General, Gaming, Esports, Social, Staff
💬 Canales: 23 canales para gaming y competitivo
👥 Roles: Gaming roles, rangos competitivos, staff
🔒 Permisos: Enfocados en gaming y torneos
```

#### **💻 Plantilla: Servidor de Desarrollo**
```
📋 Categorías: General, Desarrollo, Proyectos, Recursos, Admin
💬 Canales: 22 canales para programadores
👥 Roles: Developer, Contributor, Mentor, etc.
🔒 Permisos: Orientados a colaboración en código
```

#### **🌟 Plantilla: Comunidad General**
```
📋 Categorías: General, Social, Entretenimiento, Ayuda, Staff
💬 Canales: 20 canales para comunidad social
👥 Roles: Roles sociales y de participación
🔒 Permisos: Balanceados para interacción social
```

---

## 📁 Estructura del Proyecto

```
DaBot v2/
├── 🤖 bot.py                          # Archivo principal del bot
├── 📋 requirements.txt                # Dependencias (incluye FFmpeg)
├── 🔧 install.bat                     # Instalador automático completo
├── 🔧 install_ffmpeg.py              # Instalador específico de FFmpeg
├── 🚀 INICIAR.bat                     # Ejecutor del bot
├── 📖 README.md                       # Esta documentación
├── 🧪 test_bot.py                     # Tests de verificación
├── 🧪 test_complete_music.py          # Tests del sistema de música
├── 🗂️ modules/                        # Módulos especializados
│   ├── __init__.py                   # Inicializador de módulos
│   ├── 🎭 entertainment.py           # Comandos de entretenimiento
│   ├── 🛡️ moderation.py              # Sistema de moderación completo
│   ├── 🎵 music.py                   # Reproductor de música avanzado
│   ├── ⏰ scheduled_tasks.py         # Tareas programadas
│   ├── 📜 auto_rules.py              # Sistema de reglas automáticas
│   ├── ⭐ advanced_levels.py         # Sistema de niveles avanzado
│   ├── 🛡️ integrated_moderation.py   # Moderación integrada
│   └── 💥 destructive_commands.py    # Comandos destructivos seguros
└── 🗄️ __pycache__/                   # Archivos compilados
```

### � **Estadísticas del Proyecto**
- **11 módulos especializados** con funcionalidades únicas
- **50+ comandos** distribuidos en diferentes categorías
- **4 plantillas de servidor** completamente configuradas
- **Sistema de música** con interfaz avanzada como FlaviBot
- **Base de datos SQLite** para persistencia
- **Instalación 100% automática** con respaldos incluidos

---

## 🔧 Configuración Manual

### 🗃️ **Base de Datos**
El bot crea automáticamente `bot_database.db` con las siguientes tablas:
- `server_configs` - Configuraciones por servidor
- `user_levels` - Sistema de niveles y XP
- `moderation_logs` - Registros de moderación
- `scheduled_tasks` - Tareas programadas
- `persistent_messages` - Mensajes que sobreviven reinicios

### 🎛️ **Variables de Entorno**
```env
# Requerido
DISCORD_TOKEN=tu_token_de_discord

# Opcional
DEBUG_MODE=true                    # Modo de depuración
LOG_LEVEL=INFO                     # Nivel de logging
DATABASE_PATH=./bot_database.db    # Ruta de la base de datos
FFMPEG_PATH=auto                   # Ruta de FFmpeg (auto-detecta)
```

### 🔐 **Permisos del Bot**
Permisos requeridos para funcionamiento completo:
```
✅ Leer mensajes              ✅ Enviar mensajes
✅ Gestionar mensajes         ✅ Insertar enlaces
✅ Adjuntar archivos          ✅ Leer historial
✅ Mencionar todos            ✅ Usar emojis externos
✅ Añadir reacciones          ✅ Conectar a voz
✅ Hablar en voz              ✅ Gestionar canales
✅ Gestionar roles            ✅ Gestionar nicknames
✅ Expulsar miembros         ✅ Banear miembros
✅ Gestionar servidor         ✅ Ver canal de auditoria
```

---

## ❓ FAQ y Solución de Problemas

### 🔧 **Problemas Comunes**

#### **❌ "ffmpeg was not found"**
```bash
# El instalador lo resuelve automáticamente, pero manualmente:
# Windows:
winget install ffmpeg
# O con Chocolatey:
choco install ffmpeg
# O ejecuta: python install_ffmpeg.py
```

#### **❌ "No se puede conectar a YouTube"**
- El bot tiene **triple sistema de respaldo**
- Si falla la búsqueda principal, usa métodos alternativos
- Verifica tu conexión a internet
- Algunos países pueden tener restricciones

#### **❌ "Bot no responde a comandos"**
```python
# Verifica permisos del bot
# Ejecuta test_bot.py para diagnóstico
python test_bot.py
```

#### **❌ "Error de base de datos"**
```bash
# Elimina y regenera la base de datos
del bot_database.db
# El bot la recreará automáticamente
```

### 🆘 **Comandos de Diagnóstico**
```
/test all              # Prueba todos los sistemas
/panels verify         # Verifica mensajes persistentes
/debug database        # Información de la base de datos
/debug permissions     # Verifica permisos del bot
```

### 📞 **Soporte**
- **Issues**: [GitHub Issues](https://github.com/davito-03/dabot-v2/issues)
- **Documentación**: Archivos .md en el proyecto
- **Tests**: Ejecuta `test_bot.py` para diagnósticos

---

## 🚀 Changelog y Actualizaciones

### 🆕 **v2.0 - Versión Completa (Actual)**
- ✅ **Sistema de música** con interfaz como FlaviBot
- ✅ **4 plantillas de servidor** completas
- ✅ **Sistema de niveles** avanzado con progresión
- ✅ **Comandos destructivos** seguros con verificación
- ✅ **Instalador automático** con FFmpeg incluido
- ✅ **Triple respaldo** para YouTube y música
- ✅ **Moderación integrada** con plantillas automáticas
- ✅ **Sistema de reglas** automático por tipo de servidor
- ✅ **Mensajes persistentes** que sobreviven reinicios
- ✅ **Base de datos completa** con todas las configuraciones

### 📋 **Funcionalidades Verificadas**
- [x] **41 módulos** compilan correctamente
- [x] **Sistema de música** 100% funcional
- [x] **FFmpeg** instalado y configurado
- [x] **YouTube** con sistema de respaldo
- [x] **Base de datos** inicializada
- [x] **Instalador** completamente automático
- [x] **Tests** pasando todas las verificaciones

---

## 🤝 Contribuir

### 🛠️ **Desarrollo**
```bash
# Clona el repositorio
git clone https://github.com/davito-03/dabot-v2.git

# Instala dependencias de desarrollo
pip install -r requirements.txt

# Ejecuta tests
python test_bot.py
```

### 📝 **Contribuciones**
- **Fork** el proyecto
- **Crea** una rama para tu feature
- **Commit** tus cambios
- **Push** a la rama
- **Abre** un Pull Request

### 📄 **Licencia**
Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

---

## 🎉 Reconocimientos

- **nextcord** - Framework de Discord mejorado
- **yt-dlp** - Descarga de YouTube confiable  
- **FFmpeg** - Procesamiento de audio profesional
- **SQLite** - Base de datos ligera y eficiente
- **Comunidad de Discord** - Feedback y testing

---

<div align="center">

### 🤖 **DaBot v2 - Bot de Discord Profesional**

**Desarrollado con ❤️ para la comunidad de Discord**

[![GitHub](https://img.shields.io/badge/GitHub-davito--03-black.svg)](https://github.com/davito-03)
[![Discord](https://img.shields.io/badge/Discord-Bot%20Completo-blue.svg)]()

*¿Te gusta el proyecto? ¡Dale una ⭐ en GitHub!*

</div>
| `/skip` | Saltar canción | `/skip` |
| `/queue` | Ver cola de reproducción | `/queue` |
| `/volume <nivel>` | Cambiar volumen (1-100) | `/volume 50` |
| `/shuffle` | Mezclar cola | `/shuffle` |
| `/loop` | Repetir canción/cola | `/loop` |
| `/nowplaying` | Canción actual | `/nowplaying` |

### ⏰ **Tareas Programadas**
| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/recordatorio <tiempo> <mensaje>` | Crear recordatorio | `/recordatorio 30m Revisar correo` |
| `/evento <nombre> <fecha> <descripción>` | Crear evento | `/evento Torneo 2024-12-25 Competencia` |

### 🚀 **Configuración**
| Comando | Descripción | Uso |
|---------|-------------|-----|
| `/setup` | Configuración básica automática | Para servidores nuevos |
| `/servidor-completo` | **Configuración completa** ⭐ | Plantillas especializadas |
| `/panels verify` | Verificar mensajes persistentes | Mantenimiento |
| `/test all` | Probar todos los sistemas | Diagnóstico |

### 🆕 **Nuevos Sistemas Avanzados**
| Comando | Descripción | Funcionalidad |
|---------|-------------|---------------|
| `/setup-reglas [tipo]` | Configurar reglas automáticas | 4 plantillas de servidor |
| `/nivel [usuario]` | Ver nivel y XP de usuario | Sistema de progresión |
| `/colores` | Seleccionar color de rol por nivel | Personalización visual |
| `/reset-servidor` | **PELIGROSO** - Reset completo | Solo propietarios |
| `/configurar-moderacion [plantilla]` | Setup de roles de staff | Plantillas de permisos |
| `/privilegios` | Ver sistema de desbloqueos | Progresión por niveles |

---

## 🆕 Nuevos Sistemas Integrados

### 📜 **Sistema de Reglas Automáticas**

Configura automáticamente reglas personalizadas según el tipo de servidor:

**🎯 Plantillas Disponibles:**
- **🎮 Comunidad Gaming** - Reglas para servidores de juegos
- **📚 Servidor Educativo** - Normas académicas y de estudio  
- **💼 Comunidad Profesional** - Reglas de networking y trabajo
- **🎭 Entretenimiento General** - Normas para comunidades casuales

**✨ Características:**
- Aplicación automática de reglas por canal
- Sistema de advertencias vía DM
- Integración con moderación automática
- Personalización por servidor

### ⭐ **Sistema de Niveles Avanzado**

Sistema de progresión completo con múltiples fuentes de XP:

**💫 Fuentes de Experiencia:**
- **💬 Mensajes de texto** - 15-25 XP por mensaje (cooldown 60s)
- **🔊 Tiempo en voz** - 10 XP por minuto en canales de voz
- **🎯 Actividades especiales** - Bonificaciones por eventos

**🎨 Sistema de Recompensas:**
- **🌈 Selección de colores** - Colores únicos desbloqueables por nivel
- **⭐ Privilegios progresivos** - Funciones que se desbloquean automáticamente
- **🏆 Roles de nivel** - Jerarquía visual en el servidor
- **💎 Contenido exclusivo** - Acceso a canales especiales

### 🛡️ **Moderación Integrada**

Sistema de moderación con plantillas profesionales:

**👮 Plantillas de Staff:**
- **🔰 Helper** - Soporte básico, warns, timeout corto
- **⚔️ Moderador** - Kick, ban temporal, gestión de canales  
- **👑 Administrador** - Control total, configuración del bot
- **🛡️ Super Admin** - Acceso a comandos destructivos

**🔧 Configuración Automática:**
- Creación automática de roles con permisos
- Asignación de canales de logs
- Integración con sistema de warns
- Notificaciones de staff en tiempo real

### 💥 **Comandos Destructivos**

Sistema de seguridad para operaciones críticas:

**🔒 Medidas de Seguridad:**
- **🔑 Verificación de propietario** - Solo el dueño del servidor
- **⏱️ Timeout por intentos fallidos** - 10 minutos de penalización
- **📢 Notificaciones a staff** - Alertas de intentos no autorizados
- **💾 Respaldo automático** - Backup de configuraciones críticas

**⚠️ Operaciones Disponibles:**
- Reset completo del servidor
- Eliminación de todos los canales y roles
- Restauración a configuración inicial
- Limpieza de base de datos

---

## 🛠️ Sistema de Configuración Completa

### 🌟 **Comando Principal: `/servidor-completo`**

Este comando revolucionario configura automáticamente un servidor completo desde cero con plantillas profesionales.

### 🎯 **4 Plantillas Especializadas**

#### 🎮 **1. Comunidad de Streamer**
Perfecto para streamers y sus audiencias:

**📋 Estructura Creada:**
- **📋 INFORMACIÓN** - Bienvenida, reglas, anuncios, eventos
- **💬 CHAT GENERAL** - General, links-clips, fanart, comandos-bot
- **🎮 GAMING** - Gaming general, buscar team, logros
- **🔊 VOZ** - Lobby, Gaming (x2), Privado, Viendo Stream
- **🛠️ STAFF** - Staff chat, logs, tickets, staff voice

**👥 Roles Incluidos:**
- 👑 Owner, 🛡️ Admin, 🔨 Moderador
- 🎤 VIP, ⭐ Suscriptor
- 🎮 Gamer, 🎨 Artista, 🔇 Silenciado

#### 🎯 **2. Servidor Gaming**
Ideal para comunidades gaming diversas:

**📋 Estructura Creada:**
- **📋 INFORMACIÓN** - Bienvenida, reglas, anuncios, novedades
- **💬 GENERAL** - Chat general, gaming talk, logros, screenshots
- **🎯 BUSCAR EQUIPO** - LFG General, FPS, MOBA, Racing, RPG
- **🔊 VOICE CHANNELS** - Lobby, Gaming (x3), Privados (x2), Competitivo
- **🛠️ MODERACIÓN** - Mod chat, logs, tickets, mod voice

**👥 Roles Incluidos:**
- 👑 Owner, 🛡️ Admin, 🔨 Moderador
- 🎯 Pro Gamer
- 🔫 FPS Player, ⚔️ MOBA Player, 🏎️ Racing Fan, 🏰 RPG Lover
- 🔰 Junior Dev, 🔇 Silenciado

#### 💻 **3. Servidor de Desarrollo**
Para comunidades de programadores:

**📋 Estructura Creada:**
- **📋 INFORMACIÓN** - Bienvenida, reglas, anuncios, recursos
- **💬 GENERAL** - General, random, trabajos, logros
- **💻 DESARROLLO** - Python, web-dev, react-vue, mobile-dev, game-dev, backend, devops
- **❓ AYUDA** - Ayuda general, debug, code review, ideas
- **🔊 VOICE** - General, Coding Sessions (x2), Screen Share, Privado
- **🛠️ STAFF** - Staff chat, logs, tickets, staff voice

**👥 Roles Incluidos:**
- 👑 Owner, 🛡️ Admin, 🔨 Moderador
- ⭐ Senior Dev
- 🐍 Python Dev, 🌐 Web Dev, 📱 Mobile Dev, 🎮 Game Dev
- 🔰 Junior Dev, 🔇 Silenciado

#### 🌟 **4. Comunidad General**
Para comunidades sociales:

**📋 Estructura Creada:**
- **📋 INFORMACIÓN** - Bienvenida, reglas, anuncios, eventos
- **💬 CHAT** - General, charla casual, fotos-media, links, bot zone
- **🎭 ENTRETENIMIENTO** - Gaming, películas-series, música, libros, arte
- **🔊 VOICE** - Lobby, Charla (x2), Gaming, Música, Privado
- **🛠️ STAFF** - Staff only, mod logs, soporte, staff voice

**👥 Roles Incluidos:**
- 👑 Owner, 🛡️ Admin, 🔨 Moderador
- ⭐ VIP
- 🎮 Gamer, 🎨 Artista, 🎵 Músico, 📚 Lector
- 🔇 Silenciado

### 🚀 **Cómo Usar la Configuración Completa**

#### **1. Ejecutar el Comando**
```
/servidor-completo
```

#### **2. Seleccionar Plantilla**
- Aparecerá un menú desplegable
- Elige el tipo que mejor se adapte a tu comunidad
- Lee las descripciones detalladas

#### **3. Confirmar Configuración**
- Revisa el resumen de elementos a crear
- Confirma o cancela según tus necesidades

#### **4. Proceso Automático**
El bot creará automáticamente:
1. ✅ **Todos los roles** con permisos específicos
2. ✅ **Categorías organizadas** por función
3. ✅ **Canales especializados** (texto y voz)
4. ✅ **Configuraciones de seguridad** (staff, silenciado)
5. ✅ **Integración con sistemas del bot** (tickets, logs, etc.)

### ⚙️ **Configuraciones Automáticas Incluidas**

- **🤖 Sistemas del Bot**: Tickets, VoiceMaster, Logs, Bienvenidas
- **🔒 Permisos Especiales**: Canales staff, rol silenciado
- **📊 Base de Datos**: Configuraciones persistentes
- **🎯 Auto-roles**: Según tipo de servidor

---

## 📁 Estructura del Proyecto

```
DaBot v2/
├── 🤖 bot.py                           # Archivo principal del bot
├── 📋 requirements.txt                 # Dependencias Python
├── 🔧 install.bat                      # Instalador automático Windows
├── 📖 README.md                        # Esta documentación
├── 🧪 test_bot.py                      # Tests automatizados
├── 🗂️ modules/                         # Módulos especializados
│   ├── __init__.py                     # Inicializador de módulos
│   ├── 🎭 entertainment.py             # Comandos de entretenimiento
│   ├── 🛡️ moderation.py                # Sistema de moderación
│   ├── 🎵 music.py                     # Reproductor de música
│   ├── ⏰ scheduled_tasks.py           # Tareas programadas
│   └── 🚀 complete_server_setup.py    # Sistema de configuración completa
└── 🗄️ __pycache__/                     # Archivos compilados Python
```

---

## 🔧 Configuración Avanzada

### 🔑 **Configuración del Token**

1. **Crear aplicación de Discord:**
   - Ve a [Discord Developer Portal](https://discord.com/developers/applications)
   - Crea una nueva aplicación
   - Ve a la sección "Bot"
   - Copia el token

2. **Configurar en bot.py:**
   ```python
   # Línea ~30 en bot.py
   bot.run('TU_TOKEN_AQUI')
   ```

### 🎵 **Configuración de Música**

El bot soporta múltiples fuentes de música:
- **YouTube** (por defecto)
- **URLs directas** de audio
- **Archivos locales** (configuración avanzada)

### 🗄️ **Base de Datos**

El bot utiliza SQLite para almacenar:
- **Configuraciones del servidor**
- **Warnings de usuarios**
- **Mensajes persistentes**
- **Configuraciones de auto-roles**
- **Logs de moderación**

### 🔒 **Permisos Requeridos**

Para funcionamiento completo, el bot necesita:
- **Administrador** (recomendado) o permisos específicos:
  - Gestionar Canales
  - Gestionar Roles
  - Gestionar Mensajes
  - Conectar y Hablar (para música)
  - Usar Comandos de Barra
  - Enviar Mensajes
  - Ver Canales

---

## 🎯 Guía de Uso

### 🚀 **Para Servidores Nuevos**

1. **Invita el bot** con permisos de administrador
2. **Ejecuta `/servidor-completo`** y selecciona tu tipo de comunidad
3. **Personaliza según necesites** (nombres, permisos, etc.)
4. **¡Disfruta tu servidor organizado!**

### 🔄 **Para Servidores Existentes**

1. **Haz backup** de configuraciones importantes
2. **Usa `/setup`** para configuración básica
3. **Configura sistemas específicos** según necesites
4. **Usa comandos individuales** para personalizar

### 🎵 **Configurar Música**

1. **Conecta el bot** a un canal de voz
2. **Usa `/play <canción>`** para empezar
3. **Controla la reproducción** con los botones interactivos
4. **Gestiona la cola** con `/queue`, `/skip`, `/shuffle`

### 🛡️ **Configurar Moderación**

1. **Configura roles** de staff (Admin, Moderador)
2. **Establece canal de logs** para registros
3. **Usa el sistema de warnings** integrado
4. **Configura timeouts y bans** según políticas

### 🎫 **Sistema de Tickets**

1. **Se configura automáticamente** con `/servidor-completo`
2. **Los usuarios clickean el botón** para crear ticket
3. **Staff puede gestionar** tickets desde paneles
4. **Logs automáticos** de todas las acciones

### 📁 **Archivos de Control (Windows)**

El proyecto incluye tres archivos .bat para facilitar el uso:

#### **`install.bat`** - Instalador Automático
- ✅ Verifica Python e instala dependencias
- 🔧 Actualiza pip automáticamente
- 📦 Instala todos los paquetes necesarios
- ⚡ Proceso de instalación en un click

#### **`INICIAR.bat`** - Lanzador del Bot
- 🔍 Verifica Python y dependencias
- 🧹 Limpia procesos anteriores
- 🚀 Inicia el bot con interfaz colorida
- ⚠️ Manejo completo de errores

#### **`DETENER.bat`** - Terminador del Bot
- 🛑 Detiene todos los procesos Python del bot
- 🔓 Libera puertos utilizados (8080)
- 🧹 Limpia procesos en segundo plano
- ✅ Verificación de terminación completa

**Uso recomendado:**
```cmd
# 1. Primera vez
install.bat

# 2. Iniciar bot
INICIAR.bat

# 3. Detener bot (cuando sea necesario)
DETENER.bat
```

---

## ❓ FAQ

### **P: ¿El bot es gratuito?**
R: Sí, DaBot v2 es completamente gratuito y de código abierto.

### **P: ¿Funciona 24/7?**
R: Depende de dónde lo hostees. Necesitas un servidor o VPS para funcionamiento continuo.

### **P: ¿Puedo personalizar los comandos?**
R: Sí, el código es modular y fácilmente personalizable.

### **P: ¿Qué pasa si ya tengo canales con los mismos nombres?**
R: El bot omitirá elementos que ya existan para evitar duplicados.

### **P: ¿Puedo deshacer la configuración automática?**
R: No hay comando de "deshacer", pero puedes eliminar elementos manualmente.

### **P: ¿El bot guarda datos de usuarios?**
R: Solo información necesaria para funcionamiento (warnings, configs de servidor).

### **P: ¿Funciona en todos los idiomas?**
R: Actualmente está en español, pero es fácilmente traducible.

### **P: ¿Puedo usar el bot en múltiples servidores?**
R: Sí, cada servidor tiene configuraciones independientes.

---

## 🚀 Casos de Uso Recomendados

### ✅ **Perfecto Para:**
- **Servidores nuevos** sin configurar
- **Streamers** que empiezan su comunidad
- **Equipos de desarrollo** que necesitan organización
- **Comunidades gaming** que quieren estructura profesional
- **Migración** desde otros bots
- **Estandarización** de múltiples servidores

### ⚠️ **Considerar Antes de Usar:**
- **Servidores muy configurados** (puede crear conflictos)
- **Comunidades con necesidades muy específicas**
- **Servidores con muchos bots especializados**
- **Casos que requieren permisos muy personalizados**

---

## 🔍 Diagnóstico y Solución de Problemas

### 🧪 **Comandos de Diagnóstico**
```
/test all          # Probar todos los sistemas
/panels verify     # Verificar mensajes persistentes
```

### 🐛 **Problemas Comunes**

#### **"El bot no responde"**
- Verifica que el token sea correcto
- Comprueba permisos del bot
- Revisa que el bot esté online

#### **"Los comandos no aparecen"**
- Espera unos minutos (sincronización)
- Reinvita el bot con permisos actualizados
- Verifica que uses `/` para comandos slash

#### **"La música no funciona"**
- Verifica que el bot tenga permisos de voz
- Comprueba la conexión a internet
- Asegúrate de estar en un canal de voz

#### **"Los mensajes persistentes no funcionan"**
- Usa `/panels verify` para verificar
- Reinicia el bot si es necesario
- Verifica permisos de gestión de mensajes

---

## 📊 Estadísticas del Proyecto

- **📁 Archivos:** 12+ archivos principales
- **📋 Líneas de código:** 2000+ líneas
- **🎯 Comandos:** 25+ comandos únicos
- **🎭 Módulos:** 5 módulos especializados
- **🏗️ Plantillas:** 4 plantillas completas de servidor
- **🧪 Tests:** Sistema de testing integrado
- **📖 Documentación:** Completa y detallada

---

## 🔄 Actualizaciones y Mantenimiento

### 📅 **Versiones**
- **v2.0** - Lanzamiento inicial completo
- **v2.1** - Sistema de configuración completa de servidores
- **v2.2** - Mejoras y optimizaciones (próximamente)

### 🔄 **Cómo Actualizar**
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### 🛠️ **Mantenimiento Regular**
- **Verificar mensajes persistentes** con `/panels verify`
- **Limpiar logs antiguos** periódicamente
- **Actualizar dependencias** cuando sea necesario
- **Revisar base de datos** si hay problemas

---

## 🤝 Contribuir

### 🌟 **Formas de Contribuir**
- **🐛 Reportar bugs** en Issues
- **💡 Sugerir características** nuevas
- **📝 Mejorar documentación**
- **🔧 Enviar pull requests**
- **⭐ Dar estrella** al repositorio

### 🔧 **Desarrollo**
```bash
# 1. Fork el repositorio
# 2. Crea una rama para tu feature
git checkout -b feature/nueva-caracteristica

# 3. Haz tus cambios
# 4. Ejecuta tests
python test_bot.py

# 5. Commit tus cambios
git commit -m "Añadir nueva característica"

# 6. Push a tu fork
git push origin feature/nueva-caracteristica

# 7. Crea Pull Request
```

### 📋 **Estándares de Código**
- **Comentarios en español**
- **Docstrings descriptivas**
- **Código limpio y legible**
- **Tests para nuevas características**

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🎉 ¡Gracias por usar DaBot v2!

### 📞 **Soporte**
- **GitHub Issues:** Para bugs y sugerencias
- **Discord:** [Servidor de soporte](https://discord.gg/tu-servidor)
- **Email:** tu-email@dominio.com

### 🌟 **Síguenos**
- **GitHub:** [@davito-03](https://github.com/davito-03)
- **Discord:** tu-usuario#0000

---

## 🚀 **¡Comienza Ahora!**

```bash
# Clona e instala
git clone https://github.com/davito-03/dabot-v2.git
cd dabot-v2
pip install -r requirements.txt

# Configura tu token en bot.py
# Ejecuta el bot
python bot.py

# En Discord, usa:
/servidor-completo
```

### 🎯 **¡En minutos tendrás un servidor completamente configurado y funcional!**

---

*DaBot v2 - Tu bot de Discord definitivo* 🤖✨
