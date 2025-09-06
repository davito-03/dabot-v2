"""
Módulo de configuración del bot desde Discord
Permite configurar todo el bot usando comandos slash
"""

import logging
import nextcord
from nextcord.ext import commands
from modules.config_manager import config, get_config, set_config, save_config
import json

logger = logging.getLogger(__name__)

class BotConfig(commands.Cog):
    """Comandos de configuración del bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command(name="botconfig", description="Configuración del bot")
    async def config_main(self, interaction: nextcord.Interaction):
        """Comando principal de configuración"""
        pass  # Este es un grupo de comandos
    
    @config_main.subcommand(name="ver", description="Ver configuración actual")
    @commands.has_permissions(administrator=True)
    async def config_view(self, interaction: nextcord.Interaction, 
                         categoria: str = nextcord.SlashOption(
                             description="Categoría a ver",
                             choices=["general", "moderation", "music", "fun", "levels", "tickets", "all"]
                         )):
        """Ver configuración actual"""
        
        embed = nextcord.Embed(
            title="⚙️ Configuración del Bot",
            color=nextcord.Color.blue(),
            timestamp=interaction.created_at
        )
        
        if categoria == "general" or categoria == "all":
            general_config = {
                "Prefijo": get_config('general.prefix', '!'),
                "Idioma": get_config('general.language', 'es-ES'),
                "Debug": get_config('advanced.debug.enabled', False)
            }
            
            embed.add_field(
                name="🔧 General",
                value="\n".join([f"**{k}:** {v}" for k, v in general_config.items()]),
                inline=False
            )
        
        if categoria == "moderation" or categoria == "all":
            mod_config = {
                "Anti-spam": get_config('moderation.anti_spam.enabled', True),
                "Auto-mod": get_config('moderation.automod.enabled', True),
                "Logs": get_config('logging.enabled', True)
            }
            
            embed.add_field(
                name="🛡️ Moderación",
                value="\n".join([f"**{k}:** {v}" for k, v in mod_config.items()]),
                inline=False
            )
        
        if categoria == "music" or categoria == "all":
            music_config = {
                "Habilitado": get_config('music.enabled', True),
                "Volumen por defecto": get_config('music.default_volume', 50),
                "Auto-desconectar": get_config('music.auto_disconnect', True)
            }
            
            embed.add_field(
                name="🎵 Música",
                value="\n".join([f"**{k}:** {v}" for k, v in music_config.items()]),
                inline=False
            )
        
        if categoria == "fun" or categoria == "all":
            fun_config = {
                "Entretenimiento": get_config('fun.enabled', True),
                "Interacciones": get_config('fun.interactions.enabled', True),
                "NSFW": get_config('fun.nsfw.enabled', True)
            }
            
            embed.add_field(
                name="🎮 Diversión",
                value="\n".join([f"**{k}:** {v}" for k, v in fun_config.items()]),
                inline=False
            )
        
        embed.set_footer(text="Usa /botconfig cambiar para modificar valores")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @config_main.subcommand(name="cambiar", description="Cambiar configuración")
    @commands.has_permissions(administrator=True)
    async def config_change(self, interaction: nextcord.Interaction,
                           setting: str = nextcord.SlashOption(
                               description="Configuración a cambiar",
                               choices=[
                                   "general.prefix",
                                   "general.language", 
                                   "moderation.anti_spam.enabled",
                                   "music.enabled",
                                   "music.default_volume",
                                   "fun.enabled",
                                   "fun.nsfw.enabled",
                                   "levels.enabled",
                                   "tickets.enabled"
                               ]
                           ),
                           valor: str = nextcord.SlashOption(description="Nuevo valor")):
        """Cambiar un valor de configuración"""
        
        try:
            # Convertir valor según el tipo esperado
            if setting.endswith('.enabled'):
                valor = valor.lower() in ['true', '1', 'si', 'yes', 'on']
            elif setting == 'music.default_volume':
                valor = int(valor)
                if not 0 <= valor <= 100:
                    raise ValueError("El volumen debe estar entre 0 y 100")
            
            # Establecer nueva configuración
            set_config(setting, valor)
            save_config()
            
            embed = nextcord.Embed(
                title="✅ Configuración Actualizada",
                description=f"**{setting}** cambiado a: `{valor}`",
                color=nextcord.Color.green(),
                timestamp=interaction.created_at
            )
            
            # Aplicar cambios inmediatos si es necesario
            if setting == "general.prefix":
                self.bot.command_prefix = valor
                embed.add_field(
                    name="📝 Nota",
                    value="El nuevo prefijo se aplicará inmediatamente",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError as e:
            await interaction.response.send_message(
                f"❌ Valor inválido: {str(e)}",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error cambiando configuración: {e}")
            await interaction.response.send_message(
                "❌ Error al cambiar la configuración",
                ephemeral=True
            )
    
    @config_main.subcommand(name="modulos", description="Ver y configurar módulos")
    @commands.has_permissions(administrator=True)
    async def config_modules(self, interaction: nextcord.Interaction):
        """Ver estado de los módulos"""
        
        modules_status = {
            "🛡️ Moderación": get_config('moderation.enabled', True),
            "🎵 Música": get_config('music.enabled', True),
            "🎮 Diversión": get_config('fun.enabled', True),
            "🔞 NSFW": get_config('fun.nsfw.enabled', True),
            "📊 Niveles": get_config('levels.enabled', True),
            "🎫 Tickets": get_config('tickets.enabled', True),
            "👋 Bienvenidas": get_config('welcome.enabled', True),
            "🔊 VoiceMaster": get_config('voicemaster.enabled', True)
        }
        
        embed = nextcord.Embed(
            title="🔧 Estado de Módulos",
            color=nextcord.Color.blue(),
            timestamp=interaction.created_at
        )
        
        enabled_modules = []
        disabled_modules = []
        
        for module, status in modules_status.items():
            if status:
                enabled_modules.append(module)
            else:
                disabled_modules.append(module)
        
        if enabled_modules:
            embed.add_field(
                name="✅ Módulos Activos",
                value="\n".join(enabled_modules),
                inline=True
            )
        
        if disabled_modules:
            embed.add_field(
                name="❌ Módulos Desactivados",
                value="\n".join(disabled_modules),
                inline=True
            )
        
        embed.set_footer(text="Usa /botconfig cambiar para activar/desactivar módulos")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @config_main.subcommand(name="reset", description="Resetear configuración")
    @commands.has_permissions(administrator=True)
    async def config_reset(self, interaction: nextcord.Interaction,
                          confirmacion: str = nextcord.SlashOption(
                              description="Escribe 'CONFIRMAR' para resetear toda la configuración"
                          )):
        """Resetear toda la configuración a valores por defecto"""
        
        if confirmacion != "CONFIRMAR":
            await interaction.response.send_message(
                "❌ Para resetear la configuración, escribe exactamente `CONFIRMAR`",
                ephemeral=True
            )
            return
        
        try:
            # Configuración por defecto
            default_config = {
                "general": {
                    "prefix": "!",
                    "language": "es-ES"
                },
                "moderation": {
                    "enabled": True,
                    "anti_spam": {"enabled": True},
                    "automod": {"enabled": True}
                },
                "music": {
                    "enabled": True,
                    "default_volume": 50,
                    "auto_disconnect": True
                },
                "fun": {
                    "enabled": True,
                    "interactions": {"enabled": True},
                    "nsfw": {"enabled": True}
                },
                "levels": {"enabled": True},
                "tickets": {"enabled": True},
                "welcome": {"enabled": True},
                "voicemaster": {"enabled": True},
                "logging": {"enabled": True}
            }
            
            # Actualizar configuración global
            config.clear()
            config.update(default_config)
            save_config()
            
            embed = nextcord.Embed(
                title="🔄 Configuración Reseteada",
                description="Toda la configuración ha sido reseteada a valores por defecto",
                color=nextcord.Color.orange(),
                timestamp=interaction.created_at
            )
            
            embed.add_field(
                name="⚠️ Advertencia",
                value="Puede ser necesario reiniciar el bot para que algunos cambios tengan efecto",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error reseteando configuración: {e}")
            await interaction.response.send_message(
                "❌ Error al resetear la configuración",
                ephemeral=True
            )
    
    @config_main.subcommand(name="roles", description="Configurar roles de moderación")
    @commands.has_permissions(administrator=True)
    async def config_roles(self, interaction: nextcord.Interaction,
                          comando: str = nextcord.SlashOption(
                              description="Comando a configurar",
                              choices=["warn", "ban", "kick", "mute", "tickets"]
                          ),
                          rol: nextcord.Role = nextcord.SlashOption(
                              description="Rol requerido para usar el comando"
                          )):
        """Configurar roles necesarios para comandos"""
        
        try:
            # Guardar configuración de rol
            role_config_key = f"roles.{comando}"
            set_config(role_config_key, rol.id)
            save_config()
            
            embed = nextcord.Embed(
                title="✅ Rol Configurado",
                description=f"El comando `{comando}` ahora requiere el rol {rol.mention}",
                color=nextcord.Color.green(),
                timestamp=interaction.created_at
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error configurando rol: {e}")
            await interaction.response.send_message(
                "❌ Error al configurar el rol",
                ephemeral=True
            )

def setup(bot):
    """Función para cargar el cog"""
    return BotConfig(bot)
