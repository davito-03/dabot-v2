import nextcord
from nextcord.ext import commands
import aiohttp
import logging
import random
import asyncio

logger = logging.getLogger(__name__)

class StickerManager(commands.Cog):
    """sistema para gestionar stickers del servidor"""
    
    def __init__(self, bot):
        self.bot = bot
        self.session = None  # Se iniciará en setup_hook o cuando sea necesario
        
        # Packs de stickers populares
        self.sticker_packs = {
            "memes": {
                "name": "Pack Memes",
                "description": "Stickers de memes populares",
                "stickers": [
                    {
                        "name": "stonks",
                        "description": "Meme stonks",
                        "tags": ["meme", "stonks", "money"],
                        "url": "https://media.discordapp.net/stickers/123456789.png"
                    },
                    {
                        "name": "this_is_fine",
                        "description": "This is fine meme",
                        "tags": ["meme", "fire", "fine"],
                        "url": "https://media.discordapp.net/stickers/987654321.png"
                    }
                ]
            },
            "anime": {
                "name": "Pack Anime",
                "description": "Stickers de anime kawaii",
                "stickers": [
                    {
                        "name": "anime_happy",
                        "description": "Personaje anime feliz",
                        "tags": ["anime", "happy", "kawaii"],
                        "url": "https://media.discordapp.net/stickers/anime1.png"
                    },
                    {
                        "name": "anime_cry",
                        "description": "Personaje anime llorando",
                        "tags": ["anime", "sad", "cry"],
                        "url": "https://media.discordapp.net/stickers/anime2.png"
                    }
                ]
            },
            "cats": {
                "name": "Pack Gatos",
                "description": "Stickers de gatos adorables",
                "stickers": [
                    {
                        "name": "cat_love",
                        "description": "Gato con corazones",
                        "tags": ["cat", "love", "cute"],
                        "url": "https://media.discordapp.net/stickers/cat1.png"
                    },
                    {
                        "name": "cat_angry",
                        "description": "Gato enojado",
                        "tags": ["cat", "angry", "mad"],
                        "url": "https://media.discordapp.net/stickers/cat2.png"
                    }
                ]
            }
        }
    
    async def _ensure_session(self):
        """asegurar que la sesión aiohttp esté iniciada"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    @nextcord.slash_command(
        name="sticker",
        description="Comandos para gestionar stickers del servidor"
    )
    async def sticker_group(self, interaction: nextcord.Interaction):
        pass
    
    @sticker_group.subcommand(
        name="add",
        description="Añadir sticker personalizado al servidor"
    )
    async def add_sticker(
        self,
        interaction: nextcord.Interaction,
        url: str = nextcord.SlashOption(
            description="URL de la imagen del sticker"
        ),
        nombre: str = nextcord.SlashOption(
            description="Nombre del sticker"
        ),
        descripcion: str = nextcord.SlashOption(
            description="Descripción del sticker",
            required=False,
            default=""
        ),
        tags: str = nextcord.SlashOption(
            description="Tags separados por comas (ej: funny,meme,cool)",
            required=False,
            default=""
        )
    ):
        """añadir sticker desde URL"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Gestionar Servidor** para usar este comando.",
                ephemeral=True
            )
            return
        
        # Verificar límites de Discord (informativo)
        if interaction.guild.premium_tier < 2:
            embed = nextcord.Embed(
                title="⚠️ Limitación de Discord",
                description="Los servidores necesitan **Nitro Nivel 2+** para stickers personalizados.\n\n" +
                           "Sin embargo, puedes intentar el comando. Discord mostrará el error específico si no es posible.",
                color=nextcord.Color.orange()
            )
            embed.add_field(
                name="💡 Alternativa",
                value="Puedes usar emojis personalizados que requieren menos nivel de boost.",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # Asegurar que la sesión esté iniciada
            await self._ensure_session()
            
            # Descargar imagen
            async with self.session.get(url) as response:
                if response.status != 200:
                    await interaction.followup.send("❌ No se pudo descargar la imagen.")
                    return
                
                image_data = await response.read()
                
                # Verificar tamaño (máximo 512KB para stickers)
                if len(image_data) > 512 * 1024:
                    await interaction.followup.send("❌ La imagen es muy grande (máximo 512KB).")
                    return
            
            # Procesar tags
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
            if not tag_list:
                tag_list = ["custom"]
            
            # Crear sticker
            sticker = await interaction.guild.create_sticker(
                name=nombre,
                description=descripcion or f"Sticker personalizado: {nombre}",
                emoji="😀",  # Emoji relacionado requerido
                file=nextcord.File(
                    fp=image_data,
                    filename=f"{nombre}.png"
                ),
                reason=f"Sticker añadido por {interaction.user}"
            )
            
            embed = nextcord.Embed(
                title="✅ Sticker Añadido",
                description=f"Sticker **{sticker.name}** añadido exitosamente.",
                color=nextcord.Color.green()
            )
            embed.add_field(
                name="Descripción",
                value=sticker.description,
                inline=False
            )
            embed.add_field(
                name="Tags",
                value=", ".join(tag_list) if tag_list else "Ninguno",
                inline=False
            )
            embed.set_thumbnail(url=sticker.url)
            
            await interaction.followup.send(embed=embed)
            
        except nextcord.HTTPException as e:
            if "Maximum number of stickers reached" in str(e):
                await interaction.followup.send("❌ El servidor ha alcanzado el límite de stickers.")
            else:
                await interaction.followup.send(f"❌ Error creando sticker: {e}")
        except Exception as e:
            logger.error(f"Error añadiendo sticker: {e}")
            await interaction.followup.send("❌ Error procesando la imagen.")
    
    @sticker_group.subcommand(
        name="pack",
        description="Instalar pack de stickers temático"
    )
    async def install_sticker_pack(
        self,
        interaction: nextcord.Interaction,
        pack: str = nextcord.SlashOption(
            description="Pack de stickers a instalar",
            choices=["memes", "anime", "cats", "gaming", "reactions"]
        )
    ):
        """instalar pack de stickers"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Gestionar Servidor**.",
                ephemeral=True
            )
            return
        
        if interaction.guild.premium_tier < 2:
            embed = nextcord.Embed(
                title="⚠️ Limitación de Discord",
                description="Los servidores necesitan **Nitro Nivel 2+** para stickers personalizados.",
                color=nextcord.Color.orange()
            )
            embed.add_field(
                name="💡 Consejo",
                value="Aumenta el nivel de boost del servidor para desbloquear esta función.",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Como las URLs son de ejemplo, mostrar información del pack
        if pack in self.sticker_packs:
            pack_info = self.sticker_packs[pack]
            
            embed = nextcord.Embed(
                title=f"📦 {pack_info['name']}",
                description=pack_info['description'],
                color=nextcord.Color.blue()
            )
            
            sticker_list = ""
            for sticker in pack_info['stickers']:
                sticker_list += f"**{sticker['name']}** - {sticker['description']}\n"
                sticker_list += f"Tags: {', '.join(sticker['tags'])}\n\n"
            
            embed.add_field(
                name="Stickers Incluidos",
                value=sticker_list,
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Nota",
                value="Este es un ejemplo del sistema. Para usar URLs reales, necesitarías una API de stickers o colección propia.",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Pack no encontrado.")
    
    @sticker_group.subcommand(
        name="search",
        description="Buscar stickers en línea"
    )
    async def search_stickers(
        self,
        interaction: nextcord.Interaction,
        query: str = nextcord.SlashOption(
            description="Término de búsqueda"
        ),
        categoria: str = nextcord.SlashOption(
            description="Categoría de stickers",
            choices=["memes", "anime", "animals", "reactions", "gaming", "random"],
            required=False,
            default="random"
        )
    ):
        """buscar stickers populares"""
        
        await interaction.response.defer()
        
        # Simular búsqueda (en producción usarías APIs reales)
        resultados_ejemplo = {
            "memes": [
                {"name": "drake_no", "desc": "Drake señalando que no", "tags": ["meme", "drake", "no"]},
                {"name": "drake_yes", "desc": "Drake señalando que sí", "tags": ["meme", "drake", "yes"]},
                {"name": "stonks", "desc": "Meme de stonks", "tags": ["meme", "stonks", "money"]}
            ],
            "anime": [
                {"name": "anime_blush", "desc": "Anime sonrojado", "tags": ["anime", "blush", "cute"]},
                {"name": "anime_sparkles", "desc": "Anime con brillos", "tags": ["anime", "sparkles", "kawaii"]},
                {"name": "anime_peace", "desc": "Anime haciendo paz", "tags": ["anime", "peace", "happy"]}
            ],
            "animals": [
                {"name": "cat_thumbs_up", "desc": "Gato pulgar arriba", "tags": ["cat", "thumbs", "good"]},
                {"name": "dog_party", "desc": "Perro de fiesta", "tags": ["dog", "party", "fun"]},
                {"name": "penguin_dance", "desc": "Pingüino bailando", "tags": ["penguin", "dance", "cute"]}
            ]
        }
        
        if categoria in resultados_ejemplo:
            resultados = resultados_ejemplo[categoria]
        else:
            # Mezclar resultados para "random"
            all_results = []
            for cat_results in resultados_ejemplo.values():
                all_results.extend(cat_results)
            resultados = random.sample(all_results, min(3, len(all_results)))
        
        embed = nextcord.Embed(
            title=f"🔍 Resultados: '{query}'",
            description=f"Categoría: {categoria.title()}",
            color=nextcord.Color.blue()
        )
        
        for i, resultado in enumerate(resultados[:5], 1):
            embed.add_field(
                name=f"{i}. {resultado['name']}",
                value=f"{resultado['desc']}\nTags: {', '.join(resultado['tags'])}",
                inline=False
            )
        
        embed.add_field(
            name="💡 Uso",
            value="Para añadir un sticker, usa `/sticker add` con la URL de la imagen.",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)
    
    @sticker_group.subcommand(
        name="list",
        description="Ver stickers del servidor"
    )
    async def list_stickers(self, interaction: nextcord.Interaction):
        """listar stickers del servidor"""
        
        stickers = interaction.guild.stickers
        
        if not stickers:
            embed = nextcord.Embed(
                title="📋 Stickers del Servidor",
                description="Este servidor no tiene stickers personalizados.",
                color=nextcord.Color.orange()
            )
            
            if interaction.guild.premium_tier < 2:
                embed.add_field(
                    name="ℹ️ Requisitos",
                    value="El servidor necesita **Nitro Nivel 2+** para stickers personalizados.",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            return
        
        embed = nextcord.Embed(
            title=f"📋 Stickers de {interaction.guild.name}",
            description=f"Total: {len(stickers)}/60",
            color=nextcord.Color.blue()
        )
        
        for i, sticker in enumerate(stickers):
            embed.add_field(
                name=f"{i+1}. {sticker.name}",
                value=f"{sticker.description}\nID: `{sticker.id}`",
                inline=True
            )
            
            if i >= 9:  # Limitar a 10 para no saturar
                embed.add_field(
                    name="...",
                    value=f"Y {len(stickers) - 10} más",
                    inline=False
                )
                break
        
        await interaction.response.send_message(embed=embed)
    
    @sticker_group.subcommand(
        name="remove",
        description="Eliminar sticker del servidor"
    )
    async def remove_sticker(
        self,
        interaction: nextcord.Interaction,
        sticker_id: str = nextcord.SlashOption(
            description="ID del sticker a eliminar"
        )
    ):
        """eliminar sticker del servidor"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Gestionar Servidor**.",
                ephemeral=True
            )
            return
        
        # Buscar sticker
        sticker = nextcord.utils.get(interaction.guild.stickers, id=int(sticker_id))
        
        if not sticker:
            await interaction.response.send_message(
                f"❌ No se encontró el sticker con ID `{sticker_id}`.",
                ephemeral=True
            )
            return
        
        try:
            await sticker.delete(reason=f"Eliminado por {interaction.user}")
            
            embed = nextcord.Embed(
                title="🗑️ Sticker Eliminado",
                description=f"Sticker **{sticker.name}** eliminado exitosamente.",
                color=nextcord.Color.red()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error eliminando sticker: {e}")
            await interaction.response.send_message("❌ Error eliminando el sticker.")
    
    @sticker_group.subcommand(
        name="trending",
        description="Ver stickers populares del momento"
    )
    async def trending_stickers(self, interaction: nextcord.Interaction):
        """mostrar stickers trending"""
        
        # Lista de stickers populares (ejemplo)
        trending = [
            {"name": "Chad Wojak", "category": "Memes", "popularity": "🔥🔥🔥🔥🔥"},
            {"name": "Crying Cat", "category": "Animals", "popularity": "🔥🔥🔥🔥"},
            {"name": "Anime Smug", "category": "Anime", "popularity": "🔥🔥🔥🔥"},
            {"name": "Pepe Clap", "category": "Memes", "popularity": "🔥🔥🔥"},
            {"name": "Blob Heart", "category": "Reactions", "popularity": "🔥🔥🔥"},
        ]
        
        embed = nextcord.Embed(
            title="📈 Stickers Trending",
            description="Los stickers más populares del momento",
            color=nextcord.Color.gold()
        )
        
        for i, sticker in enumerate(trending, 1):
            embed.add_field(
                name=f"{i}. {sticker['name']}",
                value=f"Categoría: {sticker['category']}\nPopularidad: {sticker['popularity']}",
                inline=True
            )
        
        embed.add_field(
            name="💡 Tip",
            value="Busca estos stickers en Google o sitios como GIPHY para encontrar las imágenes.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    def cog_unload(self):
        """cerrar sesión al descargar"""
        # La sesión se cerrará automáticamente al finalizar el programa
        pass

def setup(bot):
    """cargar el cog"""
    bot.add_cog(StickerManager(bot))
