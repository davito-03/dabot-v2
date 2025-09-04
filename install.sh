#!/bin/bash

# Script de instalación para DaBot v2
echo "🤖 Instalando DaBot v2 - Bot Multipropósito para Discord"
echo "========================================================"

# Verificar Python
echo "📋 Verificando Python..."
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python no encontrado. Instala Python 3.8+ primero."
    exit 1
fi

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python -m venv .venv

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalación
echo "🧪 Ejecutando pruebas..."
python test_bot.py

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📝 Próximos pasos:"
echo "1. Configura tu token de Discord en el archivo .env"
echo "2. Invita el bot a tu servidor con los permisos necesarios"
echo "3. Ejecuta: python bot.py"
echo ""
echo "📖 Para más información, consulta README.md"
