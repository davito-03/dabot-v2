#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para añadir las funcionalidades completas que estaban en la versión anterior
"""

import re

def add_nsfw_to_templates():
    """Añadir categorías NSFW a las plantillas existentes"""
    
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

    # Buscar la sección VOICE CHANNELS y añadir NSFW antes
    pattern = r'(\s+{\s+"name": "🔊 VOICE CHANNELS")'
    matches = list(re.finditer(pattern, content))
    
    new_content = content
    offset = 0
    
    for match in reversed(matches):
        insertion_point = match.start() + offset
        new_content = (new_content[:insertion_point] + 
                      nsfw_category + '\n                    ' + 
                      new_content[insertion_point:])
        offset += len(nsfw_category) + len('\n                    ')
        print("✅ NSFW añadido antes de VOICE CHANNELS")
    
    if new_content != content:
        with open('modules/complete_server_setup.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Categorías NSFW añadidas correctamente")
        return True
    else:
        print("❌ No se pudieron añadir las categorías NSFW")
        return False

def add_missing_templates():
    """Añadir las plantillas que faltan"""
    
    with open('modules/complete_server_setup.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Buscar el final de las plantillas existentes (después de gaming)
    end_pattern = r'(\s+}\s+},\s+\"gaming\"[\s\S]*?}\s+},)'
    match = re.search(end_pattern, content)
    
    if not match:
        print("❌ No se encontró el final de las plantillas existentes")
        return False
    
    # Plantillas adicionales para añadir
    additional_templates = '''
            "development": {
                "name": "💻 Servidor Development",
                "description": "Configuración para comunidades de desarrolladores",
                "categories": [
                    {
                        "name": "🛡️ STAFF",
                        "channels": [
                            {"name": "👮┃staff-chat", "type": "text", "topic": "Chat privado del staff", "staff_only": True},
                            {"name": "🤖┃comandos-staff", "type": "text", "topic": "Comandos exclusivos del staff", "staff_only": True},
                            {"name": "📋┃moderación", "type": "text", "topic": "Panel de moderación", "staff_only": True},
                            {"name": "🔧 Staff Voice", "type": "voice", "limit": 5, "staff_only": True}
                        ]
                    },
                    {
                        "name": "📋 INFORMACIÓN",
                        "channels": [
                            {"name": "👋┃bienvenida", "type": "text", "topic": "¡Bienvenidos developers!"},
                            {"name": "📖┃reglas", "type": "text", "topic": "Normas de la comunidad {guild_name}"},
                            {"name": "📢┃anuncios", "type": "text", "topic": "Anuncios y actualizaciones"},
                            {"name": "📈┃level-ups", "type": "text", "topic": "Anuncios de subida de nivel"},
                            {"name": "📊┃estadísticas", "type": "text", "topic": "Estadísticas del servidor"}
                        ]
                    },
                    {
                        "name": "💬 GENERAL",
                        "channels": [
                            {"name": "💬┃chat-general", "type": "text", "topic": "Chat general"},
                            {"name": "💻┃dev-talk", "type": "text", "topic": "Habla sobre desarrollo"},
                            {"name": "📚┃recursos", "type": "text", "topic": "Comparte recursos útiles"},
                            {"name": "🐛┃debugging", "type": "text", "topic": "Ayuda con bugs y problemas"},
                            {"name": "💡┃ideas", "type": "text", "topic": "Comparte tus ideas"},
                            {"name": "🤖┃bot-commands", "type": "text", "topic": "Comandos del bot"}
                        ]
                    },
                    {
                        "name": "⚙️ DESARROLLO",
                        "channels": [
                            {"name": "🌐┃web-dev", "type": "text", "topic": "Desarrollo web"},
                            {"name": "📱┃mobile-dev", "type": "text", "topic": "Desarrollo móvil"},
                            {"name": "🎮┃game-dev", "type": "text", "topic": "Desarrollo de juegos"},
                            {"name": "🤖┃bot-dev", "type": "text", "topic": "Desarrollo de bots"},
                            {"name": "💾┃databases", "type": "text", "topic": "Bases de datos"},
                            {"name": "🔐┃security", "type": "text", "topic": "Seguridad y criptografía"}
                        ]
                    },
                    {
                        "name": "🔞 NSFW",
                        "channels": [
                            {"name": "🔞┃nsfw-general", "type": "text", "topic": "Contenido NSFW general", "nsfw": True},
                            {"name": "🍑┃nsfw-images", "type": "text", "topic": "Imágenes NSFW", "nsfw": True},
                            {"name": "💕┃nsfw-chat", "type": "text", "topic": "Chat NSFW", "nsfw": True}
                        ]
                    },
                    {
                        "name": "🎫 SOPORTE",
                        "channels": [
                            {"name": "🎫┃crear-ticket", "type": "text", "topic": "Crea un ticket de soporte aquí"},
                            {"name": "📋┃información-tickets", "type": "text", "topic": "Información sobre el sistema de tickets"}
                        ]
                    },
                    {
                        "name": "🔊 VOICE",
                        "channels": [
                            {"name": "🎤┃panel-voicemaster", "type": "text", "topic": "Panel de control de VoiceMaster", "voice_master_panel": True},
                            {"name": "🎤 General", "type": "voice", "limit": 0},
                            {"name": "💻 Coding Session 1", "type": "voice", "limit": 4},
                            {"name": "💻 Coding Session 2", "type": "voice", "limit": 4},
                            {"name": "📹 Screen Share", "type": "voice", "limit": 8},
                            {"name": "🔒 Privado", "type": "voice", "limit": 2},
                            {"name": "➕ Crear Canal", "type": "voice", "limit": 1, "voice_master": True}
                        ]
                    },
                    {
                        "name": "📊 LOGS",
                        "channels": [
                            {"name": "🎫┃registro-tickets", "type": "text", "topic": "Registro de tickets del servidor", "staff_only": True},
                            {"name": "🚪┃entradas-salidas", "type": "text", "topic": "Log de usuarios entrando/saliendo", "staff_only": True},
                            {"name": "💬┃mensajes-logs", "type": "text", "topic": "Log de mensajes editados/eliminados", "staff_only": True},
                            {"name": "🤖┃acciones-bot", "type": "text", "topic": "Log de acciones y sanciones del bot", "staff_only": True},
                            {"name": "🔊┃voice-logs", "type": "text", "topic": "Log de entradas/salidas de voice", "staff_only": True}
                        ]
                    }
                ],
                "roles": [
                    {"name": "👑 Owner", "color": 0xff0000, "permissions": ["administrator"], "hoist": True},
                    {"name": "🛡️ Admin", "color": 0xff6b6b, "permissions": ["manage_guild", "manage_channels", "manage_roles"], "hoist": True},
                    {"name": "🔨 Moderador", "color": 0x4ecdc4, "permissions": ["manage_messages", "kick_members", "mute_members"], "hoist": True},
                    {"name": "💻 Senior Dev", "color": 0xf1c40f, "permissions": [], "hoist": True},
                    {"name": "⚡ Developer", "color": 0x3498db, "permissions": [], "hoist": False},
                    {"name": "🌱 Junior Dev", "color": 0x2ecc71, "permissions": [], "hoist": False},
                    {"name": "👤 Miembro", "color": 0x95a5a6, "permissions": [], "hoist": False}
                ],
                "settings": {
                    "verification": True,
                    "default_notifications": False,
                    "welcome_channel": "👋┃bienvenida",
                    "rules_channel": "📖┃reglas",
                    "level_up_channel": "📈┃level-ups"
                }
            },'''
    
    # Insertar las nuevas plantillas después del cierre de gaming
    insertion_point = match.end()
    new_content = content[:insertion_point] + additional_templates + content[insertion_point:]
    
    with open('modules/complete_server_setup.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Plantilla 'development' añadida correctamente")
    return True

if __name__ == "__main__":
    print("🚀 Iniciando actualización del sistema de plantillas...")
    
    # Paso 1: Añadir categorías NSFW a las plantillas existentes
    print("\n📝 Paso 1: Añadiendo categorías NSFW...")
    add_nsfw_to_templates()
    
    # Paso 2: Añadir plantillas faltantes
    print("\n📝 Paso 2: Añadiendo plantillas faltantes...")
    add_missing_templates()
    
    print("\n✅ Actualización completada!")
