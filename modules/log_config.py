"""
Sistema de configuración de logs para el bot
por davito
"""

import json
import logging
import os
import nextcord
from nextcord.ext import commands
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class LogConfig(commands.Cog):
    """configuración de canales de log"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/log_config.json"
        self.log_channels: Dict[int, Dict[str, int]] = {}
        
        # crear directorio si no existe
        os.makedirs("data", exist_ok=True)
        
        # cargar configuración
        self.load_config()
    
    def load_config(self):
        """cargar configuración de logs"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # convertir keys a int
                    self.log_channels = {int(k): v for k, v in data.items()}
            else:
                self.log_channels = {}
                logger.info("archivo de configuración de logs no encontrado, creando nuevo")
        except Exception as e:
            logger.error(f"error cargando configuración de logs: {e}")
            self.log_channels = {}
    
    def save_config(self):
        """guardar configuración de logs"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.log_channels, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando configuración de logs: {e}")
    
    def get_log_channel(self, guild_id: int, log_type: str) -> Optional[int]:
        """obtener canal de log para un tipo específico"""
        guild_config = self.log_channels.get(guild_id, {})
        return guild_config.get(log_type)
    
    def set_log_channel(self, guild_id: int, log_type: str, channel_id: int):
        """configurar canal de log para un tipo específico"""
        if guild_id not in self.log_channels:
            self.log_channels[guild_id] = {}
        
        self.log_channels[guild_id][log_type] = channel_id
        self.save_config()
    
    @nextcord.slash_command(name="setup_logs", description="Configurar canales de logs del servidor")
    async def setup_logs(self, interaction: nextcord.Interaction):
        """comando para configurar logs"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ necesitas permisos de administrador.", ephemeral=True)
            return
        
        embed = nextcord.Embed(
            title="⚙️ configuración de logs",
            description="usa los botones para configurar cada tipo de log:",
            color=nextcord.Color.blue()
        )
        
        guild_config = self.log_channels.get(interaction.guild.id, {})
        
        # mostrar configuración actual
        config_text = ""
        log_types = {
            "moderation": "🛡️ moderación",
            "joins": "👋 entradas/salidas", 
            "messages": "💬 mensajes",
            "voice": "🔊 canales de voz",
            "roles": "🎭 cambios de roles",
            "channels": "📝 cambios de canales"
        }
        
        for log_type, display_name in log_types.items():
            channel_id = guild_config.get(log_type)
            if channel_id:
                channel = interaction.guild.get_channel(channel_id)
                channel_mention = channel.mention if channel else "canal eliminado"
                config_text += f"{display_name}: {channel_mention}\n"
            else:
                config_text += f"{display_name}: no configurado\n"
        
        embed.add_field(name="configuración actual:", value=config_text or "ningún log configurado", inline=False)
        
        view = LogConfigView(self, interaction.guild.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class LogConfigView(nextcord.ui.View):
    """vista con botones para configurar logs"""
    
    def __init__(self, log_config: LogConfig, guild_id: int):
        super().__init__(timeout=300)
        self.log_config = log_config
        self.guild_id = guild_id
    
    @nextcord.ui.button(label="🛡️ moderación", style=nextcord.ButtonStyle.primary)
    async def config_moderation(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.show_channel_select(interaction, "moderation", "🛡️ logs de moderación")
    
    @nextcord.ui.button(label="👋 entradas/salidas", style=nextcord.ButtonStyle.primary)
    async def config_joins(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.show_channel_select(interaction, "joins", "👋 logs de entradas/salidas")
    
    @nextcord.ui.button(label="💬 mensajes", style=nextcord.ButtonStyle.primary)
    async def config_messages(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.show_channel_select(interaction, "messages", "💬 logs de mensajes")
    
    @nextcord.ui.button(label="🔊 voz", style=nextcord.ButtonStyle.primary)
    async def config_voice(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.show_channel_select(interaction, "voice", "🔊 logs de canales de voz")
    
    @nextcord.ui.button(label="🎭 roles", style=nextcord.ButtonStyle.primary)
    async def config_roles(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.show_channel_select(interaction, "roles", "🎭 logs de cambios de roles")
    
    async def show_channel_select(self, interaction: nextcord.Interaction, log_type: str, display_name: str):
        """mostrar selector de canal"""
        select = ChannelSelect(self.log_config, self.guild_id, log_type, display_name)
        view = nextcord.ui.View()
        view.add_item(select)
        
        await interaction.response.send_message(
            f"selecciona el canal para {display_name}:",
            view=view,
            ephemeral=True
        )

class ChannelSelect(nextcord.ui.ChannelSelect):
    """selector de canal para logs"""
    
    def __init__(self, log_config: LogConfig, guild_id: int, log_type: str, display_name: str):
        super().__init__(
            placeholder=f"seleccionar canal para {display_name}",
            channel_types=[nextcord.ChannelType.text]
        )
        self.log_config = log_config
        self.guild_id = guild_id
        self.log_type = log_type
        self.display_name = display_name
    
    async def callback(self, interaction: nextcord.Interaction):
        channel = self.values[0]
        
        # configurar canal
        self.log_config.set_log_channel(self.guild_id, self.log_type, channel.id)
        
        embed = nextcord.Embed(
            title="✅ configuración guardada",
            description=f"{self.display_name} configurado en {channel.mention}",
            color=nextcord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    """función para cargar el cog"""
    return LogConfig(bot)
