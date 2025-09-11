# 🚀 Archivos de Gestión de DaBot v2

## 📁 Archivos Incluidos (Solo los Esenciales)

### 🎯 **gestor_dabot.bat** - Gestor Completo (26,645 bytes)
El archivo principal para manejar completamente el bot. Incluye todas las funcionalidades necesarias.

#### ✨ **Características Principales:**
- 🚀 **Iniciar/Detener/Reiniciar** el bot
- 📊 **Monitoreo del estado** en tiempo real
- 📦 **Instalación automática** de dependencias
- ⚙️ **Configuración completa** (token, prefijo, etc.)
- 🏁 **Autoarranque** con Windows
- 🔧 **Reparación automática** de problemas
- 📋 **Visualización de logs** y errores
- 🧪 **Sistema de pruebas** integrado
- 🔍 **Verificación completa** del sistema

#### 🎮 **Opciones del Menú:**
```
1. 🚀 Iniciar Bot                    2. ⏹️  Detener Bot
3. 🔄 Reiniciar Bot                 4. 📊 Estado del Bot
5. 📦 Instalar/Actualizar           6. ⚙️  Configurar
7. 🔧 Reparar Dependencias          8. 📋 Ver Logs
9. 🏁 Configurar Autoarranque       10. ❌ Desactivar Autoarranque
11. 🧪 Ejecutar Pruebas             12. 🔍 Verificar Sistema
13. 📂 Abrir Carpeta del Bot        14. 💻 Abrir CMD Aquí
15. 📚 Ver Documentación            16. 🆘 Ayuda
0. 🚪 Salir
```

---

### 🎉 **instalar_dabot.bat** - Instalador Automático (11,560 bytes)
Instalador completo que configura todo automáticamente para usuarios nuevos.

#### ✨ **Funcionalidades del Instalador:**
- 🐍 **Descarga e instala Python** automáticamente si no está presente
- 📦 **Configura entorno virtual** (.venv)
- 📋 **Instala todas las dependencias** necesarias
- 📝 **Crea archivo de configuración** (.env)
- 🔑 **Ayuda a configurar el token** de Discord
- 🖥️ **Crea acceso directo** en el escritorio
- 🏁 **Configura autoarranque** opcional
- 🗑️ **Genera desinstalador** automático

#### 🎯 **Proceso de Instalación:**
1. **Verificación de Python** → Descarga automática si es necesario
2. **Configuración de entorno** → Entorno virtual y dependencias
3. **Configuración inicial** → Token y preferencias
4. **Creación de accesos** → Escritorio y autoarranque
5. **Verificación final** → Testing de la instalación

---

## 🚀 Guía de Uso Rápida

### 🆕 **Primera Vez (Usuarios Nuevos):**
1. ✅ Ejecuta `instalar_dabot.bat` como **administrador**
2. ✅ Sigue las instrucciones en pantalla
3. ✅ Configura tu token de Discord cuando se solicite
4. ✅ Elige si quieres autoarranque
5. ✅ ¡Listo! Usa el acceso directo del escritorio

### 🔄 **Uso Diario:**
1. ✅ Doble clic en **"DaBot v2 Gestor"** (escritorio)
2. ✅ Opción **1** para iniciar el bot
3. ✅ Opción **2** para detener el bot
4. ✅ Opción **4** para ver el estado

### 🛠️ **Mantenimiento:**
- 🔧 **Opción 7**: Reparar dependencias si hay errores
- 📋 **Opción 8**: Ver logs para debugging
- 🧪 **Opción 11**: Ejecutar pruebas del sistema
- 🔍 **Opción 12**: Verificación completa

---

## 🏁 Sistema de Autoarranque

### ✅ **Cómo Funciona:**
1. **Configuración automática** en el startup de Windows
2. **Espera 30 segundos** después del arranque del PC
3. **Verifica conexión a internet** antes de iniciar
4. **Activa entorno virtual** automáticamente
5. **Inicia el bot en segundo plano** sin ventanas molestas

### ⚙️ **Ubicación del Script:**
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\DaBot_v2_AutoStart.bat
```

### 🔄 **Gestión del Autoarranque:**
- **Activar**: Opción 9 en el gestor
- **Desactivar**: Opción 10 en el gestor
- **Estado**: Se muestra en el menú principal

---

## 🎨 Características Visuales

### 🌈 **Interface Colorida:**
- 🟢 **Verde**: Estados exitosos y confirmaciones
- 🔴 **Rojo**: Errores y advertencias críticas
- 🟡 **Amarillo**: Advertencias y información importante
- 🔵 **Azul**: Procesos en curso y información
- 🟣 **Magenta**: Títulos y secciones especiales
- 🔘 **Cyan**: Menús y opciones

### 📊 **Información en Tiempo Real:**
- 🟢🔴 **Estado del bot**: Ejecutándose/Detenido
- 🏁⚠️ **Autoarranque**: Activado/Desactivado
- 📍 **Directorio actual** y configuración
- ⏰ **Fecha y hora** del sistema

---

## 🔧 Solución de Problemas

### ❌ **Problemas Comunes:**

#### 🐍 **"Python no encontrado"**
- **Solución**: Usar `instalar_dabot.bat` que descarga Python automáticamente
- **Manual**: Descargar desde https://python.org

#### 🔑 **"Token no configurado"**
- **Solución**: Gestor → Opción 6 → Configurar Token
- **Obtener token**: https://discord.com/developers/applications

#### 📦 **"Error en dependencias"**
- **Solución**: Gestor → Opción 7 → Reparar Dependencias
- **Alternativa**: Gestor → Opción 5 → Instalar/Actualizar

#### 🌐 **"Sin conexión"**
- **Verificar**: Gestor → Opción 12 → Verificar Sistema
- **Solución**: Revisar conexión a internet

#### 🏁 **"Autoarranque no funciona"**
- **Reconfigurar**: Gestor → Opción 9
- **Verificar**: Windows + R → `shell:startup`

### 🔍 **Debugging Avanzado:**
1. **Ver logs**: Opción 8 del gestor
2. **Ejecutar pruebas**: Opción 11 del gestor
3. **Verificación completa**: Opción 12 del gestor
4. **Abrir CMD**: Opción 14 del gestor para comandos manuales

---

## 📋 Requisitos del Sistema

### 💻 **Mínimos:**
- ✅ Windows 10/11 (Windows 7/8 compatible)
- ✅ 2 GB RAM libre
- ✅ 500 MB espacio en disco
- ✅ Conexión a internet
- ✅ Permisos de administrador (para instalación)

### 🎯 **Recomendados:**
- ✅ Windows 10/11 actualizado
- ✅ 4 GB RAM libre
- ✅ 1 GB espacio en disco
- ✅ Conexión estable a internet
- ✅ Antivirus con excepción para la carpeta del bot

---

## 🔐 Seguridad

### 🛡️ **Medidas de Seguridad:**
- 🔑 **Token encriptado** en archivo .env local
- 🚫 **No envío de datos** personales
- 🔒 **Ejecución local** completa
- 📁 **Archivos en carpeta de usuario**

### ⚠️ **Recomendaciones:**
- 🚫 **Nunca compartir** el archivo .env
- 🔄 **Regenerar token** si se compromete
- 🧹 **Limpiar logs** periódicamente
- 🛡️ **Excluir carpeta** del antivirus

---

## 📞 Soporte

### 🆘 **Obtener Ayuda:**
1. **Gestor → Opción 16**: Ayuda integrada
2. **Gestor → Opción 15**: Ver documentación
3. **Verificar sistema**: Opción 12 para diagnóstico
4. **Ver logs**: Opción 8 para detalles de errores

### 🌐 **Enlaces Útiles:**
- **Discord Developers**: https://discord.com/developers/applications
- **Python Official**: https://python.org
- **Nextcord Docs**: https://docs.nextcord.dev

---

*Archivos creados para DaBot v2 - Sistema de gestión completo*
*Actualizados el 8 de septiembre de 2025* ✅
