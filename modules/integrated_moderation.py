"""
Sistema de Moderación Integrado para DaBot v2
Configuración automática de permisos según plantillas
"""

import nextcord
from nextcord.ext import commands
import sqlite3
import json
from datetime import datetime, timedelta

class IntegratedModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_database()
        
    def init_database(self):
        """Inicializar base de datos para moderación"""
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS moderation_config (
                    guild_id INTEGER PRIMARY KEY,
                    template_type TEXT,
                    staff_roles TEXT,
                    mod_permissions TEXT,
                    auto_mod_enabled BOOLEAN DEFAULT 1,
                    log_channel_id INTEGER
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS privilege_system (
                    guild_id INTEGER,
                    level INTEGER,
                    permissions TEXT,
                    PRIMARY KEY (guild_id, level)
                )
            ''')
            conn.commit()

    async def setup_moderation_system(self, guild, template_type):
        """Configurar sistema de moderación según plantilla"""
        
        moderation_configs = {
            "streamer": {
                "staff_roles": ["Owner", "Admin", "Moderador"],
                "permissions": {
                    "Owner": [
                        "administrator",
                        "manage_guild",
                        "manage_roles",
                        "manage_channels",
                        "ban_members",
                        "kick_members",
                        "manage_messages",
                        "mute_members",
                        "all_bot_commands"
                    ],
                    "Admin": [
                        "manage_channels",
                        "ban_members", 
                        "kick_members",
                        "manage_messages",
                        "mute_members",
                        "timeout_members",
                        "advanced_bot_commands"
                    ],
                    "Moderador": [
                        "kick_members",
                        "manage_messages",
                        "mute_members",
                        "timeout_members",
                        "basic_bot_commands"
                    ]
                },
                "level_privileges": {
                    5: ["send_messages"],
                    10: ["change_nickname"],
                    20: ["attach_files", "embed_links"],
                    35: ["external_emojis", "use_voice_activation"],
                    50: ["add_reactions", "send_messages_in_threads"],
                    75: ["create_public_threads", "manage_threads"],
                    100: ["mention_everyone"]
                }
            },
            "gaming": {
                "staff_roles": ["Owner", "Admin", "Moderador"],
                "permissions": {
                    "Owner": [
                        "administrator",
                        "manage_guild",
                        "manage_roles",
                        "manage_channels",
                        "ban_members",
                        "kick_members",
                        "manage_messages",
                        "mute_members",
                        "all_bot_commands"
                    ],
                    "Admin": [
                        "manage_channels",
                        "ban_members",
                        "kick_members", 
                        "manage_messages",
                        "mute_members",
                        "timeout_members",
                        "move_members",
                        "advanced_bot_commands"
                    ],
                    "Moderador": [
                        "kick_members",
                        "manage_messages",
                        "mute_members",
                        "timeout_members",
                        "move_members",
                        "basic_bot_commands"
                    ]
                },
                "level_privileges": {
                    5: ["send_messages", "connect"],
                    15: ["change_nickname", "speak"],
                    30: ["attach_files", "embed_links", "stream"],
                    50: ["external_emojis", "use_voice_activation"],
                    75: ["add_reactions", "priority_speaker"],
                    100: ["create_public_threads"],
                    150: ["mention_everyone", "manage_threads"]
                }
            },
            "desarrollo": {
                "staff_roles": ["Owner", "Admin", "Moderador"],
                "permissions": {
                    "Owner": [
                        "administrator",
                        "manage_guild",
                        "manage_roles", 
                        "manage_channels",
                        "ban_members",
                        "kick_members",
                        "manage_messages",
                        "all_bot_commands"
                    ],
                    "Admin": [
                        "manage_channels",
                        "ban_members",
                        "kick_members",
                        "manage_messages",
                        "timeout_members",
                        "advanced_bot_commands"
                    ],
                    "Moderador": [
                        "kick_members",
                        "manage_messages",
                        "timeout_members",
                        "basic_bot_commands"
                    ]
                },
                "level_privileges": {
                    5: ["send_messages", "read_message_history"],
                    15: ["change_nickname", "attach_files"],
                    30: ["embed_links", "external_emojis"],
                    50: ["add_reactions", "use_slash_commands"],
                    75: ["create_public_threads", "send_messages_in_threads"],
                    100: ["manage_threads", "create_private_threads"],
                    150: ["mention_everyone"]
                }
            },
            "general": {
                "staff_roles": ["Owner", "Admin", "Moderador"],
                "permissions": {
                    "Owner": [
                        "administrator",
                        "manage_guild",
                        "manage_roles",
                        "manage_channels", 
                        "ban_members",
                        "kick_members",
                        "manage_messages",
                        "all_bot_commands"
                    ],
                    "Admin": [
                        "manage_channels",
                        "ban_members",
                        "kick_members",
                        "manage_messages",
                        "timeout_members",
                        "advanced_bot_commands"
                    ],
                    "Moderador": [
                        "manage_messages",
                        "timeout_members",
                        "basic_bot_commands"
                    ]
                },
                "level_privileges": {
                    5: ["send_messages"],
                    15: ["change_nickname", "attach_files"],
                    30: ["embed_links", "external_emojis"],
                    50: ["add_reactions", "connect", "speak"],
                    75: ["create_public_threads", "stream"],
                    100: ["priority_speaker", "manage_threads"],
                    150: ["mention_everyone"]
                }
            }
        }
        
        config = moderation_configs.get(template_type, moderation_configs["general"])
        
        # Configurar permisos de roles de staff
        await self.setup_staff_permissions(guild, config)
        
        # Configurar sistema de privilegios por nivel
        await self.setup_level_privileges(guild, config["level_privileges"])
        
        # Buscar o crear canal de logs
        log_channel = await self.setup_log_channel(guild)
        
        # Guardar configuración en base de datos
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO moderation_config 
                (guild_id, template_type, staff_roles, mod_permissions, auto_mod_enabled, log_channel_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                guild.id, 
                template_type,
                json.dumps(config["staff_roles"]),
                json.dumps(config["permissions"]),
                True,
                log_channel.id if log_channel else None
            ))
            conn.commit()
        
        return True

    async def setup_staff_permissions(self, guild, config):
        """Configurar permisos de roles de staff"""
        permission_mapping = {
            "manage_guild": nextcord.Permissions(manage_guild=True),
            "manage_roles": nextcord.Permissions(manage_roles=True),
            "manage_channels": nextcord.Permissions(manage_channels=True),
            "ban_members": nextcord.Permissions(ban_members=True),
            "kick_members": nextcord.Permissions(kick_members=True),
            "manage_messages": nextcord.Permissions(manage_messages=True),
            "mute_members": nextcord.Permissions(mute_members=True),
            "timeout_members": nextcord.Permissions(moderate_members=True),
            "move_members": nextcord.Permissions(move_members=True),
            "administrator": nextcord.Permissions(administrator=True)
        }
        
        for role_name, permissions in config["permissions"].items():
            # Buscar el rol
            role = nextcord.utils.get(guild.roles, name=role_name)
            if not role:
                continue
            
            # Crear permisos combinados
            combined_perms = nextcord.Permissions.none()
            
            for perm in permissions:
                if perm in permission_mapping:
                    combined_perms.update(**permission_mapping[perm].to_dict())
                elif perm == "all_bot_commands":
                    # Permisos especiales para comandos del bot
                    combined_perms.update(
                        manage_messages=True,
                        manage_roles=True,
                        manage_channels=True,
                        ban_members=True,
                        kick_members=True,
                        moderate_members=True
                    )
                elif perm == "advanced_bot_commands":
                    combined_perms.update(
                        manage_messages=True,
                        ban_members=True,
                        kick_members=True,
                        moderate_members=True
                    )
                elif perm == "basic_bot_commands":
                    combined_perms.update(
                        manage_messages=True,
                        moderate_members=True
                    )
            
            # Aplicar permisos al rol
            try:
                await role.edit(permissions=combined_perms, reason="Configuración automática de moderación")
            except Exception as e:
                print(f"Error configurando permisos para {role_name}: {e}")

    async def setup_level_privileges(self, guild, level_privileges):
        """Configurar privilegios por nivel"""
        
        # Crear overrides para canales según nivel
        permission_mapping = {
            "send_messages": {"send_messages": True},
            "attach_files": {"attach_files": True},
            "embed_links": {"embed_links": True},
            "external_emojis": {"use_external_emojis": True},
            "add_reactions": {"add_reactions": True},
            "change_nickname": {"change_nickname": True},
            "connect": {"connect": True},
            "speak": {"speak": True},
            "stream": {"stream": True},
            "use_voice_activation": {"use_voice_activation": True},
            "priority_speaker": {"priority_speaker": True},
            "create_public_threads": {"create_public_threads": True},
            "send_messages_in_threads": {"send_messages_in_threads": True},
            "manage_threads": {"manage_threads": True},
            "create_private_threads": {"create_private_threads": True},
            "mention_everyone": {"mention_everyone": True},
            "read_message_history": {"read_message_history": True},
            "use_slash_commands": {"use_application_commands": True}
        }
        
        # Guardar privilegios en base de datos
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            for level, privileges in level_privileges.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO privilege_system 
                    (guild_id, level, permissions)
                    VALUES (?, ?, ?)
                ''', (guild.id, level, json.dumps(privileges)))
            conn.commit()

    async def setup_log_channel(self, guild):
        """Configurar canal de logs de moderación"""
        # Buscar canal existente
        log_channel = None
        for channel in guild.text_channels:
            if any(name in channel.name.lower() for name in ["logs", "mod-logs", "moderacion"]):
                log_channel = channel
                break
        
        if log_channel:
            return log_channel
        
        # Si no existe, buscar categoría de staff
        staff_category = None
        for category in guild.categories:
            if "staff" in category.name.lower():
                staff_category = category
                break
        
        return log_channel

    async def apply_level_permissions(self, guild, user, level):
        """Aplicar permisos según el nivel del usuario"""
        
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT permissions FROM privilege_system 
                WHERE guild_id = ? AND level <= ?
                ORDER BY level DESC
            ''', (guild.id, level))
            
            all_permissions = []
            for row in cursor.fetchall():
                all_permissions.extend(json.loads(row[0]))
            
            # Aplicar permisos a canales específicos
            await self.update_user_permissions(guild, user, all_permissions)

    async def update_user_permissions(self, guild, user, permissions):
        """Actualizar permisos de usuario en canales"""
        
        permission_mapping = {
            "send_messages": {"send_messages": True},
            "attach_files": {"attach_files": True}, 
            "embed_links": {"embed_links": True},
            "external_emojis": {"use_external_emojis": True},
            "add_reactions": {"add_reactions": True},
            "connect": {"connect": True},
            "speak": {"speak": True},
            "stream": {"stream": True},
            "mention_everyone": {"mention_everyone": True}
        }
        
        # Aplicar permisos solo a canales generales (no staff)
        general_channels = []
        for channel in guild.text_channels + guild.voice_channels:
            if not any(name in channel.name.lower() for name in ["staff", "mod", "admin"]):
                general_channels.append(channel)
        
        for channel in general_channels:
            try:
                # Obtener overrides actuales
                overwrites = channel.overwrites_for(user)
                
                # Aplicar nuevos permisos
                for perm in permissions:
                    if perm in permission_mapping:
                        overwrites.update(**permission_mapping[perm])
                
                # Solo actualizar si hay cambios
                if overwrites != channel.overwrites_for(user):
                    await channel.set_permissions(user, overwrite=overwrites, reason=f"Privilegios de nivel {await self.get_user_level(guild.id, user.id)}")
                
            except Exception as e:
                print(f"Error aplicando permisos en {channel.name}: {e}")

    async def get_user_level(self, guild_id, user_id):
        """Obtener nivel de usuario"""
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT level FROM user_levels WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            result = cursor.fetchone()
            return result[0] if result else 0

    async def check_staff_permissions(self, user, action):
        """Verificar si el usuario tiene permisos para una acción"""
        if not user.guild:
            return False
        
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT mod_permissions FROM moderation_config WHERE guild_id = ?
            ''', (user.guild.id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            permissions = json.loads(result[0])
            
            # Verificar permisos por rol
            for role in user.roles:
                if role.name in permissions:
                    if action in permissions[role.name]:
                        return True
            
            return False

def setup(bot):
    bot.add_cog(IntegratedModeration(bot))
