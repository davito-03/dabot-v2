"""
Sistema de Memes y Entretenimiento v2.0
Incluye comandos de memes, publicaciones temáticas y más diversión
Por davito - Dabot v2
"""

import logging
import random
import aiohttp
import nextcord
from nextcord.ext import commands
import json
import os

logger = logging.getLogger(__name__)

class MemeView(nextcord.ui.View):
    """vista para interactuar con memes"""
    
    def __init__(self):
        super().__init__(timeout=300)
    
    @nextcord.ui.button(label="😂", style=nextcord.ButtonStyle.success)
    async def like_meme(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("😂 ¡Te gustó este meme!", ephemeral=True)
    
    @nextcord.ui.button(label="💀", style=nextcord.ButtonStyle.danger)
    async def dislike_meme(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("💀 Este meme no te convence...", ephemeral=True)
    
    @nextcord.ui.button(label="🔄 Otro", style=nextcord.ButtonStyle.primary)
    async def another_meme(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        meme_cog = interaction.client.get_cog("MemesAndFun")
        if meme_cog:
            await meme_cog.send_random_meme(interaction, followup=True)

class PostTypeSelect(nextcord.ui.Select):
    """selector de tipo de publicación"""
    
    def __init__(self):
        options = [
            nextcord.SelectOption(
                label="💬 General",
                description="Publicación general para cualquier tema",
                emoji="💬",
                value="general"
            ),
            nextcord.SelectOption(
                label="🎯 Debate",
                description="Tema para debate y discusión",
                emoji="🎯",
                value="debate"
            ),
            nextcord.SelectOption(
                label="❓ Pregunta",
                description="Hacer una pregunta a la comunidad",
                emoji="❓",
                value="pregunta"
            ),
            nextcord.SelectOption(
                label="🎮 Buscar gente para jugar",
                description="Buscar compañeros de juego",
                emoji="🎮",
                value="gaming"
            ),
            nextcord.SelectOption(
                label="💼 Proyectos",
                description="Colaboración en proyectos",
                emoji="💼",
                value="proyectos"
            ),
            nextcord.SelectOption(
                label="📺 Recomendaciones",
                description="Recomendar series, películas, etc.",
                emoji="📺",
                value="recomendaciones"
            ),
            nextcord.SelectOption(
                label="💡 Ideas",
                description="Compartir ideas creativas",
                emoji="💡",
                value="ideas"
            ),
            nextcord.SelectOption(
                label="🎨 Arte",
                description="Mostrar trabajos artísticos",
                emoji="🎨",
                value="arte"
            )
        ]
        
        super().__init__(
            placeholder="Elige el tipo de publicación...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: nextcord.Interaction):
        selected_type = self.values[0]
        
        type_info = {
            "general": {"emoji": "💬", "color": nextcord.Color.blue(), "title": "Publicación General"},
            "debate": {"emoji": "🎯", "color": nextcord.Color.red(), "title": "Tema de Debate"},
            "pregunta": {"emoji": "❓", "color": nextcord.Color.orange(), "title": "Pregunta a la Comunidad"},
            "gaming": {"emoji": "🎮", "color": nextcord.Color.purple(), "title": "Buscar Compañeros de Juego"},
            "proyectos": {"emoji": "💼", "color": nextcord.Color.dark_blue(), "title": "Colaboración en Proyectos"},
            "recomendaciones": {"emoji": "📺", "color": nextcord.Color.green(), "title": "Recomendaciones"},
            "ideas": {"emoji": "💡", "color": nextcord.Color.gold(), "title": "Ideas Creativas"},
            "arte": {"emoji": "🎨", "color": nextcord.Color.magenta(), "title": "Trabajo Artístico"}
        }
        
        info = type_info[selected_type]
        
        modal = PostModal(selected_type, info)
        await interaction.response.send_modal(modal)

class PostModal(nextcord.ui.Modal):
    """modal para crear publicación"""
    
    def __init__(self, post_type: str, type_info: dict):
        self.post_type = post_type
        self.type_info = type_info
        
        super().__init__(
            title=f"Crear {type_info['title']}",
            timeout=300
        )
        
        self.title_input = nextcord.ui.TextInput(
            label="Título",
            placeholder="Escribe el título de tu publicación...",
            required=True,
            max_length=100
        )
        self.add_item(self.title_input)
        
        self.content_input = nextcord.ui.TextInput(
            label="Contenido",
            placeholder="Describe tu publicación en detalle...",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
            max_length=1000
        )
        self.add_item(self.content_input)
        
        if post_type == "gaming":
            self.game_input = nextcord.ui.TextInput(
                label="Juego",
                placeholder="¿Para qué juego buscas gente?",
                required=False,
                max_length=50
            )
            self.add_item(self.game_input)
        
        if post_type == "recomendaciones":
            self.category_input = nextcord.ui.TextInput(
                label="Categoría",
                placeholder="Series, películas, libros, música...",
                required=False,
                max_length=30
            )
            self.add_item(self.category_input)
    
    async def on_submit(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title=f"{self.type_info['emoji']} {self.title_input.value}",
            description=self.content_input.value,
            color=self.type_info['color'],
            timestamp=nextcord.utils.utcnow()
        )
        
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )
        
        embed.add_field(
            name="📂 Tipo",
            value=self.type_info['title'],
            inline=True
        )
        
        if hasattr(self, 'game_input') and self.game_input.value:
            embed.add_field(
                name="🎮 Juego",
                value=self.game_input.value,
                inline=True
            )
        
        if hasattr(self, 'category_input') and self.category_input.value:
            embed.add_field(
                name="📂 Categoría",
                value=self.category_input.value,
                inline=True
            )
        
        # Botones de interacción
        view = PostInteractionView()
        
        await interaction.response.send_message(
            content=f"📢 **Nueva publicación de {interaction.user.mention}**",
            embed=embed,
            view=view
        )

class PostInteractionView(nextcord.ui.View):
    """vista para interactuar con publicaciones"""
    
    def __init__(self):
        super().__init__(timeout=None)
        self.likes = 0
        self.interested = 0
    
    @nextcord.ui.button(label="👍", style=nextcord.ButtonStyle.success, custom_id="post_like")
    async def like_post(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.likes += 1
        button.label = f"👍 {self.likes}"
        await interaction.response.edit_message(view=self)
    
    @nextcord.ui.button(label="🙋‍♂️ Me interesa", style=nextcord.ButtonStyle.primary, custom_id="post_interested")
    async def interested_post(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.interested += 1
        button.label = f"🙋‍♂️ {self.interested}"
        await interaction.response.edit_message(view=self)
    
    @nextcord.ui.button(label="💬 Comentar", style=nextcord.ButtonStyle.secondary, custom_id="post_comment")
    async def comment_post(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "💬 ¡Responde a este mensaje para comentar en la publicación!",
            ephemeral=True
        )

class PostCreateView(nextcord.ui.View):
    """vista principal para crear publicaciones"""
    
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PostTypeSelect())

class MemesAndFun(commands.Cog):
    """sistema de memes y entretenimiento"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # APIs de memes
        self.meme_apis = [
            "https://meme-api.com/gimme",
            "https://some-random-api.ml/meme",
            "https://www.reddit.com/r/memes/random/.json"
        ]
        
        # Memes locales como backup
        self.local_memes = [
            "https://i.imgur.com/example1.jpg",
            "https://i.imgur.com/example2.jpg",
            # Se pueden agregar más URLs de memes
        ]
        
        # Chistes y frases divertidas
        self.jokes = [
            "¿Por qué los programadores prefieren el modo oscuro? Porque la luz atrae a los bugs! 🐛",
            "Un bit entra a un bar y pide una cerveza. El barman le dice: 'Lo siento, pero aquí solo servimos bytes'",
            "¿Cuál es el café favorito de los desarrolladores? Java ☕",
            "¿Por qué los desarrolladores odian la naturaleza? Porque tiene demasiados bugs 🐛",
            "No es un bug, es una característica no documentada 😎",
            "99 bugs en el código, quitas uno, compilas de nuevo... 127 bugs en el código 🤦‍♂️",
            "Stack Overflow: donde las preguntas duplicadas tienen más respuestas que las originales",
            "La vida es como CSS: a veces funciona, a veces no, y nadie sabe por qué 🎨"
        ]
        
        # Verdad o reto
        self.truths = [
            "¿Cuál es tu mayor miedo?",
            "¿Cuál fue tu momento más embarazoso?",
            "¿Qué es lo más loco que has hecho por amor?",
            "¿Cuál es tu crush secreto?",
            "¿Qué es lo que nunca le contarías a tus padres?",
            "¿Cuál es tu mayor arrepentimiento?",
            "¿Qué piensas antes de dormir?",
            "¿Cuál es tu mayor inseguridad?"
        ]
        
        self.dares = [
            "Haz 10 flexiones",
            "Canta tu canción favorita",
            "Imita a un animal por 30 segundos",
            "Cuenta un chiste malo",
            "Haz una cara graciosa y tómarte una foto",
            "Baila sin música por 1 minuto",
            "Habla con acento por 5 minutos",
            "Haz una llamada rara a un amigo"
        ]
    
    @nextcord.slash_command(name="meme", description="comandos de memes")
    async def meme_group(self, interaction: nextcord.Interaction):
        pass
    
    @meme_group.subcommand(name="random", description="obtener un meme aleatorio")
    async def random_meme(self, interaction: nextcord.Interaction):
        """enviar meme aleatorio"""
        await self.send_random_meme(interaction)
    
    async def send_random_meme(self, interaction: nextcord.Interaction, followup: bool = False):
        """función auxiliar para enviar memes"""
        try:
            # Intentar obtener meme de API
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get("https://meme-api.com/gimme") as response:
                        if response.status == 200:
                            data = await response.json()
                            meme_url = data.get('url')
                            meme_title = data.get('title', 'Meme Aleatorio')
                            subreddit = data.get('subreddit', 'memes')
                        else:
                            raise Exception("API no disponible")
                except:
                    # Usar meme local como backup
                    meme_url = random.choice(self.local_memes)
                    meme_title = "Meme Aleatorio"
                    subreddit = "local"
        except:
            meme_url = random.choice(self.local_memes)
            meme_title = "Meme Aleatorio"
            subreddit = "local"
        
        embed = nextcord.Embed(
            title=f"😂 {meme_title}",
            color=nextcord.Color.random()
        )
        embed.set_image(url=meme_url)
        embed.set_footer(text=f"Fuente: r/{subreddit}")
        
        view = MemeView()
        
        if followup:
            await interaction.followup.send(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view)
    
    @meme_group.subcommand(name="chiste", description="contar un chiste aleatorio")
    async def joke(self, interaction: nextcord.Interaction):
        """contar chiste aleatorio"""
        joke = random.choice(self.jokes)
        
        embed = nextcord.Embed(
            title="😄 Chiste del Día",
            description=joke,
            color=nextcord.Color.gold()
        )
        embed.set_footer(text="¿Te gustó? Reacciona con 😂")
        
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="publicacion", description="crear una publicación temática")
    async def create_post(self, interaction: nextcord.Interaction):
        """crear publicación con diferentes temáticas"""
        embed = nextcord.Embed(
            title="📝 Crear Publicación",
            description="Elige el tipo de publicación que quieres crear:",
            color=nextcord.Color.blue()
        )
        embed.add_field(
            name="📋 Tipos Disponibles",
            value="💬 General • 🎯 Debate • ❓ Pregunta\n🎮 Gaming • 💼 Proyectos • 📺 Recomendaciones\n💡 Ideas • 🎨 Arte",
            inline=False
        )
        
        view = PostCreateView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @nextcord.slash_command(name="juegos", description="juegos de entretenimiento")
    async def games_group(self, interaction: nextcord.Interaction):
        pass
    
    @games_group.subcommand(name="verdad_o_reto", description="jugar verdad o reto")
    async def truth_or_dare(self, interaction: nextcord.Interaction, opcion: str = None):
        """juego de verdad o reto"""
        if not opcion:
            embed = nextcord.Embed(
                title="🎲 Verdad o Reto",
                description="¡Elige tu destino!",
                color=nextcord.Color.purple()
            )
            embed.add_field(
                name="✅ Opciones",
                value="• `verdad` - Te haré una pregunta personal\n• `reto` - Te daré un desafío divertido\n• `aleatorio` - Sorpréndeme",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            return
        
        opcion = opcion.lower()
        
        if opcion in ["verdad", "truth"]:
            question = random.choice(self.truths)
            embed = nextcord.Embed(
                title="🤔 Verdad",
                description=f"**{interaction.user.mention}**, {question}",
                color=nextcord.Color.blue()
            )
        elif opcion in ["reto", "dare"]:
            dare = random.choice(self.dares)
            embed = nextcord.Embed(
                title="😈 Reto",
                description=f"**{interaction.user.mention}**, {dare}",
                color=nextcord.Color.red()
            )
        elif opcion == "aleatorio":
            if random.choice([True, False]):
                question = random.choice(self.truths)
                embed = nextcord.Embed(
                    title="🤔 Verdad (Aleatorio)",
                    description=f"**{interaction.user.mention}**, {question}",
                    color=nextcord.Color.blue()
                )
            else:
                dare = random.choice(self.dares)
                embed = nextcord.Embed(
                    title="😈 Reto (Aleatorio)",
                    description=f"**{interaction.user.mention}**, {dare}",
                    color=nextcord.Color.red()
                )
        else:
            await interaction.response.send_message(
                "❌ Opción no válida. Usa: `verdad`, `reto` o `aleatorio`",
                ephemeral=True
            )
            return
        
        embed.set_footer(text="¡No hagas trampa! 😏")
        await interaction.response.send_message(embed=embed)
    
    @games_group.subcommand(name="8ball", description="pregunta a la bola mágica")
    async def eight_ball(self, interaction: nextcord.Interaction, pregunta: str):
        """bola mágica 8"""
        responses = [
            "✅ Es seguro",
            "✅ Definitivamente sí",
            "✅ Sin duda",
            "✅ Sí, definitivamente",
            "✅ Puedes confiar en ello",
            "✅ Como yo lo veo, sí",
            "✅ Muy probable",
            "✅ Las perspectivas son buenas",
            "✅ Sí",
            "✅ Los signos apuntan a que sí",
            "🤔 Respuesta confusa, intenta de nuevo",
            "🤔 Pregunta de nuevo más tarde",
            "🤔 Mejor no te lo digo ahora",
            "🤔 No puedo predecirlo ahora",
            "🤔 Concéntrate y pregunta de nuevo",
            "❌ No cuentes con ello",
            "❌ Mi respuesta es no",
            "❌ Mis fuentes dicen que no",
            "❌ Las perspectivas no son muy buenas",
            "❌ Muy dudoso"
        ]
        
        answer = random.choice(responses)
        
        embed = nextcord.Embed(
            title="🎱 Bola Mágica 8",
            color=nextcord.Color.dark_purple()
        )
        embed.add_field(
            name="❓ Pregunta",
            value=pregunta,
            inline=False
        )
        embed.add_field(
            name="🔮 Respuesta",
            value=answer,
            inline=False
        )
        embed.set_footer(text=f"Preguntado por {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @games_group.subcommand(name="numero", description="adivina el número del 1 al 100")
    async def guess_number(self, interaction: nextcord.Interaction, numero: int):
        """juego de adivinar número"""
        if numero < 1 or numero > 100:
            await interaction.response.send_message(
                "❌ El número debe estar entre 1 y 100.",
                ephemeral=True
            )
            return
        
        secret_number = random.randint(1, 100)
        
        if numero == secret_number:
            embed = nextcord.Embed(
                title="🎉 ¡GANASTE!",
                description=f"¡Increíble! El número era **{secret_number}**",
                color=nextcord.Color.green()
            )
        elif abs(numero - secret_number) <= 5:
            embed = nextcord.Embed(
                title="🔥 ¡Muy cerca!",
                description=f"Elegiste **{numero}** y el número era **{secret_number}**\n¡Estuviste muy cerca!",
                color=nextcord.Color.orange()
            )
        elif abs(numero - secret_number) <= 15:
            embed = nextcord.Embed(
                title="👍 Cerca",
                description=f"Elegiste **{numero}** y el número era **{secret_number}**\nNo estuvo mal",
                color=nextcord.Color.yellow()
            )
        else:
            embed = nextcord.Embed(
                title="❌ Lejos",
                description=f"Elegiste **{numero}** y el número era **{secret_number}**\n¡Mejor suerte la próxima vez!",
                color=nextcord.Color.red()
            )
        
        embed.set_footer(text="¡Intenta de nuevo cuando quieras!")
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="amor", description="calcular porcentaje de amor entre dos personas")
    async def love_calculator(self, interaction: nextcord.Interaction, persona1: nextcord.Member, persona2: nextcord.Member):
        """calculadora de amor"""
        # Generar porcentaje "aleatorio" pero consistente basado en IDs
        combined_id = str(persona1.id) + str(persona2.id)
        random.seed(int(combined_id[-8:]))  # Usar los últimos 8 dígitos como seed
        percentage = random.randint(0, 100)
        random.seed()  # Resetear seed
        
        if percentage >= 90:
            emoji = "💕"
            message = "¡Amor verdadero! Están hechos el uno para el otro"
        elif percentage >= 70:
            emoji = "💖"
            message = "¡Muy buena compatibilidad! Hay química"
        elif percentage >= 50:
            emoji = "💘"
            message = "Hay potencial, ¡vale la pena intentarlo!"
        elif percentage >= 30:
            emoji = "💔"
            message = "Mejor como amigos..."
        else:
            emoji = "💀"
            message = "¡Oh no! Esto no va a funcionar"
        
        embed = nextcord.Embed(
            title=f"{emoji} Calculadora de Amor",
            description=f"**{persona1.display_name}** 💕 **{persona2.display_name}**",
            color=nextcord.Color.pink()
        )
        embed.add_field(
            name="💝 Resultado",
            value=f"**{percentage}%** de compatibilidad\n\n{message}",
            inline=False
        )
        embed.set_footer(text="Los resultados son 100% científicos 😉")
        
        await interaction.response.send_message(embed=embed)

def setup(bot):
    """cargar el cog"""
    bot.add_cog(MemesAndFun(bot))
