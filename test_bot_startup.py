#!/usr/bin/env python3
"""
Script de prueba para verificar el arranque del bot paso a paso
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configurar logging para debug
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_bot_startup():
    """probar arranque del bot paso a paso"""
    print("🧪 Probando arranque del bot paso a paso...")
    
    # 1. Verificar variables de entorno
    print("1️⃣ Cargando variables de entorno...")
    load_dotenv()
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Token de Discord no encontrado")
        return False
    
    print("✅ Token encontrado")
    
    # 2. Importar nextcord
    print("2️⃣ Importando nextcord...")
    try:
        import nextcord
        print("✅ Nextcord importado")
    except Exception as e:
        print(f"❌ Error importando nextcord: {e}")
        return False
    
    # 3. Crear bot básico
    print("3️⃣ Creando bot básico...")
    try:
        from bot import DiscordBot
        bot = DiscordBot()
        print("✅ Bot creado")
    except Exception as e:
        print(f"❌ Error creando bot: {e}")
        return False
    
    # 4. Probar carga de módulos uno por uno
    print("4️⃣ Probando carga de módulos...")
    modules_to_test = [
        ("HelpSystem", "modules.help_system"),
        ("EmojiManager", "modules.emoji_manager"), 
        ("StickerManager", "modules.sticker_manager")
    ]
    
    for name, module_path in modules_to_test:
        try:
            print(f"   📦 Cargando {name}...")
            bot.load_extension(module_path)
            print(f"   ✅ {name} cargado")
        except Exception as e:
            print(f"   ❌ Error cargando {name}: {e}")
            return False
    
    print("🎉 Todos los tests pasaron!")
    print("El bot debería arrancar correctamente ahora.")
    return True

if __name__ == "__main__":
    success = test_bot_startup()
    if not success:
        sys.exit(1)
