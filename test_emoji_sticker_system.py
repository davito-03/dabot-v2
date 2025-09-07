#!/usr/bin/env python3
"""
Script de prueba para verificar los nuevos módulos de emojis y stickers
"""

import sys
import importlib.util

def test_module_import(module_name, file_path):
    """probar importación de módulo"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {module_name}: Importación exitosa")
        
        # Verificar que tiene la función setup
        if hasattr(module, 'setup'):
            print(f"✅ {module_name}: Función setup encontrada")
        else:
            print(f"❌ {module_name}: Función setup NO encontrada")
            
        return True
    except Exception as e:
        print(f"❌ {module_name}: Error de importación - {e}")
        return False

def main():
    """función principal de pruebas"""
    print("🧪 Probando nuevos módulos de Dabot v2...")
    print("=" * 50)
    
    modules_to_test = [
        ("EmojiManager", "modules/emoji_manager.py"),
        ("StickerManager", "modules/sticker_manager.py"),
        ("HelpSystem", "modules/help_system.py")
    ]
    
    all_passed = True
    
    for module_name, file_path in modules_to_test:
        success = test_module_import(module_name, file_path)
        if not success:
            all_passed = False
        print()
    
    print("=" * 50)
    if all_passed:
        print("🎉 Todos los módulos pasaron las pruebas!")
        print("\n📋 Funcionalidades añadidas:")
        print("• Sistema de gestión de emojis con packs temáticos")
        print("• Sistema de gestión de stickers personalizados")
        print("• Búsqueda de contenido popular en internet")
        print("• Integración completa con el sistema de ayuda")
        print("\n🎯 Comandos principales:")
        print("• /emoji add - Añadir emojis desde URL")
        print("• /emoji pack - Instalar packs de emojis")
        print("• /sticker add - Añadir stickers personalizados")
        print("• /sticker search - Buscar stickers populares")
        print("• /help categoria:emojis - Ver ayuda completa")
    else:
        print("❌ Algunos módulos fallaron las pruebas")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
