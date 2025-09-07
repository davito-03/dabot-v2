#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para añadir categorías NSFW correctamente a todas las plantillas
"""

import re
import json

# Leer el archivo
with open('modules/complete_server_setup.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Lista de plantillas que necesitan NSFW
templates = ['streamer', 'gaming', 'development', 'community', 'music', 'anime', 'esports']

# Definir la categoría NSFW
nsfw_category_text = '''                    {
                        "name": "🔞 NSFW",
                        "channels": [
                            {"name": "🔞┃nsfw-general", "type": "text", "topic": "Contenido NSFW general", "nsfw": True},
                            {"name": "🍑┃nsfw-images", "type": "text", "topic": "Imágenes NSFW", "nsfw": True},
                            {"name": "💕┃nsfw-chat", "type": "text", "topic": "Chat NSFW", "nsfw": True}
                        ]
                    },'''

new_content = content
changes_made = 0

# Para cada plantilla, buscar la ubicación correcta para insertar NSFW
for template in templates:
    print(f"Procesando plantilla: {template}")
    
    # Buscar el patrón específico para cada plantilla: ECONOMÍA seguida de CASINO
    pattern = rf'("{template}": {{.*?"name": "[^"]*ECONOMÍA[^"]*",.*?"channels": \[.*?\].*?}},)\s*({{.*?"name": "[^"]*CASINO[^"]*",)'
    
    # Buscar la coincidencia usando DOTALL para incluir saltos de línea
    match = re.search(pattern, new_content, re.DOTALL)
    
    if match:
        # Verificar si NSFW ya existe antes de CASINO
        before_casino = new_content[match.start():match.end()]
        if "🔞 NSFW" not in before_casino:
            # Insertar NSFW entre ECONOMÍA y CASINO
            replacement = match.group(1) + '\n' + nsfw_category_text + '\n                    ' + match.group(2)
            new_content = new_content[:match.start()] + replacement + new_content[match.end():]
            changes_made += 1
            print(f"✅ NSFW añadido a {template}")
        else:
            print(f"⚠️ NSFW ya existe en {template}")
    else:
        print(f"❌ No se encontró patrón ECONOMÍA->CASINO en {template}")

print(f"\n📊 Resumen: {changes_made} cambios realizados")

# Escribir el archivo solo si hay cambios
if changes_made > 0:
    with open('modules/complete_server_setup.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("✅ Archivo actualizado exitosamente")
else:
    print("❌ No se realizaron cambios")
