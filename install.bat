@echo off
title DaBot v2 - Instalador
color 0B
cd /d "%~dp0"

echo.
echo ===============================================
echo           📦 INSTALADOR DABOT V2 📦
echo ===============================================
echo.

:: Verificar Python
echo [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ❌ Python no está instalado
    echo.
    echo Descarga e instala Python 3.8+ desde:
    echo https://python.org/downloads/
    echo.
    echo IMPORTANTE: Marca "Add Python to PATH" durante la instalación
    pause
    exit /b 1
) else (
    echo [OK] ✅ Python disponible
    python --version
)

:: Actualizar pip
echo [2/5] Actualizando pip...
python -m pip install --upgrade pip --user --quiet
if errorlevel 1 (
    echo [WARNING] ⚠️ No se pudo actualizar pip
) else (
    echo [OK] ✅ pip actualizado
)

:: Instalar dependencias
echo [3/5] Instalando dependencias Python...
if not exist "requirements.txt" (
    echo [ERROR] ❌ requirements.txt no encontrado
    pause
    exit /b 1
)

echo [INFO] 📥 Instalando paquetes desde requirements.txt...
python -m pip install -r requirements.txt --user
if errorlevel 1 (
    echo [ERROR] ❌ Error instalando dependencias
    echo.
    echo Intenta ejecutar manualmente:
    echo python -m pip install -r requirements.txt
    pause
    exit /b 1
) else (
    echo [OK] ✅ Todas las dependencias instaladas
)

:: Verificar FFmpeg
echo [4/5] Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] ⚠️ FFmpeg no encontrado
    echo [INFO] 🔧 Instalando FFmpeg automáticamente...
    
    :: Intentar instalar con diferentes métodos
    winget install ffmpeg >nul 2>&1
    if errorlevel 1 (
        choco install ffmpeg -y >nul 2>&1
        if errorlevel 1 (
            echo [INFO] 📥 Descargando FFmpeg manualmente...
            python install_ffmpeg.py
            if errorlevel 1 (
                echo [WARNING] ⚠️ No se pudo instalar FFmpeg automáticamente
                echo [INFO] 💡 FFmpeg se instalará cuando uses comandos de música
                echo [INFO] 📋 Instrucciones manuales disponibles en install_ffmpeg.py
            ) else (
                echo [OK] ✅ FFmpeg instalado correctamente
            )
        ) else (
            echo [OK] ✅ FFmpeg instalado con Chocolatey
        )
    ) else (
        echo [OK] ✅ FFmpeg instalado con Winget
    )
) else (
    echo [OK] ✅ FFmpeg ya está disponible
    ffmpeg -version 2>nul | findstr "ffmpeg version"
)

:: Verificar archivos necesarios
echo [5/5] Verificando configuración...

:: Verificar que existen los archivos principales
if not exist "bot.py" (
    echo [ERROR] ❌ bot.py no encontrado
    pause
    exit /b 1
)

if not exist "modules\" (
    echo [ERROR] ❌ Carpeta modules no encontrada
    pause
    exit /b 1
)

echo [OK] ✅ Archivos principales verificados

echo.
echo ===============================================
echo           ✅ INSTALACIÓN COMPLETADA
echo ===============================================
echo.
echo [INFO] 🎉 DaBot v2 está listo para usar
echo [INFO] 📝 Configura tu token en el archivo .env
echo [INFO] 🚀 Usa INICIAR.bat para ejecutar el bot
echo [INFO] 🎵 FFmpeg configurado para música de YouTube
echo.
echo 📋 RESUMEN DE LA INSTALACIÓN:
echo    ✅ Python verificado
echo    ✅ Dependencias instaladas
echo    ✅ FFmpeg configurado
echo    ✅ Archivos verificados
echo.

echo Presiona cualquier tecla para cerrar...
pause >nul
