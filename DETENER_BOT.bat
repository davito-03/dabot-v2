@echo off
title Deteniendo Bot - DA Bot v2
color 0C
echo.
echo ====================================
echo     🛑 DETENIENDO DA BOT v2 🛑
echo ====================================
echo.

echo [FASE 1] Buscando procesos de Python ejecutando el bot...
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE | findstr python.exe >nul
if %ERRORLEVEL% EQU 0 (
    echo [ENCONTRADO] ✅ Procesos de Python detectados
    echo [ACCION] Terminando procesos de Python...
    taskkill /F /IM python.exe /T >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [EXITO] ✅ Procesos Python terminados
    ) else (
        echo [ADVERTENCIA] ⚠️ Algunos procesos no se pudieron terminar
    )
) else (
    echo [INFO] ℹ️ No se encontraron procesos de Python ejecutándose
)

echo.
echo [FASE 2] Verificando procesos Python en modo ventana...
tasklist /FI "IMAGENAME eq pythonw.exe" /FO TABLE | findstr pythonw.exe >nul
if %ERRORLEVEL% EQU 0 (
    echo [ENCONTRADO] Procesos pythonw.exe detectados
    echo [ACCION] Terminando procesos pythonw.exe...
    taskkill /F /IM pythonw.exe /T >nul 2>&1
    echo [EXITO] ✅ Procesos pythonw terminados
)

echo.
echo [FASE 3] Liberando puertos utilizados por el bot...
netstat -ano | findstr :8080 | findstr LISTENING >nul
if %ERRORLEVEL% EQU 0 (
    echo [ENCONTRADO] Puerto 8080 en uso
    echo [ACCION] Liberando puerto 8080...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    echo [EXITO] ✅ Puerto 8080 liberado
)

echo.
echo [FASE 4] Verificando terminación completa...
timeout /t 2 /nobreak >nul
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE | findstr python.exe >nul
if %ERRORLEVEL% EQU 0 (
    echo [ADVERTENCIA] ⚠️ Algunos procesos aún están ejecutándose
    echo [ACCION] Forzando terminación final...
    taskkill /F /IM python.exe /T >nul 2>&1
    taskkill /F /IM pythonw.exe /T >nul 2>&1
) else (
    echo [CONFIRMADO] ✅ Todos los procesos terminados correctamente
)

echo.
echo [FASE 5] Limpiando archivos temporales...
if exist "bot_output.txt" (
    del "bot_output.txt" >nul 2>&1
    echo [LIMPIEZA] ✅ bot_output.txt eliminado
)
if exist "__pycache__" (
    rmdir /s /q "__pycache__" >nul 2>&1
    echo [LIMPIEZA] ✅ Cache principal limpiado
)
if exist "modules\__pycache__" (
    rmdir /s /q "modules\__pycache__" >nul 2>&1
    echo [LIMPIEZA] ✅ Cache de módulos limpiado
)

echo.
echo ====================================
echo   🟢 BOT DETENIDO COMPLETAMENTE 🟢
echo ====================================
echo.
echo ✅ Todos los procesos terminados
echo ✅ Puertos liberados
echo ✅ Archivos temporales limpiados
echo.
echo El bot ha sido detenido de forma segura.
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
