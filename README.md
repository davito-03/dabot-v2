# 🤖 DaBot v2 - Bot de Discord Completo

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/nextcord-2.6+-green.svg)](https://nextcord.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/Version-v2.0.0-purple.svg)](CHANGELOG.md)
[![Contributors](https://img.shields.io/badge/Contributors-Welcome-orange.svg)](CONTRIBUTING.md)
[![Security](https://img.shields.io/badge/Security-Policy-red.svg)](SECURITY.md)
[![Deploy](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)](https://render.com)

**DaBot v2** es un bot de Discord multipropósito y completamente funcional, desarrollado en Python con nextcord. Incluye sistemas de moderación, entretenimiento, música, economía, tickets y mucho más.

## 📋 Tabla de Contenidos

- [✨ Características Principales](#-características-principales)
- [🚀 Instalación Rápida](#-instalación-rápida)
- [⚙️ Configuración](#️-configuración)
- [📱 Comandos Disponibles](#-comandos-disponibles)
- [🔧 Gestión del Bot](#-gestión-del-bot)
- [🌐 Deploy en Render](#-deploy-en-render)
- [📊 Estructura del Proyecto](#-estructura-del-proyecto)
- [🔒 Características de Seguridad](#-características-de-seguridad)
- [� Documentación](#-documentación)
- [🤝 Contribuciones](#-contribuciones)
- [📝 Changelog](#-changelog)
- [📄 Licencia](#-licencia)

## ✨ Características Principales

### � **Sistema de Entretenimiento**
- 🎣 **Sistema de Pesca Completo** - 32 especies de peces, 4 niveles de rareza
- 🎲 **Juegos Interactivos** - Dados, monedas, adivinanzas
- 🖼️ **Generación de Imágenes** - Memes, avatares, manipulación de imágenes
- 🎪 **Actividades Diversas** - Chistes, curiosidades, entretenimiento general

### 💰 **Sistema de Economía**
- 💵 **Moneda Virtual** - Sistema completo de créditos
- 🏪 **Tienda Virtual** - Compra y venta de items
- 📈 **Experiencia y Niveles** - Sistema de progresión
- 💎 **Items Especiales** - Coleccionables y objetos únicos

### 🔨 **Sistema de Moderación**
- 🚫 **Comandos de Moderación** - Ban, kick, mute, warn
- 📋 **Sistema de Logs** - Registro completo de actividades
- 🛡️ **Automoción** - Detección automática de spam y contenido inapropiado
- 👮 **Roles de Staff** - Gestión de permisos avanzada

### 🎵 **Sistema de Música**
- ▶️ **Reproducción de Audio** - YouTube, Spotify, URLs directas
- 📜 **Cola de Reproducción** - Sistema de queue avanzado
- 🔊 **Control de Volumen** - Ajuste dinámico del audio
- 🎤 **Comandos de Control** - Play, pause, skip, stop, queue

### 🎫 **Sistema de Tickets**
- 📩 **Creación Automática** - Tickets con categorías
- 💬 **Transcripciones** - Guardado automático de conversaciones
- 🔒 **Control de Acceso** - Permisos personalizables
- 📊 **Estadísticas** - Seguimiento de tickets y resoluciones

### 🔞 **Contenido NSFW**
- 🖼️ **APIs Múltiples** - Contenido variado con fallbacks
- 🔒 **Verificación de Canales** - Solo en canales NSFW
- 🛡️ **Filtros de Seguridad** - Contenido apropiado y seguro

### 🌐 **API Web y Dashboard**
- 📊 **Panel de Control** - Interfaz web para gestión
- 📈 **Estadísticas en Tiempo Real** - Métricas del servidor
- ⚙️ **Configuración Remota** - Ajustes desde el navegador
- 📱 **Responsive Design** - Compatible con móviles

### 🤖 **Características Técnicas**
- ⚡ **Slash Commands** - Comandos modernos de Discord
- 📝 **Base de Datos SQLite** - Almacenamiento eficiente
- 🔄 **Sistema de Cooldowns** - Prevención de spam
- 🛠️ **Gestión de Errores** - Logging completo y recuperación
- 🔧 **Hot Reload** - Recarga de módulos sin reiniciar

## 🚀 Instalación Rápida

### 📋 **Requisitos Previos**
- Python 3.8 o superior
- Git
- Cuenta de Discord Developer

### 🖥️ **Instalación Automática (Windows)**

1. **Descarga el proyecto:**
```bash
git clone https://github.com/davito-03/dabot-v2.git
cd dabot-v2
```

2. **Ejecuta el instalador automático:**
```cmd
instalar_dabot.bat
```

3. **Usa el gestor para configurar:**
```cmd
gestor_dabot.bat
```

### 🐧 **Instalación Manual (Linux/Mac)**

1. **Clona el repositorio:**
```bash
git clone https://github.com/davito-03/dabot-v2.git
cd dabot-v2
```

2. **Crea entorno virtual:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
```

3. **Instala dependencias:**
```bash
pip install -r requirements.txt
```

4. **Configura el bot:**
```bash
cp .env.example .env
nano .env  # Edita con tu token
```

5. **Inicia el bot:**
```bash
python bot.py
```

## ⚙️ Configuración

### 🔑 **Token de Discord**

1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)
2. Crea una nueva aplicación
3. Ve a "Bot" y crea un bot
4. Copia el token y añádelo al archivo `.env`:

```env
DISCORD_TOKEN=tu_token_aqui
PREFIX=!
DAILY_CHANNEL_ID=opcional_id_canal
```

### 🛠️ **Configuración Avanzada**

```env
# Configuración básica
DISCORD_TOKEN=tu_token_aqui
PREFIX=!

# Canales específicos
DAILY_CHANNEL_ID=123456789012345678
LOG_CHANNEL_ID=123456789012345678
WELCOME_CHANNEL_ID=123456789012345678

# APIs externas (opcional)
OPENAI_API_KEY=tu_api_key_openai
GIPHY_API_KEY=tu_api_key_giphy

# Base de datos (para producción)
DATABASE_URL=postgresql://user:pass@host:port/db

# Configuración web
WEB_PORT=5000
WEB_HOST=0.0.0.0
```

## 📱 Comandos Disponibles

### 🎮 **Entretenimiento**
```
!pescar                    # Sistema de pesca
!dados [lados]             # Lanzar dados
!moneda                    # Lanzar moneda
!meme [tema]               # Generar memes
!avatar [@usuario]         # Ver avatar
!chiste                    # Chiste aleatorio
!curiosidad               # Dato curioso
```

### 💰 **Economía**
```
!balance [@usuario]        # Ver dinero
!daily                     # Recompensa diaria
!work                      # Trabajar por dinero
!shop                      # Ver tienda
!buy [item]               # Comprar item
!inventory                 # Ver inventario
```

### 🔨 **Moderación**
```
!ban [@usuario] [razón]    # Banear usuario
!kick [@usuario] [razón]   # Expulsar usuario
!mute [@usuario] [tiempo]  # Mutear usuario
!warn [@usuario] [razón]   # Advertir usuario
!clear [cantidad]          # Limpiar mensajes
!slowmode [segundos]       # Modo lento
```

### 🎵 **Música**
```
!play [canción/url]        # Reproducir música
!pause                     # Pausar reproducción
!resume                    # Reanudar reproducción
!skip                      # Saltar canción
!queue                     # Ver cola
!volume [0-100]           # Ajustar volumen
!disconnect               # Desconectar del canal
```

### 🎫 **Tickets**
```
!ticket create [tema]      # Crear ticket
!ticket close             # Cerrar ticket
!ticket add [@usuario]    # Añadir usuario al ticket
!ticket remove [@usuario] # Quitar usuario del ticket
!transcript               # Generar transcripción
```

### 🔞 **NSFW** (Solo canales NSFW)
```
!nsfw [categoría]         # Contenido NSFW
!rule34 [búsqueda]        # Contenido Rule34
!boobs                    # Contenido específico
!ass                      # Contenido específico
```

### ℹ️ **Información**
```
!help [comando]           # Ayuda general
!ping                     # Latencia del bot
!stats                    # Estadísticas del bot
!serverinfo              # Información del servidor
!userinfo [@usuario]     # Información de usuario
```
- **Python 3.8+**
- **FFmpeg** (para música)
- **Token de Bot Discord**

### 1️⃣ Clonar el Repositorio
```bash
git clone https://github.com/davito-03/dabot-v2.git
cd dabot-v2
```

### 2️⃣ Configurar Token
Crear archivo `.env`:
```env
DISCORD_TOKEN=tu_token_aqui
```

### 3️⃣ Instalación Automática
**Windows:**
```batch
# Ejecutar el gestor de bot
bot_manager.bat

# Seleccionar opción 6: Instalar/Actualizar dependencias
```

**Linux/Mac:**
```bash
pip install -r requirements.txt
python bot.py
```

## 📋 Comandos Principales

### 🏆 **Sistema de Niveles**
```
/rank                    - Ver tu ranking actual
/leaderboard            - Top 10 del servidor
/leaderboard monthly    - Ranking mensual
/level-config           - Configurar sistema de XP (Admin)
/level-manage           - Gestionar niveles de usuarios (Admin)
```

### 🎚️ **VoiceMaster**
```
/voicemaster setup      - Configurar VoiceMaster
/voicemaster panel      - Panel de control de canal
```

### 🎫 **Tickets**
```
/ticket setup           - Configurar sistema de tickets
/ticket close           - Cerrar ticket
/ticket transcript      - Crear transcripción
```

### 💰 **Economía**
```
/balance               - Ver tu balance
/work                  - Trabajar para ganar dinero
/daily                 - Recompensa diaria
/shop                  - Ver tienda
/casino                - Comandos de casino
```

### 🛡️ **Moderación**
```
/ban                   - Banear usuario
/kick                  - Expulsar usuario
/mute                  - Silenciar usuario
/warn                  - Advertir usuario
/clear                 - Limpiar mensajes
```

### 🎮 **Configuración de Servidor**
```
/servidor-completo     - Setup automático completo
/canal-bienvenida      - Configurar bienvenida
/auto-roles            - Configurar roles automáticos
```

## 🏗️ Plantillas de Servidor

DaBot V2 incluye **7 plantillas profesionales** con configuración automática:

### 🎮 **1. Comunidad de Streamer**
- Canales optimizados para streamers
- Sistema de clips y fanart
- Roles para suscriptores y VIPs
- Integración con eventos

### 🎯 **2. Servidor Gaming**
- Canales LFG (Looking for Group)
- Categorías por tipo de juego
- Sistema competitivo
- Rankings y logros

### 💻 **3. Servidor de Desarrollo**
- Canales por lenguajes de programación
- Sistema de proyectos colaborativos
- Recursos y documentación
- Code review y debugging

### 🌟 **4. Comunidad General**
- Estructura social completa
- Sistema de eventos
- Canales temáticos variados
- Configuración flexible

### 🎵 **5. Servidor de Música**
- Canales por géneros musicales
- Sistema de colaboraciones
- Promoción de artistas
- Eventos musicales

### 🌸 **6. Servidor de Anime**
- Discussiones por series
- Calendario de estrenos
- Fanarts y memes
- Reviews y recomendaciones

### 🏆 **7. Equipo Esports**
- Gestión de equipos
- Scrims y entrenamientos
- Análisis y estrategias
- Reclutamiento

## 🔧 Configuración Avanzada

### 🏆 **Sistema de Niveles Configurable**

#### **Configuración de XP:**
```
/level-config xp-settings
# Configurar XP por mensaje (1-50)
# Configurar XP por minuto en voz (1-25)
```

#### **Cooldown y Canales:**
```
/level-config cooldown
# Establecer cooldown entre XP (10-300 segundos)

/level-config excluded-channels
# Excluir canales específicos del sistema XP
```

#### **Recompensas de Roles:**
```
/level-config role-rewards
# Añadir roles como recompensa por nivel
# Configurar nivel requerido para cada rol
```

#### **Reset Mensual:**
```
/level-config reset-monthly
# Activar/desactivar reset automático cada mes
# Mantener leaderboard histórico
```

### 🎚️ **VoiceMaster Avanzado**

#### **Panel de Control:**
- 🔒 **Lock/Unlock**: Bloquear o abrir canal
- 👻 **Hide/Unhide**: Ocultar o mostrar canal
- 🔇 **Mute/Unmute All**: Silenciar todos los usuarios
- 👑 **Transfer Ownership**: Transferir propiedad
- ➕ **Invite**: Invitar usuarios específicos
- ❌ **Kick**: Expulsar usuario del canal
- 📊 **Limit**: Establecer límite de usuarios
- 🎨 **Rename**: Renombrar canal

### 🎫 **Sistema de Tickets Profesional**

#### **Configuración:**
- **Canal de tickets**: Donde se crean los tickets
- **Categoría**: Dónde se mueven los tickets
- **Canal de transcripciones**: Archivo de conversaciones
- **Roles de staff**: Quién puede gestionar tickets

#### **Características:**
- **Transcripciones automáticas**: Todas las conversaciones se guardan
- **Base de datos**: Historial completo de tickets
- **Configuración por servidor**: Personalización total
- **Botones interactivos**: Interfaz fácil de usar

## 🛠️ Gestión del Bot

### **bot_manager.bat** - Script de Gestión Unificado

```batch
# Ejecutar bot_manager.bat para acceder al menú:

[1] Iniciar bot
[2] Detener bot  
[3] Reiniciar bot
[4] Ver estado del bot
[5] Ver logs en tiempo real
[6] Instalar/Actualizar dependencias
[7] Limpiar caché y datos temporales
[8] Salir
```

### **Características del Gestor:**
- ✅ **Control completo**: Iniciar, detener, reiniciar
- ✅ **Monitoreo**: Estado en tiempo real y logs
- ✅ **Mantenimiento**: Limpiar caché automáticamente
- ✅ **Dependencias**: Instalar y actualizar paquetes
- ✅ **Interfaz amigable**: Menú interactivo fácil de usar

## 📊 Estructura del Proyecto

```
dabot-v2/
├── 📁 modules/                    # Módulos principales
│   ├── advanced_level_system.py  # Sistema de niveles avanzado
│   ├── complete_server_setup.py  # Plantillas de servidor
│   ├── voicemaster.py            # Sistema VoiceMaster
│   ├── tickets_system.py         # Sistema de tickets
│   ├── economy.py                # Sistema de economía
│   ├── moderation.py             # Moderación avanzada
│   ├── music.py                  # Sistema de música
│   └── ...                       # Otros módulos
├── 📁 data/                       # Datos y configuraciones
│   ├── levels.db                 # Base de datos de niveles
│   ├── economy.db                # Base de datos de economía
│   └── config.json               # Configuraciones
├── 📁 dashboard-web/              # Dashboard web local
│   ├── index.html                # Página principal
│   ├── management.html           # Panel de gestión
│   └── assets/                   # Recursos web
├── bot.py                        # Bot principal
├── bot_manager.bat               # Gestor del bot (Windows)
├── requirements.txt              # Dependencias
└── README.md                     # Esta documentación
```

## 💰 Donaciones

Si te gusta DaBot V2 y quieres apoyar su desarrollo:

**PayPal**: https://www.paypal.com/paypalme/davito03

Usa el comando `/paypal` en el bot para obtener el enlace directo.

## 🔧 Solución de Problemas

### **Problemas Comunes:**

#### **❌ Error de FFmpeg**
```bash
# Windows - Instalar desde el gestor:
bot_manager.bat → Opción 6

# O descargar manualmente:
# https://ffmpeg.org/download.html
```

#### **❌ Error de Token**
```bash
# Verificar archivo .env
DISCORD_TOKEN=tu_token_aqui

# O usar variable de entorno
export DISCORD_TOKEN="tu_token_aqui"
```

#### **❌ Error de Permisos**
```
El bot necesita estos permisos en Discord:
- Administrator (recomendado)
- O permisos específicos según las funciones que uses
```

#### **❌ Base de Datos**
```bash
# Si hay problemas con las bases de datos:
bot_manager.bat → Opción 7 (Limpiar caché)
```

## 🔄 Actualizaciones

### **Últimas Mejoras (v2.0):**

#### **🆕 Nuevas Funcionalidades:**
- ✅ Sistema de niveles configurable como AmariBot
- ✅ 7 plantillas de servidor con NSFW
- ✅ Script de gestión unificado
- ✅ VoiceMaster con panel completo
- ✅ Sistema de tickets con transcripciones
- ✅ Dashboard web local

#### **🔧 Correcciones:**
- ✅ Todos los problemas originales solucionados (10/10)
- ✅ Sistema de economía balanceado
- ✅ Errores de emojis y stickers corregidos
- ✅ Configuración automática mejorada
- ✅ Sistema de música estabilizado

#### **⚡ Optimizaciones:**
- ✅ Mejor rendimiento y estabilidad
- ✅ Carga más rápida de módulos
- ✅ Base de datos optimizada
- ✅ Interfaz de usuario mejorada

## 📝 Changelog Detallado

### **v2.0.0 - Lanzamiento Mayor**
- 🆕 Sistema de niveles profesional con configuración completa
- 🆕 7 plantillas de servidor con categorías NSFW
- 🆕 Script de gestión unificado bot_manager.bat
- 🆕 Dashboard web local para gestión visual
- 🔧 Refactorización completa del código
- 🔧 Optimización de base de datos
- 🔧 Mejora en manejo de errores

### **v1.5.0 - Mejoras Mayores**
- 🆕 Sistema VoiceMaster avanzado
- 🆕 Sistema de tickets con transcripciones
- 🆕 3 nuevas plantillas de servidor (Music, Anime, Esports)
- 🔧 Sistema de economía mejorado
- 🔧 Corrección de 10 problemas principales

### **v1.0.0 - Lanzamiento Inicial**
- 🆕 Bot básico con comandos fundamentales
- 🆕 Sistema de moderación
- 🆕 Plantillas básicas de servidor
- 🆕 Sistema de música básico

## 🤝 Contribuir

¿Quieres contribuir al proyecto? ¡Genial!

1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Abre** un Pull Request

### **Guidelines:**
- Código limpio y comentado
- Seguir las convenciones de nomenclatura existentes
- Incluir documentación para nuevas funcionalidades
- Probar thoroughly antes de enviar PR

## 📞 Soporte

### **¿Necesitas ayuda?**

- 📧 **Email**: davito03.dev@gmail.com
- 💬 **Discord**: Únete a nuestro servidor de soporte
- 🐛 **Issues**: Reporta bugs en GitHub Issues
- 💰 **Donaciones**: `/paypal` para apoyar el desarrollo

### **Documentación Adicional:**
- 📖 **Wiki**: Guías detalladas y tutoriales
- 🎥 **Videos**: Tutoriales en YouTube
- 📝 **Blog**: Actualizaciones y noticias del proyecto

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🔧 Gestión del Bot

### 📊 **Gestor Integrado (Windows)**

El bot incluye un sistema completo de gestión con interfaz de línea de comandos:

```cmd
gestor_dabot.bat
```

**Opciones disponibles:**
- 🎮 **Control del Bot**: Iniciar, detener, reiniciar, ver estado
- ⚙️ **Configuración**: Instalar, configurar token, reparar problemas
- 🏁 **Autoarranque**: Activar/desactivar arranque automático
- 🛠️ **Herramientas**: Pruebas del sistema, verificación, acceso a logs
- 📚 **Ayuda**: Documentación y guía completa

### 📝 **Logs y Monitoreo**

```bash
# Ver logs en tiempo real
tail -f bot.log

# Ver errores específicos
grep "ERROR" bot.log

# Estadísticas de uso
!stats
```

### 🔄 **Autoarranque (Windows)**

```cmd
# Activar autoarranque con Windows
gestor_dabot.bat → Opción 9

# Desactivar autoarranque
gestor_dabot.bat → Opción 10
```

## 🌐 Deploy en Render

### 📦 **Preparación para Deploy**

1. **Archivos incluidos para Render:**
   - `render.yaml` - Configuración de servicio
   - `Dockerfile` - Containerización
   - `start.sh` - Script de inicio
   - `requirements.txt` - Dependencias

2. **Variables de entorno en Render:**
```env
DISCORD_TOKEN=tu_token
PREFIX=!
DATABASE_URL=postgresql://...
PYTHON_VERSION=3.11
```

### 🚀 **Deploy Automático**

1. **Fork este repositorio** en GitHub
2. **Conecta Render** a tu repositorio
3. **Configura variables** de entorno
4. **Deploy automático** - ¡Listo en minutos!

### 💎 **Características en Render**
- ✅ **24/7 Uptime** - Bot siempre activo
- ✅ **Auto-scaling** - Se ajusta a la carga
- ✅ **SSL/HTTPS** - Dashboard web seguro
- ✅ **PostgreSQL** - Base de datos persistente
- ✅ **Logs centralizados** - Monitoreo fácil

## 📊 Estructura del Proyecto

```
dabot-v2/
├── 📁 modules/                    # Módulos principales
│   ├── 🎮 entertainment_economy.py    # Entretenimiento + Economía
│   ├── 🔨 moderation_system.py       # Sistema de moderación
│   ├── 🎵 music.py                   # Sistema de música
│   ├── 🎫 ticket_system.py           # Sistema de tickets
│   ├── 🔞 nsfw.py                    # Contenido NSFW
│   ├── 🌐 web_api_new.py             # API web y dashboard
│   ├── 🤖 auto_help_system.py        # Sistema de ayuda automática
│   └── ⚙️ complete_server_setup.py   # Configuración de servidor
├── 📁 data/                      # Datos y configuración
│   ├── 💾 database.db               # Base de datos SQLite
│   ├── 📋 fish_data.json            # Datos de pesca
│   └── 🔧 config/                   # Archivos de configuración
├── 📁 web/                       # Dashboard web
│   ├── 🌐 templates/                # Plantillas HTML
│   ├── 🎨 static/                   # CSS, JS, imágenes
│   └── 📊 dashboard.html            # Panel principal
├── 🤖 bot.py                     # Archivo principal del bot
├── ⚙️ gestor_dabot.bat           # Gestor de Windows
├── 🔧 instalar_dabot.bat         # Instalador automático
├── 📋 requirements.txt           # Dependencias Python
├── 🌐 render.yaml                # Configuración Render
├── 🐳 Dockerfile                 # Containerización
├── 🔒 .env                       # Variables de entorno
└── 📖 README.md                  # Esta documentación
```

## 🔒 Características de Seguridad

### 🛡️ **Protecciones Implementadas**
- ✅ **Validación de permisos** - Control granular de acceso
- ✅ **Rate limiting** - Prevención de spam y abuso
- ✅ **Sanitización de inputs** - Prevención de inyecciones
- ✅ **Logs de seguridad** - Registro de actividades sospechosas
- ✅ **Encriptación de tokens** - Protección de credenciales
- ✅ **Verificación de canales** - Contenido apropiado por canal

### 🔐 **Mejores Prácticas**
- 🔑 **Nunca compartir tokens** - Mantén seguras las credenciales
- 🔒 **Permisos mínimos** - Solo los permisos necesarios
- 📝 **Logs regulares** - Monitoreo constante de actividad
- 🔄 **Actualizaciones frecuentes** - Mantén el bot actualizado

## 📝 Changelog

### 🎉 **v2.0.0** (Actual)
- ✨ **Consolidación completa** - 54 módulos → 15 módulos optimizados
- 🎣 **Sistema de pesca mejorado** - 32 especies, niveles, experiencia
- 🌐 **Dashboard web integrado** - Panel de control completo
- 🎫 **Sistema de tickets avanzado** - Con transcripciones automáticas
- 🔧 **Gestor Windows completo** - Instalación y gestión automática
- 🐳 **Soporte para Render** - Deploy en la nube
- 📊 **Sistema de estadísticas** - Métricas detalladas
- 🔒 **Seguridad mejorada** - Protecciones avanzadas

### 📈 **Correcciones Aplicadas**
- 🔧 **Bug fixes en transcripciones** - Búsqueda inteligente de canales
- 🔞 **APIs NSFW estabilizadas** - Múltiples fallbacks
- 🎵 **Sistema de música optimizado** - Mejor rendimiento
- 📝 **Logging mejorado** - Información más detallada
- ⚡ **Performance optimizado** - Menor uso de recursos

## 📚 Documentación

DaBot v2 cuenta con documentación completa y detallada para usuarios, desarrolladores y contribuidores:

### 📖 **Documentación Principal**
- 📋 **[README.md](README.md)** - Guía completa del proyecto
- 📝 **[CHANGELOG.md](CHANGELOG.md)** - Historial detallado de cambios y versiones
- 📜 **[LICENSE](LICENSE)** - Términos de licencia MIT

### 🤝 **Para Desarrolladores**
- 🛠️ **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guía completa para contribuir
- 🔒 **[SECURITY.md](SECURITY.md)** - Política de seguridad y reportes
- 📝 **[Pull Request Template](.github/pull_request_template.md)** - Plantilla para PRs

### 🐛 **Plantillas de Issues**
- 🐛 **[Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)** - Reporte de errores
- ✨ **[Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)** - Solicitud de características
- 📚 **[Documentation](.github/ISSUE_TEMPLATE/documentation.md)** - Mejoras de documentación

### 📚 **Recursos Adicionales**
- 🎯 **Arquitectura del proyecto** - Estructura modular y escalable
- 🧪 **Testing guidelines** - Estándares de pruebas automatizadas
- 🎨 **Coding standards** - Convenciones de código y estilo
- 🚀 **Deployment guides** - Guías de despliegue y configuración

### 🔗 **Enlaces Útiles**
- 📖 **[Discord.py Documentation](https://discordpy.readthedocs.io/)**
- 🎮 **[Discord Developer Portal](https://discord.com/developers/docs/)**
- 🐍 **[Python Documentation](https://docs.python.org/3/)**
- ☁️ **[Render Documentation](https://render.com/docs)**

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor, lee nuestra **[guía de contribución](CONTRIBUTING.md)** completa antes de empezar.

### 🔧 **Cómo Contribuir**
1. **Lee** la [guía de contribución](CONTRIBUTING.md) completa
2. **Fork** el proyecto y clona tu fork
3. **Configura** tu entorno de desarrollo local
4. **Crea una rama** para tu feature (`git checkout -b feature/AmazingFeature`)
5. **Commit** tus cambios (`git commit -m 'feat: add some AmazingFeature'`)
6. **Push** a la rama (`git push origin feature/AmazingFeature`)
7. **Abre un Pull Request** usando nuestra [plantilla](.github/pull_request_template.md)

### 🐛 **Reportar Bugs**
- Usa nuestra **[plantilla de bug report](.github/ISSUE_TEMPLATE/bug_report.md)**
- Incluye **logs detallados** y pasos para reproducir
- Especifica **versión** y **entorno** de ejecución
- **NO** reportes vulnerabilidades de seguridad públicamente (ver [SECURITY.md](SECURITY.md))

### ✨ **Solicitar Features**
- Usa nuestra **[plantilla de feature request](.github/ISSUE_TEMPLATE/feature_request.md)**
- Describe **detalladamente** la funcionalidad deseada
- Explica **por qué** sería útil para la comunidad
- Considera el **impacto** en el rendimiento y la mantenibilidad

### 📚 **Mejorar Documentación**
- Usa nuestra **[plantilla de documentación](.github/ISSUE_TEMPLATE/documentation.md)**
- Identifica **qué falta** o está **desactualizado**
- Propón **mejoras específicas** y **soluciones**

## 📞 Soporte

### 🆘 **¿Necesitas Ayuda?**
- 📖 **Documentación completa** - Este README
- 🎮 **Comando de ayuda** - `!help` en Discord
- 🔧 **Gestor integrado** - `gestor_dabot.bat` → Opción 16
- 🐛 **Issues en GitHub** - Para bugs y problemas
- 💬 **Discusiones** - Para preguntas generales

### 🔧 **Solución de Problemas Comunes**

**Bot no se conecta:**
```bash
# Verificar token
!config token

# Verificar permisos
!botinfo

# Ver logs
!logs
```

**Comandos no funcionan:**
```bash
# Sincronizar comandos
!sync

# Verificar permisos del bot
!permissions

# Reiniciar bot
gestor_dabot.bat → Opción 3
```

**Problemas de dependencias:**
```bash
# Reparar automáticamente
gestor_dabot.bat → Opción 7

# O manualmente
pip install --upgrade -r requirements.txt
```

## 📊 Estadísticas del Proyecto

- 📝 **Líneas de código**: ~15,000
- 📦 **Módulos**: 15 módulos optimizados
- 🎮 **Comandos**: 100+ comandos únicos
- 🎣 **Especies de peces**: 32 especies
- 🔧 **Sistemas**: 8 sistemas principales
- ⭐ **Características**: 50+ features únicas

## 🏆 Reconocimientos

- 🐍 **nextcord** - Framework principal de Discord
- 🎵 **yt-dlp** - Extracción de audio de YouTube
- 🌐 **aiohttp** - Cliente HTTP asíncrono
- 📊 **sqlite3** - Base de datos embebida
- 🎨 **Pillow** - Procesamiento de imágenes
- ⚡ **asyncio** - Programación asíncrona

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2025 davito-03

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

### 🤖 DaBot v2 - Desarrollado con ❤️ por [davito-03](https://github.com/davito-03)

[![GitHub stars](https://img.shields.io/github/stars/davito-03/dabot-v2.svg?style=social&label=Star)](https://github.com/davito-03/dabot-v2/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/davito-03/dabot-v2.svg?style=social&label=Fork)](https://github.com/davito-03/dabot-v2/network)
[![GitHub watchers](https://img.shields.io/github/watchers/davito-03/dabot-v2.svg?style=social&label=Watch)](https://github.com/davito-03/dabot-v2/watchers)

**¿Te gusta el proyecto? ¡Dale una ⭐ en GitHub!**

</div>
