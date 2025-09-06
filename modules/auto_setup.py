"""
Evento de auto-configuración cuando el bot se une a servidores
Configura automáticamente todos los sistemas necesarios
"""

import logging
import nextcord
from nextcord.ext import commands
import asyncio

logger = logging.getLogger(__name__)

class AutoSetupEvents(commands.Cog):
    """Sistema de auto-configuración para nuevos servidores"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: nextcord.Guild):
        """Configura automáticamente todos los sistemas cuando el bot se une a un servidor"""
        try:
            logger.info(f"Bot añadido al servidor: {guild.name} (ID: {guild.id})")
            
            # Esperar un poco para que el bot se establezca en el servidor
            await asyncio.sleep(2)
            
            # Lista de sistemas a configurar automáticamente
            systems_to_setup = [
                self.setup_server_manager,
                self.setup_ticket_system,
                self.setup_voicemaster,
                self.setup_persistent_messages,
                self.setup_welcome_system
            ]
            
            for setup_function in systems_to_setup:
                try:
                    await setup_function(guild)
                except Exception as e:
                    logger.error(f"Error configurando sistema en {guild.name}: {e}")
            
            # Enviar mensaje de bienvenida si es posible
            await self.send_welcome_message(guild)
            
        except Exception as e:
            logger.error(f"Error en auto-configuración para {guild.name}: {e}")
    
    async def setup_server_manager(self, guild: nextcord.Guild):
        """Configura el gestor de servidor"""
        try:
            server_manager = self.bot.get_cog('ServerManager')
            if server_manager:
                await server_manager.setup_server(guild)
                logger.info(f"ServerManager configurado en {guild.name}")
        except Exception as e:
            logger.error(f"Error configurando ServerManager en {guild.name}: {e}")
    
    async def setup_ticket_system(self, guild: nextcord.Guild):
        """Configura el sistema de tickets"""
        try:
            ticket_manager = self.bot.get_cog('TicketManager')
            if ticket_manager:
                await ticket_manager.setup_ticket_system(guild)
                logger.info(f"Sistema de tickets configurado en {guild.name}")
        except Exception as e:
            logger.error(f"Error configurando tickets en {guild.name}: {e}")
    
    async def setup_voicemaster(self, guild: nextcord.Guild):
        """Configura VoiceMaster"""
        try:
            voicemaster = self.bot.get_cog('VoiceMaster')
            if voicemaster:
                await voicemaster.setup_voicemaster(guild)
                logger.info(f"VoiceMaster configurado en {guild.name}")
        except Exception as e:
            logger.error(f"Error configurando VoiceMaster en {guild.name}: {e}")
    
    async def setup_persistent_messages(self, guild: nextcord.Guild):
        """Configura mensajes persistentes"""
        try:
            pm_manager = self.bot.get_cog('PersistentMessageManager')
            if pm_manager:
                # Verificar y crear paneles esenciales
                await pm_manager.verify_and_setup_message(guild, 'ticket_panel')
                await pm_manager.verify_and_setup_message(guild, 'voicemaster_panel')
                logger.info(f"Mensajes persistentes configurados en {guild.name}")
        except Exception as e:
            logger.error(f"Error configurando mensajes persistentes en {guild.name}: {e}")
    
    async def setup_welcome_system(self, guild: nextcord.Guild):
        """Configura el sistema de bienvenida"""
        try:
            welcome = self.bot.get_cog('Welcome')
            if welcome:
                # El sistema de bienvenida se configura automáticamente
                logger.info(f"Sistema de bienvenida configurado en {guild.name}")
        except Exception as e:
            logger.error(f"Error configurando sistema de bienvenida en {guild.name}: {e}")
    
    async def send_welcome_message(self, guild: nextcord.Guild):
        """Envía mensaje de bienvenida al servidor"""
        try:
            # Buscar canal apropiado para el mensaje
            target_channel = None
            
            # Intentar canal general
            for channel in guild.text_channels:
                if channel.name.lower() in ['general', 'chat', 'inicio', 'main']:
                    if channel.permissions_for(guild.me).send_messages:
                        target_channel = channel
                        break
            
            # Si no hay canal general, usar el primer canal donde pueda escribir
            if not target_channel:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        target_channel = channel
                        break
            
            if target_channel:
                embed = nextcord.Embed(
                    title="🤖 ¡Hola! Soy DABOT V2",
                    description="¡Gracias por añadirme a tu servidor!",
                    color=nextcord.Color.blue()
                )
                
                embed.add_field(
                    name="🚀 Configuración Automática",
                    value="He configurado automáticamente todos mis sistemas:\n"
                          "• 🎫 Sistema de tickets\n"
                          "• 🎤 VoiceMaster\n"
                          "• ⚙️ Configuración del servidor\n"
                          "• 📨 Mensajes persistentes",
                    inline=False
                )
                
                embed.add_field(
                    name="⚙️ Configuración Manual",
                    value="Usa `/serverconfig` para personalizar mis ajustes\n"
                          "Usa `/setup` para configurar sistemas específicos\n"
                          "Usa `/panels verify` para verificar paneles",
                    inline=False
                )
                
                embed.add_field(
                    name="📋 Comandos Principales",
                    value="• `/help` - Ver todos mis comandos\n"
                          "• `/ping` - Verificar mi estado\n"
                          "• `/serverconfig` - Configurar el servidor",
                    inline=False
                )
                
                embed.set_footer(text="DABOT V2 - Bot multipropósito | ¡Disfruta!")
                
                await target_channel.send(embed=embed)
                logger.info(f"Mensaje de bienvenida enviado en {guild.name}")
                
        except Exception as e:
            logger.error(f"Error enviando mensaje de bienvenida en {guild.name}: {e}")
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild: nextcord.Guild):
        """Limpia datos cuando el bot es removido de un servidor"""
        try:
            logger.info(f"Bot removido del servidor: {guild.name} (ID: {guild.id})")
            
            # Aquí podrías añadir lógica para limpiar datos del servidor
            # Por ejemplo, marcar como inactivo en las bases de datos
            
        except Exception as e:
            logger.error(f"Error en cleanup para {guild.name}: {e}")

def setup(bot):
    """Función para añadir el cog al bot"""
    return AutoSetupEvents(bot)
