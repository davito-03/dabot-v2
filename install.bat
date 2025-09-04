@echo off
echo 🤖 Instalando DaBot v2 - Bot Multipropósito para Discord
echo ========================================================

REM Verificar Python
echo 📋 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no encontrado. Instala Python 3.8+ primero.
    pause
    exit /b 1
)

REM Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv .venv

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call .venv\Scripts\activate.bat

REM Instalar dependencias
echo 📚 Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Verificar instalación
echo 🧪 Ejecutando pruebas...
python test_bot.py

echo.
echo 🎉 ¡Instalación completada!
echo.
echo 📝 Próximos pasos:
echo 1. Configura tu token de Discord en el archivo .env
echo 2. Invita el bot a tu servidor con los permisos necesarios
echo 3. Ejecuta: python bot.py
echo.
echo 📖 Para más información, consulta README.md
pause