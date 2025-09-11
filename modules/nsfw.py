"""
Módulo de comandos NSFW/Adultos para el bot - VERSIÓN MEJORADA
Solo disponible en canales marcados como NSFW
"""

import logging
import nextcord
from nextcord.ext import commands
import aiohttp
import random
import json
import re
import asyncio
from urllib.parse import quote

logger = logging.getLogger(__name__)

class NSFWCommands(commands.Cog):
    """Comandos de contenido adulto/NSFW"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Lista expandida de categorías NSFW
        self.nsfw_categories = [
            "waifu", "neko", "trap", "blowjob", "pussy", "cum", "spank",
            "gasm", "hentai", "boobs", "thigh", "ass", "paizuri", "tentacle",
            "gif", "ahegao", "uniform", "orgy", "elves", "yuri", "panties",
            "masturbation", "public", "ero", "kitsune", "hololewd", "lewdkemo",
            "femdom", "feet", "glasses", "stockings", "lesbian", "bdsm"
        ]
        
        # APIs adicionales para más variedad
        self.additional_apis = {
            "gelbooru": "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags=",
            "rule34": "https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags=",
            "danbooru": "https://danbooru.donmai.us/posts.json?tags="
        }
        
    def cog_check(self, ctx):
        """Verificar que el canal sea NSFW"""
        if isinstance(ctx.channel, nextcord.DMChannel):
            return False
        return ctx.channel.is_nsfw()
    
    async def get_nsfw_image(self, category: str):
        """Obtiene una imagen NSFW de la categoría especificada con múltiples fallbacks"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                # Método 1: waifu.pics (más confiable)
                try:
                    url = f"https://api.waifu.pics/nsfw/{category}"
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if 'url' in data:
                                return data['url']
                except Exception as e:
                    logger.debug(f"waifu.pics falló para {category}: {e}")
                
                # Método 2: nekos.life
                try:
                    # Mapear categorías para nekos.life
                    nekos_mapping = {
                        'waifu': 'neko', 'neko': 'neko', 'trap': 'trap',
                        'blowjob': 'blowjob', 'pussy': 'pussy', 'cum': 'cum',
                        'spank': 'spank', 'gasm': 'cum_jpg', 'hentai': 'hentai',
                        'boobs': 'boobs', 'thigh': 'thigh', 'ass': 'ass'
                    }
                    
                    nekos_category = nekos_mapping.get(category, 'neko')
                    fallback_url = f"https://nekos.life/api/v2/img/{nekos_category}"
                    async with session.get(fallback_url) as fallback_resp:
                        if fallback_resp.status == 200:
                            fallback_data = await fallback_resp.json()
                            if 'url' in fallback_data:
                                return fallback_data['url']
                except Exception as e:
                    logger.debug(f"nekos.life falló para {category}: {e}")
                
                # Método 3: Gelbooru (último recurso)
                try:
                    return await self.search_gelbooru(category, session)
                except Exception as e:
                    logger.debug(f"Gelbooru falló para {category}: {e}")
                
                # Método 4: Lista de URLs de respaldo estáticas
                fallback_images = {
                    'waifu': 'https://cdn.nekos.life/nsfw/neko/neko_001.jpg',
                    'neko': 'https://cdn.nekos.life/nsfw/neko/neko_002.jpg', 
                    'boobs': 'https://cdn.nekos.life/nsfw/boobs/boobs_001.jpg'
                }
                
                if category in fallback_images:
                    return fallback_images[category]
                        
        except Exception as e:
            logger.error(f"Error crítico obteniendo imagen NSFW: {e}")
        
        return None
    
    async def search_gelbooru(self, tags: str, session=None):
        """Buscar imágenes en Gelbooru con manejo mejorado de errores"""
        try:
            if not session:
                session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))
                close_session = True
            else:
                close_session = False
                
            # Preparar tags para búsqueda - limpiar y simplificar
            clean_tags = tags.replace(" ", "_").replace("-", "_")
            search_tags = f"{clean_tags}+rating:explicit+-loli+-shota"
            
            # URL con parámetros mejorados
            url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={search_tags}&limit=10&pid=0"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        if data and isinstance(data, list) and len(data) > 0:
                            # Filtrar resultados válidos
                            valid_posts = [post for post in data if post.get('file_url')]
                            if valid_posts:
                                # Seleccionar imagen aleatoria
                                post = random.choice(valid_posts)
                                file_url = post.get('file_url')
                                
                                # Verificar que la URL sea válida
                                if file_url and (file_url.startswith('http://') or file_url.startswith('https://')):
                                    return file_url
                    except (json.JSONDecodeError, KeyError) as parse_error:
                        logger.debug(f"Error parseando respuesta de Gelbooru: {parse_error}")
                else:
                    logger.debug(f"Gelbooru devolvió status {resp.status}")
                        
            if close_session:
                await session.close()
                
        except asyncio.TimeoutError:
            logger.debug("Timeout en búsqueda de Gelbooru")
        except Exception as e:
            logger.debug(f"Error en búsqueda de Gelbooru: {e}")
            
        return None
    
    async def search_rule34(self, tags: str):
        """Buscar contenido en Rule34"""
        try:
            async with aiohttp.ClientSession() as session:
                # Preparar tags para búsqueda
                search_tags = tags.replace(" ", "+")
                url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={search_tags}&limit=20"
                
                async with session.get(url) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        # Rule34 a veces devuelve XML, necesitamos parsearlo
                        if text.startswith('<?xml'):
                            return await self.parse_rule34_xml(text)
                        else:
                            data = await resp.json()
                            if data and len(data) > 0:
                                post = random.choice(data)
                                return post.get('file_url')
                                
        except Exception as e:
            logger.error(f"Error buscando en Rule34: {e}")
            
        return None
    
    async def parse_rule34_xml(self, xml_text: str):
        """Parsear respuesta XML de Rule34"""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_text)
            posts = root.findall('.//post')
            
            if posts:
                post = random.choice(posts)
                return post.get('file_url')
                
        except Exception as e:
            logger.error(f"Error parseando XML de Rule34: {e}")
            
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
        
        try:
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
                await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo más tarde.")
        except Exception as e:
            logger.error(f"Error en comando waifu: {e}")
            await interaction.followup.send("❌ Ocurrió un error interno. Inténtalo de nuevo.")

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
        
        try:
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
                await interaction.followup.send("❌ No se pudo obtener la imagen. Inténtalo de nuevo más tarde.")
        except Exception as e:
            logger.error(f"Error en comando neko: {e}")
            await interaction.followup.send("❌ Ocurrió un error interno. Inténtalo de nuevo.")

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

    @nextcord.slash_command(name="boobs", description="Obtiene una imagen de boobs NSFW")
    async def nsfw_boobs(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen boobs NSFW"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        image_url = await self.get_nsfw_image("boobs")
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Boobs NSFW",
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

    @nextcord.slash_command(name="ass", description="Obtiene una imagen ass NSFW")
    async def nsfw_ass(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen ass NSFW"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        image_url = await self.get_nsfw_image("ass")
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Ass NSFW",
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

    @nextcord.slash_command(name="thigh", description="Obtiene una imagen thigh NSFW")
    async def nsfw_thigh(self, interaction: nextcord.Interaction):
        """Comando para obtener imagen thigh NSFW"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        image_url = await self.get_nsfw_image("thigh")
        if image_url:
            embed = nextcord.Embed(
                title="🔞 Thigh NSFW",
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

    @nextcord.slash_command(name="rule34", description="Busca contenido NSFW en Rule34")
    async def nsfw_rule34(self, interaction: nextcord.Interaction, 
                         busqueda: str = nextcord.SlashOption(description="Términos de búsqueda para Rule34")):
        """Comando para buscar en Rule34"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        # Filtrar términos problemáticos
        forbidden_terms = ["loli", "shota", "child", "kid", "young", "underage", "minor"]
        if any(term.lower() in busqueda.lower() for term in forbidden_terms):
            await interaction.followup.send("❌ Términos de búsqueda no permitidos.")
            return
        
        image_url = await self.search_rule34(busqueda)
        if image_url:
            embed = nextcord.Embed(
                title=f"🔞 Rule34: {busqueda}",
                color=nextcord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name} | Búsqueda: {busqueda}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ No se encontraron resultados para '{busqueda}'. Intenta con otros términos.")

    @nextcord.slash_command(name="gelbooru", description="Busca contenido NSFW en Gelbooru")
    async def nsfw_gelbooru(self, interaction: nextcord.Interaction, 
                           busqueda: str = nextcord.SlashOption(description="Términos de búsqueda para Gelbooru")):
        """Comando para buscar en Gelbooru"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        await interaction.response.defer()
        
        # Filtrar términos problemáticos
        forbidden_terms = ["loli", "shota", "child", "kid", "young", "underage", "minor"]
        if any(term.lower() in busqueda.lower() for term in forbidden_terms):
            await interaction.followup.send("❌ Términos de búsqueda no permitidos.")
            return
        
        image_url = await self.search_gelbooru(busqueda)
        if image_url:
            embed = nextcord.Embed(
                title=f"🔞 Gelbooru: {busqueda}",
                color=nextcord.Color.red(),
                timestamp=interaction.created_at
            )
            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Solicitado por {interaction.user.display_name} | Búsqueda: {busqueda}",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ No se encontraron resultados para '{busqueda}'. Intenta con otros términos.")

    @nextcord.slash_command(name="nsfw-categorias", description="Muestra todas las categorías NSFW disponibles")
    async def nsfw_categories(self, interaction: nextcord.Interaction):
        """Mostrar todas las categorías NSFW disponibles"""
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse en canales NSFW.",
                ephemeral=True
            )
            return
            
        embed = nextcord.Embed(
            title="🔞 Categorías NSFW Disponibles",
            description="Estas son todas las categorías que puedes usar:",
            color=nextcord.Color.red(),
            timestamp=interaction.created_at
        )
        
        # Organizar categorías en columnas
        categories_list = "\n".join([f"• `{cat}`" for cat in sorted(self.nsfw_categories)])
        embed.add_field(
            name="📋 Categorías",
            value=categories_list,
            inline=False
        )
        
        embed.add_field(
            name="🔍 Búsquedas Personalizadas",
            value="• `/rule34 [búsqueda]` - Buscar en Rule34\n• `/gelbooru [búsqueda]` - Buscar en Gelbooru",
            inline=False
        )
        
        embed.set_footer(
            text=f"Solicitado por {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    """Función para añadir el cog al bot"""
    return NSFWCommands(bot)
