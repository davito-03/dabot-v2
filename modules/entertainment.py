"""
Módulo de entretenimiento avanzado para el bot
por davito
"""

import random
import logging
import asyncio
import aiohttp
import json
import nextcord
from nextcord.ext import commands

logger = logging.getLogger(__name__)

class Entertainment(commands.Cog):
    """comandos de entretenimiento avanzados"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # chistes por categorías (muchísimos más)
        self.jokes_categories = {
            "programacion": [
                "¿por qué los programadores prefieren el modo oscuro? porque la luz atrae bugs.",
                "¿cuántos programadores necesitas para cambiar una bombilla? ninguno, es un problema de hardware.",
                "¿cómo se dice 'café' en discord? java.lang.coffee",
                "¿por qué los desarrolladores odian la naturaleza? tiene muchos bugs.",
                "¿qué le dice un bit a otro bit? nos vemos en el byte.",
                "¿por qué git es como un ex? siempre vuelves a hacer commit con él.",
                "¿cuál es la diferencia entre un programador y un usuario? el programador piensa que sabe lo que el usuario quiere.",
                "¿por qué los robots nunca entran en pánico? porque tienen nerviOS de acero.",
                "¿qué hace un programador cuando no puede dormir? cuenta ovejas en binario.",
                "¿por qué los desarrolladores web llevan lentes? porque no pueden c#.",
                "un sql query entra a un bar, se acerca a dos tablas y pregunta: '¿puedo unirme?'",
                "¿cómo maldice un desarrollador de javascript? '¡nan!'",
                "¿por qué python se llama python? porque es el único lenguaje que no muerde... mucho.",
                "¿qué le dice un array a otro array? 'nos indexamos luego.'",
                "¿por qué los hackers son buenos en fiestas? porque siempre encuentran la manera de entrar.",
                "¿por qué los programadores odian la luz del sol? porque prefieren las ventanas.",
                "¿cuál es el lenguaje favorito de los vampiros? cobol.",
                "¿por qué los desarrolladores de frontend siempre están estresados? porque todo el mundo ve su trabajo.",
                "¿qué es lo que más le gusta a un programador de css? el padding, porque le da espacio personal.",
                "¿por qué los administradores de base de datos son pesimistas? porque siempre esperan un rollback."
            ],
            "adultos": [
                "mi esposa me dijo que dejara de cantar 'wonderwall'. dije 'tal vez'.",
                "¿sabes por qué no confío en las escaleras? siempre están tramando algo.",
                "estoy leyendo un libro sobre anti-gravedad. ¡no puedo dejarlo!",
                "mi jefe me dijo que tuviera un buen día, así que me fui a casa.",
                "compré zapatos a un traficante. no sé qué me dio, pero he estado viajando toda la semana.",
                "¿por qué los esqueletos no pelean? no tienen agallas.",
                "le dije a mi esposa que era hermosa. ella dijo 'gracias'. le dije 'de nada, estaba hablando por teléfono'.",
                "fui al médico y le dije 'doctor, me duele cuando hago esto'. me dijo 'pues no lo hagas'.",
                "mi suegra cayó en un pozo lleno de agua. que profundo... el pozo.",
                "¿cuál es la diferencia entre un pez y un piano? no puedes atorar un piano.",
                "me robaron el diccionario de sinónimos ayer. no tengo palabras para describir lo furioso que estoy.",
                "¿por qué los fantasmas son malos mentirosos? porque puedes ver a través de ellos.",
                "un hombre entra en una biblioteca y pide un libro sobre paranoia. la bibliotecaria susurra: 'están detrás de ti'.",
                "¿qué obtienes cuando cruzas un pez y un elefante? puedes nadar hasta el fondo del océano pero nunca olvidas el camino de vuelta.",
                "mi esposa me acusó de ser inmaduro. estaba tan sorprendido que casi me ahogo con mis cereales de formas divertidas."
            ],
            "inapropiados": [
                "¿cuál es la diferencia entre una pizza y tu opinion? que me pidieron la pizza.",
                "mi ex me dijo que nunca encontraría a alguien como ella. le dije 'espero que tengas razón'.",
                "¿por qué los hombres tienen agujeros en su ropa interior? para que puedan meter las manos en los bolsillos.",
                "mi novia me dejó por mi obsesión con los videojuegos. que lástima, estábamos en el nivel final.",
                "¿cuál es la diferencia entre tu trabajo y tu esposa? después de 10 años, tu trabajo todavía chupa.",
                "le dije a mi novia que era la única. aparentemente, también le dijo eso a las otras.",
                "¿por qué las mujeres fingen orgasmos? porque piensan que a los hombres les importa.",
                "mi psicólogo dice que tengo un complejo de superioridad preocupante. le dije que es normal que alguien inferior piense eso.",
                "¿cuál es la diferencia entre un adolescente y una batería? la batería tiene carga positiva.",
                "mi esposa me preguntó si alguna vez había tenido sexo con una fea. le dije 'no, pero si insistes...'",
                "¿por qué dios creó el alcohol? para que las feas también tuvieran oportunidad.",
                "mi novia me dijo que quería que fuéramos más espontáneos en la cama. así que vendí la cama.",
                "¿cuál es el colmo de un gay? llamarse jesús y que no le guste que lo crucifiquen.",
                "¿qué le dice un gay a otro gay? 'te presto mi brocha para que te maquilles'.",
                "mi suegra tiene 4 coches: un volvo, un bmw, un mercedes y cancer terminal."
            ],
            "generales": [
                "¿por qué los pájaros vuelan hacia el sur en invierno? porque es demasiado lejos para caminar.",
                "tengo un amigo que es adicto a los frenos. dice que puede parar cuando quiera.",
                "¿qué hace una abeja en el gimnasio? zum-ba.",
                "me compré un diccionario, pero las páginas estaban en blanco. no tengo palabras.",
                "¿por qué no puedes confiar en los átomos? porque forman todo tipo de cosas.",
                "fui a comprar camuflaje pero no encontré nada.",
                "¿cuál es el café más peligroso del mundo? el ex-preso.",
                "¿qué le dice un jardinero a otro? seamos felices mientras podamos.",
                "¿por qué los matemáticos son tan buenos en halloween? porque son buenos con los números irracionales.",
                "mi amigo dice que no entiende la clonación. le dije que hace dos de nosotros.",
                "¿cuál es el animal más antiguo? la cebra, porque está en blanco y negro.",
                "¿por qué los fantasmas van al bar? por los boos (booze).",
                "tengo un chiste sobre la construcción, pero todavía lo estoy trabajando.",
                "¿qué obtienes cuando cruzas un cocodrilo y un chaleco? un investigador.",
                "¿por qué no juegas cartas en la sabana? porque hay demasiados guepardos."
            ],
            "tecnologia": [
                "alexa, cuéntame un chiste. 'lo siento, solo puedo contar hasta 3'.",
                "mi wifi está tan lento que descargué una app para hacer ejercicio y llegó caminando.",
                "¿por qué android es verde? porque tiene envidia del iphone.",
                "mi computadora me mantiene callado. cada vez que hablo, dice 'error de sintaxis'.",
                "¿cuál es la diferencia entre un virus y windows? el virus funciona.",
                "compré un teclado de segunda mano. todas las letras están en orden aleatorio. ¡qwerty mierda!",
                "¿por qué los ingenieros confunden halloween y navidad? porque oct 31 = dec 25.",
                "mi iphone se cayó en el váter. ahora es un teléfono acuático.",
                "¿cuál es el wifi favorito de los piratas? arrr-g.",
                "google no tiene respuesta para todo. busqué 'problemas de relación' y me mostró mi historial de navegación.",
                "siri, ¿cómo hago para que mi esposa se ría? 'reproduce tus chistes, dave'.",
                "¿por qué los robots nunca tienen hijos? porque tienen tornillos sueltos.",
                "mi computadora tiene un virus. le dije 'usa mascarilla'.",
                "¿cuál es el lenguaje de programación favorito de un mago? abracadabra++.",
                "instalé un programa antivirus en mi tostadora. ahora hace pan integral."
            ]
        }
        
        # respuestas para 8ball
        self.eightball_responses = [
            "✅ sí, definitivamente.",
            "✅ es cierto.",
            "✅ sin duda alguna.",
            "✅ sí.",
            "✅ puedes confiar en ello.",
            "✅ como yo lo veo, sí.",
            "✅ muy probable.",
            "✅ las perspectivas son buenas.",
            "✅ señales apuntan a que sí.",
            "✅ respuesta nebulosa, intenta de nuevo.",
            "🤔 pregunta de nuevo más tarde.",
            "🤔 mejor no decirte ahora.",
            "🤔 no puedo predecir ahora.",
            "🤔 concéntrate y pregunta de nuevo.",
            "❌ no cuentes con ello.",
            "❌ mi respuesta es no.",
            "❌ mis fuentes dicen que no.",
            "❌ las perspectivas no son muy buenas.",
            "❌ muy dudoso.",
            "❌ no.",
            "🎲 tal vez.",
            "🎲 es posible.",
            "🎲 podría ser.",
            "🎲 las posibilidades son 50/50.",
            "🎲 depende de ti.",
            "🔮 el futuro es incierto.",
            "🔮 las estrellas no están alineadas.",
            "🔮 consulta más tarde.",
            "🔮 mi visión está nublada.",
            "🔮 los dioses aún no han decidido."
        ]
        
        # minijuegos activos
        self.active_games = {}
    
    async def get_joke_from_api(self, category: str = "general"):
        """obtener chiste desde api externa"""
        try:
            async with aiohttp.ClientSession() as session:
                # intentar con api de chistes en inglés
                url = "https://official-joke-api.appspot.com/random_joke"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return f"{data['setup']} {data['punchline']}"
        except Exception as e:
            logger.error(f"error obteniendo chiste de api: {e}")
        
        # fallback a chistes locales
        return random.choice(self.jokes_categories.get(category, self.jokes_categories["generales"]))
    
    @commands.command(name='joke', aliases=['chiste'])
    async def random_joke(self, ctx, categoria: str = None):
        """
        envía un chiste aleatorio
        uso: !joke [programacion/adultos/inapropiados/generales/tecnologia]
        """
        try:
            # verificar categoría
            if categoria and categoria.lower() not in self.jokes_categories:
                categorias_disponibles = ", ".join(self.jokes_categories.keys())
                await ctx.send(f"❌ categoría inválida. disponibles: {categorias_disponibles}")
                return
            
            # verificar si es canal nsfw para chistes adultos/inapropiados
            if categoria and categoria.lower() in ["adultos", "inapropiados"] and not ctx.channel.is_nsfw():
                await ctx.send("🔞 esa categoría solo está disponible en canales nsfw.")
                return
            
            # obtener chiste
            if categoria:
                if random.random() < 0.3:  # 30% de probabilidad de usar api
                    joke = await self.get_joke_from_api(categoria.lower())
                else:
                    joke = random.choice(self.jokes_categories[categoria.lower()])
            else:
                # categoría aleatoria (excluyendo adultos/inapropiados en canales normales)
                available_categories = list(self.jokes_categories.keys())
                if not ctx.channel.is_nsfw():
                    available_categories = [c for c in available_categories if c not in ["adultos", "inapropiados"]]
                
                categoria = random.choice(available_categories)
                joke = random.choice(self.jokes_categories[categoria])
            
            # crear embed
            embed = nextcord.Embed(
                title="😂 ¡chiste aleatorio!",
                description=joke,
                color=nextcord.Color.yellow()
            )
            embed.add_field(name="categoría", value=categoria if categoria else "aleatoria", inline=True)
            embed.set_footer(text=f"solicitado por {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            
            await ctx.send(embed=embed)
            logger.info(f"chiste enviado a {ctx.author} en {ctx.guild}: categoría {categoria}")
            
        except Exception as e:
            logger.error(f"error en comando joke: {e}")
            await ctx.send("❌ error al obtener el chiste.")
    
    @nextcord.slash_command(name="joke", description="obtén un chiste aleatorio")
    async def slash_joke(
        self,
        interaction: nextcord.Interaction,
        categoria: str = nextcord.SlashOption(
            description="categoría del chiste",
            choices=["programacion", "adultos", "inapropiados", "generales", "tecnologia"],
            required=False
        )
    ):
        """comando slash para chistes"""
        try:
            # verificar nsfw
            if categoria and categoria in ["adultos", "inapropiados"] and not interaction.channel.is_nsfw():
                await interaction.response.send_message("🔞 esa categoría solo está disponible en canales nsfw.", ephemeral=True)
                return
            
            # obtener chiste
            if categoria:
                if random.random() < 0.3:
                    joke = await self.get_joke_from_api(categoria)
                else:
                    joke = random.choice(self.jokes_categories[categoria])
            else:
                available_categories = list(self.jokes_categories.keys())
                if not interaction.channel.is_nsfw():
                    available_categories = [c for c in available_categories if c not in ["adultos", "inapropiados"]]
                
                categoria = random.choice(available_categories)
                joke = random.choice(self.jokes_categories[categoria])
            
            embed = nextcord.Embed(
                title="😂 ¡chiste aleatorio!",
                description=joke,
                color=nextcord.Color.yellow()
            )
            embed.add_field(name="categoría", value=categoria if categoria else "aleatoria", inline=True)
            embed.set_footer(text=f"solicitado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"chiste slash enviado a {interaction.user} en {interaction.guild}: categoría {categoria}")
            
        except Exception as e:
            logger.error(f"error en comando slash joke: {e}")
            await interaction.response.send_message("❌ error al obtener el chiste.", ephemeral=True)
    
    # mantener todos los comandos anteriores exactamente iguales
    @commands.command(name='8ball', aliases=['bola8', 'pregunta'])
    async def eight_ball(self, ctx, *, question=None):
        """
        responde a una pregunta con una respuesta aleatoria
        uso: !8ball ¿pregunta?
        """
        try:
            if not question:
                await ctx.send("❌ debes hacer una pregunta. ejemplo: `!8ball ¿lloverá mañana?`")
                return
            
            # verificar que la pregunta termine con signo de interrogación
            if not question.strip().endswith('?'):
                question += "?"
            
            # seleccionar respuesta aleatoria
            response = random.choice(self.eightball_responses)
            
            # crear embed para la respuesta
            embed = nextcord.Embed(
                title="🎱 bola mágica 8",
                color=nextcord.Color.purple()
            )
            embed.add_field(name="pregunta:", value=question, inline=False)
            embed.add_field(name="respuesta:", value=response, inline=False)
            embed.set_footer(text=f"preguntado por {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            
            await ctx.send(embed=embed)
            logger.info(f"8ball respondido a {ctx.author} en {ctx.guild}: {question}")
            
        except Exception as e:
            logger.error(f"error en comando 8ball: {e}")
            await ctx.send("❌ error al procesar tu pregunta.")
    
    @nextcord.slash_command(name="8ball", description="haz una pregunta a la bola mágica 8")
    async def slash_eight_ball(
        self,
        interaction: nextcord.Interaction,
        question: str = nextcord.SlashOption(description="la pregunta que quieres hacer")
    ):
        """comando slash para 8ball"""
        try:
            if not question.strip():
                await interaction.response.send_message("❌ debes hacer una pregunta.", ephemeral=True)
                return
            
            if not question.strip().endswith('?'):
                question += "?"
            
            response = random.choice(self.eightball_responses)
            
            embed = nextcord.Embed(
                title="🎱 bola mágica 8",
                color=nextcord.Color.purple()
            )
            embed.add_field(name="pregunta:", value=question, inline=False)
            embed.add_field(name="respuesta:", value=response, inline=False)
            embed.set_footer(text=f"preguntado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"8ball slash respondido a {interaction.user} en {interaction.guild}: {question}")
            
        except Exception as e:
            logger.error(f"error en comando slash 8ball: {e}")
            await interaction.response.send_message("❌ error al procesar tu pregunta.", ephemeral=True)
    
    @commands.command(name='flip', aliases=['moneda', 'coin'])
    async def coin_flip(self, ctx):
        """
        lanza una moneda virtual
        uso: !flip, !moneda o !coin
        """
        try:
            result = random.choice(['cara', 'cruz'])
            emoji = "🪙" if result == 'cara' else "💰"
            
            embed = nextcord.Embed(
                title=f"{emoji} lanzamiento de moneda",
                description=f"la moneda cayó en: **{result.upper()}**",
                color=nextcord.Color.gold()
            )
            embed.set_footer(text=f"lanzado por {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            
            await ctx.send(embed=embed)
            logger.info(f"moneda lanzada por {ctx.author} en {ctx.guild}: {result}")
            
        except Exception as e:
            logger.error(f"error en comando flip: {e}")
            await ctx.send("❌ error al lanzar la moneda.")
    
    @nextcord.slash_command(name="flip", description="lanza una moneda virtual")
    async def slash_coin_flip(self, interaction: nextcord.Interaction):
        """comando slash para lanzar moneda"""
        try:
            result = random.choice(['cara', 'cruz'])
            emoji = "🪙" if result == 'cara' else "💰"
            
            embed = nextcord.Embed(
                title=f"{emoji} lanzamiento de moneda",
                description=f"la moneda cayó en: **{result.upper()}**",
                color=nextcord.Color.gold()
            )
            embed.set_footer(text=f"lanzado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"moneda slash lanzada por {interaction.user} en {interaction.guild}: {result}")
            
        except Exception as e:
            logger.error(f"error en comando slash flip: {e}")
            await interaction.response.send_message("❌ error al lanzar la moneda.", ephemeral=True)
    
    @commands.command(name='dice', aliases=['dado'])
    async def roll_dice(self, ctx, sides: int = 6):
        """
        lanza un dado con el número de caras especificado
        uso: !dice [caras] (por defecto 6)
        """
        try:
            if sides < 2:
                await ctx.send("❌ el dado debe tener al menos 2 caras.")
                return
            
            if sides > 100:
                await ctx.send("❌ el dado no puede tener más de 100 caras.")
                return
            
            result = random.randint(1, sides)
            
            embed = nextcord.Embed(
                title="🎲 lanzamiento de dado",
                description=f"dado de {sides} caras: **{result}**",
                color=nextcord.Color.blue()
            )
            embed.set_footer(text=f"lanzado por {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
            
            await ctx.send(embed=embed)
            logger.info(f"dado lanzado por {ctx.author} en {ctx.guild}: {result}/{sides}")
            
        except ValueError:
            await ctx.send("❌ proporciona un número válido de caras.")
        except Exception as e:
            logger.error(f"error en comando dice: {e}")
            await ctx.send("❌ error al lanzar el dado.")
    
    @nextcord.slash_command(name="dice", description="lanza un dado con el número de caras especificado")
    async def slash_roll_dice(
        self,
        interaction: nextcord.Interaction,
        sides: int = nextcord.SlashOption(description="número de caras del dado (2-100)", default=6, min_value=2, max_value=100)
    ):
        """comando slash para lanzar dado"""
        try:
            result = random.randint(1, sides)
            
            embed = nextcord.Embed(
                title="🎲 lanzamiento de dado",
                description=f"dado de {sides} caras: **{result}**",
                color=nextcord.Color.blue()
            )
            embed.set_footer(text=f"lanzado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f"dado slash lanzado por {interaction.user} en {interaction.guild}: {result}/{sides}")
            
        except Exception as e:
            logger.error(f"error en comando slash dice: {e}")
            await interaction.response.send_message("❌ error al lanzar el dado.", ephemeral=True)
    
    # nuevos minijuegos
    @commands.command(name='tictactoe', aliases=['3enraya'])
    async def tic_tac_toe(self, ctx, opponent: nextcord.Member = None):
        """
        jugar al tres en raya
        uso: !tictactoe [@oponente]
        """
        try:
            if opponent is None:
                await ctx.send("❌ menciona a un oponente para jugar.")
                return
            
            if opponent == ctx.author:
                await ctx.send("❌ no puedes jugar contra ti mismo.")
                return
            
            if opponent.bot:
                await ctx.send("❌ no puedes jugar contra un bot.")
                return
            
            # crear tablero
            board = [["⬜" for _ in range(3)] for _ in range(3)]
            current_player = ctx.author
            game_id = f"{ctx.guild.id}_{ctx.channel.id}_{ctx.author.id}"
            
            self.active_games[game_id] = {
                "type": "tictactoe",
                "board": board,
                "players": [ctx.author, opponent],
                "current": 0,
                "symbols": ["❌", "⭕"]
            }
            
            embed = nextcord.Embed(
                title="🎮 tres en raya",
                description=f"{ctx.author.mention} vs {opponent.mention}",
                color=nextcord.Color.blue()
            )
            embed.add_field(name="turno actual", value=f"{current_player.mention} (❌)", inline=False)
            embed.add_field(name="tablero", value=self.format_board(board), inline=False)
            embed.add_field(name="cómo jugar", value="usa los números 1-9 para elegir posición", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error en tictactoe: {e}")
            await ctx.send("❌ error al crear el juego.")
    
    def format_board(self, board):
        """formatear tablero de tres en raya"""
        result = ""
        for i, row in enumerate(board):
            result += "".join(row) + "\n"
        return result
    
    @commands.command(name='move', aliases=['m'])
    async def make_move(self, ctx, position: int):
        """
        hacer movimiento en juego activo
        uso: !move [1-9]
        """
        try:
            game_id = f"{ctx.guild.id}_{ctx.channel.id}_{ctx.author.id}"
            
            # buscar juego donde el usuario sea jugador
            game = None
            for gid, g in self.active_games.items():
                if ctx.author in g.get("players", []):
                    game = g
                    game_id = gid
                    break
            
            if not game:
                await ctx.send("❌ no tienes ningún juego activo.")
                return
            
            if game["type"] != "tictactoe":
                await ctx.send("❌ comando solo para tres en raya.")
                return
            
            # verificar turno
            current_player_idx = game["current"]
            if game["players"][current_player_idx] != ctx.author:
                await ctx.send("❌ no es tu turno.")
                return
            
            # verificar posición válida
            if position < 1 or position > 9:
                await ctx.send("❌ posición debe ser entre 1 y 9.")
                return
            
            # convertir a coordenadas
            row = (position - 1) // 3
            col = (position - 1) % 3
            
            # verificar si está libre
            if game["board"][row][col] != "⬜":
                await ctx.send("❌ esa posición ya está ocupada.")
                return
            
            # hacer movimiento
            symbol = game["symbols"][current_player_idx]
            game["board"][row][col] = symbol
            
            # verificar ganador
            winner = self.check_winner(game["board"])
            
            if winner:
                winner_player = game["players"][0] if winner == game["symbols"][0] else game["players"][1]
                
                embed = nextcord.Embed(
                    title="🏆 tres en raya - ¡fin del juego!",
                    description=f"¡{winner_player.mention} ha ganado!",
                    color=nextcord.Color.gold()
                )
                embed.add_field(name="tablero final", value=self.format_board(game["board"]), inline=False)
                
                del self.active_games[game_id]
                
            elif self.is_board_full(game["board"]):
                embed = nextcord.Embed(
                    title="🤝 tres en raya - empate",
                    description="¡el juego terminó en empate!",
                    color=nextcord.Color.orange()
                )
                embed.add_field(name="tablero final", value=self.format_board(game["board"]), inline=False)
                
                del self.active_games[game_id]
                
            else:
                # cambiar turno
                game["current"] = 1 - current_player_idx
                next_player = game["players"][game["current"]]
                next_symbol = game["symbols"][game["current"]]
                
                embed = nextcord.Embed(
                    title="🎮 tres en raya",
                    description=f"{game['players'][0].mention} vs {game['players'][1].mention}",
                    color=nextcord.Color.blue()
                )
                embed.add_field(name="turno actual", value=f"{next_player.mention} ({next_symbol})", inline=False)
                embed.add_field(name="tablero", value=self.format_board(game["board"]), inline=False)
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ posición debe ser un número.")
        except Exception as e:
            logger.error(f"error en move: {e}")
            await ctx.send("❌ error al hacer movimiento.")
    
    def check_winner(self, board):
        """verificar ganador en tres en raya"""
        # filas
        for row in board:
            if row[0] == row[1] == row[2] != "⬜":
                return row[0]
        
        # columnas
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != "⬜":
                return board[0][col]
        
        # diagonales
        if board[0][0] == board[1][1] == board[2][2] != "⬜":
            return board[0][0]
        
        if board[0][2] == board[1][1] == board[2][0] != "⬜":
            return board[0][2]
        
        return None
    
    def is_board_full(self, board):
        """verificar si el tablero está lleno"""
        for row in board:
            if "⬜" in row:
                return False
        return True
    
    @commands.command(name='rps', aliases=['piedrapapeltijera'])
    async def rock_paper_scissors(self, ctx, choice: str = None):
        """
        jugar piedra papel tijera
        uso: !rps [piedra/papel/tijera]
        """
        try:
            choices = {
                'piedra': '🗿',
                'papel': '📄', 
                'tijera': '✂️',
                'rock': '🗿',
                'paper': '📄',
                'scissors': '✂️'
            }
            
            if not choice or choice.lower() not in choices:
                await ctx.send("❌ elige: piedra, papel o tijera")
                return
            
            user_choice = choice.lower()
            if user_choice in ['rock']: user_choice = 'piedra'
            elif user_choice in ['paper']: user_choice = 'papel'
            elif user_choice in ['scissors']: user_choice = 'tijera'
            
            bot_choice = random.choice(['piedra', 'papel', 'tijera'])
            
            # determinar ganador
            if user_choice == bot_choice:
                result = "empate"
                color = nextcord.Color.orange()
                description = "¡empate!"
            elif (user_choice == 'piedra' and bot_choice == 'tijera') or \
                 (user_choice == 'papel' and bot_choice == 'piedra') or \
                 (user_choice == 'tijera' and bot_choice == 'papel'):
                result = "ganaste"
                color = nextcord.Color.green()
                description = "¡ganaste!"
            else:
                result = "perdiste"
                color = nextcord.Color.red()
                description = "perdiste..."
            
            embed = nextcord.Embed(
                title="🎮 piedra papel tijera",
                description=description,
                color=color
            )
            embed.add_field(name="tu elección", value=f"{choices[user_choice]} {user_choice}", inline=True)
            embed.add_field(name="mi elección", value=f"{choices[bot_choice]} {bot_choice}", inline=True)
            embed.add_field(name="resultado", value=result, inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error en rps: {e}")
            await ctx.send("❌ error en el juego.")
    
    @commands.command(name='guess', aliases=['adivina'])
    async def number_guessing_game(self, ctx, number: int = None):
        """
        juego de adivinanza de números
        uso: !guess [número] (inicia el juego si no hay número)
        """
        try:
            game_id = f"{ctx.guild.id}_{ctx.channel.id}_{ctx.author.id}_guess"
            
            if number is None:
                # iniciar nuevo juego
                secret_number = random.randint(1, 100)
                self.active_games[game_id] = {
                    "type": "guess",
                    "number": secret_number,
                    "attempts": 0,
                    "max_attempts": 7
                }
                
                embed = nextcord.Embed(
                    title="🎯 juego de adivinanza",
                    description="he pensado un número entre 1 y 100. ¡adivínalo!",
                    color=nextcord.Color.blue()
                )
                embed.add_field(name="intentos", value="7 intentos máximo", inline=True)
                embed.add_field(name="cómo jugar", value="usa `!guess [número]`", inline=True)
                
                await ctx.send(embed=embed)
                return
            
            # verificar si hay juego activo
            if game_id not in self.active_games:
                await ctx.send("❌ no hay juego activo. usa `!guess` para empezar.")
                return
            
            game = self.active_games[game_id]
            
            # verificar límites
            if number < 1 or number > 100:
                await ctx.send("❌ el número debe estar entre 1 y 100.")
                return
            
            game["attempts"] += 1
            secret = game["number"]
            
            if number == secret:
                # ¡ganó!
                embed = nextcord.Embed(
                    title="🎉 ¡correcto!",
                    description=f"¡adivinaste! el número era {secret}",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="intentos utilizados", value=f"{game['attempts']}/{game['max_attempts']}", inline=True)
                
                del self.active_games[game_id]
                
            elif game["attempts"] >= game["max_attempts"]:
                # se acabaron los intentos
                embed = nextcord.Embed(
                    title="💀 game over",
                    description=f"se acabaron los intentos. el número era {secret}",
                    color=nextcord.Color.red()
                )
                
                del self.active_games[game_id]
                
            else:
                # dar pista
                hint = "muy alto" if number > secret else "muy bajo"
                remaining = game["max_attempts"] - game["attempts"]
                
                embed = nextcord.Embed(
                    title="🎯 intenta de nuevo",
                    description=f"{number} es {hint}",
                    color=nextcord.Color.orange()
                )
                embed.add_field(name="intentos restantes", value=remaining, inline=True)
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("❌ debes proporcionar un número válido.")
        except Exception as e:
            logger.error(f"error en guess: {e}")
            await ctx.send("❌ error en el juego.")
    
    @commands.command(name='trivia', aliases=['preguntita'])
    async def trivia_game(self, ctx):
        """
        juego de preguntas de trivia
        uso: !trivia
        """
        try:
            questions = [
                {
                    "question": "¿cuál es la capital de japón?",
                    "options": ["a) osaka", "b) kioto", "c) tokio", "d) hiroshima"],
                    "answer": "c",
                    "explanation": "tokio es la capital de japón desde 1868."
                },
                {
                    "question": "¿qué elemento químico tiene el símbolo 'au'?",
                    "options": ["a) plata", "b) oro", "c) aluminio", "d) argón"],
                    "answer": "b",
                    "explanation": "au viene del latín 'aurum', que significa oro."
                },
                {
                    "question": "¿en qué año llegó el hombre a la luna?",
                    "options": ["a) 1967", "b) 1968", "c) 1969", "d) 1970"],
                    "answer": "c",
                    "explanation": "neil armstrong pisó la luna el 20 de julio de 1969."
                },
                {
                    "question": "¿cuál es el océano más grande del mundo?",
                    "options": ["a) atlántico", "b) índico", "c) ártico", "d) pacífico"],
                    "answer": "d",
                    "explanation": "el océano pacífico cubre aproximadamente el 46% de la superficie acuática."
                },
                {
                    "question": "¿quién escribió 'don quijote de la mancha'?",
                    "options": ["a) lope de vega", "b) miguel de cervantes", "c) calderón de la barca", "d) francisco de quevedo"],
                    "answer": "b",
                    "explanation": "miguel de cervantes escribió esta obra maestra en 1605."
                },
                {
                    "question": "¿cuántos lados tiene un hexágono?",
                    "options": ["a) 5", "b) 6", "c) 7", "d) 8"],
                    "answer": "b",
                    "explanation": "un hexágono es un polígono de seis lados."
                },
                {
                    "question": "¿cuál es el planeta más cercano al sol?",
                    "options": ["a) venus", "b) tierra", "c) mercurio", "d) marte"],
                    "answer": "c",
                    "explanation": "mercurio es el planeta más cercano al sol."
                },
                {
                    "question": "¿qué gas es más abundante en la atmósfera terrestre?",
                    "options": ["a) oxígeno", "b) nitrógeno", "c) dióxido de carbono", "d) argón"],
                    "answer": "b",
                    "explanation": "el nitrógeno constituye aproximadamente el 78% de la atmósfera."
                }
            ]
            
            question_data = random.choice(questions)
            
            embed = nextcord.Embed(
                title="🧠 pregunta de trivia",
                description=question_data["question"],
                color=nextcord.Color.purple()
            )
            
            options_text = "\n".join(question_data["options"])
            embed.add_field(name="opciones", value=options_text, inline=False)
            embed.set_footer(text="responde con la letra (a, b, c, o d) • tienes 30 segundos")
            
            question_msg = await ctx.send(embed=embed)
            
            # esperar respuesta
            def check(message):
                return (message.author == ctx.author and 
                       message.channel == ctx.channel and 
                       message.content.lower() in ['a', 'b', 'c', 'd'])
            
            try:
                response = await self.bot.wait_for("message", timeout=30.0, check=check)
                
                if response.content.lower() == question_data["answer"]:
                    result_embed = nextcord.Embed(
                        title="🎉 ¡correcto!",
                        description="respuesta correcta",
                        color=nextcord.Color.green()
                    )
                else:
                    result_embed = nextcord.Embed(
                        title="❌ incorrecto",
                        description=f"la respuesta correcta era: {question_data['answer']}",
                        color=nextcord.Color.red()
                    )
                
                result_embed.add_field(name="explicación", value=question_data["explanation"], inline=False)
                await ctx.send(embed=result_embed)
                
            except asyncio.TimeoutError:
                timeout_embed = nextcord.Embed(
                    title="⏰ tiempo agotado",
                    description=f"la respuesta correcta era: {question_data['answer']}",
                    color=nextcord.Color.orange()
                )
                timeout_embed.add_field(name="explicación", value=question_data["explanation"], inline=False)
                await ctx.send(embed=timeout_embed)
                
        except Exception as e:
            logger.error(f"error en trivia: {e}")
            await ctx.send("❌ error en el juego de trivia.")
    
    @commands.command(name='stopgame', aliases=['pararjuego'])
    async def stop_game(self, ctx):
        """
        detener juego activo
        uso: !stopgame
        """
        try:
            # buscar juego donde el usuario sea jugador
            user_games = []
            for game_id, game in self.active_games.items():
                if ctx.author in game.get("players", []) or str(ctx.author.id) in game_id:
                    user_games.append(game_id)
            
            if not user_games:
                await ctx.send("❌ no tienes ningún juego activo.")
                return
            
            # eliminar juegos del usuario
            for game_id in user_games:
                del self.active_games[game_id]
            
            embed = nextcord.Embed(
                title="🛑 juego detenido",
                description="tu juego ha sido detenido exitosamente.",
                color=nextcord.Color.orange()
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error en stopgame: {e}")
            await ctx.send("❌ error al detener el juego.")
    
    @commands.command(name='gameinfo', aliases=['infojuego'])
    async def game_info(self, ctx):
        """
        ver información de juegos activos
        uso: !gameinfo
        """
        try:
            if not self.active_games:
                await ctx.send("📭 no hay juegos activos en este momento.")
                return
            
            # contar juegos por tipo
            game_counts = {}
            user_games = []
            
            for game_id, game in self.active_games.items():
                game_type = game.get("type", "desconocido")
                game_counts[game_type] = game_counts.get(game_type, 0) + 1
                
                if ctx.author in game.get("players", []) or str(ctx.author.id) in game_id:
                    user_games.append(game_type)
            
            embed = nextcord.Embed(
                title="🎮 información de juegos",
                color=nextcord.Color.blue()
            )
            
            if game_counts:
                game_list = "\n".join([f"{tipo}: {count}" for tipo, count in game_counts.items()])
                embed.add_field(name="juegos activos totales", value=game_list, inline=False)
            
            if user_games:
                embed.add_field(name="tus juegos activos", value=", ".join(user_games), inline=False)
            else:
                embed.add_field(name="tus juegos", value="ninguno", inline=False)
            
            embed.add_field(
                name="comandos disponibles",
                value="• `!tictactoe @usuario` - tres en raya\n• `!rps [opción]` - piedra papel tijera\n• `!guess` - adivinanza de números\n• `!trivia` - preguntas de trivia\n• `!stopgame` - detener juego",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error en gameinfo: {e}")
            await ctx.send("❌ error al obtener información de juegos.")
    
    @commands.command(name='categories', aliases=['categorias'])
    async def joke_categories(self, ctx):
        """
        mostrar categorías de chistes disponibles
        uso: !categories
        """
        try:
            embed = nextcord.Embed(
                title="😂 categorías de chistes",
                description="elige una categoría para chistes específicos",
                color=nextcord.Color.yellow()
            )
            
            categories_info = {
                "programacion": "chistes sobre programación y tecnología",
                "generales": "chistes familiares y universales",
                "tecnologia": "chistes sobre dispositivos y apps",
                "adultos": "chistes para mayores (canal nsfw)",
                "inapropiados": "humor más atrevido (canal nsfw)"
            }
            
            for category, description in categories_info.items():
                embed.add_field(
                    name=f"📁 {category}",
                    value=description,
                    inline=False
                )
            
            embed.add_field(
                name="uso",
                value="`!joke [categoría]` o `/joke categoría:[opción]`",
                inline=False
            )
            
            embed.set_footer(text="las categorías 'adultos' e 'inapropiados' requieren canales nsfw")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error en categories: {e}")
            await ctx.send("❌ error al mostrar las categorías.")

def setup(bot):
    """función para cargar el cog"""
    return Entertainment(bot)
