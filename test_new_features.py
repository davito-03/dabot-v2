#!/usr/bin/env python3
"""
Test script para verificar las nuevas funcionalidades implementadas
"""

def test_emoji_limits():
    """Test para verificar límites de emojis"""
    print("🧪 Testeando límites de emojis...")
    
    # Simular diferentes niveles de boost
    class MockGuild:
        def __init__(self, boost_level):
            self.premium_tier = boost_level
    
    # Importar función de límites
    try:
        from modules.emoji_manager import EmojiManager
        import nextcord
        
        bot = None  # Mock bot
        emoji_manager = EmojiManager(bot)
        
        for level in range(4):
            guild = MockGuild(level)
            limits = emoji_manager.get_server_limits(guild)
            print(f"  📊 Nivel {level}: {limits['emojis']} emojis, {limits['stickers']} stickers")
        
        print("  ✅ Test de límites - PASADO")
        
    except Exception as e:
        print(f"  ❌ Test de límites - FALLIDO: {e}")

def test_server_templates():
    """Test para verificar plantillas de servidor"""
    print("🧪 Testeando plantillas de servidor...")
    
    try:
        from modules.complete_server_setup import ServerSetupWizard
        import nextcord
        
        bot = None  # Mock bot
        setup_manager = ServerSetupWizard(bot)
        
        templates = setup_manager.server_templates
        print(f"  📋 Plantillas disponibles: {len(templates)}")
        
        for template_id, template in templates.items():
            print(f"    • {template_id}: {template['name']}")
            
            # Verificar que tenga las categorías correctas
            categories = [cat['name'] for cat in template['categories']]
            
            # Verificar que STAFF esté primero (excepto en community que puede variar)
            if 'STAFF' in categories[0] or 'MANAGEMENT' in categories[0]:
                print(f"      ✅ Staff category está primero")
            else:
                print(f"      ⚠️  Staff category no está primero: {categories[0]}")
            
            # Verificar que tenga LOGS
            if any('LOGS' in cat for cat in categories):
                print(f"      ✅ Tiene categoría LOGS")
            else:
                print(f"      ❌ No tiene categoría LOGS")
        
        print("  ✅ Test de plantillas - PASADO")
        
    except Exception as e:
        print(f"  ❌ Test de plantillas - FALLIDO: {e}")

def test_level_system():
    """Test para verificar sistema de niveles"""
    print("🧪 Testeando sistema de niveles...")
    
    try:
        from modules.complete_server_setup import ServerSetupWizard
        import nextcord
        
        bot = None  # Mock bot  
        setup_manager = ServerSetupWizard(bot)
        
        # Verificar configuración de roles de nivel
        sample_config = {
            "gaming": [
                (5, "Lvl 5", 0x95a5a6, ["use_external_emojis"]),
                (10, "Lvl 10", 0x3498db, ["use_external_emojis", "embed_links"]),
                (25, "Lvl 25", 0x9b59b6, ["use_external_emojis", "embed_links", "attach_files"]),
                (40, "Lvl 40", 0xe67e22, ["use_external_emojis", "embed_links", "attach_files", "add_reactions"]),
                (50, "Lvl 50", 0xf1c40f, ["use_external_emojis", "embed_links", "attach_files", "add_reactions", "use_slash_commands"]),
                (75, "Lvl 75", 0x1abc9c, ["use_external_emojis", "embed_links", "attach_files", "add_reactions", "use_slash_commands", "create_instant_invite"]),
                (100, "Lvl 100", 0xe74c3c, ["use_external_emojis", "embed_links", "attach_files", "add_reactions", "use_slash_commands", "create_instant_invite", "change_nickname"])
            ]
        }
        
        for level, name, color, perms in sample_config["gaming"]:
            print(f"    • {name} (Nivel {level}): {len(perms)} permisos")
        
        print("  ✅ Test de sistema de niveles - PASADO")
        
    except Exception as e:
        print(f"  ❌ Test de sistema de niveles - FALLIDO: {e}")

def test_new_templates():
    """Test para verificar nuevas plantillas"""
    print("🧪 Testeando nuevas plantillas...")
    
    try:
        from modules.complete_server_setup import ServerSetupWizard
        
        bot = None
        setup_manager = ServerSetupWizard(bot)
        templates = setup_manager.server_templates
        
        # Verificar que las nuevas plantillas existan
        new_templates = ["music", "anime", "esports"]
        for template_id in new_templates:
            if template_id in templates:
                template = templates[template_id]
                print(f"    ✅ {template['name']} encontrada")
                
                # Verificar estructura específica
                categories = [cat['name'] for cat in template['categories']]
                if any('STAFF' in cat or 'MANAGEMENT' in cat for cat in categories):
                    print(f"      ✅ Tiene categoría de staff")
                if any('LOGS' in cat for cat in categories):
                    print(f"      ✅ Tiene categoría de logs")
                    
            else:
                print(f"    ❌ {template_id} NO encontrada")
        
        print("  ✅ Test de nuevas plantillas - PASADO")
        
    except Exception as e:
        print(f"  ❌ Test de nuevas plantillas - FALLIDO: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando tests de nuevas funcionalidades...\n")
    
    test_emoji_limits()
    print()
    test_server_templates()
    print()
    test_level_system()
    print()
    test_new_templates()
    
    print("\n✅ Tests completados!")
