@echo off
title DaBot v2 - Launcher Automatico
color 0A

:: ASCII Art del bot
echo.
echo ██████╗  █████╗ ██████╗  ██████╗ ████████╗    ██╗   ██╗██████╗ 
echo ██╔══██╗██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝    ██║   ██║╚════██╗
echo ██║  ██║███████║██████╔╝██║   ██║   ██║       ██║   ██║ █████╔╝
echo ██║  ██║██╔══██║██╔══██╗██║   ██║   ██║       ╚██╗ ██╔╝██╔═══╝ 
echo ██████╔╝██║  ██║██████╔╝╚██████╔╝   ██║        ╚████╔╝ ███████╗
echo ╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝         ╚═══╝  ╚══════╝
echo.
echo ========================================================================
echo                    DABOT V2 - LAUNCHER AUTOMATICO
echo ========================================================================
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo.
    echo Por favor instala Python desde: https://python.org
    echo.
    pause
    exit /b 1
)

echo ✅ Python detectado correctamente
echo.

:: Verificar si existe el archivo de requisitos
if not exist requirements.txt (
    echo ❌ ERROR: No se encontró requirements.txt
    echo.
    echo Asegúrate de que estás en la carpeta correcta del bot.
    echo.
    pause
    exit /b 1
)

echo ✅ Archivo requirements.txt encontrado
echo.

:: Verificar si existe el archivo del bot
if not exist bot.py (
    echo ❌ ERROR: No se encontró bot.py
    echo.
    echo Asegúrate de que estás en la carpeta correcta del bot.
    echo.
    pause
    exit /b 1
)

echo ✅ Archivo bot.py encontrado
echo.

:: Verificar si existe el archivo .env
if not exist .env (
    echo ⚠️  AVISO: No se encontró archivo .env
    echo.
    echo Creando archivo .env de ejemplo...
    echo # Token del bot de Discord > .env
    echo DISCORD_TOKEN=TU_TOKEN_AQUI >> .env
    echo.
    echo ❗ IMPORTANTE: Edita el archivo .env y añade tu token de Discord
    echo.
    echo Presiona cualquier tecla para continuar cuando hayas editado el .env...
    pause >nul
)

echo ✅ Configuración verificada
echo.

:: Crear carpetas necesarias
if not exist data mkdir data
if not exist logs mkdir logs

echo ✅ Carpetas de datos creadas
echo.

:: Instalar/actualizar dependencias
echo 📦 Verificando e instalando dependencias...
echo.
pip install -r requirements.txt --quiet --disable-pip-version-check

if %errorlevel% neq 0 (
    echo ❌ ERROR: Falló la instalación de dependencias
    echo.
    echo Intentando con pip3...
    pip3 install -r requirements.txt --quiet --disable-pip-version-check
    
    if %errorlevel% neq 0 (
        echo ❌ ERROR: No se pudieron instalar las dependencias
        echo.
        echo Por favor instala manualmente con: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)

echo ✅ Dependencias instaladas correctamente
echo.

:: Iniciar el dashboard local en el navegador (en segundo plano)
echo 🌐 Preparando dashboard local...
if exist local_dashboard.html (
    start "" local_dashboard.html
    echo ✅ Dashboard abierto en el navegador
) else (
    echo ⚠️  Dashboard local no encontrado, pero el bot funcionará normalmente
)
echo.

:: Mostrar información de inicio
echo ========================================================================
echo                              INICIANDO BOT
echo ========================================================================
echo.
echo 🤖 Bot: DaBot v2
echo 🌐 Dashboard: http://localhost:8080
echo 💾 Datos: Guardados localmente en carpeta 'data'
echo 📝 Logs: Guardados en carpeta 'logs'
echo.
echo ℹ️  Para detener el bot presiona Ctrl+C
echo ℹ️  Para configurar canales usa: /config_canales en Discord
echo ℹ️  Para ver configuración usa: /ver_configuracion en Discord
echo.
echo ========================================================================
echo.

:: Iniciar el bot con manejo de errores
:start_bot
echo 🚀 Iniciando DaBot v2...
echo.

python bot.py

:: Verificar si el bot se cerró con error
if %errorlevel% neq 0 (
    echo.
    echo ❌ El bot se cerró con un error (código: %errorlevel%)
    echo.
    echo ¿Qué quieres hacer?
    echo [1] Reiniciar el bot
    echo [2] Ver logs de error
    echo [3] Salir
    echo.
    set /p choice=Elige una opción (1-3): 
    
    if "%choice%"=="1" (
        echo.
        echo 🔄 Reiniciando bot...
        echo.
        goto start_bot
    )
    
    if "%choice%"=="2" (
        echo.
        echo 📋 Mostrando últimos logs...
        echo.
        if exist logs\bot.log (
            type logs\bot.log | more
        ) else (
            echo No hay logs disponibles
        )
        echo.
        pause
        goto start_bot
    )
    
    if "%choice%"=="3" (
        goto end
    )
    
    :: Opción inválida, reiniciar
    echo Opción inválida, reiniciando...
    goto start_bot
)

:end
echo.
echo ========================================================================
echo                          BOT DETENIDO
echo ========================================================================
echo.
echo 👋 ¡Gracias por usar DaBot v2!
echo.
echo Si necesitas ayuda, revisa:
echo - README.md para documentación
echo - logs/ para logs de errores
echo - data/ para archivos de configuración
echo.
pause
