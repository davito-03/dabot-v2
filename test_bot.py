"""
Script de pruebas para verificar la funcionalidad del bot
Prueba la importación de módulos y configuración básica
"""

import sys
import os
import asyncio
from dotenv import load_dotenv

def test_imports():
    """Prueba la importación de todos los módulos"""
    print("🔍 Probando importaciones...")
    
    try:
        import nextcord
        print("✅ nextcord importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando nextcord: {e}")
        return False
    
    try:
        import yt_dlp
        print("✅ yt-dlp importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando yt-dlp: {e}")
        return False
    
    try:
        from modules.moderation import Moderation
        from modules.entertainment import Entertainment
        from modules.music import Music
        from modules.scheduled_tasks import ScheduledTasks
        from modules.help_commands import HelpCommands
        print("✅ Todos los módulos importados correctamente")
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        return False
    
    return True

def test_environment():
    """Prueba la configuración de variables de entorno"""
    print("\n🔧 Probando configuración de entorno...")
    
    load_dotenv()
    
    token = os.getenv('DISCORD_TOKEN')
    if token and token != 'your_bot_token_here':
        print("✅ Token de Discord configurado")
    else:
        print("⚠️ Token de Discord no configurado (usa 'your_bot_token_here' como placeholder)")
    
    daily_channel = os.getenv('DAILY_CHANNEL_ID')
    if daily_channel and daily_channel != 'your_channel_id_here':
        print("✅ Canal diario configurado")
    else:
        print("ℹ️ Canal diario no configurado (opcional)")
    
    return True

def test_bot_initialization():
    """Prueba la inicialización básica del bot"""
    print("\n🤖 Probando inicialización del bot...")
    
    try:
        import nextcord
        from nextcord.ext import commands
        
        # Configurar intents
        intents = nextcord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.voice_states = True
        intents.members = True
        
        # Crear bot
        bot = commands.Bot(
            command_prefix='!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        print("✅ Bot inicializado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando bot: {e}")
        return False

async def test_cogs():
    """Prueba la carga de cogs"""
    print("\n📦 Probando carga de módulos...")
    
    try:
        # Simplemente verificar que las clases se pueden importar
        from modules.moderation import Moderation
        from modules.entertainment import Entertainment
        from modules.music import Music
        from modules.scheduled_tasks import ScheduledTasks
        from modules.help_commands import HelpCommands
        
        print("✅ Módulo Moderación importado correctamente")
        print("✅ Módulo Entretenimiento importado correctamente")
        print("✅ Módulo Música importado correctamente")
        print("✅ Módulo Tareas Programadas importado correctamente")
        print("✅ Módulo Comandos de Ayuda importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de cogs: {e}")
        return False

def test_file_structure():
    """Verifica la estructura de archivos"""
    print("\n📁 Verificando estructura de archivos...")
    
    required_files = [
        'bot.py',
        'requirements.txt',
        '.env',
        'Procfile',
        'runtime.txt',
        'README.md',
        'modules/__init__.py',
        'modules/moderation.py',
        'modules/entertainment.py',
        'modules/music.py',
        'modules/scheduled_tasks.py',
        'modules/help_commands.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} (faltante)")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ Archivos faltantes: {', '.join(missing_files)}")
        return False
    
    print("\n✅ Todos los archivos necesarios están presentes")
    return True

def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL BOT DISCORD")
    print("=" * 50)
    
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("Importaciones", test_imports),
        ("Variables de entorno", test_environment),
        ("Inicialización del bot", test_bot_initialization),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    # Prueba asíncrona separada
    print(f"\n📋 Ejecutando: Carga de módulos")
    try:
        result = asyncio.run(test_cogs())
        results.append(("Carga de módulos", result))
    except Exception as e:
        print(f"❌ Error en carga de módulos: {e}")
        results.append(("Carga de módulos", False))
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✅ PASÓ" if passed_test else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if passed_test:
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📈 RESULTADO FINAL: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El bot está listo para ejecutarse.")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores antes de ejecutar el bot.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)