"""
Sistema de configuración avanzado para servidores de Discord
Permite configurar todos los aspectos del bot mediante comandos slash
"""

import logging
import nextcord
from nextcord.ext import commands
from typing import Optional, List
import json

try:
    from .server_manager import ServerConfigDB
except ImportError:
    from modules.server_manager import ServerConfigDB

logger = logging.getLogger(__name__)

class AdvancedConfig(commands.Cog):
    """Sistema de configuración avanzado del bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = ServerConfigDB()
    
    def has_permission(self, user: nextcord.Member) -> bool:
        """Verifica si el usuario tiene permisos para configurar el bot"""
        return user.guild_permissions.administrator or user.guild_permissions.manage_guild
    
    @nextcord.slash_command(name="serverconfig", description="Sistema de configuración avanzado del bot")
    async def config_main(self, interaction: nextcord.Interaction):
        """Comando principal de configuración avanzada"""
        pass
    
    @config_main.subcommand(name="channels", description="Configura los canales del servidor")
    async def config_channels(
        self,
        interaction: nextcord.Interaction,
        tipo: str = nextcord.SlashOption(
            description="Tipo de canal a configurar",
            choices=[
                "welcome", "goodbye", "logs", "mod_logs", 
                "music", "nsfw", "general", "announcements"
            ]
        ),
        canal: nextcord.TextChannel = nextcord.SlashOption(description="Canal a asignar")
    ):
        """Configura canales específicos del servidor"""
        if not self.has_permission(interaction.user):
            await interaction.response.send_message(
                "❌ No tienes permisos para configurar el bot.",
                ephemeral=True
            )
            return
        
        # Guardar canal en la base de datos
        self.db.set_channel(str(interaction.guild.id), tipo, str(canal.id))
        
        embed = nextcord.Embed(
            title="✅ Canal Configurado",
            description=f"Canal **{tipo}** configurado a {canal.mention}",
            color=nextcord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @config_main.subcommand(name="roles", description="Configura los roles del servidor")
    async def config_roles(
        self,
        interaction: nextcord.Interaction,
        tipo: str = nextcord.SlashOption(
            description="Tipo de rol a configurar",
            choices=["admin", "mod", "muted", "verified", "vip"]
        ),
        rol: nextcord.Role = nextcord.SlashOption(description="Rol a asignar")
    ):
        """Configura roles específicos del servidor"""
        if not self.has_permission(interaction.user):
            await interaction.response.send_message(
                "❌ No tienes permisos para configurar el bot.",
                ephemeral=True
            )
            return
        
        # Guardar rol en la base de datos
        permissions = str(rol.permissions.value)
        self.db.set_role(str(interaction.guild.id), tipo, str(rol.id), permissions)
        
        embed = nextcord.Embed(
            title="✅ Rol Configurado",
            description=f"Rol **{tipo}** configurado a {rol.mention}",
            color=nextcord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @config_main.subcommand(name="settings", description="Configura ajustes generales del bot")
    async def config_settings(
        self,
        interaction: nextcord.Interaction,
        setting: str = nextcord.SlashOption(
            description="Configuración a cambiar",
            choices=[
                "welcome_enabled", "goodbye_enabled", "logging_enabled",
                "moderation_enabled", "music_enabled", "nsfw_enabled",
                "prefix", "language"
            ]
        ),
        valor: str = nextcord.SlashOption(description="Nuevo valor para la configuración")
    ):
        """Configura ajustes generales del bot"""
        if not self.has_permission(interaction.user):
            await interaction.response.send_message(
                "❌ No tienes permisos para configurar el bot.",
                ephemeral=True
            )
            return
        
        # Validaciones específicas
        if setting in ["welcome_enabled", "goodbye_enabled", "logging_enabled", "moderation_enabled", "music_enabled", "nsfw_enabled"]:
            if valor.lower() not in ["true", "false", "sí", "no", "1", "0"]:
                await interaction.response.send_message(
                    "❌ Para configuraciones booleanas usa: true/false, sí/no, o 1/0",
                    ephemeral=True
                )
                return
            valor = str(valor.lower() in ["true", "sí", "1"]).lower()
        
        elif setting == "prefix":
            if len(valor) > 3:
                await interaction.response.send_message(
                    "❌ El prefijo no puede tener más de 3 caracteres.",
                    ephemeral=True
                )
                return
        
        elif setting == "language":
            valid_languages = ["es-ES", "en-US", "fr-FR", "de-DE", "pt-BR"]
            if valor not in valid_languages:
                await interaction.response.send_message(
                    f"❌ Idioma no válido. Idiomas disponibles: {', '.join(valid_languages)}",
                    ephemeral=True
                )
                return
        
        # Guardar configuración
        self.db.set_setting(str(interaction.guild.id), setting, valor)
        
        embed = nextcord.Embed(
            title="✅ Configuración Actualizada",
            description=f"**{setting}** configurado a: `{valor}`",
            color=nextcord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @config_main.subcommand(name="automod", description="Configura el sistema de auto-moderación")
    async def config_automod(
        self,
        interaction: nextcord.Interaction,
        anti_spam: bool = nextcord.SlashOption(description="Activar anti-spam", default=True),
        anti_links: bool = nextcord.SlashOption(description="Activar anti-enlaces", default=False),
        anti_caps: bool = nextcord.SlashOption(description="Activar anti-mayúsculas", default=False),
        bad_words: bool = nextcord.SlashOption(description="Activar filtro de palabras", default=False)
    ):
        """Configura el sistema de auto-moderación"""
        if not self.has_permission(interaction.user):
            await interaction.response.send_message(
                "❌ No tienes permisos para configurar el bot.",
                ephemeral=True
            )
            return
        
        # Guardar configuraciones de automod
        self.db.set_setting(str(interaction.guild.id), "automod_anti_spam", str(anti_spam).lower())
        self.db.set_setting(str(interaction.guild.id), "automod_anti_links", str(anti_links).lower())
        self.db.set_setting(str(interaction.guild.id), "automod_anti_caps", str(anti_caps).lower())
        self.db.set_setting(str(interaction.guild.id), "automod_bad_words", str(bad_words).lower())
        self.db.set_setting(str(interaction.guild.id), "automod_enabled", "true")
        
        embed = nextcord.Embed(
            title="✅ Auto-Moderación Configurada",
            color=nextcord.Color.green()
        )
        embed.add_field(name="🚫 Anti-Spam", value="✅" if anti_spam else "❌", inline=True)
        embed.add_field(name="🔗 Anti-Enlaces", value="✅" if anti_links else "❌", inline=True)
        embed.add_field(name="📢 Anti-Mayúsculas", value="✅" if anti_caps else "❌", inline=True)
        embed.add_field(name="🤬 Filtro Palabras", value="✅" if bad_words else "❌", inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @config_main.subcommand(name="view", description="Ver la configuración actual del servidor")
    async def config_view(self, interaction: nextcord.Interaction):
        """Muestra la configuración actual del servidor"""
        guild_id = str(interaction.guild.id)
        guild = interaction.guild
        
        embed = nextcord.Embed(
            title=f"⚙️ Configuración de {guild.name}",
            color=nextcord.Color.blue()
        )
        
        # Canales configurados
        channels_info = []
        for channel_type in ['welcome', 'goodbye', 'logs', 'mod_logs', 'music', 'nsfw', 'general', 'announcements']:
            channel_id = self.db.get_channel(guild_id, channel_type)
            if channel_id:
                channel = guild.get_channel(int(channel_id))
                if channel:
                    channels_info.append(f"**{channel_type.title()}**: {channel.mention}")
                else:
                    channels_info.append(f"**{channel_type.title()}**: Canal eliminado")
        
        if channels_info:
            embed.add_field(
                name="📝 Canales Configurados",
                value="\n".join(channels_info) if channels_info else "Ninguno configurado",
                inline=False
            )
        
        # Roles configurados
        roles_info = []
        for role_type in ['admin', 'mod', 'muted', 'verified', 'vip']:
            role_id = self.db.get_role(guild_id, role_type)
            if role_id:
                role = guild.get_role(int(role_id))
                if role:
                    roles_info.append(f"**{role_type.title()}**: {role.mention}")
                else:
                    roles_info.append(f"**{role_type.title()}**: Rol eliminado")
        
        if roles_info:
            embed.add_field(
                name="👑 Roles Configurados",
                value="\n".join(roles_info) if roles_info else "Ninguno configurado",
                inline=False
            )
        
        # Configuraciones generales
        settings_info = []
        for setting in ['prefix', 'language', 'welcome_enabled', 'logging_enabled', 'moderation_enabled']:
            value = self.db.get_setting(guild_id, setting, "No configurado")
            settings_info.append(f"**{setting.replace('_', ' ').title()}**: {value}")
        
        embed.add_field(
            name="⚙️ Configuraciones Generales",
            value="\n".join(settings_info),
            inline=False
        )
        
        # Auto-moderación
        automod_info = []
        for setting in ['automod_anti_spam', 'automod_anti_links', 'automod_anti_caps', 'automod_bad_words']:
            value = self.db.get_setting(guild_id, setting, False)
            setting_name = setting.replace('automod_', '').replace('_', ' ').title()
            automod_info.append(f"**{setting_name}**: {'✅' if value else '❌'}")
        
        embed.add_field(
            name="🛡️ Auto-Moderación",
            value="\n".join(automod_info),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @config_main.subcommand(name="reset", description="Restablecer configuración del servidor")
    async def config_reset(self, interaction: nextcord.Interaction):
        """Restablece la configuración del servidor a valores por defecto"""
        if not self.has_permission(interaction.user):
            await interaction.response.send_message(
                "❌ No tienes permisos para configurar el bot.",
                ephemeral=True
            )
            return
        
        # Crear vista de confirmación
        view = ConfirmResetView(self.db, interaction.guild.id)
        
        embed = nextcord.Embed(
            title="⚠️ Confirmar Restablecimiento",
            description="¿Estás seguro de que quieres restablecer toda la configuración del servidor?\n\n**Esto eliminará:**\n• Todos los canales configurados\n• Todos los roles configurados\n• Todas las configuraciones personalizadas\n• Configuraciones de auto-moderación",
            color=nextcord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfirmResetView(nextcord.ui.View):
    """Vista de confirmación para reset de configuración"""
    
    def __init__(self, db: ServerConfigDB, guild_id: str):
        super().__init__(timeout=30)
        self.db = db
        self.guild_id = guild_id
    
    @nextcord.ui.button(label="✅ Confirmar", style=nextcord.ButtonStyle.danger)
    async def confirm_reset(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Confirma el restablecimiento"""
        # Restablecer configuración
        default_config = self.db.get_default_config()
        self.db.save_server_config(self.guild_id, default_config)
        
        embed = nextcord.Embed(
            title="✅ Configuración Restablecida",
            description="La configuración del servidor ha sido restablecida a los valores por defecto.",
            color=nextcord.Color.green()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @nextcord.ui.button(label="❌ Cancelar", style=nextcord.ButtonStyle.secondary)
    async def cancel_reset(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Cancela el restablecimiento"""
        embed = nextcord.Embed(
            title="❌ Restablecimiento Cancelado",
            description="La configuración no ha sido modificada.",
            color=nextcord.Color.red()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)

def setup(bot):
    """Función para añadir el cog al bot"""
    return AdvancedConfig(bot)
