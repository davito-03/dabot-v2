@echo off
title DaBot v2 - Launcher Simplificado
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
echo                    DABOT V2 - LAUNCHER SIMPLIFICADO
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

:: Verificar archivos esenciales
if not exist bot.py (
    echo ❌ ERROR: No se encontró bot.py
    pause
    exit /b 1
)

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

echo ✅ Archivos verificados
echo.

:: Crear carpetas necesarias
if not exist data mkdir data
if not exist logs mkdir logs

:: Abrir dashboard local
echo 🌐 Abriendo dashboard local...
if exist local_dashboard.html (
    start "" local_dashboard.html
    echo ✅ Dashboard abierto en el navegador
) else (
    echo ⚠️  Dashboard local no encontrado
)
echo.

:: Mostrar información
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
echo.
echo ========================================================================
echo.

:: Verificar dependencias básicas
echo 🔍 Verificando dependencias...
python -c "import nextcord" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: nextcord no está instalado
    echo.
    echo 💡 SOLUCIÓN:
    echo 1. Ejecuta: INSTALAR_DEPENDENCIAS.bat
    echo 2. O manualmente: python -m pip install nextcord yt-dlp PyNaCl python-dotenv aiohttp PyJWT
    echo.
    pause
    exit /b 1
)

echo ✅ Dependencias verificadas
echo.

:: Iniciar el bot
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
    echo [3] Instalar dependencias
    echo [4] Salir
    echo.
    set /p choice=Elige una opción (1-4): 
    
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
        echo.
        echo 📦 Ejecutando instalador de dependencias...
        call INSTALAR_DEPENDENCIAS.bat
        goto start_bot
    )
    
    if "%choice%"=="4" (
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
pause
