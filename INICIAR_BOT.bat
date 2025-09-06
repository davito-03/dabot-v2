@echo off
title Iniciando Bot - DA Bot v2
color 0A
echo.
echo ====================================
echo   🚀 INICIANDO DA BOT v2 🚀
echo   Verificación + Inicio Automático
echo ====================================
echo.

set "ERROR_COUNT=0"
set "WARNING_COUNT=0"

echo [FASE 1] Verificando Python...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ❌ Python no está instalado o no está en PATH
    set /a ERROR_COUNT+=1
    goto :end_check
) else (
    echo [OK] ✅ Python instalado correctamente
    python --version
)

echo.
echo [FASE 2] Verificando pip...
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ❌ pip no está disponible
    set /a ERROR_COUNT+=1
) else (
    echo [OK] ✅ pip disponible
)

echo.
echo [FASE 3] Verificando archivo de dependencias...
if not exist "requirements.txt" (
    echo [ERROR] ❌ Archivo requirements.txt no encontrado
    set /a ERROR_COUNT+=1
    goto :check_modules
) else (
    echo [OK] ✅ requirements.txt encontrado
)

echo.
echo [FASE 4] Verificando dependencias críticas...

REM Verificar nextcord
python -c "import nextcord; print(f'nextcord {nextcord.__version__}')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ❌ nextcord no instalado - DEPENDENCIA CRÍTICA
    set /a ERROR_COUNT+=1
) else (
    echo [OK] ✅ nextcord instalado
    python -c "import nextcord; print(f'  Versión: {nextcord.__version__}')"
)

REM Verificar aiohttp
python -c "import aiohttp; print(f'aiohttp {aiohttp.__version__}')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] ⚠️ aiohttp no encontrado
    set /a WARNING_COUNT+=1
) else (
    echo [OK] ✅ aiohttp disponible
)

REM Verificar asyncio (viene con Python)
python -c "import asyncio" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ❌ asyncio no disponible
    set /a ERROR_COUNT+=1
) else (
    echo [OK] ✅ asyncio disponible
)

REM Verificar requests
python -c "import requests" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] ⚠️ requests no encontrado
    set /a WARNING_COUNT+=1
) else (
    echo [OK] ✅ requests disponible
)

:check_modules
echo.
echo [FASE 5] Verificando estructura del proyecto...

if not exist "bot.py" (
    echo [ERROR] ❌ Archivo principal bot.py no encontrado
    set /a ERROR_COUNT+=1
) else (
    echo [OK] ✅ bot.py encontrado
)

if not exist "modules" (
    echo [ERROR] ❌ Directorio modules no encontrado
    set /a ERROR_COUNT+=1
) else (
    echo [OK] ✅ Directorio modules encontrado
)

if not exist ".env" (
    echo [WARNING] ⚠️ Archivo .env no encontrado
    set /a WARNING_COUNT+=1
) else (
    echo [OK] ✅ Archivo .env encontrado
)

echo.
echo [FASE 6] Verificando importaciones del bot...
python -c "import bot; print('✅ bot.py se puede importar correctamente')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] ❌ Error al importar bot.py - revisar sintaxis
    set /a ERROR_COUNT+=1
) else (
    echo [OK] ✅ bot.py se importa sin errores
)

echo.
echo [FASE 7] Verificando módulos del bot...
python -c "from modules import entertainment, moderation, music, scheduled_tasks; print('✅ Módulos básicos OK')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] ⚠️ Algunos módulos básicos tienen problemas
    set /a WARNING_COUNT+=1
) else (
    echo [OK] ✅ Módulos básicos funcionando
)

python -c "from modules import persistent_messages, ticket_system, voicemaster, auto_setup, test_systems; print('✅ Sistema de mensajes persistentes OK')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] ⚠️ Sistema de mensajes persistentes tiene problemas
    set /a WARNING_COUNT+=1
) else (
    echo [OK] ✅ Sistema de mensajes persistentes funcionando
)

echo.
echo [FASE 8] Verificando conectividad...
python -c "import socket; sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM); result = sock.connect_ex(('discord.com', 443)); sock.close(); exit(0 if result == 0 else 1)" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] ⚠️ No se puede conectar a Discord - revisar conexión
    set /a WARNING_COUNT+=1
) else (
    echo [OK] ✅ Conectividad a Discord OK
)

:end_check
echo.
echo ====================================
echo       RESUMEN DE VERIFICACIÓN
echo ====================================

if %ERROR_COUNT% EQU 0 (
    if %WARNING_COUNT% EQU 0 (
        echo [ESTADO] 🟢 PERFECTO - Todo funcional
        echo.
        echo ✅ Sin errores críticos
        echo ✅ Sin advertencias
        echo.
        echo [ACCIÓN] Iniciando bot automáticamente en 3 segundos...
        timeout /t 3 /nobreak
        echo.
        echo ================================================
        echo          🚀 INICIANDO DA BOT v2 🚀
        echo ================================================
        echo.
        python -u bot.py
    ) else (
        echo [ESTADO] 🟡 FUNCIONAL CON ADVERTENCIAS
        echo.
        echo ✅ Sin errores críticos
        echo ⚠️ %WARNING_COUNT% advertencia(s) encontrada(s)
        echo.
        echo [ACCIÓN] Iniciando bot a pesar de las advertencias en 5 segundos...
        echo [INFO] Revisa las advertencias cuando el bot esté funcionando
        timeout /t 5 /nobreak
        echo.
        echo ================================================
        echo          🚀 INICIANDO DA BOT v2 🚀
        echo ================================================
        echo.
        python -u bot.py
    )
) else (
    echo [ESTADO] 🔴 ERRORES CRÍTICOS ENCONTRADOS
    echo.
    echo ❌ %ERROR_COUNT% error(es) crítico(s)
    echo ⚠️ %WARNING_COUNT% advertencia(s)
    echo.
    echo [ACCIÓN] ❌ NO SE PUEDE INICIAR EL BOT
    echo.
    echo 🔧 Soluciones sugeridas:
    if %ERROR_COUNT% GTR 0 (
        echo   • Instalar dependencias: pip install -r requirements.txt
        echo   • Verificar archivo .env y configuración
        echo   • Revisar sintaxis en bot.py
        echo   • Contactar al desarrollador si persisten los problemas
    )
    echo.
    echo ====================================
    echo.
    echo Presiona cualquier tecla para salir...
    pause >nul
)
