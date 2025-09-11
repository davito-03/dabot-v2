@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: ========================================
:: DABOT V2 - GESTOR COMPLETO
:: Archivo de gestión integral del bot
:: Por davito - DaBot v2
:: ========================================

title DaBot v2 - Gestor Completo

:: Variables de configuración
set "BOT_DIR=%~dp0"
set "BOT_SCRIPT=bot.py"
set "PYTHON_CMD=python"
set "VENV_DIR=.venv"
set "REQUIREMENTS_FILE=requirements.txt"
set "SERVICE_NAME=DaBot_v2"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "AUTOSTART_SCRIPT=DaBot_v2_AutoStart.bat"

:: Colores (usando escape sequences para Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "MAGENTA=[95m"
set "CYAN=[96m"
set "WHITE=[97m"
set "RESET=[0m"

:MAIN_MENU
cls
echo.
echo %CYAN%╔══════════════════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%║                     🤖 DABOT V2 - GESTOR COMPLETO 🤖                 ║%RESET%
echo %CYAN%╠══════════════════════════════════════════════════════════════════════╣%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%║                        📋 OPCIONES PRINCIPALES                       ║%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%║  %WHITE%🎮 CONTROL DEL BOT:%RESET%                                              %CYAN%║%RESET%
echo %CYAN%║    %WHITE%1.%GREEN% ▶️  Iniciar Bot%RESET%                 %WHITE%2.%RED% ⏹️  Detener Bot%RESET%         %CYAN%║%RESET%
echo %CYAN%║    %WHITE%3.%YELLOW% 🔄 Reiniciar Bot%RESET%              %WHITE%4.%BLUE% 📊 Ver Estado%RESET%           %CYAN%║%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%║  %WHITE%⚙️  CONFIGURACIÓN:%RESET%                                               %CYAN%║%RESET%
echo %CYAN%║    %WHITE%5.%MAGENTA% 📦 Instalar Todo%RESET%             %WHITE%6.%CYAN% 🔑 Configurar Token%RESET%     %CYAN%║%RESET%
echo %CYAN%║    %WHITE%7.%YELLOW% 🔧 Reparar Problemas%RESET%          %WHITE%8.%BLUE% 📋 Ver Logs/Errores%RESET%     %CYAN%║%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%║  %WHITE%🏁 AUTOARRANQUE:%RESET%                                                 %CYAN%║%RESET%
echo %CYAN%║    %WHITE%9.%GREEN% ✅ Activar Autoarranque%RESET%        %WHITE%10.%RED% ❌ Desactivar%RESET%           %CYAN%║%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%║  %WHITE%🛠️  HERRAMIENTAS:%RESET%                                                %CYAN%║%RESET%
echo %CYAN%║    %WHITE%11.%BLUE% 🧪 Probar Sistema%RESET%              %WHITE%12.%GREEN% 🔍 Verificar Todo%RESET%       %CYAN%║%RESET%
echo %CYAN%║    %WHITE%13.%CYAN% 📂 Abrir Carpeta%RESET%               %WHITE%14.%CYAN% 💻 Abrir Terminal%RESET%       %CYAN%║%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%║  %WHITE%📚 AYUDA:%RESET%                                                        %CYAN%║%RESET%
echo %CYAN%║    %WHITE%15.%BLUE% 📖 Ver Documentación%RESET%           %WHITE%16.%GREEN% 🆘 Ayuda Completa%RESET%      %CYAN%║%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%║                        %WHITE%0.%RED% 🚪 Salir del Gestor%RESET%                       %CYAN%║%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%╚══════════════════════════════════════════════════════════════════════╝%RESET%
echo.

:: Mostrar estado actual del bot
call :CHECK_BOT_STATUS
if !bot_running! equ 1 (
    echo %GREEN%🟢 ESTADO ACTUAL: Bot funcionando correctamente%RESET%
) else (
    echo %RED%🔴 ESTADO ACTUAL: Bot detenido%RESET%
)

:: Verificar autoarranque
call :CHECK_AUTOSTART
if !autostart_enabled! equ 1 (
    echo %GREEN%🏁 AUTOARRANQUE: Activado (se inicia con Windows)%RESET%
) else (
    echo %YELLOW%⚠️  AUTOARRANQUE: Desactivado%RESET%
)

echo.
echo %WHITE%╔══════════════════════════════════════════════════════════════════════╗%RESET%
echo %WHITE%║  %CYAN%💡 GUÍA RÁPIDA:%RESET%                                                     %WHITE%║%RESET%
echo %WHITE%║    %YELLOW%• Primera vez?%RESET%  %WHITE%Usa opción %MAGENTA%5%WHITE% para instalar automáticamente%RESET%  %WHITE%║%RESET%
echo %WHITE%║    %YELLOW%• Configurar?%RESET%   %WHITE%Usa opción %CYAN%6%WHITE% para configurar tu token%RESET%     %WHITE%║%RESET%
echo %WHITE%║    %YELLOW%• ¿Problemas?%RESET%   %WHITE%Usa opción %YELLOW%7%WHITE% para reparar automáticamente%RESET% %WHITE%║%RESET%
echo %WHITE%║    %YELLOW%• ¿Autostart?%RESET%   %WHITE%Usa opción %GREEN%9%WHITE% para arranque automático%RESET%     %WHITE%║%RESET%
echo %WHITE%╚══════════════════════════════════════════════════════════════════════╝%RESET%
echo.

set /p "choice=%CYAN%👉 Elige una opción (0-16): %RESET%"

if "%choice%"=="1" goto START_BOT
if "%choice%"=="2" goto STOP_BOT
if "%choice%"=="3" goto RESTART_BOT
if "%choice%"=="4" goto BOT_STATUS
if "%choice%"=="5" goto INSTALL_UPDATE
if "%choice%"=="6" goto CONFIGURE_BOT
if "%choice%"=="7" goto REPAIR_DEPENDENCIES
if "%choice%"=="8" goto VIEW_LOGS
if "%choice%"=="9" goto SETUP_AUTOSTART
if "%choice%"=="10" goto DISABLE_AUTOSTART
if "%choice%"=="11" goto RUN_TESTS
if "%choice%"=="12" goto VERIFY_SYSTEM
if "%choice%"=="13" goto OPEN_FOLDER
if "%choice%"=="14" goto OPEN_CMD
if "%choice%"=="15" goto VIEW_DOCS
if "%choice%"=="16" goto SHOW_HELP
if "%choice%"=="0" goto EXIT

echo %RED%❌ Opción inválida. Escribe un número del 0 al 16.%RESET%
echo %YELLOW%💡 Sugerencia: Para empezar, prueba la opción 5 (Instalar Todo)%RESET%
pause
goto MAIN_MENU

:START_BOT
cls
echo %GREEN%🚀 Iniciando DaBot v2...%RESET%
echo.

:: Verificar si ya está ejecutándose
call :CHECK_BOT_STATUS
if !bot_running! equ 1 (
    echo %YELLOW%⚠️  El bot ya está ejecutándose%RESET%
    echo.
    pause
    goto MAIN_MENU
)

:: Verificar Python
call :CHECK_PYTHON
if !python_ok! neq 1 (
    echo %RED%❌ Python no está disponible%RESET%
    echo %BLUE%💡 Usa la opción 5 para instalar automáticamente%RESET%
    pause
    goto MAIN_MENU
)

:: Verificar token
call :CHECK_TOKEN
if !token_ok! neq 1 (
    echo %RED%❌ Token de Discord no configurado%RESET%
    echo %BLUE%💡 Usa la opción 6 para configurar el token%RESET%
    pause
    goto MAIN_MENU
)

:: Verificar archivo bot.py
if not exist "%BOT_SCRIPT%" (
    echo %RED%❌ Archivo bot.py no encontrado%RESET%
    pause
    goto MAIN_MENU
)

echo %GREEN%✅ Iniciando bot...%RESET%
start "DaBot v2" %PYTHON_CMD% "%BOT_SCRIPT%"

timeout /t 3 /nobreak > nul

call :CHECK_BOT_STATUS
if !bot_running! equ 1 (
    echo %GREEN%✅ Bot iniciado correctamente%RESET%
) else (
    echo %RED%❌ Error al iniciar el bot%RESET%
    echo %BLUE%💡 Usa la opción 8 para ver los logs de error%RESET%
)

echo.
pause
goto MAIN_MENU

:STOP_BOT
cls
echo %RED%⏹️  Deteniendo DaBot v2...%RESET%
echo.

:: Matar procesos del bot
taskkill /f /im python.exe /fi "WINDOWTITLE eq DaBot v2" > nul 2>&1
taskkill /f /im py.exe /fi "WINDOWTITLE eq DaBot v2" > nul 2>&1

:: Método alternativo: buscar por comando
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr "bot.py"') do (
    taskkill /f /pid %%i > nul 2>&1
)

timeout /t 2 /nobreak > nul

call :CHECK_BOT_STATUS
if !bot_running! equ 0 (
    echo %GREEN%✅ Bot detenido correctamente%RESET%
) else (
    echo %YELLOW%⚠️  El bot podría seguir ejecutándose%RESET%
    echo %CYAN%💡 Verifica el administrador de tareas si es necesario%RESET%
)

echo.
pause
goto MAIN_MENU

:RESTART_BOT
cls
echo %YELLOW%🔄 Reiniciando DaBot v2...%RESET%
echo.

call :STOP_BOT_SILENT
timeout /t 3 /nobreak > nul
goto START_BOT

:BOT_STATUS
cls
echo %BLUE%📊 Estado del Sistema - DaBot v2%RESET%
echo %CYAN%═══════════════════════════════════════════════════════════════════════════%RESET%
echo.

:: Estado del bot
echo %WHITE%🤖 Estado del Bot:%RESET%
call :CHECK_BOT_STATUS
if !bot_running! equ 1 (
    echo %GREEN%   ✅ Funcionando%RESET%
    for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr "bot.py"') do (
        echo %CYAN%   📝 PID: %%i%RESET%
    )
) else (
    echo %RED%   ❌ Detenido%RESET%
)

echo.

:: Estado de Python
echo %WHITE%🐍 Python:%RESET%
call :CHECK_PYTHON
if !python_ok! equ 1 (
    for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do echo %GREEN%   ✅ %%i%RESET%
) else (
    echo %RED%   ❌ No encontrado%RESET%
)

echo.

:: Estado del token
call :CHECK_TOKEN
echo %WHITE%🔑 Token de Discord:%RESET%
if !token_ok! equ 1 (
    echo %GREEN%   ✅ Configurado%RESET%
) else (
    echo %RED%   ❌ No configurado%RESET%
)

echo.

:: Estado del autoarranque
echo %WHITE%🏁 Autoarranque:%RESET%
call :CHECK_AUTOSTART
if !autostart_enabled! equ 1 (
    echo %GREEN%   ✅ Activado%RESET%
) else (
    echo %YELLOW%   ⚠️  Desactivado%RESET%
)

echo.

:: Información adicional
echo %WHITE%📂 Directorio:%RESET% %CYAN%!BOT_DIR!%RESET%
echo %WHITE%⏰ Fecha/Hora:%RESET% %CYAN%!date! !time!%RESET%

echo.
pause
goto MAIN_MENU

:: Continuar con el resto de funciones...
:INSTALL_UPDATE
cls
echo %MAGENTA%📦 Instalación y Actualización - DaBot v2%RESET%
echo.
echo %BLUE%🔄 Instalando dependencias...%RESET%
%PYTHON_CMD% -m pip install --upgrade pip
if exist "%REQUIREMENTS_FILE%" (
    %PYTHON_CMD% -m pip install -r "%REQUIREMENTS_FILE%"
) else (
    echo %YELLOW%⚠️  Archivo requirements.txt no encontrado%RESET%
    echo %BLUE%📦 Instalando dependencias básicas...%RESET%
    %PYTHON_CMD% -m pip install nextcord aiohttp python-dotenv
)

:: Crear archivo .env si no existe
if not exist ".env" (
    echo %BLUE%📄 Creando archivo .env...%RESET%
    echo DISCORD_TOKEN=TU_TOKEN_AQUI > .env
    echo PREFIX=! >> .env
    echo DAILY_CHANNEL_ID= >> .env
)

echo %GREEN%✅ Instalación completada%RESET%
pause
goto MAIN_MENU

:CONFIGURE_BOT
cls
echo %CYAN%🔧 Configuración - DaBot v2%RESET%
echo.
pause
goto MAIN_MENU

:EXIT
cls
echo.
echo %GREEN%👋 Gracias por usar DaBot v2%RESET%
echo %CYAN%🤖 ¡Hasta la próxima!%RESET%
echo.
timeout /t 2 /nobreak > nul
exit

:: ========================================
:: FUNCIONES AUXILIARES
:: ========================================

:CHECK_BOT_STATUS
set "bot_running=0"
for /f %%i in ('tasklist /fi "imagename eq python.exe" 2^>nul ^| findstr /i "python.exe" ^| find /c /v ""') do (
    if %%i gtr 0 (
        for /f "tokens=*" %%j in ('wmic process where "name='python.exe'" get commandline /value 2^>nul ^| findstr "CommandLine" ^| findstr "bot.py"') do (
            set "bot_running=1"
        )
    )
)
exit /b

:CHECK_PYTHON
set "python_ok=0"
%PYTHON_CMD% --version > nul 2>&1
if errorlevel 0 set "python_ok=1"
exit /b

:CHECK_TOKEN
set "token_ok=0"
if exist ".env" (
    for /f "usebackq tokens=2 delims==" %%a in (".env") do (
        if not "%%a"=="TU_TOKEN_AQUI" if not "%%a"=="" (
            set "token_ok=1"
        )
    )
)
exit /b

:CHECK_AUTOSTART
set "autostart_enabled=0"
if exist "%STARTUP_DIR%\%AUTOSTART_SCRIPT%" set "autostart_enabled=1"
exit /b

:STOP_BOT_SILENT
taskkill /f /im python.exe /fi "WINDOWTITLE eq DaBot v2" > nul 2>&1
taskkill /f /im py.exe /fi "WINDOWTITLE eq DaBot v2" > nul 2>&1
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv 2^>nul ^| findstr "bot.py"') do (
    taskkill /f /pid %%i > nul 2>&1
)
exit /b
