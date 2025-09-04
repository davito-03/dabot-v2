@echo off
echo ====================================
echo      DABOT V2 - MODO LOCAL
echo ====================================
echo.
echo Iniciando bot en modo local...
echo Dashboard estara disponible en:
echo http://localhost:8080
echo.
echo Presiona Ctrl+C para detener el bot
echo.

cd /d "%~dp0"
python bot.py

pause
