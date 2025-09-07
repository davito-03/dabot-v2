@echo off
title DaBot v2 - Detener Bot
color 0C
cd /d "%~dp0"

echo.
echo ===============================================
echo           🛑 DETENIENDO DABOT V2 🛑
echo ===============================================
echo.

:: Buscar y terminar procesos Python
echo [1/3] Buscando procesos del bot...
tasklist /FI "IMAGENAME eq python.exe" | findstr python.exe >nul
if errorlevel 1 (
    echo [INFO] ℹ️ No hay procesos Python ejecutándose
) else (
    echo [ENCONTRADO] 🔍 Procesos Python detectados
    echo [ACCION] 🚫 Terminando procesos...
    taskkill /F /IM python.exe /T >nul 2>&1
    echo [OK] ✅ Procesos terminados
)

:: Verificar procesos pythonw (modo ventana)
echo [2/3] Verificando procesos en segundo plano...
tasklist /FI "IMAGENAME eq pythonw.exe" | findstr pythonw.exe >nul
if errorlevel 1 (
    echo [INFO] ℹ️ No hay procesos pythonw ejecutándose
) else (
    echo [ENCONTRADO] 🔍 Procesos pythonw detectados
    echo [ACCION] 🚫 Terminando procesos pythonw...
    taskkill /F /IM pythonw.exe /T >nul 2>&1
    echo [OK] ✅ Procesos pythonw terminados
)

:: Liberar puertos (si el bot usa dashboard web)
echo [3/3] Liberando puertos...
netstat -ano | findstr :8080 | findstr LISTENING >nul
if errorlevel 1 (
    echo [INFO] ℹ️ Puerto 8080 libre
) else (
    echo [ENCONTRADO] 🔍 Puerto 8080 en uso
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    echo [OK] ✅ Puerto liberado
)

:: Verificación final
echo.
timeout /t 2 /nobreak >nul
tasklist /FI "IMAGENAME eq python.exe" | findstr python.exe >nul
if errorlevel 1 (
    echo ===============================================
    echo           ✅ BOT DETENIDO EXITOSAMENTE
    echo ===============================================
) else (
    echo ===============================================
    echo      ⚠️ ALGUNOS PROCESOS AÚN EJECUTÁNDOSE
    echo ===============================================
    echo [INFO] Puede que necesites reiniciar manualmente
)

echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
