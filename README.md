# DaBot v2 - Bot Multipropósito para Discord

## 🤖 Descripción
DaBot v2 es un bot multipropósito para Discord desarrollado con nextcord que incluye funcionalidades de moderación, entretenimiento, música y tareas automatizadas.

## ✨ Funcionalidades

### 🛡️ Moderación
- **Ban/Kick de usuarios** con confirmación interactiva
- **Limpieza de mensajes** (hasta 100 mensajes)
- **Sistema de confirmación** con botones para todas las acciones
- **Notificaciones por DM** a usuarios afectados
- **Verificación de permisos** y jerarquía de roles

### 🎮 Entretenimiento
- **Chistes aleatorios** con más de 15 chistes programados
- **Bola mágica 8** con 25 respuestas diferentes
- **Lanzamiento de moneda** virtual
- **Dados personalizables** (2-100 caras)

### 🎵 Música
- **Reproducción desde YouTube** usando yt-dlp
- **Sistema de cola** avanzado con múltiples canciones
- **Control de volumen** (0-100%)
- **Comandos de control** (play, skip, stop, queue)
- **Búsqueda inteligente** por URL o texto
- **Manejo de errores** robusto

### ⏰ Tareas Automatizadas
- **Mensajes diarios** automáticos a las 8:00 AM
- **Configuración por servidor** independiente
- **Mensajes motivacionales** aleatorios
- **Sistema de pruebas** para verificar funcionamiento

## 🚀 Comandos Disponibles

### Comandos con Prefijo (!)

#### Moderación (Requiere permisos de administrador)
- `!ban @usuario [razón]` - Banea a un usuario
- `!kick @usuario [razón]` - Expulsa a un usuario  
- `!clear [cantidad]` - Elimina mensajes (máx. 100)

#### Entretenimiento
- `!joke` o `!chiste` - Chiste aleatorio
- `!8ball [pregunta]` - Bola mágica 8
- `!flip` o `!moneda` - Lanza moneda
- `!dice [caras]` - Lanza dado

#### Música
- `!play [URL/búsqueda]` - Reproduce música
- `!skip` - Salta canción actual
- `!stop` - Detiene música y limpia cola
- `!queue` - Muestra cola de reproducción
- `!volume [0-100]` - Ajusta volumen
- `!disconnect` - Desconecta del canal

#### Tareas Automáticas (Requiere permisos de administrador)
- `!setdaily [#canal]` - Configura mensajes diarios
- `!removedaily` - Desactiva mensajes diarios
- `!dailystatus` - Estado de mensajes diarios
- `!testdaily` - Prueba mensaje diario

#### Generales
- `!help [categoría]` - Ayuda del bot
- `!ping` - Latencia del bot
- `!info` - Información del bot

### Slash Commands (/)
Todos los comandos también están disponibles como slash commands para una mejor experiencia de usuario.

## 📋 Requisitos

### Dependencias Python
```
nextcord==2.6.0
yt-dlp==2024.8.6
PyNaCl==1.5.0
python-dotenv==1.0.1
requests==2.31.0
aiohttp==3.9.5
```

### Permisos del Bot en Discord
- Ver canales
- Enviar mensajes
- Enviar mensajes incrustados
- Adjuntar archivos
- Leer historial de mensajes
- Usar comandos de barra
- Conectar (para música)
- Hablar (para música)
- Banear miembros
- Expulsar miembros
- Gestionar mensajes

## 🔧 Configuración

### 1. Configuración de Discord
1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)
2. Crea una nueva aplicación
3. Ve a la sección "Bot" y crea un bot
4. Copia el token del bot
5. En "OAuth2 > URL Generator":
   - Scopes: `bot`, `applications.commands`
   - Permisos: Selecciona todos los permisos necesarios

### 2. Variables de Entorno
Crea un archivo `.env` con:
```env
DISCORD_TOKEN=tu_token_aqui
DAILY_CHANNEL_ID=id_del_canal_opcional
```

### 3. Instalación Local
```bash
# Clonar o descargar el proyecto
git clone <repository>
cd dabot-v2

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Edita el archivo .env con tu token

# Ejecutar el bot
python bot.py
```

## 🌐 Deployment en Render.com

### 1. Preparación
El proyecto ya incluye los archivos necesarios:
- `Procfile` - Comando de inicio
- `runtime.txt` - Versión de Python
- `requirements.txt` - Dependencias

### 2. Configuración en Render
1. Conecta tu repositorio de GitHub a Render
2. Crea un nuevo "Web Service"
3. Configura las variables de entorno:
   - `DISCORD_TOKEN`: Tu token del bot
   - `DAILY_CHANNEL_ID`: ID del canal para mensajes diarios (opcional)

### 3. Variables de Entorno en Render
```
DISCORD_TOKEN = tu_token_de_discord_aqui
DAILY_CHANNEL_ID = id_del_canal_opcional
```

### 4. Configuración del Servicio
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`
- **Environment**: Python 3.13

## 🏗️ Estructura del Proyecto

```
dabot-v2/
├── bot.py                    # Archivo principal del bot
├── requirements.txt          # Dependencias Python
├── .env                     # Variables de entorno (local)
├── Procfile                 # Comando para Render.com
├── runtime.txt              # Versión de Python para Render.com
├── README.md                # Este archivo
└── modules/                 # Módulos del bot
    ├── __init__.py
    ├── moderation.py        # Comandos de moderación
    ├── entertainment.py     # Comandos de entretenimiento
    ├── music.py            # Comandos de música
    ├── scheduled_tasks.py   # Tareas automatizadas
    └── help_commands.py     # Comandos de ayuda
```

## 🔒 Seguridad

- ✅ Token almacenado en variables de entorno
- ✅ Verificación de permisos para comandos de moderación
- ✅ Validación de jerarquía de roles
- ✅ Confirmación interactiva para acciones destructivas
- ✅ Manejo robusto de errores
- ✅ Logs detallados para debugging

## 🐛 Troubleshooting

### Error: "nextcord could not be resolved"
- Instala las dependencias: `pip install -r requirements.txt`

### Error: "Token inválido"
- Verifica que el token en `.env` sea correcto
- Asegúrate que el bot esté habilitado en Discord Developer Portal

### Error: "No tengo permisos"
- Verifica que el bot tenga los permisos necesarios en el servidor
- Revisa la jerarquía de roles

### Música no funciona
- Instala FFmpeg en el sistema
- Verifica que el bot tenga permisos de voz
- Asegúrate de estar en un canal de voz

## 📝 Logs
El bot genera logs detallados para todas las operaciones:
- Conexión y desconexión
- Ejecución de comandos
- Errores y excepciones
- Tareas automatizadas

## 🤝 Contribuir
Si encuentras bugs o quieres agregar funcionalidades:
1. Reporta issues detallando el problema
2. Propón mejoras con ejemplos específicos
3. Mantén el código limpio y comentado

## 📄 Licencia
Este proyecto es de código abierto. Úsalo y modifícalo libremente.

---
**Desarrollado con ❤️ usando nextcord**
