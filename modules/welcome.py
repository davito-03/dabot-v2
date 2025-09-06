"""
sistema de bienvenidas y despedidas
inspirado en probot y dyno
por davito
"""

import nextcord
from nextcord.ext import commands
import json
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.configs = {}
        self.load_configs()
    
    def load_configs(self):
        """cargar configuraciones"""
        try:
            with open('data/welcome_configs.json', 'r', encoding='utf-8') as f:
                self.configs = json.load(f)
        except FileNotFoundError:
            self.configs = {}
    
    def save_configs(self):
        """guardar configuraciones"""
        try:
            with open('data/welcome_configs.json', 'w', encoding='utf-8') as f:
                json.dump(self.configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando configs de bienvenida: {e}")
    
    def get_guild_config(self, guild_id):
        """obtener config del servidor"""
        return self.configs.get(str(guild_id), {
            'welcome_enabled': False,
            'welcome_channel': None,
            'welcome_message': "¡Bienvenido {user} a **{server}**! 🎉\nAhora somos **{count}** miembros.",
            'welcome_card': True,
            'welcome_dm': False,
            'welcome_dm_message': "¡Bienvenido a **{server}**! Esperamos que disfrutes tu estancia. 😊",
            'autorole': None,
            'leave_enabled': False,
            'leave_channel': None,
            'leave_message': "{user} se fue del servidor. 😢\nAhora somos **{count}** miembros."
        })
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """evento de miembro que se une"""
        if member.bot:
            return
        
        config = self.get_guild_config(member.guild.id)
        
        if not config['welcome_enabled']:
            return
        
        # autorole
        if config['autorole']:
            role = member.guild.get_role(config['autorole'])
            if role:
                try:
                    await member.add_roles(role, reason="Autorole de bienvenida")
                except:
                    pass
        
        # mensaje de bienvenida
        if config['welcome_channel']:
            channel = self.bot.get_channel(config['welcome_channel'])
            if channel:
                await self.send_welcome_message(member, channel, config)
        
        # dm de bienvenida
        if config['welcome_dm']:
            try:
                message = config['welcome_dm_message'].format(
                    user=member.mention,
                    server=member.guild.name,
                    count=member.guild.member_count
                )
                await member.send(message)
            except:
                pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """evento de miembro que se va"""
        config = self.get_guild_config(member.guild.id)
        
        if not config['leave_enabled']:
            return
        
        if config['leave_channel']:
            channel = self.bot.get_channel(config['leave_channel'])
            if channel:
                message = config['leave_message'].format(
                    user=member.display_name,
                    server=member.guild.name,
                    count=member.guild.member_count
                )
                
                embed = nextcord.Embed(
                    description=message,
                    color=0xe74c3c
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                
                await channel.send(embed=embed)
    
    async def send_welcome_message(self, member, channel, config):
        """enviar mensaje de bienvenida"""
        message = config['welcome_message'].format(
            user=member.mention,
            server=member.guild.name,
            count=member.guild.member_count
        )
        
        if config['welcome_card']:
            try:
                # crear tarjeta de bienvenida
                card = await self.create_welcome_card(member)
                if card:
                    file = nextcord.File(card, filename=f"welcome_{member.id}.png")
                    embed = nextcord.Embed(
                        description=message,
                        color=0x2ecc71
                    )
                    embed.set_image(url=f"attachment://welcome_{member.id}.png")
                    await channel.send(embed=embed, file=file)
                    return
            except Exception as e:
                logger.error(f"error creando tarjeta de bienvenida: {e}")
        
        # fallback a embed simple
        embed = nextcord.Embed(
            description=message,
            color=0x2ecc71
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)
    
    async def create_welcome_card(self, member):
        """crear tarjeta de bienvenida"""
        try:
            # crear imagen base
            width, height = 800, 400
            img = Image.new('RGB', (width, height), color=(47, 49, 54))
            draw = ImageDraw.Draw(img)
            
            # intentar cargar fuente
            try:
                font_large = ImageFont.truetype("arial.ttf", 48)
                font_medium = ImageFont.truetype("arial.ttf", 32)
                font_small = ImageFont.truetype("arial.ttf", 24)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # descargar avatar
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(str(member.display_avatar.url)) as resp:
                        avatar_data = await resp.read()
                
                avatar = Image.open(BytesIO(avatar_data))
                avatar = avatar.resize((150, 150))
                
                # hacer avatar circular
                mask = Image.new('L', (150, 150), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((0, 0, 150, 150), fill=255)
                
                avatar.putalpha(mask)
                img.paste(avatar, (50, 125), avatar)
            except:
                pass
            
            # texto de bienvenida
            draw.text((250, 100), "¡BIENVENIDO!", fill=(116, 204, 244), font=font_large)
            draw.text((250, 160), member.display_name, fill=(255, 255, 255), font=font_medium)
            draw.text((250, 200), f"a {member.guild.name}", fill=(153, 170, 181), font=font_small)
            draw.text((250, 240), f"Miembro #{member.guild.member_count}", fill=(153, 170, 181), font=font_small)
            
            # decoración
            draw.rectangle([0, 0, width, 10], fill=(116, 204, 244))
            draw.rectangle([0, height-10, width, height], fill=(116, 204, 244))
            
            # guardar en BytesIO
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            return buffer
        except Exception as e:
            logger.error(f"error creando tarjeta: {e}")
            return None
    
    @nextcord.slash_command(name="configurar-bienvenida", description="Configurar sistema de bienvenidas")
    @commands.has_permissions(manage_guild=True)
    async def config_welcome(self, interaction: nextcord.Interaction):
        """configurar bienvenidas"""
        view = WelcomeConfigView(self)
        embed = nextcord.Embed(
            title="👋 Configuración de Bienvenidas",
            description="Configura el sistema de bienvenidas y despedidas:",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @nextcord.slash_command(name="canal-bienvenida", description="Establecer canal de bienvenidas")
    @commands.has_permissions(manage_guild=True)
    async def set_welcome_channel(self, interaction: nextcord.Interaction, 
                                 canal: nextcord.TextChannel):
        """establecer canal de bienvenidas"""
        config = self.get_guild_config(interaction.guild.id)
        config['welcome_channel'] = canal.id
        config['welcome_enabled'] = True
        self.configs[str(interaction.guild.id)] = config
        self.save_configs()
        
        await interaction.response.send_message(
            f"✅ Canal de bienvenidas establecido en {canal.mention}",
            ephemeral=True
        )
    
    @nextcord.slash_command(name="canal-despedida", description="Establecer canal de despedidas")
    @commands.has_permissions(manage_guild=True)
    async def set_leave_channel(self, interaction: nextcord.Interaction, 
                               canal: nextcord.TextChannel):
        """establecer canal de despedidas"""
        config = self.get_guild_config(interaction.guild.id)
        config['leave_channel'] = canal.id
        config['leave_enabled'] = True
        self.configs[str(interaction.guild.id)] = config
        self.save_configs()
        
        await interaction.response.send_message(
            f"✅ Canal de despedidas establecido en {canal.mention}",
            ephemeral=True
        )
    
    @nextcord.slash_command(name="autorole", description="Establecer rol automático para nuevos miembros")
    @commands.has_permissions(manage_guild=True)
    async def set_autorole(self, interaction: nextcord.Interaction, 
                          rol: nextcord.Role):
        """establecer autorole"""
        config = self.get_guild_config(interaction.guild.id)
        config['autorole'] = rol.id
        self.configs[str(interaction.guild.id)] = config
        self.save_configs()
        
        await interaction.response.send_message(
            f"✅ Autorole establecido: {rol.mention}",
            ephemeral=True
        )

class WelcomeConfigView(nextcord.ui.View):
    def __init__(self, welcome_cog):
        super().__init__(timeout=300)
        self.welcome = welcome_cog
    
    @nextcord.ui.button(label="Toggle Bienvenidas", emoji="👋", style=nextcord.ButtonStyle.primary)
    async def toggle_welcome(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = self.welcome.get_guild_config(interaction.guild.id)
        config['welcome_enabled'] = not config.get('welcome_enabled', False)
        self.welcome.configs[str(interaction.guild.id)] = config
        self.welcome.save_configs()
        
        status = "✅ Activado" if config['welcome_enabled'] else "❌ Desactivado"
        await interaction.response.send_message(f"Bienvenidas: {status}", ephemeral=True)
    
    @nextcord.ui.button(label="Toggle Despedidas", emoji="😢", style=nextcord.ButtonStyle.secondary)
    async def toggle_leave(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = self.welcome.get_guild_config(interaction.guild.id)
        config['leave_enabled'] = not config.get('leave_enabled', False)
        self.welcome.configs[str(interaction.guild.id)] = config
        self.welcome.save_configs()
        
        status = "✅ Activado" if config['leave_enabled'] else "❌ Desactivado"
        await interaction.response.send_message(f"Despedidas: {status}", ephemeral=True)
    
    @nextcord.ui.button(label="Toggle Tarjetas", emoji="🎨", style=nextcord.ButtonStyle.secondary)
    async def toggle_cards(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = self.welcome.get_guild_config(interaction.guild.id)
        config['welcome_card'] = not config.get('welcome_card', True)
        self.welcome.configs[str(interaction.guild.id)] = config
        self.welcome.save_configs()
        
        status = "✅ Activado" if config['welcome_card'] else "❌ Desactivado"
        await interaction.response.send_message(f"Tarjetas de bienvenida: {status}", ephemeral=True)
    
    @nextcord.ui.button(label="Toggle DM", emoji="📩", style=nextcord.ButtonStyle.secondary)
    async def toggle_dm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = self.welcome.get_guild_config(interaction.guild.id)
        config['welcome_dm'] = not config.get('welcome_dm', False)
        self.welcome.configs[str(interaction.guild.id)] = config
        self.welcome.save_configs()
        
        status = "✅ Activado" if config['welcome_dm'] else "❌ Desactivado"
        await interaction.response.send_message(f"DM de bienvenida: {status}", ephemeral=True)

def setup(bot):
    return Welcome(bot)
