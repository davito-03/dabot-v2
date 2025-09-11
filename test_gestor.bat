@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

:: Definir colores
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
echo %CYAN%╚══════════════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %RED%🔴 ESTADO ACTUAL: Bot detenido%RESET%
echo.
echo %WHITE%╔══════════════════════════════════════════════════════════════════════╗%RESET%
echo %WHITE%║  %CYAN%💡 GUÍA RÁPIDA:%RESET%                                                     %WHITE%║%RESET%
echo %WHITE%║    %YELLOW%• Primera vez?%RESET%  %WHITE%Usa opción %MAGENTA%5%WHITE% para instalar automáticamente%RESET%  %WHITE%║%RESET%
echo %WHITE%╚══════════════════════════════════════════════════════════════════════╝%RESET%
echo.

set /p "choice=%CYAN%👉 Elige una opción (0-5): %RESET%"

if "%choice%"=="0" goto EXIT
echo %RED%Opción inválida%RESET%
pause
goto MAIN_MENU

:EXIT
echo %GREEN%¡Hasta luego!%RESET%
pause
exit /b 0
