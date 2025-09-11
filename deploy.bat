@echo off
setlocal enabledelayedexpansion
title DaBot v2 - Deploy a GitHub

echo.
echo ===============================================================================
echo                    🚀 DABOT V2 - DEPLOY A GITHUB
echo ===============================================================================
echo.

:: Verificar si estamos en un repositorio Git
if not exist ".git" (
    echo ❌ Error: No estas en un repositorio Git
    echo 💡 Ejecuta: git init
    pause
    exit /b 1
)

:: Verificar archivos importantes
echo 📋 Verificando archivos...

if not exist "README.md" (
    echo ❌ Error: README.md no encontrado
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ❌ Error: requirements.txt no encontrado
    pause
    exit /b 1
)

if not exist ".gitignore" (
    echo ❌ Error: .gitignore no encontrado
    pause
    exit /b 1
)

if not exist "bot.py" (
    echo ❌ Error: bot.py no encontrado
    pause
    exit /b 1
)

echo ✅ Archivos verificados

:: Verificar estado de Git
for /f %%i in ('git status --porcelain 2^>nul ^| find /c /v ""') do set changes=%%i
if !changes! equ 0 (
    echo ℹ️  No hay cambios para subir
    pause
    exit /b 0
)

echo.
echo 📦 Añadiendo archivos al repositorio...
git add .

:: Verificar si .env está en el repositorio (peligroso)
git ls-files --cached | findstr "^\.env$" > nul 2>&1
if !errorlevel! equ 0 (
    echo.
    echo ⚠️  ADVERTENCIA: archivo .env detectado en el repositorio
    echo 🔒 Esto puede exponer tu token de Discord
    echo.
    set /p "response=❓ ¿Continuar de todos modos? (y/N): "
    if /i not "!response!"=="y" (
        echo 🛑 Deploy cancelado por seguridad
        git reset
        pause
        exit /b 1
    )
)

echo.
echo 💬 Creando commit...

:: Crear mensaje de commit detallado
set "commit_msg=📚 Actualización completa de documentación"
set "commit_body=✨ Características agregadas:^

- 📖 README.md completo y profesional^
- 🔒 .gitignore mejorado para seguridad^
- 📄 Licencia MIT agregada^
- ⚙️ Configuración de ejemplo (.env.example)^
- 🌐 Configuración para Render (render.yaml)^
- 🛠️ Scripts de deploy automatizado^

🎯 El proyecto está listo para deploy en Render y uso público^
🔧 Incluye gestor automático para Windows^
🎮 Sistema completo con 8 módulos principales^

Desarrollado por davito-03"

git commit -m "%commit_msg%" -m "%commit_body%"

if !errorlevel! neq 0 (
    echo ❌ Error al crear commit
    pause
    exit /b 1
)

echo ✅ Commit creado exitosamente

:: Verificar remote origin
git remote get-url origin > nul 2>&1
if !errorlevel! neq 0 (
    echo.
    echo ❌ Error: No hay un repositorio remoto configurado
    echo 💡 Configura el repositorio remoto con:
    echo    git remote add origin https://github.com/tu_usuario/dabot-v2.git
    pause
    exit /b 1
)

:: Obtener información del repositorio
for /f "tokens=*" %%i in ('git remote get-url origin') do set repo_url=%%i
for /f "tokens=*" %%i in ('git branch --show-current') do set branch=%%i

echo.
echo 🌐 Repositorio: !repo_url!
echo 🌿 Rama: !branch!

echo.
echo ⬆️  Subiendo cambios a GitHub...
git push origin !branch!

if !errorlevel! equ 0 (
    echo.
    echo ===============================================================================
    echo                       🎉 ¡DEPLOY COMPLETADO EXITOSAMENTE!
    echo ===============================================================================
    echo.
    echo 📊 Resumen:
    echo ✅ Archivos subidos a GitHub
    echo ✅ README.md actualizado con documentación completa
    echo ✅ Configuración de seguridad aplicada
    echo ✅ Listo para deploy en Render
    echo.
    echo 🔗 Enlaces útiles:
    echo 📖 Repositorio: !repo_url!
    echo 🌐 Deploy en Render: https://render.com
    echo 📚 Documentación: Revisa el README.md
    echo.
    echo 🚀 Próximos pasos:
    echo 1. Ve a Render.com y conecta tu repositorio
    echo 2. Configura las variables de entorno ^(especialmente DISCORD_TOKEN^)
    echo 3. ¡Disfruta tu bot 24/7 en la nube!
    echo.
    echo 💡 Características del proyecto subido:
    echo   • 🎮 Sistema de entretenimiento con pesca
    echo   • 💰 Economía completa con tienda
    echo   • 🔨 Moderación avanzada
    echo   • 🎵 Sistema de música
    echo   • 🎫 Tickets con transcripciones
    echo   • 🌐 Dashboard web integrado
    echo   • 🔒 Seguridad y protecciones
    echo   • 🛠️ Gestor automático para Windows
    echo.
    echo ⭐ Si te gusta el proyecto, dale una estrella en GitHub!
    echo.
) else (
    echo ❌ Error al subir cambios
    echo 💡 Verifica tu conexión y permisos del repositorio
)

echo.
pause
