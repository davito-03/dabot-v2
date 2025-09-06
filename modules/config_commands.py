import nextcord
from nextcord.ext import commands
from modules.config_manager import config, get_config, is_module_enabled
import json

class ConfigCommands(commands.Cog):
    """Comandos para gestionar la configuración del bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command(
        name="viewconfig",
        description="Ver la configuración actual del bot"
    )
    async def config_main(self, interaction: nextcord.Interaction):
        """Comando principal de configuración"""
        pass
    
    @config_main.subcommand(
        name="view",
        description="Ver configuración actual de un módulo"
    )
    async def config_view(
        self,
        interaction: nextcord.Interaction,
        module: str = nextcord.SlashOption(
            description="Módulo a consultar",
            choices=[
                "general", "permissions", "moderation", "levels", 
                "economy", "music", "welcome", "tickets", "logging",
                "filters", "voicemaster", "web"
            ]
        )
    ):
        """Ver configuración de un módulo específico"""
        
        try:
            # Verificar permisos básicos
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ Necesitas permisos de administrador para usar este comando.",
                    ephemeral=True
                )
                return
                
            module_config = config.get(module, {})
            
            if not module_config:
                await interaction.response.send_message(
                    f"❌ No se encontró configuración para el módulo `{module}`",
                    ephemeral=True
                )
                return
            
            # Crear embed con la configuración
            embed = nextcord.Embed(
                title=f"⚙️ Configuración: {module.title()}",
                color=0x3498db
            )
            
            # Mostrar configuración limitada para no exceder límites
            config_text = "```yaml\n"
            for key, value in list(module_config.items())[:10]:  # Limitar a 10 elementos
                if isinstance(value, dict):
                    config_text += f"{key}:\n  [diccionario con {len(value)} elementos]\n"
                elif isinstance(value, list):
                    config_text += f"{key}: [{len(value)} elementos]\n"
                else:
                    config_text += f"{key}: {value}\n"
            
            if len(module_config) > 10:
                config_text += f"... y {len(module_config) - 10} elementos más\n"
            
            config_text += "```"
            
            embed.description = config_text
            embed.add_field(
                name="💡 Ayuda",
                value="Edita `config.yaml` manualmente para cambios avanzados",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al obtener configuración: {e}",
                ephemeral=True
            )
    
    @config_main.subcommand(
        name="modules",
        description="Ver estado de todos los módulos"
    )
    async def config_modules(self, interaction: nextcord.Interaction):
        """Ver estado de todos los módulos disponibles"""
        
        try:
            # Verificar permisos básicos
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ Necesitas permisos de administrador para usar este comando.",
                    ephemeral=True
                )
                return
                
            modules = [
                "moderation", "levels", "economy", "music", "welcome",
                "tickets", "logging", "filters", "voicemaster", "web",
                "fun", "automod"
            ]
            
            embed = nextcord.Embed(
                title="📋 Estado de Módulos",
                color=0x3498db
            )
            
            enabled_modules = []
            disabled_modules = []
            
            for module in modules:
                if is_module_enabled(module):
                    enabled_modules.append(f"✅ {module}")
                else:
                    disabled_modules.append(f"❌ {module}")
            
            if enabled_modules:
                embed.add_field(
                    name="Habilitados",
                    value="\n".join(enabled_modules),
                    inline=True
                )
            
            if disabled_modules:
                embed.add_field(
                    name="Deshabilitados",
                    value="\n".join(disabled_modules),
                    inline=True
                )
            
            embed.add_field(
                name="💡 Gestión",
                value="Edita `config.yaml` para habilitar/deshabilitar módulos",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al obtener estado de módulos: {e}",
                ephemeral=True
            )
    
    @config_main.subcommand(
        name="reload",
        description="Recargar configuración desde el archivo"
    )
    async def config_reload(self, interaction: nextcord.Interaction):
        """Recargar configuración desde config.yaml"""
        
        try:
            # Verificar permisos básicos
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ Necesitas permisos de administrador para usar este comando.",
                    ephemeral=True
                )
                return
                
            config.reload_config()
            
            embed = nextcord.Embed(
                title="🔄 Configuración Recargada",
                description="La configuración se ha recargado desde `config.yaml`",
                color=0x27ae60
            )
            embed.add_field(
                name="📝 Idioma",
                value=get_config('general.language', 'es-ES'),
                inline=True
            )
            embed.add_field(
                name="🔧 Prefijo",
                value=get_config('general.prefix', '!'),
                inline=True
            )
            embed.add_field(
                name="💡 Nota",
                value="Algunos cambios pueden requerir reiniciar el bot",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error al recargar configuración: {e}",
                ephemeral=True
            )
    
    @config_main.subcommand(
        name="info",
        description="Información sobre el archivo de configuración"
    )
    async def config_info(self, interaction: nextcord.Interaction):
        """Información sobre el sistema de configuración"""
        
        embed = nextcord.Embed(
            title="📋 Sistema de Configuración DaBot v2",
            description="Gestión completa de configuración estilo La Cabra 2.0",
            color=0x3498db
        )
        
        embed.add_field(
            name="📁 Archivo Principal",
            value="`config.yaml` - Configuración principal del bot",
            inline=False
        )
        
        embed.add_field(
            name="� Scripts de Configuración",
            value="`configurar.bat` - Configuración rápida (Windows)\n`setup_config.sh` - Configuración rápida (Linux)",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Módulos Configurables",
            value="• Moderación y AutoMod\n• Sistema de Niveles\n• Economía y Trabajo\n• Música y Entretenimiento\n• Bienvenidas y Despedidas\n• Tickets y Soporte\n• Dashboard Web\n• Y mucho más...",
            inline=False
        )
        
        embed.add_field(
            name="� Comandos Útiles",
            value="`/config view <módulo>` - Ver configuración\n`/config modules` - Estado de módulos\n`/config reload` - Recargar configuración",
            inline=False
        )
        
        current_lang = get_config('general.language', 'es-ES')
        current_prefix = get_config('general.prefix', '!')
        
        embed.add_field(
            name="📊 Estado Actual",
            value=f"Idioma: `{current_lang}`\nPrefijo: `{current_prefix}`",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    """Función para cargar el cog"""
    return ConfigCommands(bot)
