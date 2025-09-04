@echo off
title DaBot v2 - LISTO PARA USAR
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
echo                    🎉 DABOT V2 - TOTALMENTE FUNCIONAL 🎉
echo ========================================================================
echo.

cd /d "%~dp0"

:: Verificaciones básicas
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Instala Python desde: https://python.org
    pause
    exit /b 1
)

if not exist bot.py (
    echo ❌ bot.py no encontrado
    pause
    exit /b 1
)

if not exist .env (
    echo ⚠️  Creando archivo .env...
    echo DISCORD_TOKEN=TU_TOKEN_AQUI > .env
    echo.
    echo ❗ EDITA EL ARCHIVO .env Y AÑADE TU TOKEN DE DISCORD
    echo.
    notepad .env
    echo.
    echo Presiona Enter cuando hayas guardado tu token...
    pause >nul
)

:: Crear carpetas
if not exist data mkdir data
if not exist logs mkdir logs

:: Verificar nextcord
python -c "import nextcord" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Instalando nextcord...
    python -m pip install nextcord --user
)

:: Abrir dashboard
echo 🌐 Abriendo dashboard...
if exist local_dashboard.html (
    start "" local_dashboard.html
)

echo.
echo ========================================================================
echo                        🚀 INICIANDO DABOT V2
echo ========================================================================
echo.
echo ✅ Bot: Configurado y listo
echo ✅ Dashboard: http://localhost:8080
echo ✅ Datos: Se guardan en carpeta 'data'
echo ✅ Logs: Se guardan en carpeta 'logs'
echo.
echo 🎮 COMANDOS PRINCIPALES EN DISCORD:
echo    /config_canales    - Configurar todos los canales
echo    /level_config      - Configurar sistema de niveles  
echo    /ver_configuracion - Ver configuración actual
echo.
echo ℹ️  Para detener: Ctrl+C
echo ========================================================================
echo.

:: Iniciar bot
python bot.py

echo.
echo 👋 Bot detenido. Presiona cualquier tecla para salir...
pause >nul
