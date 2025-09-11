#!/bin/bash

# DaBot v2 - Script de Deploy a GitHub
# Este script automatiza la subida del proyecto a GitHub

echo "🚀 DaBot v2 - Deploy a GitHub"
echo "================================"

# Verificar si estamos en un repositorio Git
if [ ! -d ".git" ]; then
    echo "❌ Error: No estás en un repositorio Git"
    echo "💡 Ejecuta: git init"
    exit 1
fi

# Verificar si hay cambios para commit
if [ -z "$(git status --porcelain)" ]; then
    echo "ℹ️  No hay cambios para subir"
    exit 0
fi

echo "📋 Verificando archivos..."

# Verificar archivos importantes
if [ ! -f "README.md" ]; then
    echo "❌ Error: README.md no encontrado"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt no encontrado"
    exit 1
fi

if [ ! -f ".gitignore" ]; then
    echo "❌ Error: .gitignore no encontrado"
    exit 1
fi

if [ ! -f "bot.py" ]; then
    echo "❌ Error: bot.py no encontrado"
    exit 1
fi

echo "✅ Archivos verificados"

# Añadir todos los archivos
echo "📦 Añadiendo archivos al repositorio..."
git add .

# Verificar si el archivo .env fue excluido
if git ls-files --cached | grep -q "^\.env$"; then
    echo "⚠️  ADVERTENCIA: archivo .env detectado en el repositorio"
    echo "🔒 Esto puede exponer tu token de Discord"
    echo "❓ ¿Continuar de todos modos? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "🛑 Deploy cancelado por seguridad"
        git reset
        exit 1
    fi
fi

# Crear commit
echo "💬 Creando commit..."
COMMIT_MESSAGE="📚 Actualización completa de documentación

✨ Características agregadas:
- 📖 README.md completo y profesional
- 🔒 .gitignore mejorado para seguridad
- 📄 Licencia MIT agregada
- ⚙️ Configuración de ejemplo (.env.example)
- 🌐 Configuración para Render (render.yaml)
- 🐳 Soporte para Docker (si está presente)

🎯 El proyecto está listo para deploy en Render y uso público
🔧 Incluye gestor automático para Windows
🎮 Sistema completo con 8 módulos principales

Desarrollado por davito-03"

git commit -m "$COMMIT_MESSAGE"

if [ $? -eq 0 ]; then
    echo "✅ Commit creado exitosamente"
else
    echo "❌ Error al crear commit"
    exit 1
fi

# Verificar si existe un remote origin
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ Error: No hay un repositorio remoto configurado"
    echo "💡 Configura el repositorio remoto con:"
    echo "   git remote add origin https://github.com/tu_usuario/dabot-v2.git"
    exit 1
fi

# Obtener información del repositorio
REPO_URL=$(git remote get-url origin)
BRANCH=$(git branch --show-current)

echo "🌐 Repositorio: $REPO_URL"
echo "🌿 Rama: $BRANCH"

# Subir cambios
echo "⬆️  Subiendo cambios a GitHub..."
git push origin "$BRANCH"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 ¡Deploy completado exitosamente!"
    echo "=================================="
    echo ""
    echo "📊 Resumen:"
    echo "✅ Archivos subidos a GitHub"
    echo "✅ README.md actualizado"
    echo "✅ Configuración de seguridad aplicada"
    echo "✅ Listo para deploy en Render"
    echo ""
    echo "🔗 Enlaces útiles:"
    echo "📖 Repositorio: $REPO_URL"
    echo "🌐 Deploy en Render: https://render.com"
    echo "📚 Documentación: Revisa el README.md"
    echo ""
    echo "🚀 Próximos pasos:"
    echo "1. Ve a Render.com y conecta tu repositorio"
    echo "2. Configura las variables de entorno"
    echo "3. ¡Disfruta tu bot 24/7 en la nube!"
    echo ""
    echo "⭐ Si te gusta el proyecto, dale una estrella en GitHub!"
else
    echo "❌ Error al subir cambios"
    echo "💡 Verifica tu conexión y permisos del repositorio"
    exit 1
fi
