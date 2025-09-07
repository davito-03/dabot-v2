import nextcord
from nextcord.ext import commands
import aiohttp
import logging
import asyncio
import json
import random

logger = logging.getLogger(__name__)

class EmojiManager(commands.Cog):
    """sistema para añadir emojis y stickers desde internet"""
    
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        
        # URLs de APIs de emojis
        self.emoji_sources = {
            "trending": "https://emoji-api.com/emojis?access_key=YOUR_KEY",
            "categories": {
                "animals": ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯"],
                "faces": ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇"],
                "hearts": ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💕"],
                "gaming": ["🎮", "🕹️", "👾", "🎯", "🎲", "🃏", "🎪", "🎨", "🎭", "🎪"],
                "tech": ["💻", "⌚", "📱", "💾", "💿", "📀", "🖥️", "⌨️", "🖱️", "🖨️"],
                "food": ["🍎", "🍊", "🍋", "🍌", "🍉", "🍇", "🍓", "🫐", "🍈", "🍒"]
            }
        }
        
        # Pack de emojis personalizados populares
        self.custom_emoji_packs = {
            "pepe": [
                "https://cdn.7tv.app/emote/60ae958e229664e8667aea38/4x.webp",  # pepeHappy
                "https://cdn.7tv.app/emote/60ae8e5a229664e8667ae84c/4x.webp",  # pepeSad
                "https://cdn.7tv.app/emote/60ae9177229664e8667aeb13/4x.webp",  # pepeClap
                "https://cdn.7tv.app/emote/60ae945c229664e8667ae9f7/4x.webp",  # pepePog
                "https://cdn.7tv.app/emote/60ae9417229664e8667ae9d4/4x.webp"   # pepeThink
            ],
            "kappa": [
                "https://static-cdn.jtvnw.net/emoticons/v2/25/default/dark/3.0",  # Kappa
                "https://static-cdn.jtvnw.net/emoticons/v2/354/default/dark/3.0", # 4Head
                "https://static-cdn.jtvnw.net/emoticons/v2/425618/default/dark/3.0" # LUL
            ],
            "discord": [
                "https://cdn.discordapp.com/emojis/393852367751086090.gif",  # Blob dance
                "https://cdn.discordapp.com/emojis/393852367348670474.png",  # Blob happy
                "https://cdn.discordapp.com/emojis/393852367856930817.png"   # Blob love
            ]
        }
    
    @nextcord.slash_command(
        name="emoji",
        description="Comandos para gestionar emojis del servidor"
    )
    async def emoji_group(self, interaction: nextcord.Interaction):
        pass
    
    @emoji_group.subcommand(
        name="add",
        description="Añadir emoji personalizado al servidor"
    )
    async def add_emoji(
        self,
        interaction: nextcord.Interaction,
        url: str = nextcord.SlashOption(
            description="URL de la imagen del emoji"
        ),
        nombre: str = nextcord.SlashOption(
            description="Nombre del emoji (sin espacios)"
        )
    ):
        """añadir emoji desde URL"""
        
        if not interaction.user.guild_permissions.manage_emojis:
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Gestionar Emojis** para usar este comando.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            # Descargar imagen
            async with self.session.get(url) as response:
                if response.status != 200:
                    await interaction.followup.send("❌ No se pudo descargar la imagen.")
                    return
                
                image_data = await response.read()
                
                # Verificar tamaño (máximo 256KB para Discord)
                if len(image_data) > 256 * 1024:
                    await interaction.followup.send("❌ La imagen es muy grande (máximo 256KB).")
                    return
            
            # Crear emoji
            emoji = await interaction.guild.create_custom_emoji(
                name=nombre,
                image=image_data,
                reason=f"Emoji añadido por {interaction.user}"
            )
            
            embed = nextcord.Embed(
                title="✅ Emoji Añadido",
                description=f"Emoji **{emoji.name}** añadido exitosamente.",
                color=nextcord.Color.green()
            )
            embed.add_field(
                name="Uso",
                value=f"`:{emoji.name}:` o {emoji}",
                inline=False
            )
            embed.set_thumbnail(url=emoji.url)
            
            await interaction.followup.send(embed=embed)
            
        except nextcord.HTTPException as e:
            if "Maximum number of emojis reached" in str(e):
                await interaction.followup.send("❌ El servidor ha alcanzado el límite de emojis.")
            else:
                await interaction.followup.send(f"❌ Error creando emoji: {e}")
        except Exception as e:
            logger.error(f"Error añadiendo emoji: {e}")
            await interaction.followup.send("❌ Error procesando la imagen.")
    
    @emoji_group.subcommand(
        name="pack",
        description="Añadir pack de emojis temático"
    )
    async def add_emoji_pack(
        self,
        interaction: nextcord.Interaction,
        pack: str = nextcord.SlashOption(
            description="Pack de emojis a instalar",
            choices=["pepe", "kappa", "discord", "gaming", "cute"]
        )
    ):
        """instalar pack de emojis"""
        
        if not interaction.user.guild_permissions.manage_emojis:
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Gestionar Emojis**.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Pack de emojis populares
        packs = {
            "pepe": {
                "name": "Pack Pepe",
                "emojis": [
                    ("pepe_happy", "https://cdn.betterttv.net/emote/5b1740221c5a6065a7bad4b5/3x"),
                    ("pepe_sad", "https://cdn.betterttv.net/emote/5b90e5cd0972937ade816c3b/3x"),
                    ("pepe_clap", "https://cdn.betterttv.net/emote/5d38aaa592fc550c2d5996b8/3x"),
                    ("pepe_pog", "https://cdn.betterttv.net/emote/5e36584b636609bb5059b99a/3x")
                ]
            },
            "kappa": {
                "name": "Pack Twitch",
                "emojis": [
                    ("kappa", "https://static-cdn.jtvnw.net/emoticons/v2/25/default/dark/3.0"),
                    ("4head", "https://static-cdn.jtvnw.net/emoticons/v2/354/default/dark/3.0"),
                    ("lul", "https://static-cdn.jtvnw.net/emoticons/v2/425618/default/dark/3.0")
                ]
            },
            "discord": {
                "name": "Pack Discord",
                "emojis": [
                    ("blob_dance", "https://cdn.discordapp.com/attachments/302050872383242240/359406097441587200/blob_dance.gif"),
                    ("blob_happy", "https://cdn.discordapp.com/attachments/302050872383242240/358407620977516544/blob_happy.png"),
                    ("blob_love", "https://cdn.discordapp.com/attachments/302050872383242240/358410948498456597/blob_love.png")
                ]
            },
            "gaming": {
                "name": "Pack Gaming",
                "emojis": [
                    ("gg", "https://cdn.discordapp.com/attachments/123456789/gg_emoji.png"),
                    ("rip", "https://cdn.discordapp.com/attachments/123456789/rip_emoji.png"),
                    ("ez_clap", "https://cdn.discordapp.com/attachments/123456789/ez_clap.png")
                ]
            },
            "cute": {
                "name": "Pack Cute",
                "emojis": [
                    ("cat_heart", "https://cdn.discordapp.com/attachments/123456789/cat_heart.png"),
                    ("uwu", "https://cdn.discordapp.com/attachments/123456789/uwu_emoji.png"),
                    ("owo", "https://cdn.discordapp.com/attachments/123456789/owo_emoji.png")
                ]
            }
        }
        
        if pack not in packs:
            await interaction.followup.send("❌ Pack no encontrado.")
            return
        
        pack_info = packs[pack]
        added_emojis = []
        failed_emojis = []
        
        embed = nextcord.Embed(
            title=f"📦 Instalando {pack_info['name']}",
            description="Añadiendo emojis al servidor...",
            color=nextcord.Color.blue()
        )
        await interaction.followup.send(embed=embed)
        
        for name, url in pack_info['emojis']:
            try:
                # URLs de ejemplo - en producción usarías URLs reales
                if "123456789" in url:  # URLs de ejemplo
                    # Usar emojis unicode como fallback
                    fallback_emojis = {
                        "gg": "🎮",
                        "rip": "💀", 
                        "ez_clap": "👏",
                        "cat_heart": "😻",
                        "uwu": "🥺",
                        "owo": "👀"
                    }
                    continue  # Saltar URLs de ejemplo
                
                async with self.session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        if len(image_data) <= 256 * 1024:
                            emoji = await interaction.guild.create_custom_emoji(
                                name=name,
                                image=image_data,
                                reason=f"Pack {pack} por {interaction.user}"
                            )
                            added_emojis.append(emoji)
                            await asyncio.sleep(1)  # Evitar rate limit
                        else:
                            failed_emojis.append(f"{name} (muy grande)")
                    else:
                        failed_emojis.append(f"{name} (error descarga)")
                        
            except nextcord.HTTPException:
                failed_emojis.append(f"{name} (límite servidor)")
                break  # Si llegamos al límite, parar
            except Exception as e:
                failed_emojis.append(f"{name} (error)")
                logger.error(f"Error añadiendo emoji {name}: {e}")
        
        # Resultado final
        result_embed = nextcord.Embed(
            title=f"✅ {pack_info['name']} Instalado",
            color=nextcord.Color.green()
        )
        
        if added_emojis:
            emoji_list = " ".join([str(emoji) for emoji in added_emojis])
            result_embed.add_field(
                name=f"✅ Emojis Añadidos ({len(added_emojis)})",
                value=emoji_list,
                inline=False
            )
        
        if failed_emojis:
            result_embed.add_field(
                name=f"❌ Errores ({len(failed_emojis)})",
                value="\n".join(failed_emojis),
                inline=False
            )
        
        await interaction.edit_original_message(embed=result_embed)
    
    @emoji_group.subcommand(
        name="random",
        description="Añadir emoji aleatorio popular"
    )
    async def random_emoji(self, interaction: nextcord.Interaction):
        """añadir emoji aleatorio popular"""
        
        if not interaction.user.guild_permissions.manage_emojis:
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Gestionar Emojis**.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Lista de emojis populares con URLs reales
        popular_emojis = [
            ("stonks", "https://cdn.betterttv.net/emote/5f986b9ef8b3f62ceda9b78b/3x"),
            ("monkas", "https://cdn.betterttv.net/emote/56e9f494fff3cc5c35e5287e/3x"),
            ("poggers", "https://cdn.betterttv.net/emote/58ae8407ff7b7276f8e594f2/3x"),
            ("omegalul", "https://cdn.betterttv.net/emote/583089f4737a8e61abb0186b/3x")
        ]
        
        name, url = random.choice(popular_emojis)
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    emoji = await interaction.guild.create_custom_emoji(
                        name=name,
                        image=image_data,
                        reason=f"Emoji aleatorio por {interaction.user}"
                    )
                    
                    embed = nextcord.Embed(
                        title="🎲 Emoji Aleatorio Añadido",
                        description=f"¡Emoji **{emoji.name}** añadido! {emoji}",
                        color=nextcord.Color.random()
                    )
                    embed.set_thumbnail(url=emoji.url)
                    
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ Error descargando emoji aleatorio.")
                    
        except Exception as e:
            logger.error(f"Error añadiendo emoji aleatorio: {e}")
            await interaction.followup.send("❌ Error añadiendo emoji aleatorio.")
    
    @emoji_group.subcommand(
        name="list",
        description="Ver emojis del servidor"
    )
    async def list_emojis(self, interaction: nextcord.Interaction):
        """listar emojis del servidor"""
        
        emojis = interaction.guild.emojis
        
        if not emojis:
            await interaction.response.send_message("❌ Este servidor no tiene emojis personalizados.")
            return
        
        embed = nextcord.Embed(
            title=f"😀 Emojis de {interaction.guild.name}",
            description=f"Total: {len(emojis)}/{interaction.guild.emoji_limit}",
            color=nextcord.Color.blue()
        )
        
        # Mostrar emojis en grupos de 20
        emoji_text = ""
        for i, emoji in enumerate(emojis):
            emoji_text += f"{emoji} `:{emoji.name}:`\n"
            
            if (i + 1) % 20 == 0 or i == len(emojis) - 1:
                embed.add_field(
                    name=f"Emojis {i//20 + 1}",
                    value=emoji_text or "Ninguno",
                    inline=True
                )
                emoji_text = ""
        
        await interaction.response.send_message(embed=embed)
    
    @emoji_group.subcommand(
        name="remove",
        description="Eliminar emoji del servidor"
    )
    async def remove_emoji(
        self,
        interaction: nextcord.Interaction,
        emoji: str = nextcord.SlashOption(
            description="Nombre del emoji a eliminar"
        )
    ):
        """eliminar emoji del servidor"""
        
        if not interaction.user.guild_permissions.manage_emojis:
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Gestionar Emojis**.",
                ephemeral=True
            )
            return
        
        # Buscar emoji
        emoji_obj = nextcord.utils.get(interaction.guild.emojis, name=emoji)
        
        if not emoji_obj:
            await interaction.response.send_message(
                f"❌ No se encontró el emoji `{emoji}`.",
                ephemeral=True
            )
            return
        
        try:
            await emoji_obj.delete(reason=f"Eliminado por {interaction.user}")
            
            embed = nextcord.Embed(
                title="🗑️ Emoji Eliminado",
                description=f"Emoji **{emoji}** eliminado exitosamente.",
                color=nextcord.Color.red()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error eliminando emoji: {e}")
            await interaction.response.send_message("❌ Error eliminando el emoji.")
    
    async def cog_unload(self):
        """cerrar sesión al descargar"""
        await self.session.close()

def setup(bot):
    """cargar el cog"""
    bot.add_cog(EmojiManager(bot))
