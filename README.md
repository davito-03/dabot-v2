# 🤖 DaBot V2 - Bot de Discord Avanzado

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Discord](https://img.shields.io/badge/Discord-Bot-7289da?style=for-the-badge&logo=discord)
![Status](https://img.shields.io/badge/Status-Operativo-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Un bot de Discord completo y profesional con más de 25 características avanzadas**

[Características](#-características) •
[Instalación](#-instalación-rápida) •
[Comandos](#-comandos-principales) •
[Plantillas](#-plantillas-de-servidor) •
[Configuración](#-configuración-avanzada) •
[Soporte](#-soporte)

</div>

---

## 🎯 Descripción

DaBot V2 es un bot de Discord multipropósito desarrollado en Python con **nextcord**, diseñado para proporcionar una experiencia completa de gestión de servidores con características avanzadas como sistema de niveles configurable, plantillas de servidor automatizadas, VoiceMaster, sistema de tickets y mucho más.

## ✨ Características Principales

### 🚀 **Sistemas Avanzados**
- **🏆 Sistema de Niveles Profesional**: Configurable como AmariBot con XP, cooldowns, recompensas y rankings
- **🎚️ VoiceMaster Completo**: Canales temporales con control total del usuario
- **🎫 Sistema de Tickets**: Con transcripciones automáticas y configuración avanzada
- **💰 Economía Completa**: Trabajos, tienda, casino, daily rewards
- **🛡️ Moderación Avanzada**: Logs automáticos, sanciones y verificación anti-bot
- **🎮 Plantillas de Servidor**: 7 tipos diferentes con configuración automática

### 💎 **Características Únicas**
- **📊 Dashboard Web**: Panel de control local para gestión visual
- **🔞 Canales NSFW**: Integrados en todas las plantillas
- **🎵 Sistema de Música**: Reproductor avanzado con colas y filtros
- **📝 Confesiones Anónimas**: Sistema seguro de confesiones
- **🎨 Stickers y Emojis**: Gestión avanzada de contenido visual
- **⚡ Auto-Setup**: Configuración completa automática por tipo de servidor

## 🚀 Instalación Rápida

### Prerequisitos
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

---

<div align="center">

**⭐ Si te gusta DaBot V2, no olvides darle una estrella al repositorio ⭐**

**Desarrollado con ❤️ por [Davito-03](https://github.com/davito-03)**

![GitHub Stars](https://img.shields.io/github/stars/davito-03/dabot-v2?style=social)
![GitHub Forks](https://img.shields.io/github/forks/davito-03/dabot-v2?style=social)

</div>
