# 🎊 DABOT V2 - ACTUALIZACIÓN COMPLETA CON CONFIGURACIÓN PERSISTENTE

## ✨ NUEVAS FUNCIONALIDADES AÑADIDAS

### 🔞 COMANDOS NSFW EXPANDIDOS
- ✅ **`/waifu`** - Imágenes waifu NSFW
- ✅ **`/neko`** - Imágenes neko NSFW  
- ✅ **`/nekotina`** - Nekotinas especiales (variación única)
- ✅ **`/trap`** - Imágenes trap NSFW
- ✅ **`/ahegao`** - Imágenes ahegao NSFW
- ✅ **`/yuri`** - Imágenes yuri NSFW
- ✅ **`/blowjob`** - Imágenes blowjob NSFW
- ✅ **`/hentai`** - Imágenes hentai NSFW
- ✅ **`/nsfw-random`** - Imagen NSFW aleatoria de cualquier categoría

**Características:**
- 🔒 Solo funcionan en canales marcados como NSFW
- 🎨 Múltiples APIs como respaldo (waifu.pics, nekos.life)
- 🎲 Sistema de categorías aleatorias
- 🖼️ Embeds mejorados con información del solicitante

### 🗄️ SISTEMA DE CONFIGURACIÓN PERSISTENTE

#### **Base de Datos SQLite Integrada**
- 📊 **Tabla `server_configs`** - Configuraciones completas por servidor
- 📝 **Tabla `server_channels`** - Canales especiales por servidor
- 👑 **Tabla `server_roles`** - Roles importantes por servidor  
- ⚙️ **Tabla `server_settings`** - Configuraciones específicas por servidor

#### **Detección Automática al Unirse a Servidores**
- 🔍 **Auto-detección de canales:**
  - `general`, `chat`, `inicio`, `main` → Canal general
  - `welcome`, `bienvenida`, `entrada` → Canal de bienvenida
  - `logs`, `registro`, `audit` → Canal de registros
  - Canales NSFW automáticamente detectados
  
- 🔍 **Auto-detección de roles:**
  - Roles con permisos de administrador
  - Roles con permisos de moderación
  - Roles de "muted" o "silenciado"

### 🎛️ COMANDOS DE CONFIGURACIÓN AVANZADA

#### **`/setup` - Configuración Automática**
- 🚀 Configura el bot automáticamente al unirse a un servidor
- 📋 Muestra resumen de configuración detectada
- ✅ Activa todos los sistemas básicos

#### **`/serverconfig` - Configuración Manual Avanzada**

**Subcomandos disponibles:**

- **`/serverconfig channels [tipo] [canal]`**
  - Tipos: `welcome`, `goodbye`, `logs`, `mod_logs`, `music`, `nsfw`, `general`, `announcements`
  - Asigna canales específicos para cada función

- **`/serverconfig roles [tipo] [rol]`**  
  - Tipos: `admin`, `mod`, `muted`, `verified`, `vip`
  - Configura roles con permisos específicos

- **`/serverconfig settings [setting] [valor]`**
  - Settings: `welcome_enabled`, `goodbye_enabled`, `logging_enabled`, `moderation_enabled`, `music_enabled`, `nsfw_enabled`, `prefix`, `language`
  - Configuraciones booleanas y de texto

- **`/serverconfig automod [opciones]`**
  - `anti_spam`, `anti_links`, `anti_caps`, `bad_words`
  - Configuración completa de auto-moderación

- **`/serverconfig view`**
  - Ver toda la configuración actual del servidor
  - Información organizada por categorías

- **`/serverconfig reset`**
  - Restablecer configuración a valores por defecto
  - Sistema de confirmación de seguridad

### 🔧 INTEGRACIÓN CON SISTEMA EXISTENTE

#### **ConfigManager Mejorado**
- 🔄 **Compatibilidad híbrida:** Configuración global (YAML) + configuración por servidor (SQLite)
- 🎯 **Prioridad inteligente:** Configuración de servidor sobrescribe configuración global
- 🛡️ **Fallback automático:** Si falla la base de datos, usa configuración global
- 🔍 **Conversión automática:** Convierte paths de configuración entre formatos

#### **Nuevas Funciones del ConfigManager**
```python
# Obtener configuración con prioridad de servidor
get_config('moderation.enabled', guild_id="123456789")

# Configurar específicamente para un servidor  
set_server_config(guild_id, 'nsfw_enabled', True)

# Obtener canales y roles configurados
get_server_channel(guild_id, 'welcome')
get_server_role(guild_id, 'admin')
```

## 🎯 COMANDOS DISPONIBLES AHORA

### 🔞 **NSFW (Solo canales NSFW)**
- `/waifu`, `/neko`, `/nekotina`, `/trap`
- `/ahegao`, `/yuri`, `/blowjob`, `/hentai`
- `/nsfw-random`

### ⚙️ **Configuración**
- `/setup` - Auto-configuración
- `/serverconfig` - Configuración manual avanzada
- `/botconfig` - Configuración general del bot  
- `/viewconfig` - Ver configuración YAML

### 🎮 **Todos los comandos existentes**
- Moderación, música, diversión, niveles, tickets, etc.
- Ahora todos usan la configuración persistente

## 🚀 FLUJO DE USO RECOMENDADO

### **Para servidores nuevos:**
1. 🤖 El bot se añade al servidor
2. 📧 Envía mensaje de bienvenida automático
3. 🔍 Detecta canales y roles automáticamente
4. ⚙️ Admin usa `/setup` para confirmar configuración
5. 🎯 Opcionalmente usar `/serverconfig` para ajustes específicos

### **Para configuración avanzada:**
1. 📝 `/serverconfig channels welcome #bienvenidas`
2. 👑 `/serverconfig roles mod @Moderadores`  
3. ⚙️ `/serverconfig settings prefix !`
4. 🛡️ `/serverconfig automod anti_spam:True`
5. 👀 `/serverconfig view` para verificar

## 📊 BENEFICIOS DEL NUEVO SISTEMA

### ✅ **Para Usuarios:**
- 🚀 **Configuración automática** - El bot funciona inmediatamente
- 💾 **Persistencia total** - No se pierde configuración al reiniciar
- 🎯 **Configuración por servidor** - Cada servidor es independiente
- 🔧 **Flexibilidad completa** - Configuración automática + manual

### ✅ **Para Desarrolladores:**
- 🗄️ **Base de datos integrada** - Sistema robusto de almacenamiento
- 🔄 **Compatibilidad híbrida** - No rompe configuración existente
- 🛡️ **Sistema de fallback** - Resistente a errores
- 📈 **Escalabilidad** - Soporta miles de servidores

## 🎊 RESULTADO FINAL

¡El bot ahora es completamente autónomo y se configura automáticamente en cada servidor! Los usuarios pueden simplemente añadir el bot y comenzar a usarlo inmediatamente, mientras que los administradores tienen control total sobre cada aspecto de la configuración.

**🎯 Todo funciona desde Discord, nada de interfaces web, y la configuración se mantiene para siempre.**
