@echo off
chcp 65001 > nul
title DaBot v2 - Instalador Rápido

:: Colores
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "WHITE=[97m"
set "RESET=[0m"

cls
echo.
echo %CYAN%╔══════════════════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%║                    🤖 DABOT V2 - INSTALADOR RÁPIDO 🤖                ║%RESET%
echo %CYAN%╠══════════════════════════════════════════════════════════════════════╣%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%║  %WHITE%Este instalador configurará automáticamente DaBot v2 en tu PC%CYAN%    ║%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%║  %GREEN%✅ Instala Python si no está disponible%CYAN%                       ║%RESET%
echo %CYAN%║  %GREEN%✅ Configura entorno virtual%CYAN%                                  ║%RESET%
echo %CYAN%║  %GREEN%✅ Instala todas las dependencias%CYAN%                             ║%RESET%
echo %CYAN%║  %GREEN%✅ Configura autoarranque opcional%CYAN%                            ║%RESET%
echo %CYAN%║  %GREEN%✅ Crea acceso directo en escritorio%CYAN%                          ║%RESET%
echo %CYAN%║                                                                      ║%RESET%
echo %CYAN%╚══════════════════════════════════════════════════════════════════════╝%RESET%
echo.

echo %YELLOW%⚠️  ANTES DE CONTINUAR:%RESET%
echo %WHITE%   • Asegúrate de tener tu token de Discord listo%RESET%
echo %WHITE%   • Cierra cualquier antivirus temporalmente%RESET%
echo %WHITE%   • Ejecuta como administrador si es necesario%RESET%
echo.

set /p "continue=¿Continuar con la instalación? (s/n): "
if /i not "%continue%"=="s" exit

echo.
echo %BLUE%🚀 Iniciando instalación automática...%RESET%
echo.

:: Verificar Python
echo %BLUE%🐍 Verificando Python...%RESET%
python --version > nul 2>&1
if errorlevel 1 (
    echo %YELLOW%⚠️  Python no encontrado. Descargando...%RESET%
    
    :: Descargar Python usando PowerShell
    powershell -Command "& {
        $url = 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe'
        $output = 'python_installer.exe'
        Write-Host 'Descargando Python 3.11.5...' -ForegroundColor Cyan
        Invoke-WebRequest -Uri $url -OutFile $output
        Write-Host 'Ejecutando instalador de Python...' -ForegroundColor Cyan
        Start-Process -FilePath $output -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait
        Remove-Item $output -Force
    }"
    
    :: Verificar instalación
    timeout /t 5 /nobreak > nul
    python --version > nul 2>&1
    if errorlevel 1 (
        echo %RED%❌ Error instalando Python%RESET%
        echo %YELLOW%💡 Instala Python manualmente desde https://python.org%RESET%
        pause
        exit
    )
    echo %GREEN%✅ Python instalado correctamente%RESET%
) else (
    echo %GREEN%✅ Python ya está instalado%RESET%
)

:: Crear entorno virtual
echo %BLUE%📦 Configurando entorno virtual...%RESET%
if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo %RED%❌ Error creando entorno virtual%RESET%
        pause
        exit
    )
)
echo %GREEN%✅ Entorno virtual configurado%RESET%

:: Activar entorno virtual
call ".venv\Scripts\activate.bat"

:: Actualizar pip
echo %BLUE%🔄 Actualizando pip...%RESET%
python -m pip install --upgrade pip > nul 2>&1

:: Instalar dependencias
echo %BLUE%📋 Instalando dependencias...%RESET%
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    python -m pip install nextcord aiohttp python-dotenv
)

if errorlevel 1 (
    echo %RED%❌ Error instalando dependencias%RESET%
    pause
    exit
)
echo %GREEN%✅ Dependencias instaladas%RESET%

:: Crear archivo .env
echo %BLUE%📝 Configurando archivo de configuración...%RESET%
if not exist ".env" (
    (
        echo DISCORD_TOKEN=TU_TOKEN_AQUI
        echo PREFIX=!
        echo DAILY_CHANNEL_ID=
    ) > .env
)
echo %GREEN%✅ Archivo de configuración creado%RESET%

:: Configurar token
echo.
echo %CYAN%🔑 CONFIGURACIÓN DEL TOKEN DE DISCORD%RESET%
echo %YELLOW%════════════════════════════════════════════════%RESET%
echo.
echo %WHITE%Para obtener tu token:%RESET%
echo %CYAN%1. Ve a https://discord.com/developers/applications%RESET%
echo %CYAN%2. Crea una nueva aplicación%RESET%
echo %CYAN%3. Ve a la sección "Bot" y crea un bot%RESET%
echo %CYAN%4. Copia el token (botón "Copy")%RESET%
echo.
echo %RED%⚠️  NUNCA compartas tu token con nadie%RESET%
echo.

set /p "token=Pega tu token de Discord aquí: "

if not "%token%"=="" (
    powershell -Command "(Get-Content .env) | ForEach-Object { $_ -replace '^DISCORD_TOKEN=.*', 'DISCORD_TOKEN=%token%' } | Set-Content .env"
    echo %GREEN%✅ Token configurado correctamente%RESET%
) else (
    echo %YELLOW%⚠️  Token no configurado. Hazlo más tarde con el gestor%RESET%
)

:: Crear acceso directo en escritorio
echo %BLUE%🖥️  Creando acceso directo...%RESET%
set "desktop=%USERPROFILE%\Desktop"
set "shortcut_path=%desktop%\DaBot v2 Gestor.lnk"

powershell -Command "& {
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('%shortcut_path%')
    $Shortcut.TargetPath = '%cd%\gestor_dabot.bat'
    $Shortcut.WorkingDirectory = '%cd%'
    $Shortcut.IconLocation = 'shell32.dll,25'
    $Shortcut.Description = 'DaBot v2 - Gestor Completo'
    $Shortcut.Save()
}"

if exist "%shortcut_path%" (
    echo %GREEN%✅ Acceso directo creado en el escritorio%RESET%
) else (
    echo %YELLOW%⚠️  No se pudo crear el acceso directo%RESET%
)

:: Preguntar por autoarranque
echo.
echo %CYAN%🏁 CONFIGURACIÓN DE AUTOARRANQUE%RESET%
echo %YELLOW%═════════════════════════════════════════%RESET%
echo.
set /p "autostart=¿Quieres que el bot se inicie automáticamente con Windows? (s/n): "

if /i "%autostart%"=="s" (
    echo %BLUE%🔧 Configurando autoarranque...%RESET%
    
    set "startup_dir=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
    set "autostart_script=!startup_dir!\DaBot_v2_AutoStart.bat"
    
    (
        echo @echo off
        echo title DaBot v2 - Autoarranque
        echo cd /d "%cd%"
        echo timeout /t 30 /nobreak ^> nul
        echo :CHECK_INTERNET
        echo ping -n 1 8.8.8.8 ^> nul
        echo if errorlevel 1 ^(
        echo     timeout /t 10 /nobreak ^> nul
        echo     goto CHECK_INTERNET
        echo ^)
        echo if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"
        echo start "DaBot v2" /min python bot.py
    ) > "!autostart_script!"
    
    echo %GREEN%✅ Autoarranque configurado%RESET%
)

:: Crear archivo de desinstalación
echo %BLUE%🗑️  Creando desinstalador...%RESET%
(
    echo @echo off
    echo title DaBot v2 - Desinstalador
    echo echo Desinstalando DaBot v2...
    echo.
    echo :: Detener bot
    echo taskkill /f /im python.exe /fi "WINDOWTITLE eq DaBot v2" ^> nul 2^>^&1
    echo.
    echo :: Eliminar autoarranque
    echo del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\DaBot_v2_AutoStart.bat" ^> nul 2^>^&1
    echo.
    echo :: Eliminar acceso directo
    echo del "%USERPROFILE%\Desktop\DaBot v2 Gestor.lnk" ^> nul 2^>^&1
    echo.
    echo :: Eliminar entorno virtual
    echo rmdir /s /q ".venv" ^> nul 2^>^&1
    echo.
    echo echo ✅ DaBot v2 desinstalado correctamente
    echo echo.
    echo echo ⚠️  Archivos de configuración mantenidos
    echo echo    ^(bot.py, .env, modules, etc.^)
    echo echo.
    echo pause
    echo del "%%~f0"
) > "desinstalar_dabot.bat"

echo %GREEN%✅ Desinstalador creado%RESET%

:: Verificar instalación
echo.
echo %BLUE%🧪 Verificando instalación...%RESET%
python -c "import nextcord; print('✅ Nextcord OK')" 2>nul || echo %RED%❌ Nextcord ERROR%RESET%
python -c "import aiohttp; print('✅ Aiohttp OK')" 2>nul || echo %RED%❌ Aiohttp ERROR%RESET%
python -c "import dotenv; print('✅ Python-dotenv OK')" 2>nul || echo %RED%❌ Python-dotenv ERROR%RESET%

:: Resumen final
echo.
echo %GREEN%╔══════════════════════════════════════════════════════════════════════╗%RESET%
echo %GREEN%║                    🎉 INSTALACIÓN COMPLETADA 🎉                     ║%RESET%
echo %GREEN%╠══════════════════════════════════════════════════════════════════════╣%RESET%
echo %GREEN%║                                                                      ║%RESET%
echo %GREEN%║  %WHITE%✅ DaBot v2 instalado correctamente%GREEN%                             ║%RESET%
echo %GREEN%║  %WHITE%✅ Entorno virtual configurado%GREEN%                                 ║%RESET%
echo %GREEN%║  %WHITE%✅ Dependencias instaladas%GREEN%                                     ║%RESET%
echo %GREEN%║  %WHITE%✅ Configuración inicial creada%GREEN%                               ║%RESET%
if exist "%shortcut_path%" echo %GREEN%║  %WHITE%✅ Acceso directo en escritorio%GREEN%                             ║%RESET%
if /i "%autostart%"=="s" echo %GREEN%║  %WHITE%✅ Autoarranque configurado%GREEN%                                  ║%RESET%
echo %GREEN%║                                                                      ║%RESET%
echo %GREEN%╚══════════════════════════════════════════════════════════════════════╝%RESET%
echo.

echo %CYAN%📋 PRÓXIMOS PASOS:%RESET%
echo %WHITE%   1. Usa el acceso directo "DaBot v2 Gestor" en tu escritorio%RESET%
echo %WHITE%   2. O ejecuta "gestor_dabot.bat" desde esta carpeta%RESET%
echo %WHITE%   3. Configura tu token si no lo hiciste (opción 6)%RESET%
echo %WHITE%   4. Inicia el bot (opción 1)%RESET%
echo.
echo %CYAN%🔗 ENLACES ÚTILES:%RESET%
echo %WHITE%   • Discord Developer Portal: https://discord.com/developers/applications%RESET%
echo %WHITE%   • Invitar bot: https://discord.com/api/oauth2/authorize?client_id=TU_ID&permissions=8&scope=bot%%20applications.commands%RESET%
echo.

set /p "open_manager=¿Abrir el gestor ahora? (s/n): "
if /i "%open_manager%"=="s" (
    start "" "gestor_dabot.bat"
) else (
    echo %GREEN%¡Gracias por instalar DaBot v2!%RESET%
    pause
)

exit
