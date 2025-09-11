@echo off
setlocal enabledelayedexpansion
title DaBot v2 - Gestor Completo

:: Variables de configuración
set "BOT_DIR=%~dp0"
set "BOT_SCRIPT=bot.py"
set "PYTHON_CMD=python"
set "REQUIREMENTS_FILE=requirements.txt"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "AUTOSTART_SCRIPT=DaBot_v2_AutoStart.bat"

:MAIN_MENU
cls
echo.
echo ===============================================================================
echo                      DABOT V2 - GESTOR COMPLETO
echo ===============================================================================
echo.
echo                         OPCIONES PRINCIPALES
echo.
echo   CONTROL DEL BOT:
echo     1. Iniciar Bot                    2. Detener Bot
echo     3. Reiniciar Bot                  4. Ver Estado
echo.
echo   CONFIGURACION:
echo     5. Instalar Todo                  6. Configurar Token
echo     7. Reparar Problemas              8. Ver Logs/Errores
echo.
echo   AUTOARRANQUE:
echo     9. Activar Autoarranque          10. Desactivar
echo.
echo   HERRAMIENTAS:
echo    11. Probar Sistema                12. Verificar Todo
echo    13. Abrir Carpeta                 14. Abrir Terminal
echo.
echo   AYUDA:
echo    15. Ver Documentacion             16. Ayuda Completa
echo.
echo                         0. Salir del Gestor
echo.
echo ===============================================================================

:: Mostrar estado actual del bot
call :CHECK_BOT_STATUS
if !bot_running! equ 1 (
    echo ESTADO ACTUAL: Bot funcionando correctamente
) else (
    echo ESTADO ACTUAL: Bot detenido
)

:: Verificar autoarranque
call :CHECK_AUTOSTART
if !autostart_enabled! equ 1 (
    echo AUTOARRANQUE: Activado ^(se inicia con Windows^)
) else (
    echo AUTOARRANQUE: Desactivado
)

echo.
echo GUIA RAPIDA:
echo   - Primera vez? Usa opcion 5 para instalar automaticamente
echo   - Configurar? Usa opcion 6 para configurar tu token
echo   - Problemas? Usa opcion 7 para reparar automaticamente
echo   - Autostart? Usa opcion 9 para arranque automatico
echo.

set /p "choice=Elige una opcion (0-16): "

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

echo Opcion invalida. Escribe un numero del 0 al 16.
echo Sugerencia: Para empezar, prueba la opcion 5 ^(Instalar Todo^)
pause
goto MAIN_MENU

:START_BOT
cls
echo Iniciando DaBot v2...
echo.

:: Verificar si ya está ejecutándose
call :CHECK_BOT_STATUS
if !bot_running! equ 1 (
    echo El bot ya esta ejecutandose
    echo.
    pause
    goto MAIN_MENU
)

:: Verificar Python
call :CHECK_PYTHON
if !python_ok! neq 1 (
    echo Python no esta disponible
    echo Usa la opcion 5 para instalar automaticamente
    pause
    goto MAIN_MENU
)

:: Verificar token
call :CHECK_TOKEN
if !token_ok! neq 1 (
    echo Token de Discord no configurado
    echo Usa la opcion 6 para configurar el token
    pause
    goto MAIN_MENU
)

:: Verificar archivo bot.py
if not exist "%BOT_SCRIPT%" (
    echo Archivo bot.py no encontrado
    pause
    goto MAIN_MENU
)

echo Iniciando bot...
start "DaBot v2" %PYTHON_CMD% "%BOT_SCRIPT%"

echo Esperando conexion del bot...
timeout /t 5 /nobreak > nul

call :CHECK_BOT_STATUS
if !bot_running! equ 1 (
    echo Bot iniciado correctamente
) else (
    echo Verificando estado del bot...
    timeout /t 3 /nobreak > nul
    call :CHECK_BOT_STATUS
    if !bot_running! equ 1 (
        echo Bot iniciado correctamente ^(deteccion retrasada^)
    ) else (
        echo NOTA: El bot puede estar iniciandose en segundo plano
        echo Verifica el log con la opcion 8 para confirmar la conexion
        echo Si ves mensajes como "se ha conectado" el bot esta funcionando
    )
)

echo.
pause
goto MAIN_MENU

:STOP_BOT
cls
echo Deteniendo DaBot v2...
echo.

:: Matar procesos del bot
taskkill /f /im python.exe /fi "WINDOWTITLE eq DaBot v2" > nul 2>&1
taskkill /f /im py.exe /fi "WINDOWTITLE eq DaBot v2" > nul 2>&1

timeout /t 2 /nobreak > nul

call :CHECK_BOT_STATUS
if !bot_running! equ 0 (
    echo Bot detenido correctamente
) else (
    echo El bot podria seguir ejecutandose
    echo Verifica el administrador de tareas si es necesario
)

echo.
pause
goto MAIN_MENU

:RESTART_BOT
cls
echo Reiniciando DaBot v2...
echo.
call :STOP_BOT_SILENT
timeout /t 3 /nobreak > nul
goto START_BOT

:BOT_STATUS
cls
echo Estado del Sistema - DaBot v2
echo ===============================================================================
echo.

:: Estado del bot
echo Estado del Bot:
call :CHECK_BOT_STATUS
if !bot_running! equ 1 (
    echo    Funcionando
    
    :: Mostrar información adicional si el bot está funcionando
    echo.
    echo Informacion adicional:
    for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv 2^>nul ^| findstr "bot.py"') do (
        echo    PID del proceso: %%i
    )
    
    :: Verificar conectividad reciente
    if exist "bot.log" (
        echo    Ultimo log actualizado:
        for /f "tokens=*" %%i in ('powershell -Command "(Get-Item 'bot.log').LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss')"') do echo      %%i
        
        echo    Estado de conexion ^(ultimas 3 lineas^):
        powershell -Command "Get-Content bot.log -Tail 3 | ForEach-Object { '      ' + $_ }"
    )
) else (
    echo    Detenido o no detectado
    echo.
    echo    NOTA: Si acabas de iniciar el bot, puede tomar unos segundos
    echo    en ser detectado. Verifica el log con la opcion 8.
)

echo.

:: Estado de Python
echo Python:
call :CHECK_PYTHON
if !python_ok! equ 1 (
    for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do echo    %%i
) else (
    echo    No encontrado
)

echo.

:: Estado del token
call :CHECK_TOKEN
echo Token de Discord:
if !token_ok! equ 1 (
    echo    Configurado
) else (
    echo    No configurado
)

echo.

:: Estado del autoarranque
echo Autoarranque:
call :CHECK_AUTOSTART
if !autostart_enabled! equ 1 (
    echo    Activado
) else (
    echo    Desactivado
)

echo.
pause
goto MAIN_MENU

:INSTALL_UPDATE
cls
echo Instalacion y Actualizacion - DaBot v2
echo.
echo Instalando dependencias...
%PYTHON_CMD% -m pip install --upgrade pip
if exist "%REQUIREMENTS_FILE%" (
    %PYTHON_CMD% -m pip install -r "%REQUIREMENTS_FILE%"
) else (
    echo Archivo requirements.txt no encontrado
    echo Instalando dependencias basicas...
    %PYTHON_CMD% -m pip install nextcord aiohttp python-dotenv
)

:: Crear archivo .env si no existe
if not exist ".env" (
    echo Creando archivo .env...
    echo DISCORD_TOKEN=TU_TOKEN_AQUI > .env
    echo PREFIX=! >> .env
    echo DAILY_CHANNEL_ID= >> .env
)

echo Instalacion completada
pause
goto MAIN_MENU

:CONFIGURE_BOT
cls
echo Configuracion - DaBot v2
echo.
echo Esta funcion permite configurar el token del bot.
echo.
set /p "new_token=Introduce tu token de Discord: "
if "%new_token%"=="" (
    echo Token vacio, cancelando...
    pause
    goto MAIN_MENU
)

powershell -Command "(Get-Content .env) | ForEach-Object { $_ -replace '^DISCORD_TOKEN=.*', 'DISCORD_TOKEN=%new_token%' } | Set-Content .env"
echo Token configurado correctamente
pause
goto MAIN_MENU

:REPAIR_DEPENDENCIES
cls
echo Reparando Dependencias
echo.
echo Reinstalando dependencias...
%PYTHON_CMD% -m pip install --upgrade pip
%PYTHON_CMD% -m pip install --upgrade nextcord aiohttp python-dotenv
echo Reparacion completada
pause
goto MAIN_MENU

:VIEW_LOGS
cls
echo Ver Logs/Errores
echo.
if exist "bot.log" (
    echo Mostrando ultimas lineas del log:
    powershell -Command "Get-Content bot.log -Tail 20"
) else (
    echo No se encontro archivo bot.log
)
echo.
pause
goto MAIN_MENU

:SETUP_AUTOSTART
cls
echo Configurando Autoarranque
echo.
set "autostart_path=%STARTUP_DIR%\%AUTOSTART_SCRIPT%"
echo @echo off > "%autostart_path%"
echo timeout /t 30 /nobreak ^> nul >> "%autostart_path%"
echo cd /d "%BOT_DIR%" >> "%autostart_path%"
echo start "" %PYTHON_CMD% "%BOT_SCRIPT%" >> "%autostart_path%"
echo Autoarranque configurado
pause
goto MAIN_MENU

:DISABLE_AUTOSTART
cls
echo Desactivando Autoarranque
echo.
if exist "%STARTUP_DIR%\%AUTOSTART_SCRIPT%" (
    del "%STARTUP_DIR%\%AUTOSTART_SCRIPT%"
    echo Autoarranque desactivado
) else (
    echo Autoarranque no estaba activado
)
pause
goto MAIN_MENU

:RUN_TESTS
cls
echo Ejecutando Pruebas del Sistema
echo.
if exist "test_bot.py" (
    echo Ejecutando tests del bot...
    %PYTHON_CMD% test_bot.py
) else (
    echo No se encontro test_bot.py
)
pause
goto MAIN_MENU

:VERIFY_SYSTEM
cls
echo Verificacion Completa del Sistema
echo.
echo Verificando Python...
call :CHECK_PYTHON
if !python_ok! equ 1 (
    echo    Python encontrado
) else (
    echo    Python no encontrado
)

echo Verificando token...
call :CHECK_TOKEN
if !token_ok! equ 1 (
    echo    Token configurado
) else (
    echo    Token no configurado
)
pause
goto MAIN_MENU

:OPEN_FOLDER
start "" "%BOT_DIR%"
goto MAIN_MENU

:OPEN_CMD
start "" cmd /k "cd /d %BOT_DIR%"
goto MAIN_MENU

:VIEW_DOCS
cls
echo Documentacion
echo.
echo DaBot v2 - Bot de Discord
echo.
echo Comandos basicos:
echo - !ping - Verificar conexion
echo - !help - Ayuda completa
pause
goto MAIN_MENU

:SHOW_HELP
cls
echo Ayuda Completa - DaBot v2
echo.
echo OPCIONES IMPORTANTES:
echo.
echo OPCION 1 - INICIAR BOT:
echo    - Inicia el bot de Discord
echo    - Requiere tener token configurado
echo.
echo OPCION 5 - INSTALAR TODO:
echo    - Instala todas las dependencias
echo    - USALA PRIMERO si es tu primera vez
echo.
echo OPCION 6 - CONFIGURAR TOKEN:
echo    - Configura tu token de Discord
echo    - Obten el token en: discord.com/developers/applications
pause
goto MAIN_MENU

:EXIT
cls
echo.
echo Gracias por usar DaBot v2
echo Hasta la proxima!
echo.
timeout /t 2 /nobreak > nul
exit

:: ========================================
:: FUNCIONES AUXILIARES
:: ========================================

:CHECK_BOT_STATUS
set "bot_running=0"

:: Método 1: Buscar procesos de Python ejecutando bot.py
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv 2^>nul ^| findstr /v "PID"') do (
    for /f "tokens=*" %%j in ('wmic process where "ProcessId=%%~i" get commandline /value 2^>nul ^| findstr "CommandLine" ^| findstr "bot.py"') do (
        set "bot_running=1"
    )
)

:: Método 2: Verificar si hay un archivo de proceso activo (si existe)
if exist "bot.pid" (
    for /f %%i in (bot.pid) do (
        tasklist /fi "PID eq %%i" 2>nul | findstr "%%i" >nul
        if !errorlevel! equ 0 set "bot_running=1"
    )
)

:: Método 3: Verificar logs recientes (última hora)
if exist "bot.log" (
    powershell -Command "if ((Get-Date) - (Get-Item 'bot.log').LastWriteTime).TotalMinutes -lt 60 { exit 0 } else { exit 1 }" 2>nul
    if !errorlevel! equ 0 set "bot_running=1"
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
exit /b
