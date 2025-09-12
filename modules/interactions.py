"""
comandos de interacciones y animales
inspirado en nekotina y otros bots
por davito
"""

import nextcord
from nextcord.ext import commands
import aiohttp
import random
import json
import logging

logger = logging.getLogger(__name__)

class Interactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # apis para imágenes
        self.apis = {
            'cat': 'https://api.thecatapi.com/v1/images/search',
            'dog': 'https://dog.ceo/api/breeds/image/random',
            'fox': 'https://randomfox.ca/floof/',
            'duck': 'https://random-d.uk/api/random'
        }
        
        # apis para interacciones
        self.interaction_apis = {
            'hug': 'https://api.waifu.pics/sfw/hug',
            'kiss': 'https://api.waifu.pics/sfw/kiss',
            'slap': 'https://api.waifu.pics/sfw/slap',
            'pat': 'https://api.waifu.pics/sfw/pat',
            'cuddle': 'https://api.waifu.pics/sfw/cuddle',
            'poke': 'https://api.waifu.pics/sfw/poke',
            'wink': 'https://api.waifu.pics/sfw/wink',
            'smile': 'https://api.waifu.pics/sfw/smile',
            'wave': 'https://api.waifu.pics/sfw/wave',
            'highfive': 'https://api.waifu.pics/sfw/highfive',
            'handhold': 'https://api.waifu.pics/sfw/handhold',
            'nom': 'https://api.waifu.pics/sfw/nom',
            'bite': 'https://api.waifu.pics/sfw/bite',
            'glomp': 'https://api.waifu.pics/sfw/glomp',
            'bonk': 'https://api.waifu.pics/sfw/bonk',
            'yeet': 'https://api.waifu.pics/sfw/yeet',
            'blush': 'https://api.waifu.pics/sfw/blush',
            'happy': 'https://api.waifu.pics/sfw/happy',
            'dance': 'https://api.waifu.pics/sfw/dance'
        }
        
        # textos para interacciones
        self.interaction_texts = {
            'hug': [
                "{author} abraza cariñosamente a {target} 🤗",
                "{author} le da un abrazo cálido a {target} ❤️",
                "{target} recibe un gran abrazo de {author}! 🫂"
            ],
            'kiss': [
                "{author} le da un beso a {target} 😘",
                "{author} besa tiernamente a {target} 💋",
                "{target} recibe un dulce beso de {author}! 😚"
            ],
            'slap': [
                "{author} abofetea a {target} 👋",
                "¡{author} le da una cachetada a {target}! 😤",
                "{target} recibe un buen golpe de {author}!"
            ],
            'pat': [
                "{author} acaricia la cabeza de {target} 😊",
                "{author} le hace mimos a {target} 🥰",
                "{target} recibe caricias de {author}!"
            ],
            'cuddle': [
                "{author} se acurruca con {target} 🥰",
                "{author} abraza y mima a {target} ❤️",
                "{target} se acurruca con {author}!"
            ],
            'poke': [
                "{author} toca a {target} con el dedo 👉",
                "¡{author} le hace cosquillas a {target}! 😄",
                "{target} recibe un toque de {author}!"
            ],
            'bite': [
                "{author} muerde suavemente a {target} 😈",
                "¡{author} le da un mordisquito a {target}! 😏",
                "{target} recibe un mordisco juguetón de {author}!"
            ],
            'bonk': [
                "{author} golpea a {target} con un bate de plástico! 🏏",
                "¡{author} bonk! {target} va a horny jail! 😤",
                "{target} recibe un bonk de {author}!"
            ]
        }
    
    async def get_image_url(self, api_type):
        """obtener url de imagen de api"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.apis[api_type]) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if api_type == 'cat':
                            return data[0]['url']
                        elif api_type == 'dog':
                            return data['message']
                        elif api_type == 'fox':
                            return data['image']
                        elif api_type == 'duck':
                            return data['url']
                        
        except Exception as e:
            logger.error(f"error obteniendo imagen {api_type}: {e}")
            return None
    
    async def get_interaction_gif(self, interaction_type):
        """obtener gif de interacción"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.interaction_apis[interaction_type]) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['url']
        except Exception as e:
            logger.error(f"error obteniendo gif {interaction_type}: {e}")
            return None
    
    @nextcord.slash_command(name="gato", description="Muestra una imagen aleatoria de un gato")
    async def cat_command(self, interaction: nextcord.Interaction):
        """comando de gato"""
        await interaction.response.defer()
        
        image_url = await self.get_image_url('cat')
        
        if image_url:
            embed = nextcord.Embed(
                title="🐱 ¡Aquí tienes un gato!",
                color=0xff6b6b
            )
            embed.set_image(url=image_url)
            embed.set_footer(text="Powered by TheCatAPI")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No pude obtener una imagen de gato. ¡Inténtalo de nuevo!")
    
    @nextcord.slash_command(name="perro", description="Muestra una imagen aleatoria de un perro")
    async def dog_command(self, interaction: nextcord.Interaction):
        """comando de perro"""
        await interaction.response.defer()
        
        image_url = await self.get_image_url('dog')
        
        if image_url:
            embed = nextcord.Embed(
                title="🐶 ¡Aquí tienes un perro!",
                color=0x4ecdc4
            )
            embed.set_image(url=image_url)
            embed.set_footer(text="Powered by Dog API")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No pude obtener una imagen de perro. ¡Inténtalo de nuevo!")
    
    @nextcord.slash_command(name="zorro", description="Muestra una imagen aleatoria de un zorro")
    async def fox_command(self, interaction: nextcord.Interaction):
        """comando de zorro"""
        await interaction.response.defer()
        
        image_url = await self.get_image_url('fox')
        
        if image_url:
            embed = nextcord.Embed(
                title="🦊 ¡Aquí tienes un zorro!",
                color=0xff9500
            )
            embed.set_image(url=image_url)
            embed.set_footer(text="Powered by RandomFox")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No pude obtener una imagen de zorro. ¡Inténtalo de nuevo!")
    
    @nextcord.slash_command(name="pato", description="Muestra una imagen aleatoria de un pato")
    async def duck_command(self, interaction: nextcord.Interaction):
        """comando de pato"""
        await interaction.response.defer()
        
        image_url = await self.get_image_url('duck')
        
        if image_url:
            embed = nextcord.Embed(
                title="🦆 ¡Aquí tienes un pato!",
                color=0xffd93d
            )
            embed.set_image(url=image_url)
            embed.set_footer(text="Powered by Random-d.uk")
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ No pude obtener una imagen de pato. ¡Inténtalo de nuevo!")
    
    # comandos de interacciones
    async def execute_interaction(self, interaction: nextcord.Interaction, usuario: nextcord.Member, interaction_type: str):
        """ejecutar comando de interacción genérico"""
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(f"❌ ¡No puedes {interaction_type} a ti mismo!", ephemeral=True)
            return
        
        if usuario.bot:
            await interaction.response.send_message("❌ ¡No puedes interactuar con bots!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        gif_url = await self.get_interaction_gif(interaction_type)
        
        if gif_url:
            # elegir texto aleatorio
            texts = self.interaction_texts.get(interaction_type, [f"{{author}} {interaction_type} a {{target}}"])
            text = random.choice(texts).format(
                author=interaction.user.display_name,
                target=usuario.display_name
            )
            
            embed = nextcord.Embed(
                description=text,
                color=0xe91e63
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text="Powered by waifu.pics")
            
            await interaction.followup.send(embed=embed)
        else:
            text = f"{interaction.user.display_name} {interaction_type} a {usuario.display_name}!"
            await interaction.followup.send(text)
    
    @nextcord.slash_command(name="abrazar", description="Abraza a alguien")
    async def hug_command(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """comando de abrazo"""
        await self.execute_interaction(interaction, usuario, 'hug')
    
    @nextcord.slash_command(name="besar", description="Besa a alguien")
    async def kiss_command(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """comando de beso"""
        await self.execute_interaction(interaction, usuario, 'kiss')
    
    @nextcord.slash_command(name="abofetear", description="Abofetea a alguien")
    async def slap_command(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """comando de bofetada"""
        await self.execute_interaction(interaction, usuario, 'slap')
    
    @nextcord.slash_command(name="acariciar", description="Acaricia a alguien")
    async def pat_command(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """comando de caricias"""
        await self.execute_interaction(interaction, usuario, 'pat')
    
    @nextcord.slash_command(name="acurrucar", description="Te acurrucas con alguien")
    async def cuddle_command(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """comando de acurrucarse"""
        await self.execute_interaction(interaction, usuario, 'cuddle')
    
    @nextcord.slash_command(name="tocar", description="Toca a alguien")
    async def poke_command(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """comando de tocar"""
        await self.execute_interaction(interaction, usuario, 'poke')
    
    @nextcord.slash_command(name="morder", description="Muerde a alguien")
    async def bite_command(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """comando de morder"""
        await self.execute_interaction(interaction, usuario, 'bite')
    
    @nextcord.slash_command(name="bonk", description="Bonk a alguien (horny jail)")
    async def bonk_command(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """comando de bonk"""
        await self.execute_interaction(interaction, usuario, 'bonk')
    
    @nextcord.slash_command(name="interact", description="Menú de interacciones rápidas")
    async def interact_menu(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """menú de interacciones"""
        if usuario.id == interaction.user.id:
            await interaction.response.send_message("❌ ¡No puedes interactuar contigo mismo!", ephemeral=True)
            return
        
        if usuario.bot:
            await interaction.response.send_message("❌ ¡No puedes interactuar con bots!", ephemeral=True)
            return
        
        view = InteractionView(self, interaction.user, usuario)
        embed = nextcord.Embed(
            title="💫 Menú de Interacciones",
            description=f"Elige cómo interactuar con {usuario.display_name}:",
            color=0xe91e63
        )
        
        await interaction.response.send_message(embed=embed, view=view)

class InteractionView(nextcord.ui.View):
    def __init__(self, interactions_cog, author, target):
        super().__init__(timeout=60)
        self.interactions = interactions_cog
        self.author = author
        self.target = target
    
    @nextcord.ui.button(emoji="🤗", label="Abrazo", style=nextcord.ButtonStyle.primary)
    async def hug_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        await self.perform_interaction('hug', interaction)
    
    @nextcord.ui.button(emoji="😘", label="Beso", style=nextcord.ButtonStyle.primary)
    async def kiss_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        await self.perform_interaction('kiss', interaction)
    
    @nextcord.ui.button(emoji="👋", label="Bofetada", style=nextcord.ButtonStyle.danger)
    async def slap_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        await self.perform_interaction('slap', interaction)
    
    @nextcord.ui.button(emoji="😊", label="Caricias", style=nextcord.ButtonStyle.success)
    async def pat_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        await self.perform_interaction('pat', interaction)
    
    @nextcord.ui.button(emoji="🏏", label="Bonk", style=nextcord.ButtonStyle.danger)
    async def bonk_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        await self.perform_interaction('bonk', interaction)
    
    async def perform_interaction(self, interaction_type, interaction):
        """realizar interacción"""
        gif_url = await self.interactions.get_interaction_gif(interaction_type)
        
        if gif_url:
            texts = self.interactions.interaction_texts.get(interaction_type, [f"{{author}} {interaction_type} a {{target}}"])
            text = random.choice(texts).format(
                author=self.author.display_name,
                target=self.target.display_name
            )
            
            embed = nextcord.Embed(
                description=text,
                color=0xe91e63
            )
            embed.set_image(url=gif_url)
            embed.set_footer(text="Powered by waifu.pics")
            
            await interaction.followup.send(embed=embed)
        else:
            text = f"{self.author.display_name} {interaction_type} a {self.target.display_name}!"
            await interaction.followup.send(text)

def setup(bot):
    return Interactions(bot)
