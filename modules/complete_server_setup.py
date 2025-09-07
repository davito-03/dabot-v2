"""
Sistema de auto-configuración completa para servidores
Crea automáticamente canales, categorías, roles y configuraciones según el tipo de servidor
Incluye: reglas automáticas, sistema de niveles, moderación integrada
Por: Davito
"""

import logging
import nextcord
from nextcord.ext import commands
from typing import Dict, List, Optional, Any
import asyncio
import sqlite3
from modules.server_manager import ServerConfigDB

logger = logging.getLogger(__name__)

class ServerSetupWizard(commands.Cog):
    """Sistema completo de configuración automática de servidores"""
    
    def __init__(self, bot):
        self.bot = bot
        # Inicializar sistemas integrados
        self.setup_integrated_systems()
        
    def setup_integrated_systems(self):
        """Configurar sistemas integrados"""
        try:
            from .auto_rules import AutoRules
            from .advanced_levels import AdvancedLevelSystem 
            from .integrated_moderation import IntegratedModeration
            from .destructive_commands import DestructiveCommands
            
            self.auto_rules = AutoRules(self.bot)
            self.level_system = AdvancedLevelSystem(self.bot)
            self.moderation = IntegratedModeration(self.bot)
            self.destructive = DestructiveCommands(self.bot)
            
            logger.info("✅ Sistemas integrados inicializados correctamente")
        except Exception as e:
            logger.error(f"❌ Error inicializando sistemas integrados: {e}")
            # Sistemas básicos como fallback
            self.auto_rules = None
            self.level_system = None
            self.moderation = None
            self.destructive = None
        self.db = ServerConfigDB()
        
        # Plantillas de configuración por tipo de servidor
        self.server_templates = {
            "streamer": {
                "name": "🎮 Comunidad de Streamer",
                "description": "Configuración perfecta para la comunidad de un streamer",
                "categories": [
                    {
                        "name": "📋 INFORMACIÓN",
                        "channels": [
                            {"name": "👋┃bienvenida", "type": "text", "topic": "¡Bienvenidos a la comunidad!"},
                            {"name": "📖┃reglas", "type": "text", "topic": "Normas del servidor"},
                            {"name": "📢┃anuncios", "type": "text", "topic": "Anuncios importantes"},
                            {"name": "🎉┃eventos", "type": "text", "topic": "Eventos y sorteos"}
                        ]
                    },
                    {
                        "name": "💬 CHAT GENERAL",
                        "channels": [
                            {"name": "💬┃general", "type": "text", "topic": "Chat general de la comunidad"},
                            {"name": "🔗┃links-y-clips", "type": "text", "topic": "Comparte clips y links del stream"},
                            {"name": "🎨┃fanart", "type": "text", "topic": "Arte creado por la comunidad"},
                            {"name": "🤖┃comandos-bot", "type": "text", "topic": "Usa comandos del bot aquí"}
                        ]
                    },
                    {
                        "name": "🎮 GAMING",
                        "channels": [
                            {"name": "🎮┃gaming-general", "type": "text", "topic": "Habla sobre juegos"},
                            {"name": "🎯┃buscar-team", "type": "text", "topic": "Busca compañeros de juego"},
                            {"name": "🏆┃logros", "type": "text", "topic": "Comparte tus logros"}
                        ]
                    },
                    {
                        "name": "🔊 VOZ",
                        "channels": [
                            {"name": "🎤 Lobby", "type": "voice", "limit": 0},
                            {"name": "🎮 Gaming 1", "type": "voice", "limit": 4},
                            {"name": "🎮 Gaming 2", "type": "voice", "limit": 4},
                            {"name": "🔒 Privado", "type": "voice", "limit": 2},
                            {"name": "📺 Viendo Stream", "type": "voice", "limit": 10}
                        ]
                    },
                    {
                        "name": "🛠️ STAFF",
                        "channels": [
                            {"name": "👮┃staff-chat", "type": "text", "topic": "Chat privado del staff", "staff_only": True},
                            {"name": "📊┃logs", "type": "text", "topic": "Logs de moderación", "staff_only": True},
                            {"name": "🎫┃tickets", "type": "text", "topic": "Sistema de tickets"},
                            {"name": "🔧 Staff Voice", "type": "voice", "limit": 5, "staff_only": True}
                        ]
                    }
                ],
                "roles": [
                    {"name": "👑 Owner", "color": 0xff0000, "permissions": ["administrator"], "hoist": True},
                    {"name": "🛡️ Admin", "color": 0xff6b6b, "permissions": ["manage_guild", "manage_channels", "manage_roles"], "hoist": True},
                    {"name": "🔨 Moderador", "color": 0x4ecdc4, "permissions": ["manage_messages", "kick_members", "mute_members"], "hoist": True},
                    {"name": "🎤 VIP", "color": 0xf1c40f, "permissions": [], "hoist": True},
                    {"name": "⭐ Suscriptor", "color": 0x9b59b6, "permissions": [], "hoist": False},
                    {"name": "🎮 Gamer", "color": 0x3498db, "permissions": [], "hoist": False},
                    {"name": "🎨 Artista", "color": 0xe67e22, "permissions": [], "hoist": False},
                    {"name": "🔇 Silenciado", "color": 0x95a5a6, "permissions": [], "hoist": False}
                ]
            },
            
            "gaming": {
                "name": "🎮 Servidor Gaming",
                "description": "Configuración para servidor de gaming general",
                "categories": [
                    {
                        "name": "📋 INFORMACIÓN",
                        "channels": [
                            {"name": "👋┃bienvenida", "type": "text", "topic": "¡Bienvenidos gamers!"},
                            {"name": "📖┃reglas", "type": "text", "topic": "Normas del servidor"},
                            {"name": "📢┃anuncios", "type": "text", "topic": "Anuncios y novedades"},
                            {"name": "🆕┃novedades-gaming", "type": "text", "topic": "Últimas noticias del gaming"}
                        ]
                    },
                    {
                        "name": "💬 GENERAL",
                        "channels": [
                            {"name": "💬┃chat-general", "type": "text", "topic": "Chat general"},
                            {"name": "🎮┃gaming-talk", "type": "text", "topic": "Habla sobre videojuegos"},
                            {"name": "🏆┃logros", "type": "text", "topic": "Comparte tus logros"},
                            {"name": "📷┃screenshots", "type": "text", "topic": "Screenshots y clips épicos"},
                            {"name": "🤖┃bot-commands", "type": "text", "topic": "Comandos del bot"}
                        ]
                    },
                    {
                        "name": "🎯 BUSCAR EQUIPO",
                        "channels": [
                            {"name": "👥┃lfg-general", "type": "text", "topic": "Buscar grupo general"},
                            {"name": "🔫┃lfg-fps", "type": "text", "topic": "Buscar equipo para FPS"},
                            {"name": "⚔️┃lfg-moba", "type": "text", "topic": "Buscar equipo para MOBA"},
                            {"name": "🏎️┃lfg-racing", "type": "text", "topic": "Buscar equipo para carreras"},
                            {"name": "🏰┃lfg-rpg", "type": "text", "topic": "Buscar equipo para RPG"}
                        ]
                    },
                    {
                        "name": "🔊 VOICE CHANNELS",
                        "channels": [
                            {"name": "🎤 Lobby General", "type": "voice", "limit": 0},
                            {"name": "🎮 Gaming 1", "type": "voice", "limit": 6},
                            {"name": "🎮 Gaming 2", "type": "voice", "limit": 6},
                            {"name": "🎮 Gaming 3", "type": "voice", "limit": 6},
                            {"name": "🔒 Privado 1", "type": "voice", "limit": 4},
                            {"name": "🔒 Privado 2", "type": "voice", "limit": 4},
                            {"name": "🎯 Competitivo", "type": "voice", "limit": 5}
                        ]
                    },
                    {
                        "name": "🛠️ MODERACIÓN",
                        "channels": [
                            {"name": "👮┃mod-chat", "type": "text", "topic": "Chat de moderadores", "staff_only": True},
                            {"name": "📊┃logs", "type": "text", "topic": "Logs del servidor", "staff_only": True},
                            {"name": "🎫┃tickets", "type": "text", "topic": "Sistema de soporte"},
                            {"name": "🔧 Mod Voice", "type": "voice", "limit": 5, "staff_only": True}
                        ]
                    },
                    {
                        "name": "📊 ESTADÍSTICAS & INFORMACIÓN",
                        "channels": [
                            {"name": "📈┃level-ups", "type": "text", "topic": "Anuncios de subida de nivel"},
                            {"name": "📊┃estadísticas", "type": "text", "topic": "Estadísticas del servidor"},
                            {"name": "📋┃información", "type": "text", "topic": "Información e invitaciones del servidor"},
                            {"name": "🎯┃logros", "type": "text", "topic": "Logros y reconocimientos"}
                        ]
                    }
                ],
                "roles": [
                    {"name": "👑 Owner", "color": 0xff0000, "permissions": ["administrator"], "hoist": True},
                    {"name": "🛡️ Admin", "color": 0xff6b6b, "permissions": ["manage_guild", "manage_channels"], "hoist": True},
                    {"name": "🔨 Moderador", "color": 0x4ecdc4, "permissions": ["manage_messages", "kick_members"], "hoist": True},
                    {"name": "🎯 Pro Gamer", "color": 0xf1c40f, "permissions": [], "hoist": True},
                    {"name": "🔫 FPS Player", "color": 0xe74c3c, "permissions": [], "hoist": False},
                    {"name": "⚔️ MOBA Player", "color": 0x9b59b6, "permissions": [], "hoist": False},
                    {"name": "🏎️ Racing Fan", "color": 0x3498db, "permissions": [], "hoist": False},
                    {"name": "🏰 RPG Lover", "color": 0xe67e22, "permissions": [], "hoist": False},
                    {"name": "🔇 Silenciado", "color": 0x95a5a6, "permissions": [], "hoist": False}
                ]
            },
            
            "development": {
                "name": "💻 Servidor de Desarrollo",
                "description": "Configuración para comunidad de desarrolladores",
                "categories": [
                    {
                        "name": "📋 INFORMACIÓN",
                        "channels": [
                            {"name": "👋┃bienvenida", "type": "text", "topic": "¡Bienvenidos desarrolladores!"},
                            {"name": "📖┃reglas", "type": "text", "topic": "Normas del servidor"},
                            {"name": "📢┃anuncios", "type": "text", "topic": "Anuncios importantes"},
                            {"name": "📚┃recursos", "type": "text", "topic": "Recursos útiles para developers"}
                        ]
                    },
                    {
                        "name": "💬 GENERAL",
                        "channels": [
                            {"name": "💬┃general", "type": "text", "topic": "Chat general"},
                            {"name": "☕┃random", "type": "text", "topic": "Chat random y off-topic"},
                            {"name": "💼┃trabajos", "type": "text", "topic": "Ofertas de trabajo y freelance"},
                            {"name": "🎉┃logros", "type": "text", "topic": "Comparte tus proyectos"},
                            {"name": "🤖┃bot-commands", "type": "text", "topic": "Comandos del bot"}
                        ]
                    },
                    {
                        "name": "💻 DESARROLLO",
                        "channels": [
                            {"name": "🐍┃python", "type": "text", "topic": "Todo sobre Python"},
                            {"name": "🌐┃web-dev", "type": "text", "topic": "Desarrollo web (HTML, CSS, JS)"},
                            {"name": "⚛️┃react-vue", "type": "text", "topic": "React, Vue y otros frameworks"},
                            {"name": "📱┃mobile-dev", "type": "text", "topic": "Desarrollo móvil"},
                            {"name": "🎮┃game-dev", "type": "text", "topic": "Desarrollo de videojuegos"},
                            {"name": "🗄️┃backend", "type": "text", "topic": "Backend y bases de datos"},
                            {"name": "☁️┃devops", "type": "text", "topic": "DevOps y deployment"}
                        ]
                    },
                    {
                        "name": "❓ AYUDA",
                        "channels": [
                            {"name": "🆘┃ayuda-general", "type": "text", "topic": "Ayuda general con código"},
                            {"name": "🐛┃debug", "type": "text", "topic": "Ayuda con bugs y errores"},
                            {"name": "📝┃code-review", "type": "text", "topic": "Revisión de código"},
                            {"name": "💡┃ideas", "type": "text", "topic": "Ideas y sugerencias de proyectos"}
                        ]
                    },
                    {
                        "name": "🔊 VOICE",
                        "channels": [
                            {"name": "🎤 General", "type": "voice", "limit": 0},
                            {"name": "💻 Coding Session 1", "type": "voice", "limit": 4},
                            {"name": "💻 Coding Session 2", "type": "voice", "limit": 4},
                            {"name": "📹 Screen Share", "type": "voice", "limit": 8},
                            {"name": "🔒 Privado", "type": "voice", "limit": 2}
                        ]
                    },
                    {
                        "name": "🛠️ STAFF",
                        "channels": [
                            {"name": "👮┃staff-chat", "type": "text", "topic": "Chat privado del staff", "staff_only": True},
                            {"name": "📊┃logs", "type": "text", "topic": "Logs del servidor", "staff_only": True},
                            {"name": "🎫┃tickets", "type": "text", "topic": "Sistema de soporte"},
                            {"name": "🔧 Staff Voice", "type": "voice", "limit": 5, "staff_only": True}
                        ]
                    }
                ],
                "roles": [
                    {"name": "👑 Owner", "color": 0xff0000, "permissions": ["administrator"], "hoist": True},
                    {"name": "🛡️ Admin", "color": 0xff6b6b, "permissions": ["manage_guild", "manage_channels"], "hoist": True},
                    {"name": "🔨 Moderador", "color": 0x4ecdc4, "permissions": ["manage_messages", "kick_members"], "hoist": True},
                    {"name": "⭐ Senior Dev", "color": 0xf1c40f, "permissions": [], "hoist": True},
                    {"name": "🐍 Python Dev", "color": 0x3498db, "permissions": [], "hoist": False},
                    {"name": "🌐 Web Dev", "color": 0xe67e22, "permissions": [], "hoist": False},
                    {"name": "📱 Mobile Dev", "color": 0x9b59b6, "permissions": [], "hoist": False},
                    {"name": "🎮 Game Dev", "color": 0x2ecc71, "permissions": [], "hoist": False},
                    {"name": "🔰 Junior Dev", "color": 0x95a5a6, "permissions": [], "hoist": False},
                    {"name": "🔇 Silenciado", "color": 0x95a5a6, "permissions": [], "hoist": False}
                ]
            },
            
            "community": {
                "name": "🌟 Comunidad General",
                "description": "Configuración para comunidad general y social",
                "categories": [
                    {
                        "name": "📋 INFORMACIÓN",
                        "channels": [
                            {"name": "👋┃bienvenida", "type": "text", "topic": "¡Bienvenidos a la comunidad!"},
                            {"name": "📖┃reglas", "type": "text", "topic": "Normas del servidor"},
                            {"name": "📢┃anuncios", "type": "text", "topic": "Anuncios importantes"},
                            {"name": "🎉┃eventos", "type": "text", "topic": "Eventos de la comunidad"}
                        ]
                    },
                    {
                        "name": "💬 CHAT",
                        "channels": [
                            {"name": "💬┃general", "type": "text", "topic": "Chat general"},
                            {"name": "☕┃charla-casual", "type": "text", "topic": "Conversaciones casuales"},
                            {"name": "📷┃fotos-y-media", "type": "text", "topic": "Comparte fotos y videos"},
                            {"name": "🔗┃links-interesantes", "type": "text", "topic": "Links y contenido interesante"},
                            {"name": "🤖┃bot-zone", "type": "text", "topic": "Zona para comandos de bot"}
                        ]
                    },
                    {
                        "name": "🎭 ENTRETENIMIENTO",
                        "channels": [
                            {"name": "🎮┃gaming", "type": "text", "topic": "Todo sobre videojuegos"},
                            {"name": "🎬┃peliculas-series", "type": "text", "topic": "Películas y series"},
                            {"name": "🎵┃musica", "type": "text", "topic": "Comparte y habla de música"},
                            {"name": "📚┃libros", "type": "text", "topic": "Recomendaciones de libros"},
                            {"name": "🎨┃arte-creativo", "type": "text", "topic": "Arte y creatividad"}
                        ]
                    },
                    {
                        "name": "🔊 VOICE",
                        "channels": [
                            {"name": "🎤 Lobby", "type": "voice", "limit": 0},
                            {"name": "💬 Charla 1", "type": "voice", "limit": 6},
                            {"name": "💬 Charla 2", "type": "voice", "limit": 6},
                            {"name": "🎮 Gaming", "type": "voice", "limit": 5},
                            {"name": "🎵 Música", "type": "voice", "limit": 8},
                            {"name": "🔒 Privado", "type": "voice", "limit": 2}
                        ]
                    },
                    {
                        "name": "🛠️ STAFF",
                        "channels": [
                            {"name": "👮┃staff-only", "type": "text", "topic": "Chat privado del staff", "staff_only": True},
                            {"name": "📊┃mod-logs", "type": "text", "topic": "Logs de moderación", "staff_only": True},
                            {"name": "🎫┃soporte", "type": "text", "topic": "Sistema de soporte"},
                            {"name": "🔧 Staff Voice", "type": "voice", "limit": 5, "staff_only": True}
                        ]
                    },
                    {
                        "name": "📊 ESTADÍSTICAS & INFO",
                        "channels": [
                            {"name": "🎉┃anuncios-nivel", "type": "text", "topic": "Anuncios de subida de nivel"},
                            {"name": "📈┃stats", "type": "text", "topic": "Estadísticas de la comunidad"},
                            {"name": "📋┃info", "type": "text", "topic": "Información e invitaciones del servidor"}
                        ]
                    }
                ],
                "roles": [
                    {"name": "👑 Owner", "color": 0xff0000, "permissions": ["administrator"], "hoist": True},
                    {"name": "🛡️ Admin", "color": 0xff6b6b, "permissions": ["manage_guild", "manage_channels"], "hoist": True},
                    {"name": "🔨 Moderador", "color": 0x4ecdc4, "permissions": ["manage_messages", "kick_members"], "hoist": True},
                    {"name": "⭐ VIP", "color": 0xf1c40f, "permissions": [], "hoist": True},
                    {"name": "🎮 Gamer", "color": 0x3498db, "permissions": [], "hoist": False},
                    {"name": "🎨 Artista", "color": 0xe67e22, "permissions": [], "hoist": False},
                    {"name": "🎵 Músico", "color": 0x9b59b6, "permissions": [], "hoist": False},
                    {"name": "📚 Lector", "color": 0x2ecc71, "permissions": [], "hoist": False},
                    {"name": "🔇 Silenciado", "color": 0x95a5a6, "permissions": [], "hoist": False}
                ]
            }
        }
    
    @nextcord.slash_command(name="servidor-completo", description="Configuración completa automática del servidor")
    async def complete_server_setup(self, interaction: nextcord.Interaction):
        """Comando principal para configuración completa"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitas permisos de administrador para usar este comando.",
                ephemeral=True
            )
            return
        
        # Mostrar selector de tipo de servidor
        view = ServerTypeSelector(self)
        embed = nextcord.Embed(
            title="🚀 Configuración Completa del Servidor",
            description="Selecciona el tipo de servidor para crear automáticamente:\n\n" +
                       "• **Canales organizados por categorías**\n" +
                       "• **Roles con permisos apropiados**\n" +
                       "• **Configuraciones optimizadas**\n" +
                       "• **Sistema de bots integrado**",
            color=nextcord.Color.blue()
        )
        
        for template_id, template in self.server_templates.items():
            embed.add_field(
                name=template["name"], 
                value=template["description"],
                inline=False
            )
        
        embed.add_field(
            name="⚠️ Advertencia",
            value="Este proceso creará muchos canales y roles. Asegúrate de que realmente quieres esto.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def setup_complete_server(self, interaction: nextcord.Interaction, template_id: str):
        """Configura el servidor completo según la plantilla"""
        await interaction.response.defer()
        
        template = self.server_templates[template_id]
        guild = interaction.guild
        
        setup_embed = nextcord.Embed(
            title=f"🚀 Configurando: {template['name']}",
            description="Iniciando configuración completa del servidor...",
            color=nextcord.Color.blue()
        )
        setup_message = await interaction.followup.send(embed=setup_embed)
        
        try:
            created_categories = {}
            created_channels = {}
            created_roles = {}
            
            # Paso 1: Crear roles
            setup_embed.description = "📝 Creando roles..."
            await setup_message.edit(embed=setup_embed)
            
            for role_data in template["roles"]:
                try:
                    # Verificar si el rol ya existe
                    existing_role = nextcord.utils.get(guild.roles, name=role_data["name"])
                    if existing_role:
                        created_roles[role_data["name"]] = existing_role
                        continue
                    
                    # Crear permisos
                    permissions = nextcord.Permissions.none()
                    for perm in role_data.get("permissions", []):
                        if hasattr(permissions, perm):
                            setattr(permissions, perm, True)
                    
                    # Crear rol
                    role = await guild.create_role(
                        name=role_data["name"],
                        color=nextcord.Color(role_data["color"]),
                        permissions=permissions,
                        hoist=role_data.get("hoist", False),
                        reason=f"Configuración automática - {template['name']}"
                    )
                    created_roles[role_data["name"]] = role
                    
                    # Pequeña pausa para evitar rate limits
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error creando rol {role_data['name']}: {e}")
            
            # Paso 2: Crear categorías y canales
            setup_embed.description = "📁 Creando categorías y canales..."
            await setup_message.edit(embed=setup_embed)
            
            for category_data in template["categories"]:
                try:
                    # Crear categoría
                    category = await guild.create_category(
                        name=category_data["name"],
                        reason=f"Configuración automática - {template['name']}"
                    )
                    created_categories[category_data["name"]] = category
                    
                    # Crear canales en la categoría
                    for channel_data in category_data["channels"]:
                        try:
                            # Configurar permisos si es staff only
                            overwrites = {}
                            if channel_data.get("staff_only", False):
                                # Denegar acceso a @everyone
                                overwrites[guild.default_role] = nextcord.PermissionOverwrite(
                                    read_messages=False,
                                    send_messages=False
                                )
                                
                                # Permitir acceso a roles de staff
                                staff_roles = ["Owner", "Admin", "Moderador", "🛡️ Admin", "🔨 Moderador"]
                                for role_name in staff_roles:
                                    role = created_roles.get(role_name) or created_roles.get(f"👑 {role_name}") or created_roles.get(f"🛡️ {role_name}") or created_roles.get(f"🔨 {role_name}")
                                    if role:
                                        overwrites[role] = nextcord.PermissionOverwrite(
                                            read_messages=True,
                                            send_messages=True
                                        )
                            
                            if channel_data["type"] == "text":
                                channel = await guild.create_text_channel(
                                    name=channel_data["name"],
                                    category=category,
                                    topic=channel_data.get("topic", ""),
                                    overwrites=overwrites,
                                    reason=f"Configuración automática - {template['name']}"
                                )
                            else:  # voice
                                channel = await guild.create_voice_channel(
                                    name=channel_data["name"],
                                    category=category,
                                    user_limit=channel_data.get("limit", 0),
                                    overwrites=overwrites,
                                    reason=f"Configuración automática - {template['name']}"
                                )
                            
                            created_channels[channel_data["name"]] = channel
                            
                            # Pausa para evitar rate limits
                            await asyncio.sleep(0.8)
                            
                        except Exception as e:
                            logger.error(f"Error creando canal {channel_data['name']}: {e}")
                    
                    # Pausa entre categorías
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error creando categoría {category_data['name']}: {e}")
            
            # Paso 3: Configurar bot
            setup_embed.description = "🤖 Configurando sistemas del bot..."
            await setup_message.edit(embed=setup_embed)
            
            await self.configure_bot_systems(guild, created_channels, created_roles, template_id)
            
            # Paso 4: Configurar permisos especiales
            setup_embed.description = "🔧 Configurando permisos especiales..."
            await setup_message.edit(embed=setup_embed)
            
            await self.configure_special_permissions(guild, created_channels, created_roles)
            
            # Resultado final
            success_embed = nextcord.Embed(
                title="✅ ¡Configuración Completada!",
                description=f"Servidor configurado exitosamente como: **{template['name']}**",
                color=nextcord.Color.green()
            )
            
            success_embed.add_field(
                name="📊 Elementos Creados",
                value=f"• **{len(created_categories)}** categorías\n" +
                      f"• **{len(created_channels)}** canales\n" +
                      f"• **{len(created_roles)}** roles",
                inline=True
            )
            
            success_embed.add_field(
                name="🤖 Sistemas Configurados",
                value="• Sistema de niveles con roles automáticos\n• Anuncios de subida de nivel\n• Estadísticas de usuarios\n• Sistema de invitaciones permanentes\n• Tickets y VoiceMaster\n• Logs de moderación\n• Bienvenidas y auto-roles",
                inline=True
            )
            
            success_embed.add_field(
                name="🎯 Próximos Pasos",
                value="• Personaliza los roles y permisos\n• Revisa las invitaciones creadas\n• Usa `/nivel` para ver el sistema de XP\n• Usa `/stats` para ver estadísticas\n• ¡Disfruta tu servidor completamente configurado!",
                inline=False
            )
            
            await setup_message.edit(embed=success_embed)
            
        except Exception as e:
            error_embed = nextcord.Embed(
                title="❌ Error en la Configuración",
                description=f"Ocurrió un error durante la configuración: {str(e)}",
                color=nextcord.Color.red()
            )
            await setup_message.edit(embed=error_embed)
            logger.error(f"Error en configuración completa: {e}")
    
    async def configure_bot_systems(self, guild: nextcord.Guild, channels: Dict, roles: Dict, template_id: str):
        """Configura los sistemas del bot"""
        try:
            guild_id = str(guild.id)
            
            # Configurar canales especiales en la base de datos
            if "👋┃bienvenida" in channels:
                self.db.set_channel(guild_id, "welcome", str(channels["👋┃bienvenida"].id))
            
            if "📊┃logs" in channels:
                self.db.set_channel(guild_id, "logs", str(channels["📊┃logs"].id))
            elif "📊┃mod-logs" in channels:
                self.db.set_channel(guild_id, "logs", str(channels["📊┃mod-logs"].id))
            
            if "🎫┃tickets" in channels:
                self.db.set_channel(guild_id, "tickets", str(channels["🎫┃tickets"].id))
            elif "🎫┃soporte" in channels:
                self.db.set_channel(guild_id, "tickets", str(channels["🎫┃soporte"].id))
            
            # =============== NUEVOS SISTEMAS INTEGRADOS ===============
            
            # 1. Configurar sistema de reglas automáticas
            if self.auto_rules:
                try:
                    rules_channel = await self.auto_rules.setup_server_rules(guild, template_id)
                    if rules_channel:
                        logger.info(f"✅ Reglas automáticas configuradas en {rules_channel.name}")
                    
                    await self.auto_rules.setup_channel_rules(guild, template_id)
                    logger.info("✅ Reglas por canal configuradas")
                except Exception as e:
                    logger.error(f"❌ Error configurando reglas automáticas: {e}")
            
            # 2. Configurar sistema de niveles avanzado CON ANUNCIOS Y ROLES
            await self.setup_level_system(guild, channels, roles, template_id)
            
            # 3. Configurar estadísticas de usuarios
            await self.setup_user_stats(guild, channels, template_id)
            
            # 4. Configurar sistema de invitaciones del servidor
            await self.setup_server_invites(guild, channels, template_id)
            
            # 5. Configurar moderación integrada
            if self.moderation:
                try:
                    await self.moderation.setup_moderation_system(guild, template_id)
                    logger.info("✅ Sistema de moderación integrado configurado")
                except Exception as e:
                    logger.error(f"❌ Error configurando moderación: {e}")
            
            # ============================================================
            
            if "💬┃general" in channels:
                self.db.set_channel(guild_id, "general", str(channels["💬┃general"].id))
            elif "💬┃chat-general" in channels:
                self.db.set_channel(guild_id, "general", str(channels["💬┃chat-general"].id))
            
            # Configurar roles especiales
            muted_role = roles.get("🔇 Silenciado")
            if muted_role:
                self.db.set_role(guild_id, "muted", str(muted_role.id))
            
            # Configurar auto-role basado en el tipo de servidor
            auto_role = None
            if template_id == "streamer" and "⭐ Suscriptor" in roles:
                auto_role = roles["⭐ Suscriptor"]
            elif template_id == "gaming" and "🔰 Junior Dev" in roles:
                auto_role = roles["🔰 Junior Dev"]  # Para development
            elif template_id == "community":
                # No auto-role para comunidad general
                pass
            
            if auto_role:
                self.db.set_role(guild_id, "auto", str(auto_role.id))
            
            # Configurar settings básicos
            self.db.set_setting(guild_id, "welcome_enabled", "true")
            self.db.set_setting(guild_id, "logging_enabled", "true")
            self.db.set_setting(guild_id, "moderation_enabled", "true")
            self.db.set_setting(guild_id, "prefix", "!")
            self.db.set_setting(guild_id, "language", "es-ES")
            
            # Configurar sistemas específicos del bot si existen
            await self.setup_bot_panels(guild, channels)
            
        except Exception as e:
            logger.error(f"Error configurando sistemas del bot: {e}")
    
    # =============== NUEVOS COMANDOS SLASH ===============
    
    @nextcord.slash_command(
        name="elegir-color",
        description="🎨 Elige tu color de rol personalizado (nivel 50+)"
    )
    async def choose_color_command(self, interaction: nextcord.Interaction):
        """Comando para elegir color personalizado"""
        if not self.level_system:
            await interaction.response.send_message("❌ Sistema de niveles no disponible.", ephemeral=True)
            return
        
        # Verificar nivel del usuario
        user_level = await self.level_system.get_user_level(interaction.guild.id, interaction.user.id)
        
        if user_level < 50:
            embed = nextcord.Embed(
                title="🔒 Nivel Insuficiente",
                description=f"Necesitas ser **nivel 50** o superior para elegir color.\nTu nivel actual: **{user_level}**",
                color=0xff6600
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Crear menú de colores
        color_options = []
        for name, color_value in list(self.level_system.available_colors.items())[:20]:  # Limitamos a 20 por Discord
            color_options.append(
                nextcord.SelectOption(
                    label=name,
                    value=str(color_value),
                    description=f"Color: {name.split(' ', 1)[1] if ' ' in name else name}"
                )
            )
        
        select = nextcord.ui.Select(
            placeholder="🎨 Elige tu color personalizado...",
            options=color_options
        )
        
        async def color_callback(select_interaction):
            selected_color = int(select.values[0])
            color_name = next(name for name, value in self.level_system.available_colors.items() if value == selected_color)
            
            # Buscar rol de color existente del usuario
            user_color_role = None
            for role in interaction.user.roles:
                if role.name.startswith("🎨 Color:"):
                    user_color_role = role
                    break
            
            # Crear o actualizar rol de color
            role_name = f"🎨 Color: {color_name.split(' ', 1)[1] if ' ' in color_name else color_name}"
            
            try:
                if user_color_role:
                    await user_color_role.edit(color=nextcord.Color(selected_color), name=role_name)
                else:
                    color_role = await interaction.guild.create_role(
                        name=role_name,
                        color=nextcord.Color(selected_color),
                        reason="Color personalizado elegido por usuario"
                    )
                    await interaction.user.add_roles(color_role)
                
                embed = nextcord.Embed(
                    title="🎨 Color Actualizado",
                    description=f"Tu color ha sido cambiado a **{color_name}**",
                    color=selected_color
                )
                await select_interaction.response.send_message(embed=embed, ephemeral=True)
                
            except Exception as e:
                await select_interaction.response.send_message(f"❌ Error aplicando color: {e}", ephemeral=True)
        
        select.callback = color_callback
        view = nextcord.ui.View()
        view.add_item(select)
        
        embed = nextcord.Embed(
            title="🎨 Selector de Color Personalizado",
            description=f"¡Felicidades! Has alcanzado el nivel {user_level}.\nAhora puedes elegir un color personalizado para tu nombre.",
            color=0x00ff88
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @nextcord.slash_command(
        name="mi-nivel",
        description="📊 Ver tu nivel, XP y progreso actual"
    )
    async def my_level_command(self, interaction: nextcord.Interaction):
        """Comando para ver nivel personal"""
        if not self.level_system:
            await interaction.response.send_message("❌ Sistema de niveles no disponible.", ephemeral=True)
            return
        
        user_xp = await self.level_system.get_user_xp(interaction.guild.id, interaction.user.id)
        user_level = self.level_system.calculate_level(user_xp)
        
        next_level_xp = self.level_system.calculate_xp_for_level(user_level + 1)
        needed_xp = next_level_xp - user_xp
        
        # Obtener estadísticas adicionales
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT messages_sent, voice_time FROM user_levels 
                WHERE guild_id = ? AND user_id = ?
            ''', (interaction.guild.id, interaction.user.id))
            
            result = cursor.fetchone()
            messages_sent = result[0] if result else 0
            voice_time = result[1] if result else 0
        
        embed = nextcord.Embed(
            title=f"📊 Nivel de {interaction.user.display_name}",
            color=0x00ff88
        )
        
        embed.add_field(
            name="🎯 Nivel Actual",
            value=f"**{user_level}**",
            inline=True
        )
        
        embed.add_field(
            name="⭐ XP Total",
            value=f"**{user_xp:,}**",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Siguiente Nivel",
            value=f"**{needed_xp:,}** XP restantes",
            inline=True
        )
        
        embed.add_field(
            name="💬 Mensajes Enviados",
            value=f"**{messages_sent:,}**",
            inline=True
        )
        
        embed.add_field(
            name="🔊 Tiempo en Voz",
            value=f"**{voice_time:,}** minutos",
            inline=True
        )
        
        embed.add_field(
            name="📈 Progreso",
            value=f"**{((user_xp - self.level_system.calculate_xp_for_level(user_level)) / (next_level_xp - self.level_system.calculate_xp_for_level(user_level)) * 100):.1f}%**",
            inline=True
        )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="¡Sigue participando para subir de nivel!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @nextcord.slash_command(
        name="top-niveles",
        description="🏆 Ver el ranking de niveles del servidor"
    )
    async def leaderboard_command(self, interaction: nextcord.Interaction):
        """Comando para ver leaderboard"""
        if not self.level_system:
            await interaction.response.send_message("❌ Sistema de niveles no disponible.", ephemeral=True)
            return
        
        leaderboard = await self.level_system.get_leaderboard(interaction.guild, 10)
        
        embed = nextcord.Embed(
            title="🏆 Top 10 - Ranking de Niveles",
            color=0xffd700
        )
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        description = ""
        for i, (user_id, xp, level, messages, voice_time) in enumerate(leaderboard):
            user = interaction.guild.get_member(user_id)
            if user:
                medal = medals[i] if i < len(medals) else f"{i+1}."
                description += f"{medal} **{user.display_name}** - Nivel {level} ({xp:,} XP)\n"
        
        if not description:
            description = "No hay datos de niveles aún."
        
        embed.description = description
        embed.set_footer(text="¡Participa activamente para aparecer en el ranking!")
        
        await interaction.response.send_message(embed=embed)
    
    async def setup_bot_panels(self, guild: nextcord.Guild, channels: Dict):
        """Configura los paneles del bot"""
        try:
            # Configurar panel de tickets
            ticket_channel = None
            for name, channel in channels.items():
                if "ticket" in name.lower() or "soporte" in name.lower():
                    ticket_channel = channel
                    break
            
            if ticket_channel:
                # Obtener el gestor de mensajes persistentes
                pm_manager = self.bot.get_cog('PersistentMessageManager')
                if pm_manager:
                    await pm_manager.create_message(guild, 'ticket_panel', ticket_channel.id)
            
            # Configurar panel de VoiceMaster si hay canales de voz
            voice_category = None
            for category in guild.categories:
                if "VOZ" in category.name.upper() or "VOICE" in category.name.upper():
                    voice_category = category
                    break
            
            if voice_category and ticket_channel:  # Usar el mismo canal para VoiceMaster
                vm_manager = self.bot.get_cog('VoiceMaster')
                if vm_manager:
                    await vm_manager.setup_voicemaster(guild)
            
        except Exception as e:
            logger.error(f"Error configurando paneles del bot: {e}")
    
    async def configure_special_permissions(self, guild: nextcord.Guild, channels: Dict, roles: Dict):
        """Configura permisos especiales adicionales"""
        try:
            # Configurar permisos para rol silenciado
            muted_role = roles.get("🔇 Silenciado")
            if muted_role:
                for channel in guild.text_channels:
                    try:
                        await channel.set_permissions(
                            muted_role,
                            send_messages=False,
                            add_reactions=False,
                            speak=False,
                            reason="Configuración automática - Rol silenciado"
                        )
                    except:
                        pass
                
                for channel in guild.voice_channels:
                    try:
                        await channel.set_permissions(
                            muted_role,
                            speak=False,
                            stream=False,
                            reason="Configuración automática - Rol silenciado"
                        )
                    except:
                        pass
            
        except Exception as e:
            logger.error(f"Error configurando permisos especiales: {e}")
    
    async def setup_level_system(self, guild: nextcord.Guild, channels: Dict, roles: Dict, template_id: str):
        """Configurar sistema de niveles con anuncios y roles de nivel"""
        try:
            # Base de datos para el sistema de niveles
            conn = sqlite3.connect('bot_data.db')
            cursor = conn.cursor()
            
            # Crear tabla de configuración de niveles si no existe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS level_config (
                    guild_id TEXT PRIMARY KEY,
                    announcement_channel TEXT,
                    level_up_message TEXT,
                    enabled BOOLEAN DEFAULT 1
                )
            ''')
            
            # Crear tabla de roles de nivel si no existe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS level_roles (
                    guild_id TEXT,
                    level INTEGER,
                    role_id TEXT,
                    role_name TEXT,
                    PRIMARY KEY (guild_id, level)
                )
            ''')
            
            guild_id = str(guild.id)
            
            # Configurar canal de anuncios de nivel
            announcement_channel = None
            for channel_name in ["📈┃level-ups", "🎉┃anuncios", "💬┃general", "💬┃chat-general"]:
                if channel_name in channels:
                    announcement_channel = channels[channel_name]
                    break
            
            if announcement_channel:
                # Configurar sistema de niveles
                cursor.execute('''
                    INSERT OR REPLACE INTO level_config 
                    (guild_id, announcement_channel, level_up_message, enabled) 
                    VALUES (?, ?, ?, ?)
                ''', (
                    guild_id,
                    str(announcement_channel.id),
                    "🎉 ¡Felicidades {user}! Has subido al **Nivel {level}**! 🎊",
                    True
                ))
                
                # Crear roles de nivel según el tipo de servidor
                level_roles_config = {
                    "gaming": [
                        (5, "🏅 Novato", 0x95a5a6),
                        (10, "⚔️ Aventurero", 0x3498db),
                        (20, "🛡️ Guerrero", 0x9b59b6),
                        (35, "👑 Héroe", 0xe67e22),
                        (50, "🌟 Leyenda", 0xf1c40f),
                        (75, "💎 Maestro", 0x1abc9c),
                        (100, "🔥 Dios del Gaming", 0xe74c3c)
                    ],
                    "community": [
                        (5, "🌱 Nuevo Miembro", 0x95a5a6),
                        (10, "💬 Conversador", 0x3498db),
                        (25, "🤝 Colaborador", 0x9b59b6),
                        (40, "🌟 Estrella", 0xe67e22),
                        (60, "💎 VIP", 0xf1c40f),
                        (80, "👑 Elite", 0x1abc9c),
                        (100, "🏆 Leyenda de la Comunidad", 0xe74c3c)
                    ],
                    "dev": [
                        (5, "🔰 Junior Dev", 0x95a5a6),
                        (15, "💻 Developer", 0x3498db),
                        (30, "🚀 Senior Dev", 0x9b59b6),
                        (50, "🏗️ Architect", 0xe67e22),
                        (75, "🧠 Tech Lead", 0xf1c40f),
                        (100, "🔥 Code Master", 0xe74c3c)
                    ],
                    "streamer": [
                        (5, "👀 Viewer", 0x95a5a6),
                        (10, "⭐ Fan", 0x3498db),
                        (25, "💎 VIP", 0x9b59b6),
                        (40, "👑 Moderador VIP", 0xe67e22),
                        (60, "🎭 Streamer Amigo", 0xf1c40f),
                        (100, "🏆 Leyenda del Stream", 0xe74c3c)
                    ]
                }
                
                roles_for_template = level_roles_config.get(template_id, level_roles_config["community"])
                
                # Crear roles de nivel
                created_level_roles = 0
                for level, role_name, color in roles_for_template:
                    try:
                        # Verificar si el rol ya existe
                        existing_role = nextcord.utils.get(guild.roles, name=role_name)
                        if existing_role:
                            role = existing_role
                        else:
                            # Crear el rol
                            role = await guild.create_role(
                                name=role_name,
                                color=nextcord.Color(color),
                                hoist=True,
                                reason=f"Rol de nivel {level} - Configuración automática"
                            )
                        
                        # Guardar en base de datos
                        cursor.execute('''
                            INSERT OR REPLACE INTO level_roles 
                            (guild_id, level, role_id, role_name) 
                            VALUES (?, ?, ?, ?)
                        ''', (guild_id, level, str(role.id), role_name))
                        
                        created_level_roles += 1
                        await asyncio.sleep(0.5)  # Evitar rate limit
                        
                    except Exception as e:
                        logger.error(f"Error creando rol de nivel {level} ({role_name}): {e}")
                
                conn.commit()
                logger.info(f"✅ Sistema de niveles configurado: {created_level_roles} roles de nivel creados")
                
                # Enviar mensaje de confirmación al canal
                embed = nextcord.Embed(
                    title="🎉 Sistema de Niveles Activado",
                    description=f"¡El sistema de niveles está ahora activo en **{guild.name}**!",
                    color=nextcord.Color.gold()
                )
                embed.add_field(
                    name="📊 Roles de Nivel",
                    value=f"Se han creado **{created_level_roles}** roles de nivel automáticos",
                    inline=False
                )
                embed.add_field(
                    name="📢 Anuncios",
                    value=f"Los anuncios de subida de nivel aparecerán en {announcement_channel.mention}",
                    inline=False
                )
                embed.add_field(
                    name="🎯 ¿Cómo funciona?",
                    value="• Gana XP chateando en el servidor\n• Sube de nivel automáticamente\n• Recibe roles especiales por tu actividad\n• Usa `/nivel` para ver tu progreso",
                    inline=False
                )
                
                await announcement_channel.send(embed=embed)
                
            conn.close()
            
        except Exception as e:
            logger.error(f"Error configurando sistema de niveles: {e}")
    
    async def setup_user_stats(self, guild: nextcord.Guild, channels: Dict, template_id: str):
        """Configurar sistema de estadísticas de usuarios"""
        try:
            # Base de datos para estadísticas
            conn = sqlite3.connect('bot_data.db')
            cursor = conn.cursor()
            
            # Crear tabla de estadísticas si no existe
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    guild_id TEXT,
                    user_id TEXT,
                    messages_sent INTEGER DEFAULT 0,
                    voice_time INTEGER DEFAULT 0,
                    commands_used INTEGER DEFAULT 0,
                    reactions_given INTEGER DEFAULT 0,
                    join_date TEXT,
                    last_active TEXT,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')
            
            # Crear tabla de estadísticas del servidor
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server_stats (
                    guild_id TEXT PRIMARY KEY,
                    stats_channel TEXT,
                    total_messages INTEGER DEFAULT 0,
                    total_members INTEGER DEFAULT 0,
                    active_members INTEGER DEFAULT 0,
                    last_updated TEXT
                )
            ''')
            
            guild_id = str(guild.id)
            
            # Configurar canal de estadísticas
            stats_channel = None
            for channel_name in ["📊┃estadísticas", "📈┃stats", "📊┃server-stats"]:
                if channel_name in channels:
                    stats_channel = channels[channel_name]
                    break
            
            if stats_channel:
                # Configurar estadísticas del servidor
                cursor.execute('''
                    INSERT OR REPLACE INTO server_stats 
                    (guild_id, stats_channel, total_members) 
                    VALUES (?, ?, ?)
                ''', (guild_id, str(stats_channel.id), guild.member_count))
                
                # Crear embed inicial de estadísticas
                embed = nextcord.Embed(
                    title=f"📊 Estadísticas de {guild.name}",
                    color=nextcord.Color.blue()
                )
                embed.add_field(
                    name="👥 Miembros",
                    value=f"**{guild.member_count}** miembros totales",
                    inline=True
                )
                embed.add_field(
                    name="📈 Canales",
                    value=f"**{len(guild.channels)}** canales",
                    inline=True
                )
                embed.add_field(
                    name="🎭 Roles",
                    value=f"**{len(guild.roles)}** roles",
                    inline=True
                )
                embed.add_field(
                    name="🤖 Sistema de Stats",
                    value="• Estadísticas de mensajes\n• Tiempo en canales de voz\n• Comandos utilizados\n• Actividad general",
                    inline=False
                )
                embed.set_footer(text="Estadísticas actualizadas automáticamente cada hora")
                
                # Enviar mensaje de estadísticas
                await stats_channel.send(embed=embed)
                
                logger.info(f"✅ Sistema de estadísticas configurado en {stats_channel.name}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error configurando estadísticas: {e}")
    
    async def setup_server_invites(self, guild: nextcord.Guild, channels: Dict, template_id: str):
        """Configurar sistema de invitaciones del servidor"""
        try:
            # Crear invitaciones permanentes para canales principales
            invite_channels = []
            
            # Buscar canal principal para invitación
            main_channel = None
            for channel_name in ["👋┃bienvenida", "💬┃general", "📢┃anuncios", "💬┃chat-general"]:
                if channel_name in channels:
                    main_channel = channels[channel_name]
                    break
            
            if main_channel:
                # Crear invitación permanente
                invite = await main_channel.create_invite(
                    max_age=0,  # Sin expiración
                    max_uses=0,  # Usos ilimitados
                    unique=False,
                    reason="Invitación permanente del servidor - Configuración automática"
                )
                
                invite_channels.append({
                    "channel": main_channel.name,
                    "invite": invite.url
                })
                
                # Buscar canal de invitaciones o información
                info_channel = None
                for channel_name in ["📋┃información", "📋┃info", "🔗┃invitaciones", "📢┃anuncios"]:
                    if channel_name in channels:
                        info_channel = channels[channel_name]
                        break
                
                if info_channel:
                    # Crear mensaje con información del servidor e invitación
                    embed = nextcord.Embed(
                        title=f"🎉 ¡Bienvenido a {guild.name}!",
                        description="¡Únete a nuestra increíble comunidad!",
                        color=nextcord.Color.blue()
                    )
                    
                    # Descripción según tipo de servidor
                    descriptions = {
                        "gaming": "🎮 Una comunidad para gamers donde compartir, competir y divertirse juntos",
                        "community": "🤝 Una comunidad abierta y amigable para todos",
                        "dev": "💻 Una comunidad de desarrolladores para aprender y compartir conocimiento",
                        "streamer": "📺 Únete a la comunidad del stream y disfruta del contenido"
                    }
                    
                    embed.description = descriptions.get(template_id, descriptions["community"])
                    
                    embed.add_field(
                        name="🔗 Invitación Permanente",
                        value=f"[**Únete aquí**]({invite.url})",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="📊 Estadísticas del Servidor",
                        value=f"👥 **{guild.member_count}** miembros\n📈 **{len(guild.channels)}** canales\n🎭 **{len(guild.roles)}** roles",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="🎯 Características",
                        value="• Sistema de niveles\n• Moderación automática\n• Eventos regulares\n• Comunidad activa",
                        inline=True
                    )
                    
                    if guild.icon:
                        embed.set_thumbnail(url=guild.icon.url)
                    
                    embed.set_footer(text=f"Servidor creado automáticamente • {guild.name}")
                    
                    await info_channel.send(embed=embed)
                    
                    logger.info(f"✅ Sistema de invitaciones configurado: {invite.url}")
                
                # Base de datos para tracking de invitaciones
                conn = sqlite3.connect('bot_data.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS server_invites (
                        guild_id TEXT,
                        invite_code TEXT,
                        channel_id TEXT,
                        uses INTEGER DEFAULT 0,
                        permanent BOOLEAN DEFAULT 1,
                        created_date TEXT,
                        PRIMARY KEY (guild_id, invite_code)
                    )
                ''')
                
                cursor.execute('''
                    INSERT OR REPLACE INTO server_invites 
                    (guild_id, invite_code, channel_id, permanent, created_date) 
                    VALUES (?, ?, ?, ?, datetime('now'))
                ''', (str(guild.id), invite.code, str(main_channel.id), True))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            logger.error(f"Error configurando invitaciones: {e}")

class ServerTypeSelector(nextcord.ui.View):
    """Selector de tipo de servidor"""
    
    def __init__(self, setup_wizard: ServerSetupWizard):
        super().__init__(timeout=300)
        self.wizard = setup_wizard
    
    @nextcord.ui.select(
        placeholder="Selecciona el tipo de servidor...",
        options=[
            nextcord.SelectOption(
                label="🎮 Comunidad de Streamer",
                value="streamer",
                description="Para comunidades de streamers con chat, gaming y eventos",
                emoji="🎮"
            ),
            nextcord.SelectOption(
                label="🎯 Servidor Gaming",
                value="gaming", 
                description="Para gaming general con LFG y múltiples juegos",
                emoji="🎯"
            ),
            nextcord.SelectOption(
                label="💻 Servidor de Desarrollo",
                value="development",
                description="Para comunidades de desarrolladores y programadores",
                emoji="💻"
            ),
            nextcord.SelectOption(
                label="🌟 Comunidad General",
                value="community",
                description="Para comunidades generales y sociales",
                emoji="🌟"
            )
        ]
    )
    async def select_server_type(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        template_id = select.values[0]
        template = self.wizard.server_templates[template_id]
        
        # Mostrar confirmación
        confirm_embed = nextcord.Embed(
            title=f"⚠️ Confirmar: {template['name']}",
            description=f"¿Estás seguro de que quieres configurar este servidor como **{template['name']}**?\n\n" +
                       f"{template['description']}\n\n" +
                       "**Esto creará:**",
            color=nextcord.Color.orange()
        )
        
        categories_count = len(template['categories'])
        channels_count = sum(len(cat['channels']) for cat in template['categories'])
        roles_count = len(template['roles'])
        
        confirm_embed.add_field(
            name="📊 Elementos a Crear",
            value=f"• {categories_count} categorías\n• {channels_count} canales\n• {roles_count} roles",
            inline=True
        )
        
        confirm_embed.add_field(
            name="⚠️ Advertencia",
            value="Esta acción no se puede deshacer fácilmente.\nAsegúrate de que realmente quieres esto.",
            inline=False
        )
        
        view = ConfirmationView(self.wizard, template_id)
        await interaction.response.edit_message(embed=confirm_embed, view=view)

class ConfirmationView(nextcord.ui.View):
    """Vista de confirmación"""
    
    def __init__(self, setup_wizard: ServerSetupWizard, template_id: str):
        super().__init__(timeout=60)
        self.wizard = setup_wizard
        self.template_id = template_id
    
    @nextcord.ui.button(label="✅ Sí, Configurar", style=nextcord.ButtonStyle.success)
    async def confirm_setup(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.wizard.setup_complete_server(interaction, self.template_id)
    
    @nextcord.ui.button(label="❌ Cancelar", style=nextcord.ButtonStyle.danger)
    async def cancel_setup(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        cancel_embed = nextcord.Embed(
            title="❌ Configuración Cancelada",
            description="La configuración automática ha sido cancelada.",
            color=nextcord.Color.red()
        )
        await interaction.response.edit_message(embed=cancel_embed, view=None)

def setup(bot):
    """Función para añadir el cog al bot"""
    return ServerSetupWizard(bot)
