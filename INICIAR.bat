@echo off
title DaBot v2 - Iniciar Bot
color 0A
cd /d "%~dp0"

echo.
echo ===============================================
echo           🤖 INICIANDO DABOT V2 🤖
echo ===============================================
echo.

:: Verificar Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ❌ Python no está instalado
    echo Descarga Python desde: https://python.org
    pause
    exit /b 1
) else (
    echo [OK] ✅ Python disponible
)

:: Verificar dependencias críticas
echo [2/4] Verificando dependencias...
python -c "import nextcord" >nul 2>&1
if errorlevel 1 (
    echo [INFO] 📦 Instalando dependencias...
    python -m pip install -r requirements.txt --user --quiet
    if errorlevel 1 (
        echo [ERROR] ❌ Error instalando dependencias
        pause
        exit /b 1
    )
    echo [OK] ✅ Dependencias instaladas
) else (
    echo [OK] ✅ Dependencias verificadas
)

:: Verificar archivo principal
echo [3/4] Verificando archivo bot.py...
if not exist "bot.py" (
    echo [ERROR] ❌ bot.py no encontrado
    pause
    exit /b 1
) else (
    echo [OK] ✅ bot.py encontrado
)

:: Limpiar procesos anteriores
echo [4/4] Limpiando procesos anteriores...
taskkill /f /im python.exe >nul 2>&1
timeout /t 1 /nobreak >nul

:: Iniciar bot
echo.
echo ===============================================
echo           🚀 EJECUTANDO BOT...
echo ===============================================
echo.
echo [INFO] Presiona Ctrl+C para detener el bot
echo [INFO] El bot se está iniciando...
echo.

python bot.py

echo.
if errorlevel 1 (
    echo [ERROR] ❌ El bot se cerró con errores
) else (
    echo [INFO] ℹ️ El bot se cerró correctamente
)

echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
