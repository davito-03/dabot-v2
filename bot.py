"""
Bot multipropósito para Discord
Incluye moderación, entretenimiento, música, economía, anti-spam y logs
por davito
"""

import os
import sys
import logging
import asyncio
from datetime import datetime, time
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands, tasks

# Configurar codificación para Windows
if sys.platform == "win32":
    import codecs
    # Configurar stdout y stderr para UTF-8 pero sin interferir con logging
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        # Fallback para versiones más antiguas de Python
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

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
from modules.log_config import LogConfig
from modules.level_system import LevelSystem
from modules.channel_config import ChannelConfig
from modules.automod import AutoMod
from modules.levels import Levels
from modules.interactions import Interactions
from modules.welcome import Welcome
from modules.nsfw import NSFWCommands
from modules.bot_config import BotConfig
from modules.config_manager import config, get_config, is_module_enabled

# Cargar variables de entorno
load_dotenv()

# Configurar logging
log_level = get_config('advanced.debug.log_level', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
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
        
        # Obtener prefijo desde configuración
        prefix = get_config('general.prefix', '!')
        
        # Inicializar el bot con prefijo y configuraciones
        super().__init__(
            command_prefix=prefix,
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
        
        # Aplicar configuración de estado
        await self.change_presence(
            status=nextcord.Status.online,
            activity=nextcord.Activity(
                type=nextcord.ActivityType.watching,
                name="langostitas en el mar 🦞"
            )
        )
        
        # Sincronizar slash commands solo si es necesario (evitar rate limit)
        try:
            # Solo sincronizar en desarrollo o si es la primera vez
            sync_commands = get_config('advanced.debug.sync_commands', False)
            if sync_commands:
                logger.info("Sincronizando slash commands...")
                try:
                    synced = await self.sync_all_application_commands()
                    if synced:
                        logger.info(f"✅ {len(synced)} slash commands sincronizados")
                    else:
                        logger.info("✅ Slash commands sincronizados (sin count)")
                except Exception as sync_error:
                    logger.warning(f"⚠️ Error en sincronización específica: {sync_error}")
            else:
                logger.info("⏭️ Sincronización de slash commands omitida (configuración)")
        except Exception as e:
            logger.warning(f"⚠️ Error en configuración de sincronización (ignorado): {e}")
            logger.info("El bot continuará funcionando normalmente")
        
        # Configurar actividad del bot (comentado por nueva configuración arriba)
        # activity = nextcord.Activity(
        #     type=nextcord.ActivityType.listening,
        #     name="!help | /help"
        # )
        # await self.change_presence(activity=activity)
        
        # Iniciar tarea diaria si está configurada
        daily_channel = os.getenv('DAILY_CHANNEL_ID')
        if daily_channel and daily_channel.strip() and daily_channel.isdigit():
            self.daily_channel_id = int(daily_channel)
            self.daily_message.start()
            logger.info("Tarea diaria iniciada")
        else:
            logger.info("Canal diario no configurado, omitiendo tarea diaria")
    
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
    print("🚀 Iniciando DABOT V2...")
    
    # Verificar que el token esté configurado
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ Token de Discord no encontrado. Configura DISCORD_TOKEN en el archivo .env")
        logger.error("❌ Token de Discord no encontrado. Configura DISCORD_TOKEN en el archivo .env")
        return
    
    print(f"✅ Token encontrado")
    
    # Crear instancia del bot
    bot = DiscordBot()
    
    try:
        print("📦 Cargando módulos...")
        # Cargar módulos con funciones setup (con verificación de configuración)
        setup_modules = [
            # Módulos básicos (siempre activos)
            ("HelpCommands", "modules.help_commands", None),  # Contiene ping, help, info
            ("BotConfig", "modules.bot_config", None),  # Configuración del bot
            ("ServerManager", "modules.server_manager", None),  # Gestión automática de servidores
            ("AdvancedConfig", "modules.advanced_config", None),  # Configuración avanzada
            ("PersistentMessageManager", "modules.persistent_messages", None),  # Mensajes persistentes
            ("AutoSetupEvents", "modules.auto_setup", None),  # Auto-configuración de servidores
            ("TestPersistentSystems", "modules.test_systems", None),  # Comandos de prueba
            ("Moderation", "modules.moderation", "moderation"),
            ("Warnings", "modules.warnings", "moderation"),
            ("AntiSpam", "modules.anti_spam", "moderation.anti_spam"),
            ("LoggingSystem", "modules.logging_system", "logging"),
            ("Economy", "modules.economy", "economy"),
            ("ChannelConfig", "modules.channel_config", None),  # Siempre activo
            ("ConfigCommands", "modules.config_commands", None),  # Siempre activo
            
            # Módulos de entretenimiento
            ("Music", "modules.music", "music"),
            ("Entertainment", "modules.entertainment", "fun"),
            ("Interactions", "modules.interactions", "fun.interactions"),
            ("NSFWCommands", "modules.nsfw", "fun.nsfw"),
            
            # Módulos de utilidad
            ("VoiceMaster", "modules.voicemaster", "voicemaster"),
            ("TicketManager", "modules.ticket_system", "tickets"),
            ("Welcome", "modules.welcome", "welcome"),
            ("Levels", "modules.levels", "levels"),
            ("LevelSystem", "modules.level_system", "levels"),
            
            # Módulos de moderación avanzada
            ("AutoMod", "modules.automod", "moderation"),
            ("ModerationRoles", "modules.moderation_roles", "moderation"),
            ("Appeals", "modules.appeals", "moderation.appeals"),
            
            # Módulos de sistemas integrados nuevos
            ("AutoRules", "modules.auto_rules", None),  # Sistema de reglas automáticas
            ("AdvancedLevelSystem", "modules.advanced_levels", None),  # Sistema de niveles avanzado
            ("IntegratedModeration", "modules.integrated_moderation", None),  # Moderación integrada
            ("DestructiveCommands", "modules.destructive_commands", None),  # Comandos destructivos
            
            # Módulo de configuración completa de servidores
            ("ServerSetupWizard", "modules.complete_server_setup", None)  # Siempre disponible
        ]
        
        for name, module_path, config_key in setup_modules:
            try:
                # Verificar si el módulo está habilitado
                if config_key and not is_module_enabled(config_key):
                    logger.info(f"⏭️ {name} deshabilitado en configuración")
                    continue
                    
                logger.info(f"Cargando {name}...")
                
                # Importar módulo
                try:
                    module = __import__(module_path, fromlist=['setup'])
                    
                    # Verificar que tiene función setup
                    if not hasattr(module, 'setup'):
                        logger.error(f"❌ {name} no tiene función setup")
                        continue
                    
                    # Ejecutar setup
                    result = module.setup(bot)
                    
                    # Si setup devuelve una instancia, añadirla al bot
                    if result is not None:
                        bot.add_cog(result)
                    
                    logger.info(f"✅ {name} cargado exitosamente")
                        
                except ImportError as import_error:
                    logger.error(f"❌ Error importando {name}: {import_error}")
                    continue
                except Exception as setup_error:
                    logger.error(f"❌ Error en setup de {name}: {setup_error}")
                    continue
                
            except Exception as e:
                logger.error(f"❌ Error cargando {name}: {e}")
                continue
        
        logger.info("Proceso de carga de módulos completado")
        
        # Mostrar información del bot
        logger.info("=" * 50)
        logger.info("🚀 DABOT V2 INICIADO CORRECTAMENTE")
        logger.info("=" * 50)
        logger.info(f" Configuración cargada desde: config.yaml")
        logger.info(f"🌍 Idioma: {get_config('general.language', 'es-ES')}")
        logger.info(f"📝 Prefijo: {get_config('general.prefix', '!')}")
        logger.info(f"🦞 Estado: Viendo langostitas en el mar")
        logger.info("=" * 50)
        
        # Ejecutar el bot
        try:
            await bot.start(token)
        except Exception as start_error:
            logger.error(f"❌ Error al iniciar bot: {start_error}")
            raise
        
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
