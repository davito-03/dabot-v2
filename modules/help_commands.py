"""
Módulo de Comandos de Ayuda para el bot de Discord
Proporciona información sobre todos los comandos disponibles
"""

import logging
import nextcord
from nextcord.ext import commands

logger = logging.getLogger(__name__)

class HelpCommands(commands.Cog):
    """Clase para comandos de ayuda"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='help', aliases=['ayuda'])
    async def help_command(self, ctx, category: str = None):
        """
        Muestra información de ayuda sobre los comandos
        Uso: !help [categoría]
        """
        try:
            if category is None:
                # Mostrar ayuda general
                embed = nextcord.Embed(
                    title="🤖 Ayuda del Bot - DaBot v2",
                    description="Bot multipropósito para Discord con moderación, entretenimiento, música y más.",
                    color=nextcord.Color.blue()
                )
                
                embed.add_field(
                    name="📋 Categorías disponibles:",
                    value=(
                        "`!help moderacion` - Comandos de moderación\n"
                        "`!help entretenimiento` - Comandos de entretenimiento\n"
                        "`!help musica` - Comandos de música\n"
                        "`!help tareas` - Comandos de tareas automáticas\n"
                        "`!help general` - Comandos generales"
                    ),
                    inline=False
                )
                
                embed.add_field(
                    name="ℹ️ Información:",
                    value=(
                        "• Usa tanto comandos con prefijo `!` como slash commands `/`\n"
                        "• Los comandos de moderación requieren permisos de administrador\n"
                        "• Para música, necesitas estar en un canal de voz"
                    ),
                    inline=False
                )
                
                embed.set_footer(text="Usa !help [categoría] para ver comandos específicos")
                
            elif category.lower() in ['moderacion', 'mod']:
                embed = nextcord.Embed(
                    title="🛡️ Comandos de Moderación",
                    description="Comandos para administrar el servidor (requieren permisos de administrador)",
                    color=nextcord.Color.red()
                )
                
                embed.add_field(
                    name="!ban @usuario [razón]",
                    value="Banea a un usuario del servidor",
                    inline=False
                )
                
                embed.add_field(
                    name="!kick @usuario [razón]",
                    value="Expulsa a un usuario del servidor",
                    inline=False
                )
                
                embed.add_field(
                    name="!clear [cantidad]",
                    value="Elimina mensajes (máximo 100, por defecto 5)",
                    inline=False
                )
                
                embed.add_field(
                    name="📝 Notas:",
                    value=(
                        "• Todos los comandos requieren confirmación\n"
                        "• También disponibles como slash commands (/ban, /kick, /clear)\n"
                        "• Se envía notificación por DM al usuario afectado"
                    ),
                    inline=False
                )
                
            elif category.lower() in ['entretenimiento', 'fun']:
                embed = nextcord.Embed(
                    title="🎮 Comandos de Entretenimiento",
                    description="Comandos divertidos para amenizar el servidor",
                    color=nextcord.Color.yellow()
                )
                
                embed.add_field(
                    name="!joke o !chiste",
                    value="Obtén un chiste aleatorio",
                    inline=False
                )
                
                embed.add_field(
                    name="!8ball [pregunta]",
                    value="Haz una pregunta a la bola mágica 8",
                    inline=False
                )
                
                embed.add_field(
                    name="!flip o !moneda",
                    value="Lanza una moneda virtual",
                    inline=False
                )
                
                embed.add_field(
                    name="!dice [caras]",
                    value="Lanza un dado (por defecto 6 caras, máximo 100)",
                    inline=False
                )
                
                embed.add_field(
                    name="📝 Ejemplos:",
                    value=(
                        "• `!8ball ¿Lloverá mañana?`\n"
                        "• `!dice 20` (dado de 20 caras)\n"
                        "• Todos también disponibles como slash commands"
                    ),
                    inline=False
                )
                
            elif category.lower() in ['musica', 'music']:
                embed = nextcord.Embed(
                    title="🎵 Comandos de Música",
                    description="Comandos para reproducir música desde YouTube",
                    color=nextcord.Color.green()
                )
                
                embed.add_field(
                    name="!play [URL o búsqueda]",
                    value="Reproduce música desde YouTube",
                    inline=False
                )
                
                embed.add_field(
                    name="!skip o !s",
                    value="Salta la canción actual",
                    inline=False
                )
                
                embed.add_field(
                    name="!stop",
                    value="Detiene la música y limpia la cola",
                    inline=False
                )
                
                embed.add_field(
                    name="!queue o !q",
                    value="Muestra la cola de reproducción",
                    inline=False
                )
                
                embed.add_field(
                    name="!volume [0-100]",
                    value="Ajusta el volumen de reproducción",
                    inline=False
                )
                
                embed.add_field(
                    name="!disconnect",
                    value="Desconecta el bot del canal de voz",
                    inline=False
                )
                
                embed.add_field(
                    name="📝 Requisitos:",
                    value=(
                        "• Debes estar en un canal de voz\n"
                        "• El bot necesita permisos para conectarse y hablar\n"
                        "• Soporta URLs de YouTube y búsquedas por texto"
                    ),
                    inline=False
                )
                
            elif category.lower() in ['tareas', 'tasks', 'automaticas']:
                embed = nextcord.Embed(
                    title="⏰ Comandos de Tareas Automáticas",
                    description="Comandos para configurar mensajes automáticos",
                    color=nextcord.Color.purple()
                )
                
                embed.add_field(
                    name="!setdaily [#canal]",
                    value="Configura mensajes diarios automáticos (8:00 AM)",
                    inline=False
                )
                
                embed.add_field(
                    name="!removedaily",
                    value="Desactiva los mensajes diarios",
                    inline=False
                )
                
                embed.add_field(
                    name="!dailystatus",
                    value="Muestra el estado de los mensajes diarios",
                    inline=False
                )
                
                embed.add_field(
                    name="!testdaily",
                    value="Envía un mensaje diario de prueba",
                    inline=False
                )
                
                embed.add_field(
                    name="📝 Notas:",
                    value=(
                        "• Requiere permisos de administrador\n"
                        "• Los mensajes se envían a las 8:00 AM hora del servidor\n"
                        "• Si no especificas canal, usa el canal actual"
                    ),
                    inline=False
                )
                
            elif category.lower() in ['general']:
                embed = nextcord.Embed(
                    title="🔧 Comandos Generales",
                    description="Comandos básicos del bot",
                    color=nextcord.Color.gray()
                )
                
                embed.add_field(
                    name="!help [categoría]",
                    value="Muestra esta ayuda",
                    inline=False
                )
                
                embed.add_field(
                    name="!ping",
                    value="Muestra la latencia del bot",
                    inline=False
                )
                
                embed.add_field(
                    name="!info",
                    value="Información del bot y del servidor",
                    inline=False
                )
                
            else:
                embed = nextcord.Embed(
                    title="❌ Categoría no encontrada",
                    description=f"La categoría `{category}` no existe.",
                    color=nextcord.Color.red()
                )
                
                embed.add_field(
                    name="Categorías disponibles:",
                    value=(
                        "`moderacion`, `entretenimiento`, `musica`, `tareas`, `general`"
                    ),
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en comando help: {e}")
            await ctx.send("❌ Error al mostrar la ayuda.")
    
    @nextcord.slash_command(name="help", description="Muestra ayuda sobre los comandos del bot")
    async def slash_help(
        self,
        interaction: nextcord.Interaction,
        category: str = nextcord.SlashOption(
            description="Categoría de comandos",
            choices=["moderacion", "entretenimiento", "musica", "tareas", "general"],
            required=False
        )
    ):
        """Comando slash para ayuda"""
        ctx = await commands.Context.from_interaction(interaction)
        await self.help_command(ctx, category)
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """
        Muestra la latencia del bot
        Uso: !ping
        """
        try:
            latency = round(self.bot.latency * 1000)
            
            embed = nextcord.Embed(
                title="🏓 Pong!",
                description=f"Latencia: **{latency}ms**",
                color=nextcord.Color.green() if latency < 100 else nextcord.Color.orange() if latency < 300 else nextcord.Color.red()
            )
            
            # Agregar indicador de estado
            if latency < 100:
                embed.add_field(name="Estado", value="🟢 Excelente", inline=True)
            elif latency < 300:
                embed.add_field(name="Estado", value="🟡 Bueno", inline=True)
            else:
                embed.add_field(name="Estado", value="🔴 Lento", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en comando ping: {e}")
            await ctx.send("❌ Error al verificar la latencia.")
    
    @nextcord.slash_command(name="ping", description="Muestra la latencia del bot")
    async def slash_ping(self, interaction: nextcord.Interaction):
        """Comando slash para ping"""
        latency = round(self.bot.latency * 1000)
        embed = nextcord.Embed(
            title="🏓 Pong!",
            description=f"Latencia: {latency}ms",
            color=nextcord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    
    @commands.command(name='info')
    async def server_info(self, ctx):
        """
        Muestra información del bot y del servidor
        Uso: !info
        """
        try:
            embed = nextcord.Embed(
                title="🤖 Información del Bot",
                description="DaBot v2 - Bot multipropósito para Discord",
                color=nextcord.Color.blue()
            )
            
            # Información del bot
            embed.add_field(
                name="📊 Estadísticas del Bot:",
                value=(
                    f"**Servidores:** {len(self.bot.guilds)}\n"
                    f"**Usuarios:** {len(self.bot.users)}\n"
                    f"**Comandos cargados:** {len(self.bot.commands)}\n"
                    f"**Latencia:** {round(self.bot.latency * 1000)}ms"
                ),
                inline=True
            )
            
            # Información del servidor actual
            embed.add_field(
                name="🏠 Información del Servidor:",
                value=(
                    f"**Nombre:** {ctx.guild.name}\n"
                    f"**ID:** {ctx.guild.id}\n"
                    f"**Miembros:** {ctx.guild.member_count}\n"
                    f"**Creado:** {ctx.guild.created_at.strftime('%d/%m/%Y')}"
                ),
                inline=True
            )
            
            # Información técnica
            embed.add_field(
                name="⚙️ Información Técnica:",
                value=(
                    f"**Lenguaje:** Python 3.13\n"
                    f"**Librería:** nextcord 2.6.0\n"
                    f"**Host:** Render.com\n"
                    f"**Prefijo:** !"
                ),
                inline=True
            )
            
            # Funcionalidades
            embed.add_field(
                name="🎯 Funcionalidades:",
                value=(
                    "🛡️ Moderación\n"
                    "🎮 Entretenimiento\n"
                    "🎵 Música\n"
                    "⏰ Tareas automáticas"
                ),
                inline=True
            )
            
            embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            embed.set_footer(text="Desarrollado con ❤️ usando nextcord")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en comando info: {e}")
            await ctx.send("❌ Error al mostrar la información.")
    
    @nextcord.slash_command(name="info", description="Muestra información del bot y del servidor")
    async def slash_info(self, interaction: nextcord.Interaction):
        """Comando slash para información"""
        try:
            embed = nextcord.Embed(
                title="🤖 Información del Bot",
                description="DaBot v2 - Bot multipropósito para Discord",
                color=nextcord.Color.blue()
            )
            
            # Información del bot
            embed.add_field(
                name="📊 Estadísticas del Bot:",
                value=(
                    f"**Servidores:** {len(self.bot.guilds)}\n"
                    f"**Usuarios:** {len(self.bot.users)}\n"
                    f"**Comandos cargados:** {len(self.bot.commands)}\n"
                    f"**Latencia:** {round(self.bot.latency * 1000)}ms"
                ),
                inline=True
            )
            
            # Información del servidor actual
            embed.add_field(
                name="🏠 Información del Servidor:",
                value=(
                    f"**Nombre:** {interaction.guild.name}\n"
                    f"**ID:** {interaction.guild.id}\n"
                    f"**Miembros:** {interaction.guild.member_count}\n"
                    f"**Creado:** {interaction.guild.created_at.strftime('%d/%m/%Y')}"
                ),
                inline=True
            )
            
            # Información técnica
            embed.add_field(
                name="⚙️ Información Técnica:",
                value=(
                    f"**Lenguaje:** Python 3.13\n"
                    f"**Librería:** nextcord 2.6.0\n"
                    f"**Host:** Render.com\n"
                    f"**Prefijo:** !"
                ),
                inline=True
            )
            
            # Funcionalidades
            embed.add_field(
                name="🎯 Funcionalidades:",
                value=(
                    "🛡️ Moderación\n"
                    "🎮 Entretenimiento\n"
                    "🎵 Música\n"
                    "⏰ Tareas automáticas"
                ),
                inline=True
            )
            
            embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
            embed.set_footer(text="Desarrollado con ❤️ usando nextcord")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en comando info: {e}")
            await interaction.response.send_message("❌ Error al mostrar la información.", ephemeral=True)

def setup(bot):
    """Función setup para cargar el cog"""
    return HelpCommands(bot)
