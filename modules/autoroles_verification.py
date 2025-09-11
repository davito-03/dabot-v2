"""
Sistema avanzado de autoroles y verificación
Incluye autoroles por plantillas específicas y canal de verificación con ocultación automática
Por: Davito
"""

import logging
import nextcord
from nextcord.ext import commands
from typing import Dict, List, Optional, Any
import asyncio
import sqlite3
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AutorolesVerification(commands.Cog):
    """Sistema de autoroles y verificación avanzado"""
    
    def __init__(self, bot):
        self.bot = bot
        self.init_database()
        
        # Plantillas de autoroles por tipo de servidor
        self.autorole_templates = {
            "gaming": {
                "name": "🎮 Gaming Server",
                "categories": {
                    "juegos_populares": {
                        "name": "🔥 Juegos Populares",
                        "roles": [
                            {"name": "🎯 Valorant", "color": 0xFF4654, "emoji": "🎯"},
                            {"name": "🌍 Fortnite", "color": 0x00D4FF, "emoji": "🌍"},
                            {"name": "⚡ Apex Legends", "color": 0xFF6600, "emoji": "⚡"},
                            {"name": "🎮 CS2", "color": 0x0066CC, "emoji": "🎮"},
                            {"name": "🏆 League of Legends", "color": 0xC8AA6E, "emoji": "🏆"},
                            {"name": "🎪 Fall Guys", "color": 0xFF69B4, "emoji": "🎪"},
                            {"name": "🚀 Rocket League", "color": 0x0099FF, "emoji": "🚀"},
                            {"name": "🎲 Among Us", "color": 0xFF0000, "emoji": "🎲"}
                        ]
                    },
                    "rangos_valorant": {
                        "name": "⚔️ Rangos Valorant",
                        "roles": [
                            {"name": "🥉 Hierro", "color": 0x8B4513, "emoji": "🥉"},
                            {"name": "🥈 Bronce", "color": 0xCD7F32, "emoji": "🥈"},
                            {"name": "🥇 Plata", "color": 0xC0C0C0, "emoji": "🥇"},
                            {"name": "💎 Oro", "color": 0xFFD700, "emoji": "💎"},
                            {"name": "🏆 Platino", "color": 0x00CED1, "emoji": "🏆"},
                            {"name": "💎 Diamante", "color": 0x6495ED, "emoji": "💎"},
                            {"name": "👑 Inmortal", "color": 0xFF1493, "emoji": "👑"},
                            {"name": "🌟 Radiante", "color": 0xFFFF00, "emoji": "🌟"}
                        ]
                    },
                    "plataformas": {
                        "name": "📱 Plataformas",
                        "roles": [
                            {"name": "🖥️ PC Master Race", "color": 0x00FF00, "emoji": "🖥️"},
                            {"name": "🎮 PlayStation", "color": 0x0070D1, "emoji": "🎮"},
                            {"name": "🎯 Xbox", "color": 0x107C10, "emoji": "🎯"},
                            {"name": "📱 Mobile", "color": 0xFF6B35, "emoji": "📱"},
                            {"name": "🎪 Nintendo Switch", "color": 0xE60012, "emoji": "🎪"}
                        ]
                    }
                }
            },
            "music": {
                "name": "🎵 Music Server",
                "categories": {
                    "generos_principales": {
                        "name": "🎼 Géneros Principales",
                        "roles": [
                            {"name": "🎸 Rock", "color": 0x8B0000, "emoji": "🎸"},
                            {"name": "🎤 Pop", "color": 0xFF69B4, "emoji": "🎤"},
                            {"name": "🎧 Electronic", "color": 0x00BFFF, "emoji": "🎧"},
                            {"name": "🎺 Jazz", "color": 0x8B4513, "emoji": "🎺"},
                            {"name": "🎵 Classical", "color": 0x800080, "emoji": "🎵"},
                            {"name": "🎭 Hip Hop", "color": 0x000000, "emoji": "🎭"},
                            {"name": "🌊 Reggaeton", "color": 0x32CD32, "emoji": "🌊"},
                            {"name": "🔥 Trap", "color": 0xFF4500, "emoji": "🔥"}
                        ]
                    },
                    "subgeneros": {
                        "name": "🎶 Subgéneros",
                        "roles": [
                            {"name": "⚡ Hardstyle", "color": 0xFF0080, "emoji": "⚡"},
                            {"name": "🌙 Lo-fi", "color": 0x9370DB, "emoji": "🌙"},
                            {"name": "🎪 Dubstep", "color": 0x00FF7F, "emoji": "🎪"},
                            {"name": "🎻 Orchestral", "color": 0x4B0082, "emoji": "🎻"},
                            {"name": "🏠 House", "color": 0xFF6347, "emoji": "🏠"},
                            {"name": "🎷 Smooth Jazz", "color": 0xDAA520, "emoji": "🎷"}
                        ]
                    },
                    "actividades": {
                        "name": "🎯 Actividades Musicales",
                        "roles": [
                            {"name": "🎼 Compositor", "color": 0x4169E1, "emoji": "🎼"},
                            {"name": "🎤 Cantante", "color": 0xFF1493, "emoji": "🎤"},
                            {"name": "🎸 Instrumentista", "color": 0x228B22, "emoji": "🎸"},
                            {"name": "🎧 DJ/Producer", "color": 0x00CED1, "emoji": "🎧"},
                            {"name": "👂 Melómano", "color": 0xDDA0DD, "emoji": "👂"}
                        ]
                    }
                }
            },
            "community": {
                "name": "👥 Community Server",
                "categories": {
                    "intereses": {
                        "name": "💡 Intereses",
                        "roles": [
                            {"name": "🎨 Arte", "color": 0xFF69B4, "emoji": "🎨"},
                            {"name": "📚 Lectura", "color": 0x8B4513, "emoji": "📚"},
                            {"name": "🎬 Películas", "color": 0x800080, "emoji": "🎬"},
                            {"name": "📺 Series", "color": 0x0000FF, "emoji": "📺"},
                            {"name": "🍳 Cocina", "color": 0xFF6347, "emoji": "🍳"},
                            {"name": "🏃 Deportes", "color": 0x00FF00, "emoji": "🏃"},
                            {"name": "🧬 Ciencia", "color": 0x00BFFF, "emoji": "🧬"},
                            {"name": "💻 Tecnología", "color": 0x32CD32, "emoji": "💻"}
                        ]
                    },
                    "personalidad": {
                        "name": "🎭 Personalidad",
                        "roles": [
                            {"name": "😄 Extrovertido", "color": 0xFFD700, "emoji": "😄"},
                            {"name": "🤔 Introvertido", "color": 0x9370DB, "emoji": "🤔"},
                            {"name": "🎉 Fiestero", "color": 0xFF4500, "emoji": "🎉"},
                            {"name": "📖 Tranquilo", "color": 0x20B2AA, "emoji": "📖"},
                            {"name": "🤝 Social", "color": 0xFF69B4, "emoji": "🤝"},
                            {"name": "🧘 Zen", "color": 0x7FFF00, "emoji": "🧘"}
                        ]
                    },
                    "zona_horaria": {
                        "name": "🌍 Zona Horaria",
                        "roles": [
                            {"name": "🌅 GMT-5 (Colombia)", "color": 0xFFD700, "emoji": "🌅"},
                            {"name": "🌇 GMT-3 (Argentina)", "color": 0x87CEEB, "emoji": "🌇"},
                            {"name": "🌆 GMT+1 (España)", "color": 0xFF6347, "emoji": "🌆"},
                            {"name": "🌃 GMT-8 (México)", "color": 0x00FA9A, "emoji": "🌃"},
                            {"name": "🌄 GMT-4 (Venezuela)", "color": 0xDDA0DD, "emoji": "🌄"},
                            {"name": "🌉 Otro GMT", "color": 0x696969, "emoji": "🌉"}
                        ]
                    }
                }
            },
            "study": {
                "name": "📚 Study Server",
                "categories": {
                    "materias": {
                        "name": "📖 Materias",
                        "roles": [
                            {"name": "🧮 Matemáticas", "color": 0x0000FF, "emoji": "🧮"},
                            {"name": "🧬 Ciencias", "color": 0x00FF00, "emoji": "🧬"},
                            {"name": "📜 Historia", "color": 0x8B4513, "emoji": "📜"},
                            {"name": "🗣️ Idiomas", "color": 0xFF69B4, "emoji": "🗣️"},
                            {"name": "🎨 Arte", "color": 0xFF6347, "emoji": "🎨"},
                            {"name": "💻 Programación", "color": 0x32CD32, "emoji": "💻"},
                            {"name": "📊 Economía", "color": 0xFFD700, "emoji": "📊"},
                            {"name": "⚖️ Derecho", "color": 0x800080, "emoji": "⚖️"}
                        ]
                    },
                    "nivel_educativo": {
                        "name": "🎓 Nivel Educativo",
                        "roles": [
                            {"name": "🏫 Secundaria", "color": 0x87CEEB, "emoji": "🏫"},
                            {"name": "🎓 Universidad", "color": 0x4169E1, "emoji": "🎓"},
                            {"name": "📚 Postgrado", "color": 0x800080, "emoji": "📚"},
                            {"name": "👨‍🏫 Profesor", "color": 0xFF6347, "emoji": "👨‍🏫"},
                            {"name": "🔬 Investigador", "color": 0x00CED1, "emoji": "🔬"}
                        ]
                    },
                    "metodos_estudio": {
                        "name": "📝 Métodos de Estudio",
                        "roles": [
                            {"name": "👥 Estudio Grupal", "color": 0xFF69B4, "emoji": "👥"},
                            {"name": "🧘 Estudio Individual", "color": 0x9370DB, "emoji": "🧘"},
                            {"name": "🎧 Con Música", "color": 0x00BFFF, "emoji": "🎧"},
                            {"name": "🔇 En Silencio", "color": 0x696969, "emoji": "🔇"},
                            {"name": "☕ Café Lover", "color": 0x8B4513, "emoji": "☕"}
                        ]
                    }
                }
            }
        }
        
        # Sistema de verificación
        self.verification_templates = {
            "simple": {
                "name": "Verificación Simple",
                "description": "Solo requiere reaccionar para verificarse",
                "rules": []
            },
            "captcha": {
                "name": "Verificación con Captcha",
                "description": "Requiere completar un captcha simple",
                "rules": []
            },
            "questions": {
                "name": "Verificación con Preguntas",
                "description": "Requiere responder preguntas sobre las reglas",
                "rules": []
            }
        }
    
    def init_database(self):
        """Inicializar base de datos para autoroles y verificación"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            # Tabla de configuración de autoroles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS autorole_config (
                    guild_id INTEGER PRIMARY KEY,
                    template_type TEXT,
                    enabled_categories TEXT,
                    autorole_channel_id INTEGER,
                    config_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de configuración de verificación
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verification_config (
                    guild_id INTEGER PRIMARY KEY,
                    verification_channel_id INTEGER,
                    verified_role_id INTEGER,
                    verification_type TEXT,
                    welcome_message TEXT,
                    verification_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de usuarios verificados
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verified_users (
                    guild_id INTEGER,
                    user_id INTEGER,
                    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verification_method TEXT,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Base de datos de autoroles y verificación inicializada")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
    
    @nextcord.slash_command(name="autoroles", description="Configurar sistema de autoroles avanzado")
    async def autoroles_setup(self, interaction: nextcord.Interaction):
        """Comando principal para configurar autoroles"""
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ No tienes permisos para gestionar roles.", ephemeral=True)
            return
        
        embed = nextcord.Embed(
            title="🎭 Sistema de Autoroles Avanzado",
            description="Configura autoroles específicos según el tipo de servidor",
            color=nextcord.Color.blue()
        )
        
        view = AutorolesSetupView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @nextcord.slash_command(name="verification", description="Configurar sistema de verificación")
    async def verification_setup(self, interaction: nextcord.Interaction):
        """Comando para configurar el sistema de verificación"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ No tienes permisos para gestionar el servidor.", ephemeral=True)
            return
        
        embed = nextcord.Embed(
            title="🛡️ Sistema de Verificación",
            description="Configura la verificación de nuevos miembros",
            color=nextcord.Color.green()
        )
        
        view = VerificationSetupView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def create_autoroles(self, guild: nextcord.Guild, template_type: str, categories: List[str]) -> Dict[str, Any]:
        """Crear roles automáticamente según la plantilla"""
        if template_type not in self.autorole_templates:
            return {"success": False, "error": "Plantilla no encontrada"}
        
        template = self.autorole_templates[template_type]
        created_roles = {}
        
        try:
            for category_key in categories:
                if category_key not in template["categories"]:
                    continue
                
                category = template["categories"][category_key]
                created_roles[category_key] = []
                
                for role_data in category["roles"]:
                    try:
                        # Verificar si el rol ya existe
                        existing_role = nextcord.utils.get(guild.roles, name=role_data["name"])
                        if existing_role:
                            created_roles[category_key].append(existing_role)
                            continue
                        
                        # Crear nuevo rol
                        role = await guild.create_role(
                            name=role_data["name"],
                            color=nextcord.Color(role_data["color"]),
                            mentionable=True,
                            reason=f"Autorole - {template['name']}"
                        )
                        created_roles[category_key].append(role)
                        
                        # Pequeña pausa para evitar rate limits
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"Error creando rol {role_data['name']}: {e}")
                        continue
            
            return {"success": True, "roles": created_roles}
            
        except Exception as e:
            logger.error(f"Error creando autoroles: {e}")
            return {"success": False, "error": str(e)}
    
    async def setup_autorole_channel(self, guild: nextcord.Guild, template_type: str, created_roles: Dict) -> nextcord.TextChannel:
        """Crear canal de autoroles con mensajes interactivos"""
        try:
            # Crear canal de autoroles
            channel = await guild.create_text_channel(
                name="🎭・autoroles",
                topic="Elige tus roles aquí para personalizar tu experiencia en el servidor",
                reason="Canal de autoroles automático"
            )
            
            template = self.autorole_templates[template_type]
            
            # Mensaje de bienvenida
            welcome_embed = nextcord.Embed(
                title=f"🎭 Autoroles - {template['name']}",
                description="¡Personaliza tu experiencia eligiendo los roles que más te representen!\n\n"
                           "Simplemente haz clic en los botones de abajo para obtener o quitar roles.",
                color=nextcord.Color.blue()
            )
            
            await channel.send(embed=welcome_embed)
            
            # Crear mensajes por categoría
            for category_key, roles in created_roles.items():
                if not roles:
                    continue
                
                category_info = template["categories"][category_key]
                
                embed = nextcord.Embed(
                    title=f"{category_info['name']}",
                    description=f"Elige los roles de esta categoría:",
                    color=nextcord.Color.purple()
                )
                
                # Crear vista con botones para esta categoría
                view = AutoroleView(roles, category_key)
                
                # Añadir información de los roles al embed
                role_list = []
                for role in roles:
                    emoji = None
                    # Buscar emoji en la plantilla
                    for role_data in category_info["roles"]:
                        if role_data["name"] == role.name:
                            emoji = role_data["emoji"]
                            break
                    
                    role_info = f"{emoji} {role.mention}" if emoji else f"• {role.mention}"
                    role_list.append(role_info)
                
                embed.add_field(
                    name="Roles Disponibles:",
                    value="\n".join(role_list[:10]),  # Máximo 10 roles por mensaje
                    inline=False
                )
                
                await channel.send(embed=embed, view=view)
                await asyncio.sleep(1)  # Pausa entre mensajes
            
            return channel
            
        except Exception as e:
            logger.error(f"Error configurando canal de autoroles: {e}")
            return None
    
    async def setup_verification_system(self, guild: nextcord.Guild, verification_type: str) -> Dict[str, Any]:
        """Configurar sistema de verificación completo"""
        try:
            # Crear rol de verificado
            verified_role = await guild.create_role(
                name="✅ Verificado",
                color=nextcord.Color.green(),
                reason="Rol de verificación automática"
            )
            
            # Crear canal de verificación
            verification_channel = await guild.create_text_channel(
                name="🛡️・verificacion",
                topic="Canal de verificación para nuevos miembros",
                reason="Canal de verificación automática"
            )
            
            # Configurar permisos del canal de verificación
            # Solo miembros no verificados pueden ver este canal
            await verification_channel.set_permissions(
                guild.default_role,
                read_messages=False,
                send_messages=False
            )
            
            # Los no verificados pueden ver el canal
            overwrites = {
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                verified_role: nextcord.PermissionOverwrite(read_messages=False)  # Los verificados NO pueden ver
            }
            
            await verification_channel.edit(overwrites=overwrites)
            
            # Configurar el resto del servidor para requerir verificación
            await self.configure_server_permissions(guild, verified_role)
            
            # Crear mensaje de verificación
            await self.create_verification_message(verification_channel, verification_type)
            
            # Guardar configuración en base de datos
            await self.save_verification_config(guild.id, verification_channel.id, verified_role.id, verification_type)
            
            return {
                "success": True,
                "verification_channel": verification_channel,
                "verified_role": verified_role
            }
            
        except Exception as e:
            logger.error(f"Error configurando verificación: {e}")
            return {"success": False, "error": str(e)}
    
    async def configure_server_permissions(self, guild: nextcord.Guild, verified_role: nextcord.Role):
        """Configurar permisos del servidor para requerir verificación"""
        try:
            # Configurar permisos para que solo los verificados puedan ver la mayoría de canales
            for channel in guild.channels:
                if isinstance(channel, nextcord.TextChannel):
                    # Saltar canal de verificación y canales del sistema
                    if "verificacion" in channel.name.lower() or "rules" in channel.name.lower():
                        continue
                    
                    # Configurar permisos
                    await channel.set_permissions(
                        guild.default_role,
                        read_messages=False,
                        send_messages=False
                    )
                    
                    await channel.set_permissions(
                        verified_role,
                        read_messages=True,
                        send_messages=True
                    )
                    
                    await asyncio.sleep(0.5)  # Evitar rate limits
                    
        except Exception as e:
            logger.error(f"Error configurando permisos del servidor: {e}")
    
    async def create_verification_message(self, channel: nextcord.TextChannel, verification_type: str):
        """Crear mensaje de verificación interactivo"""
        try:
            if verification_type == "simple":
                embed = nextcord.Embed(
                    title="🛡️ Verificación Requerida",
                    description="¡Bienvenido al servidor!\n\n"
                               "Para acceder a todos los canales, debes verificarte haciendo clic en el botón de abajo.\n\n"
                               "**¿Por qué verificarse?**\n"
                               "• Protege el servidor contra bots y spam\n"
                               "• Asegura una comunidad de usuarios reales\n"
                               "• Te da acceso completo al servidor",
                    color=nextcord.Color.green()
                )
                
                embed.add_field(
                    name="📋 Proceso de Verificación",
                    value="1️⃣ Lee las reglas del servidor\n"
                          "2️⃣ Haz clic en **Verificarme**\n"
                          "3️⃣ ¡Disfruta del servidor!",
                    inline=False
                )
                
                view = SimpleVerificationView(self)
                
            elif verification_type == "captcha":
                embed = nextcord.Embed(
                    title="🛡️ Verificación con Captcha",
                    description="Para verificarte, deberás completar un captcha simple.",
                    color=nextcord.Color.orange()
                )
                
                view = CaptchaVerificationView(self)
                
            elif verification_type == "questions":
                embed = nextcord.Embed(
                    title="🛡️ Verificación con Preguntas",
                    description="Para verificarte, deberás responder algunas preguntas sobre las reglas.",
                    color=nextcord.Color.red()
                )
                
                view = QuestionVerificationView(self)
            
            embed.set_footer(text="Este canal se ocultará automáticamente una vez te verifiques")
            
            await channel.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error creando mensaje de verificación: {e}")
    
    async def save_verification_config(self, guild_id: int, channel_id: int, role_id: int, verification_type: str):
        """Guardar configuración de verificación en base de datos"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO verification_config 
                (guild_id, verification_channel_id, verified_role_id, verification_type)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, channel_id, role_id, verification_type))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error guardando configuración de verificación: {e}")
    
    async def verify_user(self, interaction: nextcord.Interaction, method: str = "simple"):
        """Verificar un usuario y darle acceso al servidor"""
        try:
            guild = interaction.guild
            user = interaction.user
            
            # Obtener configuración de verificación
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT verified_role_id, verification_channel_id 
                FROM verification_config 
                WHERE guild_id = ?
            ''', (guild.id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                await interaction.response.send_message("❌ Sistema de verificación no configurado.", ephemeral=True)
                return
            
            verified_role_id, verification_channel_id = result
            verified_role = guild.get_role(verified_role_id)
            
            if not verified_role:
                await interaction.response.send_message("❌ Rol de verificación no encontrado.", ephemeral=True)
                return
            
            # Verificar si ya está verificado
            if verified_role in user.roles:
                await interaction.response.send_message("✅ Ya estás verificado.", ephemeral=True)
                return
            
            # Dar rol de verificado
            await user.add_roles(verified_role, reason=f"Verificado mediante {method}")
            
            # Registrar verificación
            await self.save_verified_user(guild.id, user.id, method)
            
            # Responder al usuario
            await interaction.response.send_message(
                f"✅ ¡Verificación completada! Ahora tienes acceso completo al servidor.\n"
                f"El canal de verificación se ocultará automáticamente.",
                ephemeral=True
            )
            
            # Ocultar canal de verificación para este usuario
            verification_channel = guild.get_channel(verification_channel_id)
            if verification_channel:
                await verification_channel.set_permissions(
                    user,
                    read_messages=False,
                    send_messages=False
                )
            
        except Exception as e:
            logger.error(f"Error verificando usuario: {e}")
            await interaction.response.send_message("❌ Error durante la verificación.", ephemeral=True)
    
    async def save_verified_user(self, guild_id: int, user_id: int, method: str):
        """Guardar usuario verificado en base de datos"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO verified_users 
                (guild_id, user_id, verification_method)
                VALUES (?, ?, ?)
            ''', (guild_id, user_id, method))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error guardando usuario verificado: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        """Manejar nuevos miembros para el sistema de verificación"""
        try:
            guild = member.guild
            
            # Verificar si hay sistema de verificación configurado
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT verification_channel_id, welcome_message 
                FROM verification_config 
                WHERE guild_id = ?
            ''', (guild.id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return
            
            verification_channel_id, welcome_message = result
            verification_channel = guild.get_channel(verification_channel_id)
            
            if verification_channel:
                # Dar permisos al nuevo miembro para ver el canal de verificación
                await verification_channel.set_permissions(
                    member,
                    read_messages=True,
                    send_messages=False
                )
                
                # Enviar mensaje de bienvenida si está configurado
                if welcome_message:
                    try:
                        await member.send(welcome_message)
                    except:
                        pass  # No se pudo enviar DM
                        
        except Exception as e:
            logger.error(f"Error manejando nuevo miembro: {e}")


class AutorolesSetupView(nextcord.ui.View):
    """Vista para configurar autoroles"""
    
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
    
    @nextcord.ui.select(
        placeholder="Selecciona el tipo de servidor...",
        options=[
            nextcord.SelectOption(
                label="🎮 Gaming Server",
                value="gaming",
                description="Roles para juegos, rangos y plataformas",
                emoji="🎮"
            ),
            nextcord.SelectOption(
                label="🎵 Music Server", 
                value="music",
                description="Roles para géneros musicales y actividades",
                emoji="🎵"
            ),
            nextcord.SelectOption(
                label="👥 Community Server",
                value="community", 
                description="Roles para intereses y personalidad",
                emoji="👥"
            ),
            nextcord.SelectOption(
                label="📚 Study Server",
                value="study",
                description="Roles para materias y métodos de estudio", 
                emoji="📚"
            )
        ]
    )
    async def select_template(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        template_type = select.values[0]
        template = self.cog.autorole_templates[template_type]
        
        embed = nextcord.Embed(
            title=f"🎭 {template['name']}",
            description="Selecciona las categorías de roles que quieres crear:",
            color=nextcord.Color.blue()
        )
        
        # Crear vista de categorías
        view = CategorySelectionView(self.cog, template_type)
        await interaction.response.edit_message(embed=embed, view=view)


class CategorySelectionView(nextcord.ui.View):
    """Vista para seleccionar categorías de autoroles"""
    
    def __init__(self, cog, template_type):
        super().__init__(timeout=300)
        self.cog = cog
        self.template_type = template_type
        self.selected_categories = []
        
        # Agregar botones para cada categoría
        template = cog.autorole_templates[template_type]
        for category_key, category_data in template["categories"].items():
            button = nextcord.ui.Button(
                label=category_data["name"],
                style=nextcord.ButtonStyle.secondary,
                custom_id=category_key
            )
            button.callback = self.category_callback
            self.add_item(button)
        
        # Botón para confirmar selección
        confirm_button = nextcord.ui.Button(
            label="✅ Crear Autoroles",
            style=nextcord.ButtonStyle.success,
            custom_id="confirm"
        )
        confirm_button.callback = self.confirm_callback
        self.add_item(confirm_button)
    
    async def category_callback(self, interaction: nextcord.Interaction):
        category_key = interaction.data["custom_id"]
        
        if category_key in self.selected_categories:
            self.selected_categories.remove(category_key)
            # Cambiar botón a no seleccionado
            for item in self.children:
                if item.custom_id == category_key:
                    item.style = nextcord.ButtonStyle.secondary
                    break
        else:
            self.selected_categories.append(category_key)
            # Cambiar botón a seleccionado
            for item in self.children:
                if item.custom_id == category_key:
                    item.style = nextcord.ButtonStyle.primary
                    break
        
        template = self.cog.autorole_templates[self.template_type]
        embed = nextcord.Embed(
            title=f"🎭 {template['name']}",
            description=f"Categorías seleccionadas: {len(self.selected_categories)}\n\n" +
                       "\n".join([f"✅ {template['categories'][cat]['name']}" for cat in self.selected_categories]),
            color=nextcord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def confirm_callback(self, interaction: nextcord.Interaction):
        if not self.selected_categories:
            await interaction.response.send_message("❌ Selecciona al menos una categoría.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Crear roles
        result = await self.cog.create_autoroles(interaction.guild, self.template_type, self.selected_categories)
        
        if not result["success"]:
            await interaction.followup.send(f"❌ Error creando roles: {result['error']}")
            return
        
        # Crear canal de autoroles
        channel = await self.cog.setup_autorole_channel(interaction.guild, self.template_type, result["roles"])
        
        if channel:
            embed = nextcord.Embed(
                title="✅ Autoroles Configurados",
                description=f"Se han creado los autoroles y el canal {channel.mention}",
                color=nextcord.Color.green()
            )
            
            total_roles = sum(len(roles) for roles in result["roles"].values())
            embed.add_field(
                name="📊 Estadísticas",
                value=f"• **Categorías:** {len(self.selected_categories)}\n"
                      f"• **Roles creados:** {total_roles}\n"
                      f"• **Canal:** {channel.mention}",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("⚠️ Roles creados pero error configurando canal.")


class AutoroleView(nextcord.ui.View):
    """Vista para botones de autoroles"""
    
    def __init__(self, roles: List[nextcord.Role], category: str):
        super().__init__(timeout=None)
        self.roles = roles
        self.category = category
        
        # Crear botones para cada rol (máximo 25 botones por vista)
        for i, role in enumerate(roles[:25]):
            button = nextcord.ui.Button(
                label=role.name,
                style=nextcord.ButtonStyle.secondary,
                custom_id=f"autorole_{role.id}",
                row=i // 5  # Máximo 5 botones por fila
            )
            button.callback = self.role_callback
            self.add_item(button)
    
    async def role_callback(self, interaction: nextcord.Interaction):
        role_id = int(interaction.data["custom_id"].split("_")[1])
        role = interaction.guild.get_role(role_id)
        
        if not role:
            await interaction.response.send_message("❌ Rol no encontrado.", ephemeral=True)
            return
        
        user = interaction.user
        
        if role in user.roles:
            # Quitar rol
            await user.remove_roles(role, reason="Autorole - Usuario removió rol")
            await interaction.response.send_message(f"➖ Te he quitado el rol {role.mention}", ephemeral=True)
        else:
            # Dar rol
            await user.add_roles(role, reason="Autorole - Usuario pidió rol")
            await interaction.response.send_message(f"➕ Te he dado el rol {role.mention}", ephemeral=True)


class VerificationSetupView(nextcord.ui.View):
    """Vista para configurar verificación"""
    
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
    
    @nextcord.ui.select(
        placeholder="Selecciona el tipo de verificación...",
        options=[
            nextcord.SelectOption(
                label="🟢 Verificación Simple",
                value="simple",
                description="Solo requiere hacer clic en un botón",
                emoji="🟢"
            ),
            nextcord.SelectOption(
                label="🟡 Verificación con Captcha",
                value="captcha",
                description="Requiere completar un captcha",
                emoji="🟡"
            ),
            nextcord.SelectOption(
                label="🔴 Verificación con Preguntas",
                value="questions",
                description="Requiere responder preguntas",
                emoji="🔴"
            )
        ]
    )
    async def select_verification(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        verification_type = select.values[0]
        
        await interaction.response.defer()
        
        # Configurar sistema de verificación
        result = await self.cog.setup_verification_system(interaction.guild, verification_type)
        
        if result["success"]:
            embed = nextcord.Embed(
                title="✅ Verificación Configurada",
                description=f"Sistema de verificación configurado exitosamente",
                color=nextcord.Color.green()
            )
            
            embed.add_field(
                name="📋 Configuración",
                value=f"• **Tipo:** {verification_type.title()}\n"
                      f"• **Canal:** {result['verification_channel'].mention}\n"
                      f"• **Rol:** {result['verified_role'].mention}",
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Importante",
                value="• Los nuevos miembros solo verán el canal de verificación\n"
                      f"• Una vez verificados, el canal se ocultará automáticamente\n"
                      f"• Los miembros verificados tendrán acceso completo al servidor",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ Error configurando verificación: {result['error']}")


class SimpleVerificationView(nextcord.ui.View):
    """Vista para verificación simple"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @nextcord.ui.button(label="✅ Verificarme", style=nextcord.ButtonStyle.success, emoji="✅")
    async def verify_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.cog.verify_user(interaction, "simple")


class CaptchaVerificationView(nextcord.ui.View):
    """Vista para verificación con captcha"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @nextcord.ui.button(label="🔍 Resolver Captcha", style=nextcord.ButtonStyle.primary, emoji="🔍")
    async def captcha_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        # Aquí implementarías el captcha
        # Por simplicidad, usaremos verificación simple
        await self.cog.verify_user(interaction, "captcha")


class QuestionVerificationView(nextcord.ui.View):
    """Vista para verificación con preguntas"""
    
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog
    
    @nextcord.ui.button(label="❓ Responder Preguntas", style=nextcord.ButtonStyle.danger, emoji="❓")
    async def questions_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        # Aquí implementarías las preguntas
        # Por simplicidad, usaremos verificación simple
        await self.cog.verify_user(interaction, "questions")


def setup(bot):
    """Cargar el cog"""
    bot.add_cog(AutorolesVerification(bot))
