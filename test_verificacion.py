"""
Script de verificación para DABOT V2
Verifica que todos los módulos y funcionalidades estén correctamente implementados
"""

import sys
import os
import sqlite3

def check_modules():
    """Verifica que todos los módulos existen"""
    print("🔍 Verificando módulos...")
    
    required_modules = [
        "modules/nsfw.py",
        "modules/server_manager.py", 
        "modules/advanced_config.py",
        "modules/bot_config.py",
        "modules/config_manager.py"
    ]
    
    for module in required_modules:
        if os.path.exists(module):
            print(f"  ✅ {module}")
        else:
            print(f"  ❌ {module} - FALTA")
    
    print()

def check_database():
    """Verifica la estructura de la base de datos"""
    print("🗄️ Verificando base de datos...")
    
    if not os.path.exists("data"):
        print("  ❌ Directorio 'data' no existe")
        return
    
    print("  ✅ Directorio 'data' existe")
    
    # Crear base de datos temporal para verificar estructura
    try:
        from modules.server_manager import ServerConfigDB
        db = ServerConfigDB("data/test.db")
        
        # Verificar tablas
        with sqlite3.connect("data/test.db") as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['server_configs', 'server_channels', 'server_roles', 'server_settings']
            
            for table in expected_tables:
                if table in tables:
                    print(f"  ✅ Tabla '{table}' creada")
                else:
                    print(f"  ❌ Tabla '{table}' falta")
        
        # Limpiar archivo de test
        os.remove("data/test.db")
        
    except Exception as e:
        print(f"  ❌ Error verificando base de datos: {e}")
    
    print()

def check_nsfw_commands():
    """Verifica que los comandos NSFW estén implementados"""
    print("🔞 Verificando comandos NSFW...")
    
    try:
        with open("modules/nsfw.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        expected_commands = [
            'name="waifu"',
            'name="neko"', 
            'name="nekotina"',
            'name="trap"',
            'name="ahegao"',
            'name="yuri"',
            'name="blowjob"',
            'name="hentai"',
            'name="nsfw-random"'
        ]
        
        for cmd in expected_commands:
            if cmd in content:
                print(f"  ✅ Comando {cmd}")
            else:
                print(f"  ❌ Comando {cmd} - FALTA")
                
    except Exception as e:
        print(f"  ❌ Error verificando comandos NSFW: {e}")
    
    print()

def check_config_commands():
    """Verifica que los comandos de configuración estén implementados"""
    print("⚙️ Verificando comandos de configuración...")
    
    config_files = {
        "modules/advanced_config.py": [
            'name="serverconfig"',
            'subcommand(name="channels"',
            'subcommand(name="roles"',
            'subcommand(name="settings"',
            'subcommand(name="automod"',
            'subcommand(name="view"',
            'subcommand(name="reset"'
        ],
        "modules/server_manager.py": [
            'name="setup"',
            'auto_detect_channels',
            'auto_detect_roles',
            'send_welcome_message'
        ]
    }
    
    for file_path, commands in config_files.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print(f"  📁 {file_path}:")
            for cmd in commands:
                if cmd in content:
                    print(f"    ✅ {cmd}")
                else:
                    print(f"    ❌ {cmd} - FALTA")
                    
        except Exception as e:
            print(f"  ❌ Error verificando {file_path}: {e}")
    
    print()

def check_bot_integration():
    """Verifica que los módulos estén integrados en bot.py"""
    print("🤖 Verificando integración en bot.py...")
    
    try:
        with open("bot.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        expected_integrations = [
            'ServerManager',
            'AdvancedConfig', 
            'NSFWCommands',
            'modules.server_manager',
            'modules.advanced_config',
            'modules.nsfw'
        ]
        
        for integration in expected_integrations:
            if integration in content:
                print(f"  ✅ {integration}")
            else:
                print(f"  ❌ {integration} - FALTA")
                
    except Exception as e:
        print(f"  ❌ Error verificando bot.py: {e}")
    
    print()

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN DE DABOT V2 - NUEVAS FUNCIONALIDADES")
    print("=" * 60)
    print()
    
    check_modules()
    check_database()
    check_nsfw_commands()
    check_config_commands()
    check_bot_integration()
    
    print("✅ Verificación completada!")
    print("\n🚀 Para probar el bot:")
    print("1. Ejecuta: python bot.py")
    print("2. Añade el bot a un servidor de test")
    print("3. Usa /setup para configuración automática")
    print("4. Prueba /serverconfig para configuración avanzada")
    print("5. En un canal NSFW, prueba /nekotina")

if __name__ == "__main__":
    main()
