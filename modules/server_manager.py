"""
Sistema de gestión de configuración persistente para servidores
Guarda configuraciones en base de datos SQLite
"""

import sqlite3
import json
import logging
import asyncio
import nextcord
from nextcord.ext import commands
from typing import Dict, Any, Optional, List
import os

logger = logging.getLogger(__name__)

class ServerConfigDB:
    """Clase para manejar la base de datos de configuraciones de servidor"""
    
    def __init__(self, db_path: str = "data/server_configs.db"):
        self.db_path = db_path
        self.ensure_data_dir()
        self.init_database()
    
    def ensure_data_dir(self):
        """Asegura que el directorio de datos existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla principal de configuraciones de servidor
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server_configs (
                    guild_id TEXT PRIMARY KEY,
                    config_data TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de canales especiales
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server_channels (
                    guild_id TEXT,
                    channel_type TEXT,
                    channel_id TEXT,
                    PRIMARY KEY (guild_id, channel_type)
                )
            ''')
            
            # Tabla de roles especiales
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server_roles (
                    guild_id TEXT,
                    role_type TEXT,
                    role_id TEXT,
                    permissions TEXT,
                    PRIMARY KEY (guild_id, role_type)
                )
            ''')
            
            # Tabla de configuraciones específicas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server_settings (
                    guild_id TEXT,
                    setting_key TEXT,
                    setting_value TEXT,
                    PRIMARY KEY (guild_id, setting_key)
                )
            ''')
            
            conn.commit()
    
    def save_server_config(self, guild_id: str, config: Dict[str, Any]):
        """Guarda la configuración completa de un servidor"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_configs (guild_id, config_data)
                VALUES (?, ?)
            ''', (guild_id, json.dumps(config)))
            conn.commit()
    
    def get_server_config(self, guild_id: str) -> Dict[str, Any]:
        """Obtiene la configuración completa de un servidor"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT config_data FROM server_configs WHERE guild_id = ?
            ''', (guild_id,))
            result = cursor.fetchone()
            
            if result:
                return json.loads(result[0])
            else:
                # Configuración por defecto
                return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Obtiene la configuración por defecto para un servidor nuevo"""
        return {
            "channels": {
                "welcome": None,
                "goodbye": None,
                "logs": None,
                "mod_logs": None,
                "music": None,
                "nsfw": None,
                "general": None,
                "announcements": None
            },
            "roles": {
                "admin": [],
                "mod": [],
                "muted": None,
                "verified": None,
                "vip": None
            },
            "settings": {
                "auto_role": None,
                "welcome_enabled": True,
                "goodbye_enabled": True,
                "logging_enabled": True,
                "moderation_enabled": True,
                "music_enabled": True,
                "nsfw_enabled": True,
                "prefix": "!",
                "language": "es-ES"
            },
            "automod": {
                "enabled": False,
                "anti_spam": True,
                "anti_links": False,
                "anti_caps": False,
                "bad_words_filter": False
            }
        }
    
    def set_channel(self, guild_id: str, channel_type: str, channel_id: str):
        """Establece un canal especial para el servidor"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_channels (guild_id, channel_type, channel_id)
                VALUES (?, ?, ?)
            ''', (guild_id, channel_type, channel_id))
            conn.commit()
    
    def get_channel(self, guild_id: str, channel_type: str) -> Optional[str]:
        """Obtiene el ID de un canal especial"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT channel_id FROM server_channels 
                WHERE guild_id = ? AND channel_type = ?
            ''', (guild_id, channel_type))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def set_role(self, guild_id: str, role_type: str, role_id: str, permissions: str = ""):
        """Establece un rol especial para el servidor"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_roles (guild_id, role_type, role_id, permissions)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, role_type, role_id, permissions))
            conn.commit()
    
    def get_role(self, guild_id: str, role_type: str) -> Optional[str]:
        """Obtiene el ID de un rol especial"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role_id FROM server_roles 
                WHERE guild_id = ? AND role_type = ?
            ''', (guild_id, role_type))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def set_setting(self, guild_id: str, setting_key: str, setting_value: str):
        """Establece una configuración específica"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO server_settings (guild_id, setting_key, setting_value)
                VALUES (?, ?, ?)
            ''', (guild_id, setting_key, setting_value))
            conn.commit()
    
    def get_setting(self, guild_id: str, setting_key: str, default: Any = None) -> Any:
        """Obtiene una configuración específica"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT setting_value FROM server_settings 
                WHERE guild_id = ? AND setting_key = ?
            ''', (guild_id, setting_key))
            result = cursor.fetchone()
            
            if result:
                # Intenta convertir a tipo original
                value = result[0]
                if value.lower() in ['true', 'false']:
                    return value.lower() == 'true'
                elif value.isdigit():
                    return int(value)
                else:
                    return value
            return default

class ServerManager(commands.Cog):
    """Sistema de gestión y configuración automática de servidores"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = ServerConfigDB()
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Se ejecuta cuando el bot se une a un servidor"""
        logger.info(f"Bot añadido al servidor: {guild.name} (ID: {guild.id})")
        
        # Crear configuración inicial
        config = self.db.get_default_config()
        self.db.save_server_config(str(guild.id), config)
        
        # Intentar detectar canales automáticamente
        await self.auto_detect_channels(guild)
        
        # Enviar mensaje de bienvenida si hay un canal general
        await self.send_welcome_message(guild)
    
    async def auto_detect_channels(self, guild: nextcord.Guild):
        """Detecta automáticamente canales importantes del servidor"""
        try:
            # Detectar canal general
            general_channel = None
            for channel in guild.text_channels:
                if channel.name.lower() in ['general', 'chat', 'inicio', 'main']:
                    general_channel = channel
                    self.db.set_channel(str(guild.id), 'general', str(channel.id))
                    break
            
            # Detectar canal de bienvenida
            welcome_channel = None
            for channel in guild.text_channels:
                if any(word in channel.name.lower() for word in ['welcome', 'bienvenida', 'entrada']):
                    welcome_channel = channel
                    self.db.set_channel(str(guild.id), 'welcome', str(channel.id))
                    break
            
            # Detectar canal de logs
            logs_channel = None
            for channel in guild.text_channels:
                if any(word in channel.name.lower() for word in ['logs', 'registro', 'audit']):
                    logs_channel = channel
                    self.db.set_channel(str(guild.id), 'logs', str(channel.id))
                    break
            
            # Detectar canal NSFW
            nsfw_channel = None
            for channel in guild.text_channels:
                if channel.is_nsfw() or 'nsfw' in channel.name.lower():
                    nsfw_channel = channel
                    self.db.set_channel(str(guild.id), 'nsfw', str(channel.id))
                    break
            
            # Detectar roles importantes
            await self.auto_detect_roles(guild)
            
            logger.info(f"Auto-detección completada para {guild.name}")
            
        except Exception as e:
            logger.error(f"Error en auto-detección para {guild.name}: {e}")
    
    async def auto_detect_roles(self, guild: nextcord.Guild):
        """Detecta automáticamente roles importantes del servidor"""
        try:
            # Detectar rol de administrador
            for role in guild.roles:
                if role.permissions.administrator and not role.is_bot_managed():
                    self.db.set_role(str(guild.id), 'admin', str(role.id))
                    break
            
            # Detectar rol de moderador
            for role in guild.roles:
                if (role.permissions.manage_messages or role.permissions.kick_members) and not role.permissions.administrator:
                    self.db.set_role(str(guild.id), 'mod', str(role.id))
                    break
            
            # Detectar rol muted
            for role in guild.roles:
                if 'muted' in role.name.lower() or 'silenciado' in role.name.lower():
                    self.db.set_role(str(guild.id), 'muted', str(role.id))
                    break
            
        except Exception as e:
            logger.error(f"Error detectando roles en {guild.name}: {e}")
    
    async def send_welcome_message(self, guild: nextcord.Guild):
        """Envía mensaje de bienvenida cuando el bot se une al servidor"""
        try:
            # Buscar canal para enviar mensaje
            channel = None
            
            # Intentar usar canal general detectado
            general_id = self.db.get_channel(str(guild.id), 'general')
            if general_id:
                channel = guild.get_channel(int(general_id))
            
            # Si no hay canal general, usar el primer canal disponible
            if not channel:
                for c in guild.text_channels:
                    if c.permissions_for(guild.me).send_messages:
                        channel = c
                        break
            
            if channel:
                embed = nextcord.Embed(
                    title="🤖 ¡Hola! Soy DABOT V2",
                    description="¡Gracias por añadirme a tu servidor!",
                    color=nextcord.Color.blue()
                )
                embed.add_field(
                    name="🚀 ¿Qué puedo hacer?",
                    value="• Moderación avanzada\n• Sistema de música\n• Comandos de diversión\n• Sistema de niveles\n• Y mucho más!",
                    inline=False
                )
                embed.add_field(
                    name="⚙️ Configuración",
                    value="Usa `/setup` para configurar el bot automáticamente\nO `/config` para configuración manual",
                    inline=False
                )
                embed.add_field(
                    name="📚 Ayuda",
                    value="Usa `/help` para ver todos mis comandos",
                    inline=False
                )
                embed.set_thumbnail(url=self.bot.user.display_avatar.url)
                
                await channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error enviando mensaje de bienvenida: {e}")
    
    @nextcord.slash_command(name="setup", description="Configuración automática del bot para este servidor")
    async def auto_setup(self, interaction: nextcord.Interaction):
        """Comando para configuración automática del servidor"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitas permisos de administrador para usar este comando.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            
            # Re-ejecutar detección automática
            await self.auto_detect_channels(guild)
            
            # Crear embed con configuración detectada
            embed = nextcord.Embed(
                title="🔧 Configuración Automática Completada",
                description="He detectado y configurado automáticamente los siguientes elementos:",
                color=nextcord.Color.green()
            )
            
            # Mostrar canales detectados
            channels_info = []
            for channel_type in ['general', 'welcome', 'logs', 'nsfw']:
                channel_id = self.db.get_channel(str(guild.id), channel_type)
                if channel_id:
                    channel = guild.get_channel(int(channel_id))
                    if channel:
                        channels_info.append(f"**{channel_type.title()}**: {channel.mention}")
            
            if channels_info:
                embed.add_field(
                    name="📝 Canales Detectados",
                    value="\n".join(channels_info),
                    inline=False
                )
            
            # Mostrar roles detectados
            roles_info = []
            for role_type in ['admin', 'mod', 'muted']:
                role_id = self.db.get_role(str(guild.id), role_type)
                if role_id:
                    role = guild.get_role(int(role_id))
                    if role:
                        roles_info.append(f"**{role_type.title()}**: {role.mention}")
            
            if roles_info:
                embed.add_field(
                    name="👑 Roles Detectados",
                    value="\n".join(roles_info),
                    inline=False
                )
            
            embed.add_field(
                name="✅ ¿Qué puedes hacer ahora?",
                value="• Usar `/config` para ajustes manuales\n• Los comandos del bot ya funcionan\n• El sistema de logs está activo\n• La moderación está configurada",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en setup automático: {e}")
            await interaction.followup.send("❌ Ocurrió un error durante la configuración automática.")

def setup(bot):
    """Función para añadir el cog al bot"""
    return ServerManager(bot)
