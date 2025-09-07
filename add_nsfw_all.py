#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para añadir categorías NSFW a todas las plantillas que no las tengan
"""

import re

def add_nsfw_to_all_templates():
    """Añadir NSFW a todas las plantillas que no lo tengan"""
    
    with open('modules/complete_server_setup.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Categoría NSFW para insertar
    nsfw_category = '''                    {
                        "name": "🔞 NSFW",
                        "channels": [
                            {"name": "🔞┃nsfw-general", "type": "text", "topic": "Contenido NSFW general", "nsfw": True},
                            {"name": "🍑┃nsfw-images", "type": "text", "topic": "Imágenes NSFW", "nsfw": True},
                            {"name": "💕┃nsfw-chat", "type": "text", "topic": "Chat NSFW", "nsfw": True}
                        ]
                    },'''

    # Plantillas que necesitan NSFW (todas excepto gaming que ya lo tiene)
    templates_to_fix = ['streamer', 'development', 'community', 'music', 'anime', 'esports']
    
    new_content = content
    changes_made = 0
    
    for template in templates_to_fix:
        print(f"Procesando plantilla: {template}")
        
        # Buscar la sección de VOICE CHANNELS en cada plantilla
        # Patrón: encontrar VOICE CHANNELS que no tenga NSFW antes
        pattern = rf'("{template}":.*?)((\s+{{\s+"name":\s+"[^"]*VOICE[^"]*"))'
        
        match = re.search(pattern, new_content, re.DOTALL)
        
        if match:
            # Verificar si ya tiene NSFW antes de VOICE
            before_voice = match.group(1)
            if "🔞 NSFW" not in before_voice:
                # Insertar NSFW antes de VOICE CHANNELS
                replacement = match.group(1) + nsfw_category + '\n                    ' + match.group(2)
                new_content = new_content[:match.start()] + replacement + new_content[match.end():]
                changes_made += 1
                print(f"✅ NSFW añadido a {template}")
            else:
                print(f"⚠️ NSFW ya existe en {template}")
        else:
            print(f"❌ No se encontró sección VOICE en {template}")
    
    print(f"\n📊 Resumen: {changes_made} cambios realizados")
    
    # Escribir archivo solo si hay cambios
    if changes_made > 0:
        with open('modules/complete_server_setup.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Archivo actualizado exitosamente")
        return True
    else:
        print("❌ No se realizaron cambios")
        return False

if __name__ == "__main__":
    print("🚀 Añadiendo categorías NSFW a todas las plantillas...")
    add_nsfw_to_all_templates()
