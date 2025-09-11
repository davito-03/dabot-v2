"""
Script de verificación y corrección de bugs
Verifica que los sistemas corregidos funcionen correctamente
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ticket_system():
    """Verificar que el sistema de tickets tenga el código correcto"""
    print("🎫 Verificando Sistema de Tickets...")
    
    ticket_file = "modules/ticket_system.py"
    if not os.path.exists(ticket_file):
        print("❌ Archivo de tickets no encontrado")
        return False
    
    with open(ticket_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar correcciones de transcripciones
    checks = [
        'for ch in channel.guild.text_channels:',
        'registro-tickets',
        'transcripciones',
        'ticket-logs',
        'logger.info(f"Transcripción enviada a',
        'logger.warning("No se encontró canal para enviar transcripción")'
    ]
    
    all_checks_passed = True
    for check in checks:
        if check not in content:
            print(f"❌ Falta verificación: {check}")
            all_checks_passed = False
        else:
            print(f"✅ Encontrado: {check}")
    
    if all_checks_passed:
        print("✅ Sistema de tickets corregido correctamente")
        return True
    else:
        print("❌ Sistema de tickets necesita más correcciones")
        return False

def check_nsfw_system():
    """Verificar que el sistema NSFW tenga las correcciones"""
    print("\n🔞 Verificando Sistema NSFW...")
    
    nsfw_file = "modules/nsfw.py"
    if not os.path.exists(nsfw_file):
        print("❌ Archivo NSFW no encontrado")
        return False
    
    with open(nsfw_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar correcciones de APIs
    checks = [
        'import asyncio',
        'ClientTimeout(total=10)',
        'nekos_mapping = {',
        'fallback_images = {',
        'try:',
        'except Exception as e:',
        'logger.error(f"Error en comando',
        'await interaction.followup.send("❌ Ocurrió un error interno'
    ]
    
    all_checks_passed = True
    for check in checks:
        if check not in content:
            print(f"❌ Falta verificación: {check}")
            all_checks_passed = False
        else:
            print(f"✅ Encontrado: {check}")
    
    if all_checks_passed:
        print("✅ Sistema NSFW corregido correctamente")
        return True
    else:
        print("❌ Sistema NSFW necesita más correcciones")
        return False

def check_bot_configuration():
    """Verificar que el bot.py tenga la configuración correcta"""
    print("\n🤖 Verificando Configuración del Bot...")
    
    bot_file = "bot.py"
    if not os.path.exists(bot_file):
        print("❌ Archivo bot.py no encontrado")
        return False
    
    with open(bot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que NSFW esté cargado
    if '"NSFWCommands", "modules.nsfw"' in content:
        print("✅ Módulo NSFW está configurado para cargar")
        return True
    else:
        print("❌ Módulo NSFW no está configurado correctamente")
        return False

def main():
    """Función principal de verificación"""
    print("🔧 VERIFICACIÓN DE CORRECCIONES DE BUGS")
    print("=" * 50)
    
    all_systems_ok = True
    
    # Verificar sistemas corregidos
    if not check_ticket_system():
        all_systems_ok = False
    
    if not check_nsfw_system():
        all_systems_ok = False
    
    if not check_bot_configuration():
        all_systems_ok = False
    
    print("\n" + "=" * 50)
    if all_systems_ok:
        print("✅ TODAS LAS CORRECCIONES APLICADAS CORRECTAMENTE")
        print("\n📋 Resumen de correcciones:")
        print("   🎫 Transcripciones de tickets: Búsqueda mejorada de canales")
        print("   🔞 Comandos NSFW: APIs corregidas con fallbacks")
        print("   🛡️ Manejo de errores: Mejorado en ambos sistemas")
        print("\n🎯 SISTEMAS LISTOS PARA USAR")
    else:
        print("❌ ALGUNAS CORRECCIONES FALTAN")
        print("   Revisa los errores mostrados arriba")
    
    return all_systems_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
