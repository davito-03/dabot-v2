"""
Módulo de comandos NSFW/Adultos para el bot
Solo disponible en canales marcados como NSFW
"""

import logging
import nextcord
from nextcord.ext import commands
import aiohttp
import random
import json

logger = logging.getLogger(__name__)

class NSFWCommands(commands.Cog):
    """Comandos de contenido adulto/NSFW"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Lista de categorías NSFW disponibles en la API
        self.nsfw_categories = [
            "waifu", "neko", "trap", "blowjob", "pussy", "cum", "spank",
            "gasm", "hentai", "boobs", "thigh", "ass", "paizuri", "tentacle",
            "gif", "ahegao", "uniform", "orgy", "elves", "yuri", "panties",
            "masturbation", "public", "ero", "kitsune", "hololewd", "lewdkemo"
        ]
        
    def cog_check(self, ctx):
        """Verificar que el canal sea NSFW"""
        if isinstance(ctx.channel, nextcord.DMChannel):
            return False
        return ctx.channel.is_nsfw()
    
    async def get_nsfw_image(self, category: str):
        """Obtiene una imagen NSFW de la categoría especificada"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.waifu.pics/nsfw/{category}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('url')
                    else:
                        # Fallback a nekos.life para algunas categorías
                        fallback_url = f"https://nekos.life/api/v2/img/{category}"
                        async with session.get(fallback_url) as fallback_resp:
                            if fallback_resp.status == 200:
                                fallback_data = await fallback_resp.json()
                                return fallback_data.get('url')
        except Exception as e:
            logger.error(f"Error obteniendo imagen NSFW: {e}")
        return None

    @nextcord.slash_command(name="waifu", description="Obtiene una imagen waifu NSFW")
    async def nsfw_waifu(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen waifu NSFW"""
        # Verificar que sea canal NSFW
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        image_url = await self.get_nsfw_image("waifu")
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Waifu NSFW",
                color=nextcord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo.")

    @nextcord.slash_command(name="neko", description="Obtiene una imagen neko NSFW")
    async def nsfw_neko(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen neko NSFW"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        image_url = await self.get_nsfw_image("neko")
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Neko NSFW",
                color=nextcord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo.")

    @nextcord.slash_command(name="nekotina", description="Obtiene una imagen nekotina especial NSFW")
    async def nsfw_nekotina(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen nekotina NSFW (variante especial de neko)"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        # Usa tanto neko como lewdkemo para más variedad
        category = random.choice(["neko", "lewdkemo", "kitsune"])
        image_url = await self.get_nsfw_image(category)
        
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Nekotina Especial",
                description="✨ Una nekotina especial para ti~",
                color=nextcord.Color.magenta(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo.")

    @nextcord.slash_command(name="trap", description="Obtiene una imagen trap NSFW")
    async def nsfw_trap(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen trap NSFW"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        image_url = await self.get_nsfw_image("trap")
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Trap NSFW",
                color=nextcord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo.")

    @nextcord.slash_command(name="ahegao", description="Obtiene una imagen ahegao NSFW")
    async def nsfw_ahegao(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen ahegao NSFW"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        image_url = await self.get_nsfw_image("ahegao")
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Ahegao NSFW",
                color=nextcord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo.")

    @nextcord.slash_command(name="yuri", description="Obtiene una imagen yuri NSFW")
    async def nsfw_yuri(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen yuri NSFW"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        image_url = await self.get_nsfw_image("yuri")
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Yuri NSFW",
                color=nextcord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo.")

    @nextcord.slash_command(name="blowjob", description="Obtiene una imagen blowjob NSFW")
    async def nsfw_blowjob(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen blowjob NSFW"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        image_url = await self.get_nsfw_image("blowjob")
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Blowjob NSFW",
                color=nextcord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo.")

    @nextcord.slash_command(name="hentai", description="Obtiene una imagen hentai NSFW")
    async def nsfw_hentai(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen hentai NSFW"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        image_url = await self.get_nsfw_image("hentai")
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Hentai NSFW",
                color=nextcord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo.")

    @nextcord.slash_command(name="nsfw-random", description="Obtiene una imagen NSFW aleatoria")
    async def nsfw_random(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen NSFW aleatoria"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        # Selecciona una categoría aleatoria
        category = random.choice(self.nsfw_categories)
        image_url = await self.get_nsfw_image(category)
        
        if image_url:
            embed = nextcord.Embed(
                title=f"🔞 {category.title()} NSFW (Aleatorio)",
                color=nextcord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo.")

def setup(bot):
    """Función para añadir el cog al bot"""
    return NSFWCommands(bot)
