# 🚀 DA Bot v2 - Guía de Uso

## 📁 Archivos de Control del Bot

### 🟢 **INICIAR_BOT.bat** - Archivo Principal
- **Función**: Verifica dependencias e inicia el bot automáticamente
- **Uso**: Doble clic para ejecutar
- **Proceso**:
  1. ✅ Verifica Python e instalación
  2. ✅ Comprueba dependencias críticas (nextcord, etc.)
  3. ✅ Verifica estructura del proyecto
  4. ✅ Prueba importaciones del bot
  5. ✅ Verifica conectividad a Discord
  6. 🚀 **Inicia el bot automáticamente**

### 🔴 **DETENER_BOT.bat** - Parada Segura
- **Función**: Detiene el bot de forma segura y completa
- **Uso**: Ejecutar cuando quieras parar el bot
- **Proceso**:
  1. 🛑 Termina procesos de Python
  2. 🛑 Libera puertos utilizados
  3. 🧹 Limpia archivos temporales
  4. ✅ Confirma detención completa

### 📦 **install.bat** - Instalación de Dependencias
- **Función**: Instala todas las dependencias necesarias
- **Uso**: Ejecutar solo si hay problemas con dependencias
- **Proceso**: Instala paquetes desde requirements.txt

---

## 🎯 **Flujo de Uso Recomendado**

### Para Iniciar el Bot:
1. **Ejecuta**: `INICIAR_BOT.bat`
   - Si todo está OK → El bot se inicia automáticamente
   - Si hay errores → Te muestra qué arreglar

### Para Detener el Bot:
1. **Ejecuta**: `DETENER_BOT.bat`
   - Detiene todo de forma segura

### Si Hay Problemas de Dependencias:
1. **Ejecuta**: `install.bat`
2. **Luego**: `INICIAR_BOT.bat`

---

## 🟢 Estados del Sistema

- **🟢 PERFECTO**: Sin errores → Inicio automático en 3 segundos
- **🟡 ADVERTENCIAS**: Funcional pero con avisos → Inicio en 5 segundos
- **🔴 ERRORES CRÍTICOS**: No se puede iniciar → Muestra soluciones

---

## 📝 Comandos del Bot

Una vez iniciado, puedes usar:
- `/test all` - Verificar todos los sistemas
- `/panels verify` - Verificar mensajes persistentes
- `/ticket setup` - Configurar sistema de tickets
- `/voicemaster setup` - Configurar VoiceMaster

---

## 🛠️ Solución de Problemas

Si `INICIAR_BOT.bat` muestra errores:

1. **Error de Python**: Instala Python 3.8+ y añádelo al PATH
2. **Error de dependencias**: Ejecuta `install.bat`
3. **Error de .env**: Verifica que existe y tiene el TOKEN
4. **Error de conectividad**: Verifica conexión a internet

---

## 📂 Estructura Simplificada

```
📁 dabot v2/
├── 🚀 INICIAR_BOT.bat      ← USAR ESTE PARA INICIAR
├── 🛑 DETENER_BOT.bat      ← USAR ESTE PARA PARAR
├── 📦 install.bat          ← Solo si hay problemas
├── 🤖 bot.py               ← Código principal del bot
└── 📁 modules/             ← Módulos del bot
```

---

**💡 Tip**: Solo necesitas usar `INICIAR_BOT.bat` para todo. Este archivo verifica que todo esté bien antes de iniciar el bot automáticamente.
