"""
sistema de niveles y experiencia
inspirado en mee6 pero mejorado
por davito
"""

import nextcord
from nextcord.ext import commands, tasks
import json
import asyncio
import random
from datetime import datetime, timedelta
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data = {}
        self.guild_configs = {}
        self.load_data()
        self.save_data_task.start()
    
    def load_data(self):
        """cargar datos de niveles"""
        try:
            with open('data/levels.json', 'r', encoding='utf-8') as f:
                self.user_data = json.load(f)
        except FileNotFoundError:
            self.user_data = {}
        
        try:
            with open('data/level_configs.json', 'r', encoding='utf-8') as f:
                self.guild_configs = json.load(f)
        except FileNotFoundError:
            self.guild_configs = {}
    
    @tasks.loop(minutes=5)
    async def save_data_task(self):
        """guardar datos periódicamente"""
        self.save_data()
    
    def save_data(self):
        """guardar datos"""
        try:
            with open('data/levels.json', 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=2)
            with open('data/level_configs.json', 'w', encoding='utf-8') as f:
                json.dump(self.guild_configs, f, indent=2)
        except Exception as e:
            logger.error(f"error guardando datos de niveles: {e}")
    
    def get_guild_config(self, guild_id):
        """obtener configuración del servidor"""
        return self.guild_configs.get(str(guild_id), {
            'enabled': True,
            'xp_per_message': [15, 25],
            'level_up_message': True,
            'level_up_channel': None,
            'no_xp_channels': [],
            'multiplier_roles': {},
            'level_roles': {}
        })
    
    def get_user_data(self, guild_id, user_id):
        """obtener datos del usuario"""
        guild_key = str(guild_id)
        user_key = str(user_id)
        
        if guild_key not in self.user_data:
            self.user_data[guild_key] = {}
        
        if user_key not in self.user_data[guild_key]:
            self.user_data[guild_key][user_key] = {
                'xp': 0,
                'level': 1,
                'messages': 0,
                'last_message': 0
            }
        
        return self.user_data[guild_key][user_key]
    
    def xp_to_level(self, xp):
        """calcular nivel basado en xp"""
        return int((xp / 100) ** 0.5) + 1
    
    def level_to_xp(self, level):
        """calcular xp necesaria para un nivel"""
        return ((level - 1) ** 2) * 100
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """dar xp por mensajes"""
        if not message.guild or message.author.bot:
            return
        
        config = self.get_guild_config(message.guild.id)
        
        if not config['enabled']:
            return
        
        if message.channel.id in config['no_xp_channels']:
            return
        
        user_data = self.get_user_data(message.guild.id, message.author.id)
        
        # cooldown de 1 minuto
        current_time = datetime.now().timestamp()
        if current_time - user_data['last_message'] < 60:
            return
        
        # calcular xp ganada
        base_xp = random.randint(*config['xp_per_message'])
        
        # multiplicador por roles
        multiplier = 1.0
        for role in message.author.roles:
            if str(role.id) in config['multiplier_roles']:
                multiplier = max(multiplier, config['multiplier_roles'][str(role.id)])
        
        xp_gained = int(base_xp * multiplier)
        
        # actualizar datos
        user_data['xp'] += xp_gained
        user_data['messages'] += 1
        user_data['last_message'] = current_time
        
        old_level = user_data['level']
        new_level = self.xp_to_level(user_data['xp'])
        user_data['level'] = new_level
        
        # verificar level up
        if new_level > old_level:
            await self.handle_level_up(message, new_level, config)
    
    async def handle_level_up(self, message, new_level, config):
        """manejar subida de nivel"""
        if config['level_up_message']:
            embed = nextcord.Embed(
                title="🎉 ¡Subiste de nivel!",
                description=f"{message.author.mention} alcanzó el **nivel {new_level}**!",
                color=0xf1c40f
            )
            
            channel = message.channel
            if config['level_up_channel']:
                channel = self.bot.get_channel(config['level_up_channel'])
                if not channel:
                    channel = message.channel
            
            await channel.send(embed=embed)
        
        # asignar roles por nivel
        for level_str, role_id in config['level_roles'].items():
            required_level = int(level_str)
            if new_level >= required_level:
                role = message.guild.get_role(role_id)
                if role and role not in message.author.roles:
                    try:
                        await message.author.add_roles(role)
                    except:
                        pass
    
    @nextcord.slash_command(name="nivel", description="Ver tu nivel y experiencia")
    async def level_command(self, interaction: nextcord.Interaction, 
                           usuario: nextcord.Member = None):
        """comando para ver nivel"""
        target = usuario or interaction.user
        user_data = self.get_user_data(interaction.guild.id, target.id)
        
        current_level = user_data['level']
        current_xp = user_data['xp']
        xp_for_current = self.level_to_xp(current_level)
        xp_for_next = self.level_to_xp(current_level + 1)
        xp_progress = current_xp - xp_for_current
        xp_needed = xp_for_next - xp_for_current
        
        # crear tarjeta de nivel
        try:
            card = await self.create_level_card(target, user_data, xp_progress, xp_needed)
            file = nextcord.File(card, filename=f"nivel_{target.id}.png")
            await interaction.response.send_message(file=file)
        except Exception as e:
            # fallback a embed simple
            embed = nextcord.Embed(
                title=f"📊 Nivel de {target.display_name}",
                color=0x3498db
            )
            embed.add_field(name="Nivel", value=current_level, inline=True)
            embed.add_field(name="XP Total", value=f"{current_xp:,}", inline=True)
            embed.add_field(name="Mensajes", value=f"{user_data['messages']:,}", inline=True)
            embed.add_field(name="Progreso", value=f"{xp_progress}/{xp_needed} XP", inline=False)
            
            progress_bar = self.create_progress_bar(xp_progress, xp_needed)
            embed.add_field(name="Barra de progreso", value=progress_bar, inline=False)
            
            embed.set_thumbnail(url=target.display_avatar.url)
            await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="ranking", description="Ver el ranking del servidor")
    async def leaderboard(self, interaction: nextcord.Interaction, pagina: int = 1):
        """comando de ranking"""
        guild_data = self.user_data.get(str(interaction.guild.id), {})
        
        if not guild_data:
            embed = nextcord.Embed(
                title="📊 Ranking del servidor",
                description="No hay datos de niveles aún.",
                color=0xe74c3c
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # ordenar usuarios por xp
        sorted_users = sorted(
            guild_data.items(),
            key=lambda x: x[1]['xp'],
            reverse=True
        )
        
        # paginación
        per_page = 10
        start = (pagina - 1) * per_page
        end = start + per_page
        page_users = sorted_users[start:end]
        
        if not page_users:
            await interaction.response.send_message("❌ Página no encontrada.", ephemeral=True)
            return
        
        embed = nextcord.Embed(
            title="🏆 Ranking del servidor",
            color=0xf1c40f
        )
        
        description = ""
        for i, (user_id, data) in enumerate(page_users, start + 1):
            user = interaction.guild.get_member(int(user_id))
            if user:
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                description += f"{medal} **{user.display_name}** - Nivel {data['level']} ({data['xp']:,} XP)\n"
        
        embed.description = description
        embed.set_footer(text=f"Página {pagina} • Total: {len(sorted_users)} usuarios")
        
        await interaction.response.send_message(embed=embed)
    
    def create_progress_bar(self, current, total, length=20):
        """crear barra de progreso textual"""
        if total == 0:
            percentage = 0
        else:
            percentage = current / total
        
        filled = int(length * percentage)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}] {percentage:.1%}"
    
    async def create_level_card(self, user, data, xp_progress, xp_needed):
        """crear tarjeta de nivel visual"""
        # crear imagen base
        width, height = 800, 300
        img = Image.new('RGB', (width, height), color=(47, 49, 54))
        draw = ImageDraw.Draw(img)
        
        # intentar cargar fuente
        try:
            font_large = ImageFont.truetype("arial.ttf", 48)
            font_medium = ImageFont.truetype("arial.ttf", 32)
            font_small = ImageFont.truetype("arial.ttf", 24)
        except:
            # fuente por defecto si no encuentra arial
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # descargar avatar
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(user.display_avatar.url)) as resp:
                    avatar_data = await resp.read()
            
            avatar = Image.open(BytesIO(avatar_data))
            avatar = avatar.resize((200, 200))
            img.paste(avatar, (50, 50))
        except:
            pass
        
        # dibujar información
        draw.text((280, 70), user.display_name, fill=(255, 255, 255), font=font_large)
        draw.text((280, 130), f"Nivel {data['level']}", fill=(116, 204, 244), font=font_medium)
        draw.text((280, 170), f"{data['xp']:,} XP total", fill=(153, 170, 181), font=font_small)
        
        # barra de progreso
        bar_x, bar_y = 280, 220
        bar_width, bar_height = 450, 30
        
        # fondo de la barra
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                      fill=(32, 34, 37), outline=(54, 57, 63))
        
        # progreso
        if xp_needed > 0:
            progress_width = int((xp_progress / xp_needed) * bar_width)
            draw.rectangle([bar_x, bar_y, bar_x + progress_width, bar_y + bar_height], 
                          fill=(116, 204, 244))
        
        # texto de progreso
        progress_text = f"{xp_progress}/{xp_needed} XP"
        draw.text((bar_x + bar_width // 2, bar_y + 35), progress_text, 
                 fill=(255, 255, 255), font=font_small, anchor="mm")
        
        # guardar en BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    @nextcord.slash_command(name="configurar-niveles", description="Configurar sistema de niveles")
    @commands.has_permissions(manage_guild=True)
    async def config_levels(self, interaction: nextcord.Interaction):
        """configurar niveles"""
        view = LevelsConfigView(self)
        embed = nextcord.Embed(
            title="⚙️ Configuración de Niveles",
            description="Selecciona qué configurar:",
            color=0x3498db
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class LevelsConfigView(nextcord.ui.View):
    def __init__(self, levels_cog):
        super().__init__(timeout=300)
        self.levels = levels_cog
    
    @nextcord.ui.button(label="Toggle Sistema", emoji="🔄", style=nextcord.ButtonStyle.primary)
    async def toggle_system(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = self.levels.get_guild_config(interaction.guild.id)
        config['enabled'] = not config.get('enabled', True)
        self.levels.guild_configs[str(interaction.guild.id)] = config
        self.levels.save_data()
        
        status = "✅ Activado" if config['enabled'] else "❌ Desactivado"
        await interaction.response.send_message(f"Sistema de niveles: {status}", ephemeral=True)
    
    @nextcord.ui.button(label="Mensajes Level Up", emoji="📢", style=nextcord.ButtonStyle.secondary)
    async def toggle_messages(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = self.levels.get_guild_config(interaction.guild.id)
        config['level_up_message'] = not config.get('level_up_message', True)
        self.levels.guild_configs[str(interaction.guild.id)] = config
        self.levels.save_data()
        
        status = "✅ Activado" if config['level_up_message'] else "❌ Desactivado"
        await interaction.response.send_message(f"Mensajes de subida de nivel: {status}", ephemeral=True)

def setup(bot):
    return Levels(bot)
