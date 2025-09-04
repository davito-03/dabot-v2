@echo off
title Instalar Dependencias - DaBot v2
color 0A

echo.
echo ========================================================================
echo                    INSTALADOR DE DEPENDENCIAS
echo ========================================================================
echo.

cd /d "%~dp0"

echo 📦 Instalando dependencias de DaBot v2...
echo.

:: Lista de paquetes esenciales
echo Instalando paquetes uno por uno...
echo.

echo [1/8] Instalando nextcord...
python -m pip install nextcord==2.6.0 --user
echo.

echo [2/8] Instalando yt-dlp...
python -m pip install yt-dlp --user
echo.

echo [3/8] Instalando PyNaCl...
python -m pip install PyNaCl --user
echo.

echo [4/8] Instalando ffmpeg-python...
python -m pip install ffmpeg-python --user
echo.

echo [5/8] Instalando python-dotenv...
python -m pip install python-dotenv --user
echo.

echo [6/8] Instalando requests...
python -m pip install requests --user
echo.

echo [7/8] Instalando aiohttp...
python -m pip install aiohttp --user
echo.

echo [8/8] Instalando paquetes adicionales...
python -m pip install PyJWT cryptography pillow --user
echo.

echo ✅ ¡Instalación completada!
echo.
echo Ahora puedes ejecutar LAUNCH_BOT.bat
echo.
pause
