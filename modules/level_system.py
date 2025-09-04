"""
Sistema de niveles y experiencia para el bot
por davito
"""

import json
import logging
import os
import random
import math
from datetime import datetime, timedelta
import nextcord
from nextcord.ext import commands
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class LevelSystem(commands.Cog):
    """sistema de niveles y experiencia"""
    
    def __init__(self, bot):
        self.bot = bot
        self.levels_file = "data/levels.json"
        self.config_file = "data/level_config.json"
        self.user_data: Dict[str, Dict[str, Dict]] = {}
        self.guild_configs: Dict[str, Dict] = {}
        self.cooldowns: Dict[str, datetime] = {}
        
        # configuración por defecto
        self.default_config = {
            "enabled": True,
            "xp_per_message": {"min": 15, "max": 25},
            "xp_cooldown": 60,  # segundos
            "level_up_channel": None,
            "level_roles": {},  # {nivel: rol_id}
            "xp_multiplier": 1.0
        }
        
        # crear directorio si no existe
        os.makedirs("data", exist_ok=True)
        
        # cargar datos
        self.load_data()
        self.load_config()
    
    def load_data(self):
        """cargar datos de niveles"""
        try:
            if os.path.exists(self.levels_file):
                with open(self.levels_file, 'r', encoding='utf-8') as f:
                    self.user_data = json.load(f)
            else:
                self.user_data = {}
                logger.info("archivo de niveles no encontrado, creando nuevo")
        except Exception as e:
            logger.error(f"error cargando datos de niveles: {e}")
            self.user_data = {}
    
    def load_config(self):
        """cargar configuración de niveles"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.guild_configs = json.load(f)
            else:
                self.guild_configs = {}
                logger.info("configuración de niveles no encontrada, usando por defecto")
        except Exception as e:
            logger.error(f"error cargando configuración de niveles: {e}")
            self.guild_configs = {}
    
    def save_data(self):
        """guardar datos de niveles"""
        try:
            with open(self.levels_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando datos de niveles: {e}")
    
    def save_config(self):
        """guardar configuración de niveles"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.guild_configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando configuración de niveles: {e}")
    
    def get_guild_config(self, guild_id: int) -> Dict:
        """obtener configuración del guild"""
        config = self.guild_configs.get(str(guild_id), self.default_config.copy())
        # asegurar que tiene todas las claves
        for key, value in self.default_config.items():
            if key not in config:
                config[key] = value
        return config
    
    def calculate_level(self, xp: int) -> int:
        """calcular nivel basado en experiencia"""
        # fórmula: nivel = floor(sqrt(xp / 100))
        return int(math.sqrt(xp / 100))
    
    def calculate_xp_for_level(self, level: int) -> int:
        """calcular xp necesaria para un nivel"""
        return (level ** 2) * 100
    
    def get_user_data(self, guild_id: int, user_id: int) -> Dict:
        """obtener datos de usuario"""
        guild_key = str(guild_id)
        user_key = str(user_id)
        
        if guild_key not in self.user_data:
            self.user_data[guild_key] = {}
        
        if user_key not in self.user_data[guild_key]:
            self.user_data[guild_key][user_key] = {
                "xp": 0,
                "level": 0,
                "messages": 0,
                "last_message": None
            }
        
        return self.user_data[guild_key][user_key]
    
    def add_xp(self, guild_id: int, user_id: int, xp_amount: int) -> Tuple[bool, int, int]:
        """añadir experiencia a un usuario"""
        user_data = self.get_user_data(guild_id, user_id)
        old_level = user_data["level"]
        
        user_data["xp"] += xp_amount
        user_data["messages"] += 1
        user_data["last_message"] = datetime.now().isoformat()
        
        new_level = self.calculate_level(user_data["xp"])
        user_data["level"] = new_level
        
        level_up = new_level > old_level
        self.save_data()
        
        return level_up, old_level, new_level
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """listener para mensajes - ganar xp"""
        # ignorar bots y mensajes sin guild
        if message.author.bot or not message.guild:
            return
        
        guild_config = self.get_guild_config(message.guild.id)
        
        # verificar si está habilitado
        if not guild_config["enabled"]:
            return
        
        # verificar cooldown
        cooldown_key = f"{message.guild.id}_{message.author.id}"
        now = datetime.now()
        
        if cooldown_key in self.cooldowns:
            if now - self.cooldowns[cooldown_key] < timedelta(seconds=guild_config["xp_cooldown"]):
                return
        
        self.cooldowns[cooldown_key] = now
        
        # calcular xp ganada
        xp_range = guild_config["xp_per_message"]
        base_xp = random.randint(xp_range["min"], xp_range["max"])
        final_xp = int(base_xp * guild_config["xp_multiplier"])
        
        # añadir xp
        level_up, old_level, new_level = self.add_xp(message.guild.id, message.author.id, final_xp)
        
        # manejar level up
        if level_up:
            await self.handle_level_up(message, old_level, new_level)
    
    async def handle_level_up(self, message, old_level: int, new_level: int):
        """manejar subida de nivel con integración al sistema de canales"""
        guild_config = self.get_guild_config(message.guild.id)
        
        # obtener canal usando el sistema de configuración de canales
        target_channel = message.channel  # canal por defecto
        
        try:
            # intentar obtener el canal desde channel_config primero
            channel_config_cog = self.bot.get_cog('ChannelConfig')
            if channel_config_cog:
                configured_channel = channel_config_cog.get_channel(
                    message.guild.id, 
                    'notifications', 
                    'level_up'
                )
                if configured_channel:
                    target_channel = configured_channel
            
            # si no hay channel_config o no está configurado, usar el canal del level_system
            if target_channel == message.channel:
                channel_id = guild_config.get("level_up_channel")
                if channel_id:
                    level_channel = message.guild.get_channel(channel_id)
                    if level_channel:
                        target_channel = level_channel
                        
        except Exception as e:
            logger.error(f"Error obteniendo canal para level up: {e}")
            # usar canal por defecto
        
        embed = nextcord.Embed(
            title="🎉 ¡nivel aumentado!",
            description=f"{message.author.mention} ha subido al **nivel {new_level}**!",
            color=nextcord.Color.gold()
        )
        
        user_data = self.get_user_data(message.guild.id, message.author.id)
        next_level_xp = self.calculate_xp_for_level(new_level + 1)
        
        embed.add_field(
            name="progreso:",
            value=f"**xp actual:** {user_data['xp']}\n**siguiente nivel:** {next_level_xp} xp",
            inline=True
        )
        
        embed.set_thumbnail(url=message.author.display_avatar.url)
        
        try:
            await target_channel.send(embed=embed)
        except:
            pass  # ignorar errores de permisos
        
        # asignar rol de nivel si está configurado
        level_roles = guild_config.get("level_roles", {})
        if str(new_level) in level_roles:
            role_id = level_roles[str(new_level)]
            role = message.guild.get_role(role_id)
            if role:
                try:
                    await message.author.add_roles(role, reason=f"nivel {new_level} alcanzado")
                except:
                    pass  # ignorar errores de permisos
    
    @nextcord.slash_command(name="level", description="Ver tu nivel y experiencia")
    async def level_command(self, interaction: nextcord.Interaction, usuario: nextcord.Member = None):
        """comando para ver nivel"""
        target = usuario or interaction.user
        
        if target.bot:
            await interaction.response.send_message("❌ los bots no tienen niveles.", ephemeral=True)
            return
        
        user_data = self.get_user_data(interaction.guild.id, target.id)
        
        current_xp = user_data["xp"]
        current_level = user_data["level"]
        current_level_xp = self.calculate_xp_for_level(current_level)
        next_level_xp = self.calculate_xp_for_level(current_level + 1)
        
        # calcular progreso
        xp_in_level = current_xp - current_level_xp
        xp_needed = next_level_xp - current_level_xp
        progress_percent = (xp_in_level / xp_needed) * 100 if xp_needed > 0 else 100
        
        # crear barra de progreso
        bar_length = 20
        filled_length = int(bar_length * progress_percent / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        embed = nextcord.Embed(
            title=f"📊 nivel de {target.display_name}",
            color=nextcord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 información:",
            value=(
                f"**nivel:** {current_level}\n"
                f"**xp total:** {current_xp:,}\n"
                f"**mensajes:** {user_data['messages']:,}"
            ),
            inline=True
        )
        
        embed.add_field(
            name="📈 progreso al siguiente nivel:",
            value=(
                f"```{bar}```\n"
                f"**{xp_in_level:,}** / **{xp_needed:,}** xp\n"
                f"**{progress_percent:.1f}%** completado"
            ),
            inline=False
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="leaderboard", description="Ver ranking de niveles del servidor")
    async def leaderboard_command(self, interaction: nextcord.Interaction):
        """comando para ver leaderboard"""
        guild_data = self.user_data.get(str(interaction.guild.id), {})
        
        if not guild_data:
            await interaction.response.send_message("❌ no hay datos de niveles en este servidor.", ephemeral=True)
            return
        
        # ordenar usuarios por xp
        sorted_users = sorted(
            guild_data.items(),
            key=lambda x: x[1]["xp"],
            reverse=True
        )[:10]  # top 10
        
        embed = nextcord.Embed(
            title="🏆 ranking de niveles",
            description=f"top 10 usuarios en {interaction.guild.name}",
            color=nextcord.Color.gold()
        )
        
        leaderboard_text = ""
        for i, (user_id, data) in enumerate(sorted_users, 1):
            user = interaction.guild.get_member(int(user_id))
            if user:
                medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"**{i}.**"
                leaderboard_text += f"{medal} {user.display_name} - nivel {data['level']} ({data['xp']:,} xp)\n"
        
        embed.description = leaderboard_text or "no hay usuarios en el ranking"
        
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="level_config", description="Configurar sistema de niveles")
    async def level_config_command(self, interaction: nextcord.Interaction):
        """comando para configurar niveles"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ necesitas permisos de administrador.", ephemeral=True)
            return
        
        view = LevelConfigView(self, interaction.guild.id)
        
        guild_config = self.get_guild_config(interaction.guild.id)
        
        embed = nextcord.Embed(
            title="⚙️ configuración de niveles",
            description="usa los botones para configurar el sistema:",
            color=nextcord.Color.blue()
        )
        
        embed.add_field(
            name="estado:",
            value="✅ habilitado" if guild_config["enabled"] else "❌ deshabilitado",
            inline=True
        )
        
        embed.add_field(
            name="xp por mensaje:",
            value=f"{guild_config['xp_per_message']['min']}-{guild_config['xp_per_message']['max']}",
            inline=True
        )
        
        embed.add_field(
            name="cooldown:",
            value=f"{guild_config['xp_cooldown']}s",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class LevelConfigView(nextcord.ui.View):
    """vista para configurar niveles"""
    
    def __init__(self, level_system: LevelSystem, guild_id: int):
        super().__init__(timeout=300)
        self.level_system = level_system
        self.guild_id = guild_id
    
    @nextcord.ui.button(label="toggle sistema", style=nextcord.ButtonStyle.primary, emoji="🔄")
    async def toggle_system(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = self.level_system.get_guild_config(self.guild_id)
        config["enabled"] = not config["enabled"]
        
        self.level_system.guild_configs[str(self.guild_id)] = config
        self.level_system.save_config()
        
        status = "habilitado" if config["enabled"] else "deshabilitado"
        await interaction.response.send_message(f"✅ sistema de niveles {status}.", ephemeral=True)

def setup(bot):
    """función para cargar el cog"""
    return LevelSystem(bot)
