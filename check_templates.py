#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar plantillas disponibles
"""

import sys
sys.path.append('.')

try:
    from modules.complete_server_setup import ServerSetupWizard
    
    # Crear instancia sin bot
    wizard = ServerSetupWizard(None)
    
    print("🎯 Plantillas disponibles actualmente:")
    print("=" * 50)
    
    for template_id, template_data in wizard.server_templates.items():
        print(f"✅ {template_id}: {template_data['name']}")
        print(f"   Descripción: {template_data['description']}")
        
        # Verificar si tiene NSFW
        has_nsfw = False
        for category in template_data.get('categories', []):
            if 'NSFW' in category.get('name', ''):
                has_nsfw = True
                break
        
        print(f"   NSFW: {'✅ Sí' if has_nsfw else '❌ No'}")
        print()
    
    print(f"📊 Total de plantillas: {len(wizard.server_templates)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
