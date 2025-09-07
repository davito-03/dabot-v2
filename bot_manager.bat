@echo off
chcp 65001 >nul
title DABOT V2 - Gestor de Bot
color 0A

:MENU
cls
echo.
echo ████████████████████████████████████████████████████████████
echo ██                                                        ██
echo ██                    🤖 DABOT V2 MANAGER                ██
echo ██                                                        ██
echo ████████████████████████████████████████████████████████████
echo.
echo [1] 🚀 INICIAR BOT
echo [2] 🔴 DETENER BOT  
echo [3] 🔄 REINICIAR BOT
echo [4] 📊 ESTADO DEL BOT
echo [5] 📝 VER LOGS
echo [6] 🔧 INSTALAR DEPENDENCIAS
echo [7] 🧹 LIMPIAR LOGS
echo [8] ❌ SALIR
echo.
echo ████████████████████████████████████████████████████████████
echo.

set /p choice="Selecciona una opción (1-8): "

if "%choice%"=="1" goto START_BOT
if "%choice%"=="2" goto STOP_BOT
if "%choice%"=="3" goto RESTART_BOT
if "%choice%"=="4" goto STATUS_BOT
if "%choice%"=="5" goto VIEW_LOGS
if "%choice%"=="6" goto INSTALL_DEPS
if "%choice%"=="7" goto CLEAN_LOGS
if "%choice%"=="8" goto EXIT

echo.
echo ❌ Opción inválida. Presiona cualquier tecla para continuar...
pause >nul
goto MENU

:START_BOT
cls
echo.
echo 🚀 Iniciando DABOT V2...
echo.

:: Verificar si ya está ejecutándose
tasklist | find /i "python.exe" | find /i "bot.py" >nul
if %errorlevel% equ 0 (
    echo ⚠️  El bot ya está ejecutándose.
    echo.
    echo ¿Deseas reiniciarlo? (S/N):
    set /p restart_choice=">>> "
    if /i "%restart_choice%"=="S" goto RESTART_BOT
    goto MENU_RETURN
)

:: Verificar que existe el archivo bot.py
if not exist "bot.py" (
    echo ❌ Error: No se encontró bot.py
    echo    Asegúrate de ejecutar este script desde la carpeta del bot.
    goto MENU_RETURN
)

:: Verificar que existe el archivo .env
if not exist ".env" (
    echo ❌ Error: No se encontró el archivo .env
    echo    Crea el archivo .env con tu token de Discord.
    echo.
    echo    Ejemplo de contenido para .env:
    echo    DISCORD_TOKEN=tu_token_aqui
    goto MENU_RETURN
)

:: Iniciar el bot en segundo plano
echo ✅ Iniciando bot en segundo plano...
start /min "DABOT V2" python bot.py

:: Esperar un momento para verificar si se inició correctamente
timeout /t 3 /nobreak >nul

:: Verificar si se está ejecutando
tasklist | find /i "python.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ Bot iniciado correctamente!
    echo 📊 El bot está ejecutándose en segundo plano.
    echo 📝 Para ver logs en tiempo real, usa la opción [5] del menú.
) else (
    echo ❌ Error al iniciar el bot.
    echo 💡 Verifica los logs para más detalles.
)

goto MENU_RETURN

:STOP_BOT
cls
echo.
echo 🔴 Deteniendo DABOT V2...
echo.

:: Buscar y matar procesos de Python que ejecuten bot.py
for /f "tokens=2" %%i in ('tasklist ^| find /i "python.exe"') do (
    wmic process where "ProcessId=%%i and CommandLine like '%%bot.py%%'" delete >nul 2>&1
)

:: Método alternativo usando taskkill
taskkill /f /im python.exe /fi "WINDOWTITLE eq DABOT V2" >nul 2>&1

echo ✅ Bot detenido correctamente.
goto MENU_RETURN

:RESTART_BOT
cls
echo.
echo 🔄 Reiniciando DABOT V2...
echo.

:: Detener el bot primero
echo 🔴 Deteniendo bot actual...
for /f "tokens=2" %%i in ('tasklist ^| find /i "python.exe"') do (
    wmic process where "ProcessId=%%i and CommandLine like '%%bot.py%%'" delete >nul 2>&1
)
taskkill /f /im python.exe /fi "WINDOWTITLE eq DABOT V2" >nul 2>&1

:: Esperar un momento
echo ⏳ Esperando 3 segundos...
timeout /t 3 /nobreak >nul

:: Iniciar nuevamente
echo 🚀 Iniciando bot nuevamente...
start /min "DABOT V2" python bot.py

timeout /t 3 /nobreak >nul

tasklist | find /i "python.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ Bot reiniciado correctamente!
) else (
    echo ❌ Error al reiniciar el bot.
)

goto MENU_RETURN

:STATUS_BOT
cls
echo.
echo 📊 Estado del DABOT V2
echo.
echo ████████████████████████████████████████████████████████████

:: Verificar si está ejecutándose
tasklist | find /i "python.exe" | find /i "bot.py" >nul
if %errorlevel% equ 0 (
    echo 🟢 Estado: EJECUTÁNDOSE
    echo.
    echo 📋 Procesos activos:
    tasklist | find /i "python.exe"
) else (
    echo 🔴 Estado: DETENIDO
)

echo.
echo 📂 Archivos importantes:
if exist "bot.py" (echo ✅ bot.py - OK) else (echo ❌ bot.py - NO ENCONTRADO)
if exist ".env" (echo ✅ .env - OK) else (echo ❌ .env - NO ENCONTRADO)
if exist "requirements.txt" (echo ✅ requirements.txt - OK) else (echo ❌ requirements.txt - NO ENCONTRADO)

echo.
echo 📁 Carpetas de datos:
if exist "data" (echo ✅ data/ - OK) else (echo ⚠️  data/ - NO ENCONTRADA)
if exist "modules" (echo ✅ modules/ - OK) else (echo ❌ modules/ - NO ENCONTRADA)

echo ████████████████████████████████████████████████████████████
goto MENU_RETURN

:VIEW_LOGS
cls
echo.
echo 📝 Visualizando logs del bot...
echo.
echo Presiona Ctrl+C para volver al menú principal
echo ████████████████████████████████████████████████████████████
echo.

if exist "bot.log" (
    type bot.log
) else (
    echo ⚠️  No se encontraron logs del bot.
    echo    Los logs aparecerán aquí cuando el bot esté ejecutándose.
)

echo.
echo ████████████████████████████████████████████████████████████
goto MENU_RETURN

:INSTALL_DEPS
cls
echo.
echo 🔧 Instalando dependencias...
echo.

if not exist "requirements.txt" (
    echo ❌ Error: No se encontró requirements.txt
    goto MENU_RETURN
)

echo 📦 Instalando paquetes de Python...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo ✅ Dependencias instaladas correctamente!
) else (
    echo ❌ Error al instalar dependencias.
    echo 💡 Verifica tu conexión a internet y que Python esté instalado.
)

goto MENU_RETURN

:CLEAN_LOGS
cls
echo.
echo 🧹 Limpiando logs...
echo.

if exist "bot.log" (
    del "bot.log"
    echo ✅ Logs limpiados correctamente.
) else (
    echo ⚠️  No se encontraron logs para limpiar.
)

if exist "data\*.log" (
    del "data\*.log" >nul 2>&1
    echo ✅ Logs de la carpeta data limpiados.
)

goto MENU_RETURN

:MENU_RETURN
echo.
echo Presiona cualquier tecla para volver al menú principal...
pause >nul
goto MENU

:EXIT
cls
echo.
echo 👋 ¡Gracias por usar DABOT V2 Manager!
echo.
echo    Desarrollado por davito
echo    Bot: DABOT V2
echo.
timeout /t 2 /nobreak >nul
exit /b 0
