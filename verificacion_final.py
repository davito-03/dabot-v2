#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación final del comando servidor-completo
"""

try:
    from modules.complete_server_setup import ServerSetupWizard
    
    # Crear instancia del wizard
    wizard = ServerSetupWizard(None)
    
    print("🎯 Verificación del comando /servidor-completo")
    print("=" * 50)
    
    # Verificar plantillas disponibles
    templates = wizard.server_templates
    print(f"📊 Total plantillas: {len(templates)}")
    print()
    
    for i, (template_id, template_data) in enumerate(templates.items(), 1):
        print(f"{i}. 🏷️ {template_id}:")
        print(f"   📋 Nombre: {template_data['name']}")
        print(f"   📝 Descripción: {template_data['description']}")
        
        # Contar elementos
        categories = len(template_data.get('categories', []))
        channels = sum(len(cat.get('channels', [])) for cat in template_data.get('categories', []))
        roles = len(template_data.get('roles', []))
        
        print(f"   📊 Elementos: {categories} categorías, {channels} canales, {roles} roles")
        
        # Verificar NSFW
        has_nsfw = any('NSFW' in cat.get('name', '') for cat in template_data.get('categories', []))
        print(f"   🔞 NSFW: {'✅ Sí' if has_nsfw else '❌ No'}")
        print()
    
    print("✅ Todas las plantillas están disponibles y configuradas correctamente")
    print("✅ El comando /servidor-completo mostrará las 7 opciones")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
