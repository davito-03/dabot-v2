"""
Bot multipropósito para Discord
Incluye moderación, entretenimiento, música, economía, anti-spam y logs
por davito
"""

import os
import logging
import asyncio
from datetime import datetime, time
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands, tasks

# Importar módulos personalizados
from modules.moderation import Moderation
from modules.entertainment import Entertainment
from modules.music import Music
from modules.scheduled_tasks import ScheduledTasks
from modules.help_commands import HelpCommands
from modules.warnings import Warnings
from modules.anti_spam import AntiSpam
from modules.logging_system import LoggingSystem
from modules.economy import Economy
from modules.voicemaster import VoiceMaster
from modules.ticket_system import TicketSystem
from modules.web_api import WebAPI

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    """Clase principal del bot de Discord"""
    
    def __init__(self):
        # Configurar intents necesarios
        intents = nextcord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.voice_states = True
        intents.members = True
        
        # Inicializar el bot con prefijo y configuraciones
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        # Variable para canal de mensajes diarios
        self.daily_channel_id = None
        
    async def on_ready(self):
        """Evento que se ejecuta cuando el bot se conecta"""
        logger.info(f'{self.user} se ha conectado a Discord!')
        logger.info(f'Bot ID: {self.user.id}')
        logger.info(f'Servidores conectados: {len(self.guilds)}')
        
        # Configurar actividad del bot
        activity = nextcord.Activity(
            type=nextcord.ActivityType.listening,
            name="!help | /help"
        )
        await self.change_presence(activity=activity)
        
        # Iniciar tarea diaria si está configurada
        if os.getenv('DAILY_CHANNEL_ID'):
            self.daily_channel_id = int(os.getenv('DAILY_CHANNEL_ID'))
            self.daily_message.start()
            logger.info("Tarea diaria iniciada")
    
    async def on_command_error(self, ctx, error):
        """Manejo global de errores de comandos"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ No tienes permisos para ejecutar este comando.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Faltan argumentos requeridos. Usa `!help` para más información.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ El bot no tiene los permisos necesarios para ejecutar este comando.")
        else:
            logger.error(f"Error en comando: {error}")
            await ctx.send("❌ Ocurrió un error inesperado.")
    
    @tasks.loop(time=time(8, 0))  # 8:00 AM
    async def daily_message(self):
        """Envía un mensaje diario al canal configurado"""
        if self.daily_channel_id:
            try:
                channel = self.get_channel(self.daily_channel_id)
                if channel:
                    embed = nextcord.Embed(
                        title="🌅 ¡Buenos días!",
                        description="¡Que tengas un excelente día!",
                        color=nextcord.Color.gold(),
                        timestamp=datetime.now()
                    )
                    await channel.send(embed=embed)
                    logger.info("Mensaje diario enviado")
            except Exception as e:
                logger.error(f"Error enviando mensaje diario: {e}")
    
    @daily_message.before_loop
    async def before_daily_message(self):
        """Espera a que el bot esté listo antes de iniciar la tarea diaria"""
        await self.wait_until_ready()

async def main():
    """Función principal para ejecutar el bot"""
    # Verificar que el token esté configurado
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ Token de Discord no encontrado. Configura DISCORD_TOKEN en el archivo .env")
        return
    
    # Crear instancia del bot
    bot = DiscordBot()
    
    try:
        # Agregar módulos al bot
        cogs = [
            Moderation(bot),
            Entertainment(bot),
            Music(bot),
            ScheduledTasks(bot),
            HelpCommands(bot),
            Warnings(bot),
            AntiSpam(bot),
            LoggingSystem(bot),
            Economy(bot),
            VoiceMaster(bot),
            TicketSystem(bot),
            WebAPI(bot)
        ]
        
        for cog in cogs:
            if cog is not None:
                await bot.add_cog(cog)
                logger.info(f"Cog {cog.__class__.__name__} cargado exitosamente")
            else:
                logger.warning(f"Cog es None, saltando...")
        
        logger.info("Todos los módulos cargados exitosamente")
        
        # Ejecutar el bot
        await bot.start(token)
        
    except nextcord.LoginFailure:
        logger.error("❌ Token de Discord inválido")
    except Exception as e:
        logger.error(f"❌ Error al iniciar el bot: {e}")
    finally:
        await bot.close()

if __name__ == '__main__':
    # Ejecutar el bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"Error crítico: {e}")
