"""
Sistema de configuración completa de canales para el bot
Incluye logs, avisos de niveles, y todas las configuraciones posibles
por davito
"""

import json
import os
import nextcord
from nextcord.ext import commands
from nextcord import SlashOption, ChannelType
import logging

logger = logging.getLogger(__name__)

class ChannelConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/channel_config.json"
        self.ensure_data_dir()
        self.load_config()

    def ensure_data_dir(self):
        """Asegurar que existe el directorio de datos"""
        os.makedirs("data", exist_ok=True)

    def load_config(self):
        """Cargar configuración de canales"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
            self.save_config()
        except Exception as e:
            logger.error(f"Error cargando configuración de canales: {e}")
            self.config = {}

    def save_config(self):
        """Guardar configuración de canales"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando configuración de canales: {e}")

    def get_guild_config(self, guild_id):
        """Obtener configuración de un servidor"""
        guild_id = str(guild_id)
        if guild_id not in self.config:
            self.config[guild_id] = {
                "logs": {
                    "moderation": None,      # Logs de moderación (ban, kick, etc)
                    "messages": None,        # Logs de mensajes (editar, borrar)
                    "voice": None,           # Logs de canales de voz
                    "joins": None,           # Logs de entradas/salidas
                    "roles": None,           # Logs de cambios de roles
                    "channels": None,        # Logs de cambios de canales
                    "general": None          # Logs generales
                },
                "notifications": {
                    "level_up": None,        # Avisos de subida de nivel
                    "warnings": None,        # Avisos de warnings
                    "welcome": None,         # Mensajes de bienvenida
                    "goodbye": None,         # Mensajes de despedida
                    "announcements": None    # Anuncios generales
                },
                "features": {
                    "tickets": None,         # Canal para crear tickets
                    "suggestions": None,     # Canal para sugerencias
                    "reports": None,         # Canal para reportes
                    "music_requests": None,  # Canal para pedidos de música
                    "bot_commands": None     # Canal exclusivo para comandos
                },
                "auto_moderation": {
                    "spam_alerts": None,     # Alertas de spam
                    "raid_alerts": None,     # Alertas de raids
                    "automod_log": None      # Log de moderación automática
                }
            }
            self.save_config()
        return self.config[guild_id]

    def set_channel(self, guild_id, category, channel_type, channel_id):
        """Establecer un canal para una categoría específica"""
        config = self.get_guild_config(guild_id)
        if category in config and channel_type in config[category]:
            config[category][channel_type] = channel_id
            self.save_config()
            return True
        return False

    def get_channel(self, guild_id, category, channel_type):
        """Obtener el canal configurado para una categoría específica"""
        config = self.get_guild_config(guild_id)
        if category in config and channel_type in config[category]:
            channel_id = config[category][channel_type]
            if channel_id:
                return self.bot.get_channel(channel_id)
        return None

    @nextcord.slash_command(
        name="config_canales",
        description="Configurar todos los canales del bot"
    )
    async def setup_all_channels(self, interaction: nextcord.Interaction):
        """Comando principal para configurar todos los canales"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ No tienes permisos para usar este comando.", ephemeral=True
            )
            return

        embed = nextcord.Embed(
            title="🔧 Configuración de Canales",
            description="Selecciona qué tipo de canales quieres configurar:",
            color=0x7289DA
        )

        view = ChannelConfigView(self, interaction.guild.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @nextcord.slash_command(
        name="canal_logs",
        description="Configurar canales de logs específicos"
    )
    async def setup_log_channel(
        self,
        interaction: nextcord.Interaction,
        tipo: str = SlashOption(
            description="Tipo de log",
            choices={
                "Moderación": "moderation",
                "Mensajes": "messages", 
                "Voz": "voice",
                "Entradas/Salidas": "joins",
                "Roles": "roles",
                "Canales": "channels",
                "General": "general"
            }
        ),
        canal: nextcord.TextChannel = SlashOption(description="Canal donde enviar los logs")
    ):
        """Configurar un canal de logs específico"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ No tienes permisos para usar este comando.", ephemeral=True
            )
            return

        self.set_channel(interaction.guild.id, "logs", tipo, canal.id)
        
        await interaction.response.send_message(
            f"✅ Canal de logs de **{tipo}** configurado en {canal.mention}",
            ephemeral=True
        )

    @nextcord.slash_command(
        name="canal_notificaciones",
        description="Configurar canales de notificaciones"
    )
    async def setup_notification_channel(
        self,
        interaction: nextcord.Interaction,
        tipo: str = SlashOption(
            description="Tipo de notificación",
            choices={
                "Subida de Nivel": "level_up",
                "Warnings": "warnings",
                "Bienvenida": "welcome",
                "Despedida": "goodbye",
                "Anuncios": "announcements"
            }
        ),
        canal: nextcord.TextChannel = SlashOption(description="Canal para las notificaciones")
    ):
        """Configurar un canal de notificaciones específico"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ No tienes permisos para usar este comando.", ephemeral=True
            )
            return

        self.set_channel(interaction.guild.id, "notifications", tipo, canal.id)
        
        await interaction.response.send_message(
            f"✅ Canal de notificaciones de **{tipo}** configurado en {canal.mention}",
            ephemeral=True
        )

    @nextcord.slash_command(
        name="ver_configuracion",
        description="Ver la configuración actual de canales"
    )
    async def view_config(self, interaction: nextcord.Interaction):
        """Ver la configuración actual de todos los canales"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ No tienes permisos para usar este comando.", ephemeral=True
            )
            return

        config = self.get_guild_config(interaction.guild.id)
        
        embed = nextcord.Embed(
            title="📋 Configuración Actual de Canales",
            color=0x00FF00
        )

        # Logs
        logs_text = ""
        for log_type, channel_id in config["logs"].items():
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                logs_text += f"**{log_type.title()}:** {channel.mention if channel else 'Canal no encontrado'}\n"
            else:
                logs_text += f"**{log_type.title()}:** No configurado\n"
        
        if logs_text:
            embed.add_field(name="📝 Logs", value=logs_text, inline=False)

        # Notificaciones
        notif_text = ""
        for notif_type, channel_id in config["notifications"].items():
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                notif_text += f"**{notif_type.replace('_', ' ').title()}:** {channel.mention if channel else 'Canal no encontrado'}\n"
            else:
                notif_text += f"**{notif_type.replace('_', ' ').title()}:** No configurado\n"
        
        if notif_text:
            embed.add_field(name="🔔 Notificaciones", value=notif_text, inline=False)

        # Características
        features_text = ""
        for feature_type, channel_id in config["features"].items():
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                features_text += f"**{feature_type.replace('_', ' ').title()}:** {channel.mention if channel else 'Canal no encontrado'}\n"
            else:
                features_text += f"**{feature_type.replace('_', ' ').title()}:** No configurado\n"
        
        if features_text:
            embed.add_field(name="⚙️ Características", value=features_text, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

class ChannelConfigView(nextcord.ui.View):
    def __init__(self, channel_config, guild_id):
        super().__init__(timeout=300)
        self.channel_config = channel_config
        self.guild_id = guild_id

    @nextcord.ui.button(label="📝 Logs", style=nextcord.ButtonStyle.primary)
    async def logs_button(self, button, interaction):
        view = LogChannelSelectView(self.channel_config, self.guild_id)
        embed = nextcord.Embed(
            title="📝 Configurar Canales de Logs",
            description="Selecciona el tipo de log que quieres configurar:",
            color=0x7289DA
        )
        await interaction.response.edit_message(embed=embed, view=view)

    @nextcord.ui.button(label="🔔 Notificaciones", style=nextcord.ButtonStyle.success)
    async def notifications_button(self, button, interaction):
        view = NotificationChannelSelectView(self.channel_config, self.guild_id)
        embed = nextcord.Embed(
            title="🔔 Configurar Canales de Notificaciones",
            description="Selecciona el tipo de notificación que quieres configurar:",
            color=0x00FF00
        )
        await interaction.response.edit_message(embed=embed, view=view)

    @nextcord.ui.button(label="⚙️ Características", style=nextcord.ButtonStyle.secondary)
    async def features_button(self, button, interaction):
        view = FeatureChannelSelectView(self.channel_config, self.guild_id)
        embed = nextcord.Embed(
            title="⚙️ Configurar Canales de Características",
            description="Selecciona la característica que quieres configurar:",
            color=0xFFFF00
        )
        await interaction.response.edit_message(embed=embed, view=view)

class LogChannelSelectView(nextcord.ui.View):
    def __init__(self, channel_config, guild_id):
        super().__init__(timeout=300)
        self.channel_config = channel_config
        self.guild_id = guild_id

    @nextcord.ui.select(
        placeholder="Selecciona el tipo de log...",
        options=[
            nextcord.SelectOption(label="Moderación", value="moderation", emoji="🛡️"),
            nextcord.SelectOption(label="Mensajes", value="messages", emoji="💬"),
            nextcord.SelectOption(label="Voz", value="voice", emoji="🔊"),
            nextcord.SelectOption(label="Entradas/Salidas", value="joins", emoji="🚪"),
            nextcord.SelectOption(label="Roles", value="roles", emoji="👑"),
            nextcord.SelectOption(label="Canales", value="channels", emoji="📁"),
            nextcord.SelectOption(label="General", value="general", emoji="📋")
        ]
    )
    async def log_select(self, select, interaction):
        log_type = select.values[0]
        view = ChannelSelectView(self.channel_config, self.guild_id, "logs", log_type)
        
        embed = nextcord.Embed(
            title=f"📝 Configurar Logs de {log_type.title()}",
            description="Selecciona el canal donde quieres que se envíen estos logs:",
            color=0x7289DA
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class NotificationChannelSelectView(nextcord.ui.View):
    def __init__(self, channel_config, guild_id):
        super().__init__(timeout=300)
        self.channel_config = channel_config
        self.guild_id = guild_id

    @nextcord.ui.select(
        placeholder="Selecciona el tipo de notificación...",
        options=[
            nextcord.SelectOption(label="Subida de Nivel", value="level_up", emoji="📈"),
            nextcord.SelectOption(label="Warnings", value="warnings", emoji="⚠️"),
            nextcord.SelectOption(label="Bienvenida", value="welcome", emoji="👋"),
            nextcord.SelectOption(label="Despedida", value="goodbye", emoji="👋"),
            nextcord.SelectOption(label="Anuncios", value="announcements", emoji="📢")
        ]
    )
    async def notification_select(self, select, interaction):
        notif_type = select.values[0]
        view = ChannelSelectView(self.channel_config, self.guild_id, "notifications", notif_type)
        
        embed = nextcord.Embed(
            title=f"🔔 Configurar Notificaciones de {notif_type.replace('_', ' ').title()}",
            description="Selecciona el canal donde quieres que se envíen estas notificaciones:",
            color=0x00FF00
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class FeatureChannelSelectView(nextcord.ui.View):
    def __init__(self, channel_config, guild_id):
        super().__init__(timeout=300)
        self.channel_config = channel_config
        self.guild_id = guild_id

    @nextcord.ui.select(
        placeholder="Selecciona la característica...",
        options=[
            nextcord.SelectOption(label="Tickets", value="tickets", emoji="🎫"),
            nextcord.SelectOption(label="Sugerencias", value="suggestions", emoji="💡"),
            nextcord.SelectOption(label="Reportes", value="reports", emoji="🚨"),
            nextcord.SelectOption(label="Pedidos de Música", value="music_requests", emoji="🎵"),
            nextcord.SelectOption(label="Comandos del Bot", value="bot_commands", emoji="🤖")
        ]
    )
    async def feature_select(self, select, interaction):
        feature_type = select.values[0]
        view = ChannelSelectView(self.channel_config, self.guild_id, "features", feature_type)
        
        embed = nextcord.Embed(
            title=f"⚙️ Configurar {feature_type.replace('_', ' ').title()}",
            description="Selecciona el canal para esta característica:",
            color=0xFFFF00
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class ChannelSelectView(nextcord.ui.View):
    def __init__(self, channel_config, guild_id, category, channel_type):
        super().__init__(timeout=300)
        self.channel_config = channel_config
        self.guild_id = guild_id
        self.category = category
        self.channel_type = channel_type

    @nextcord.ui.channel_select(
        channel_types=[ChannelType.text],
        placeholder="Selecciona un canal...",
        max_values=1
    )
    async def channel_select(self, select, interaction):
        selected_channel = select.values[0]
        
        self.channel_config.set_channel(
            self.guild_id, 
            self.category, 
            self.channel_type, 
            selected_channel.id
        )
        
        embed = nextcord.Embed(
            title="✅ Canal Configurado",
            description=f"**{self.channel_type.replace('_', ' ').title()}** configurado en {selected_channel.mention}",
            color=0x00FF00
        )
        
        await interaction.response.edit_message(embed=embed, view=None)

def setup(bot):
    bot.add_cog(ChannelConfig(bot))
