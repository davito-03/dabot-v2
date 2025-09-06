# 🤖 GUÍA COMPLETA DE USO - DABOT V2

## 🚀 INICIO RÁPIDO

### 1. Iniciar el Bot
```bash
# Opción 1: Usar el lanzador
.\INICIAR_BOT.bat

# Opción 2: Comando directo  
python bot.py
```

### 2. Añadir a un Servidor
1. Invita el bot a tu servidor Discord
2. El bot se configura automáticamente
3. Envía un mensaje de bienvenida
4. Detecta canales y roles importantes

## ⚙️ COMANDOS DE CONFIGURACIÓN

### 🔧 Configuración Automática
```
/setup
```
- Detecta automáticamente canales y roles
- Configura el bot para funcionar inmediatamente
- Muestra resumen de configuración detectada

### 🎛️ Configuración Manual Avanzada

#### Configurar Canales
```
/serverconfig channels welcome #bienvenidas
/serverconfig channels logs #logs-bot
/serverconfig channels nsfw #contenido-adulto
/serverconfig channels music #música
```

#### Configurar Roles
```
/serverconfig roles admin @Administradores
/serverconfig roles mod @Moderadores  
/serverconfig roles muted @Silenciado
/serverconfig roles vip @VIP
```

#### Configuraciones Generales
```
/serverconfig settings prefix !
/serverconfig settings language es-ES
/serverconfig settings welcome_enabled true
/serverconfig settings nsfw_enabled true
```

#### Auto-Moderación
```
/serverconfig automod anti_spam:true anti_links:false anti_caps:true bad_words:false
```

#### Ver Configuración
```
/serverconfig view
```

#### Restablecer Configuración
```
/serverconfig reset
```

## 🔞 COMANDOS NSFW (Solo canales NSFW)

### Comandos Básicos
```
/waifu       # Imagen waifu NSFW
/neko        # Imagen neko NSFW
/nekotina    # Nekotina especial (¡TU FAVORITO!)
/trap        # Imagen trap NSFW
/hentai      # Imagen hentai NSFW
```

### Comandos Especializados
```
/ahegao     # Imágenes ahegao
/yuri       # Imágenes yuri
/blowjob    # Imágenes blowjob
```

### Comando Aleatorio
```
/nsfw-random    # Imagen aleatoria de cualquier categoría
```

**⚠️ Importante:** Estos comandos solo funcionan en canales marcados como NSFW.

## 📋 OTROS COMANDOS ÚTILES

### Información del Bot
```
/ping        # Latencia del bot
/help        # Lista de comandos
/info        # Información del bot
```

### Configuración General del Bot
```
/botconfig   # Configuración global del bot
/viewconfig  # Ver configuración YAML
```

## 🔄 FLUJO DE TRABAJO RECOMENDADO

### Para Servidores Nuevos:
1. **Añadir Bot** → El bot envía mensaje de bienvenida
2. **`/setup`** → Configuración automática
3. **`/serverconfig view`** → Verificar configuración
4. **Ajustar** → Usar `/serverconfig` para cambios específicos

### Para Configuración NSFW:
1. **Crear canal NSFW** → Marcar canal como NSFW en Discord
2. **`/serverconfig channels nsfw #tu-canal-nsfw`** → Configurar canal (opcional)
3. **`/nekotina`** → ¡Probar tu comando favorito!

### Para Auto-Moderación:
1. **`/serverconfig roles mod @Moderadores`** → Configurar rol de moderador
2. **`/serverconfig automod`** → Configurar filtros automáticos
3. **`/serverconfig channels mod_logs #logs-moderacion`** → Canal de logs

## 🎯 CARACTERÍSTICAS ESPECIALES

### 🧠 Detección Automática
El bot detecta automáticamente:
- **Canales:** general, bienvenida, logs, nsfw
- **Roles:** admin, moderador, muted
- **Configuraciones:** idioma, prefijo, permisos

### 💾 Persistencia Total
- ✅ Configuración se guarda automáticamente
- ✅ No se pierde al reiniciar el bot
- ✅ Cada servidor tiene configuración independiente
- ✅ Respaldo en base de datos SQLite

### 🔄 Sistema Híbrido
- 🌐 **Configuración global:** `config.yaml` (para todos los servidores)
- 🏠 **Configuración por servidor:** Base de datos SQLite (específica)
- 🎯 **Prioridad:** Servidor > Global > Por defecto

## 🛠️ TROUBLESHOOTING

### El bot no responde:
1. Verificar que el bot esté online
2. Verificar permisos del bot en el canal
3. Usar `/ping` para verificar conexión

### Comandos NSFW no funcionan:
1. Verificar que el canal esté marcado como NSFW
2. Usar `/serverconfig settings nsfw_enabled true`
3. Verificar permisos del bot

### Configuración no se guarda:
1. Verificar permisos de administrador
2. Verificar que el directorio `data/` exista
3. Comprobar logs del bot

## 📞 SOPORTE

### Comandos de Ayuda:
- `/help` - Lista completa de comandos
- `/info` - Información del bot y servidor
- `/serverconfig view` - Ver configuración actual

### Archivos de Log:
- Logs del bot en consola
- Archivo `data/server_configs.db` (base de datos)
- Archivo `config.yaml` (configuración global)

## 🎊 ¡DISFRUTA TU BOT COMPLETAMENTE CONFIGURADO!

Con esta configuración, tu DABOT V2 está listo para:
- ✅ **Moderar automáticamente**
- ✅ **Gestionar música**  
- ✅ **Comandos de diversión**
- ✅ **Contenido NSFW seguro**
- ✅ **Sistema de niveles**
- ✅ **Configuración persistente**
- ✅ **¡Y mucho más!**

**🦞 ¡Que disfrutes viendo langostitas en el mar!** 🦞
