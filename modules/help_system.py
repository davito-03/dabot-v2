import nextcord
from nextcord.ext import commands
import logging

logger = logging.getLogger(__name__)

class HelpSystem(commands.Cog):
    """sistema de ayuda completo"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command(
        name="help",
        description="Muestra todos los comandos disponibles de Dabot"
    )
    async def help_command(
        self,
        interaction: nextcord.Interaction,
        categoria: str = nextcord.SlashOption(
            description="Categoría específica de comandos",
            required=False,
            choices=[
                "general", "moderacion", "entretenimiento", "economia",
                "musica", "tickets", "voicemaster", "servidor", "emojis", "admin"
            ]
        )
    ):
        """comando de ayuda completo"""
        
        if categoria:
            await self._show_category_help(interaction, categoria)
        else:
            await self._show_main_help(interaction)
    
    async def _show_main_help(self, interaction: nextcord.Interaction):
        """mostrar ayuda principal"""
        
        embed = nextcord.Embed(
            title="🤖 Dabot v2 - Sistema de Ayuda",
            description="¡Hola! Soy **Dabot**, tu asistente completo para Discord. Aquí están todas mis funciones:",
            color=nextcord.Color.blue()
        )
        
        # Categorías principales
        categories = {
            "🎯 **General**": "`/help categoria:general` - Comandos básicos y utilidades",
            "🛡️ **Moderación**": "`/help categoria:moderacion` - Herramientas de moderación",
            "🎮 **Entretenimiento**": "`/help categoria:entretenimiento` - Memes, juegos y diversión",
            "💰 **Economía**": "`/help categoria:economia` - Sistema económico completo",
            "🎵 **Música**": "`/help categoria:musica` - Reproductor de música avanzado",
            "🎫 **Tickets**": "`/help categoria:tickets` - Sistema de soporte",
            "🎙️ **VoiceMaster**": "`/help categoria:voicemaster` - Canales de voz temporales",
            "🏗️ **Servidor**": "`/help categoria:servidor` - Plantillas y configuración",
            "😀 **Emojis & Stickers**": "`/help categoria:emojis` - Personalización visual",
            "⚙️ **Administración**": "`/help categoria:admin` - Comandos administrativos"
        }
        
        description = embed.description + "\n\n"
        for category, desc in categories.items():
            description += f"{category}\n{desc}\n\n"
        
        embed.description = description
        
        embed.add_field(
            name="🔗 Enlaces Útiles",
            value="• [Servidor de Soporte](https://discord.gg/tu-servidor)\n• [Invitar Bot](https://discord.com/oauth2/authorize?client_id=TU_BOT_ID&permissions=8&scope=bot%20applications.commands)\n• [GitHub](https://github.com/davito-03/dabot-v2)",
            inline=False
        )
        
        embed.add_field(
            name="📊 Estadísticas",
            value=f"• Servidores: {len(self.bot.guilds)}\n• Usuarios: {len(self.bot.users)}\n• Comandos: 50+",
            inline=True
        )
        
        embed.add_field(
            name="💡 Tip",
            value="Usa `/help categoria:nombre` para ver comandos específicos de cada categoría",
            inline=True
        )
        
        embed.set_footer(text="Dabot v2 | Bot desarrollado con ❤️ para la comunidad")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)
    
    async def _show_category_help(self, interaction: nextcord.Interaction, categoria: str):
        """mostrar ayuda de categoría específica"""
        
        embeds = {
            "general": self._get_general_help(),
            "moderacion": self._get_moderation_help(),
            "entretenimiento": self._get_entertainment_help(),
            "economia": self._get_economy_help(),
            "musica": self._get_music_help(),
            "tickets": self._get_tickets_help(),
            "voicemaster": self._get_voicemaster_help(),
            "servidor": self._get_server_help(),
            "emojis": self._get_emojis_help(),
            "admin": self._get_admin_help()
        }
        
        embed = embeds.get(categoria)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Categoría no encontrada.", ephemeral=True)
    
    def _get_general_help(self):
        embed = nextcord.Embed(
            title="🎯 Comandos Generales",
            description="Comandos básicos y utilidades generales",
            color=nextcord.Color.green()
        )
        
        commands_list = [
            "`/help` - Muestra este menú de ayuda",
            "`/ping` - Verifica la latencia del bot",
            "`/userinfo [usuario]` - Información de un usuario",
            "`/serverinfo` - Información del servidor",
            "`/avatar [usuario]` - Avatar de un usuario",
            "`/nivel [usuario]` - Ver nivel y experiencia"
        ]
        
        embed.add_field(
            name="📋 Comandos Disponibles",
            value="\n".join(commands_list),
            inline=False
        )
        
        return embed
    
    def _get_moderation_help(self):
        embed = nextcord.Embed(
            title="🛡️ Comandos de Moderación",
            description="Herramientas para mantener el orden en tu servidor",
            color=nextcord.Color.red()
        )
        
        commands_list = [
            "`/ban [usuario] [razón]` - Banear usuario",
            "`/kick [usuario] [razón]` - Expulsar usuario",
            "`/timeout [usuario] [tiempo] [razón]` - Silenciar temporalmente",
            "`/warn [usuario] [razón]` - Advertir usuario",
            "`/clear [cantidad]` - Limpiar mensajes",
            "`/slowmode [segundos]` - Modo lento del canal"
        ]
        
        embed.add_field(
            name="⚖️ Comandos Disponibles",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Permisos Requeridos",
            value="La mayoría requieren permisos de **Gestionar Servidor** o **Moderar Miembros**",
            inline=False
        )
        
        return embed
    
    def _get_entertainment_help(self):
        embed = nextcord.Embed(
            title="🎮 Comandos de Entretenimiento",
            description="Diversión, memes y juegos para tu servidor",
            color=nextcord.Color.purple()
        )
        
        commands_list = [
            "`/meme random` - Meme aleatorio",
            "`/meme chiste` - Chiste del día",
            "`/juegos verdad_o_reto` - Juego de verdad o reto",
            "`/juegos bola8 [pregunta]` - Bola mágica 8",
            "`/amor [usuario1] [usuario2]` - Calculadora de amor",
            "`/publicacion` - Crear publicación temática",
            "`/confesion enviar` - Enviar confesión anónima"
        ]
        
        embed.add_field(
            name="🎲 Comandos Disponibles",
            value="\n".join(commands_list),
            inline=False
        )
        
        return embed
    
    def _get_economy_help(self):
        embed = nextcord.Embed(
            title="💰 Sistema de Economía",
            description="Sistema económico completo estilo Mee6",
            color=nextcord.Color.gold()
        )
        
        commands_list = [
            "`/economia balance [usuario]` - Ver monedas",
            "`/economia trabajar` - Trabajar para ganar dinero",
            "`/economia apostar [cantidad]` - Apostar en el casino",
            "`/economia robar [usuario]` - Intentar robar",
            "`/economia invertir [cantidad] [tiempo]` - Invertir dinero",
            "`/economia crypto` - Ver mercado de criptomonedas",
            "`/tienda ver` - Ver tienda del servidor",
            "`/tienda comprar [item]` - Comprar artículo"
        ]
        
        embed.add_field(
            name="💎 Comandos Disponibles",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.add_field(
            name="🏆 Características",
            value="• 10 trabajos diferentes\n• Casino con múltiples juegos\n• Sistema de inversiones\n• Criptomonedas simuladas\n• Tienda personalizable",
            inline=False
        )
        
        return embed
    
    def _get_music_help(self):
        embed = nextcord.Embed(
            title="🎵 Comandos de Música",
            description="Reproductor de música avanzado con múltiples fuentes",
            color=nextcord.Color.orange()
        )
        
        commands_list = [
            "`/play [canción/url]` - Reproducir música",
            "`/pause` - Pausar reproducción",
            "`/resume` - Reanudar reproducción",
            "`/stop` - Detener y limpiar cola",
            "`/skip` - Saltar canción actual",
            "`/queue` - Ver cola de reproducción",
            "`/volume [0-100]` - Ajustar volumen",
            "`/nowplaying` - Canción actual"
        ]
        
        embed.add_field(
            name="🎶 Comandos Disponibles",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.add_field(
            name="🌐 Fuentes Compatibles",
            value="• YouTube\n• Spotify\n• SoundCloud\n• Enlaces directos",
            inline=False
        )
        
        return embed
    
    def _get_tickets_help(self):
        embed = nextcord.Embed(
            title="🎫 Sistema de Tickets",
            description="Sistema de soporte con transcripciones automáticas",
            color=nextcord.Color.blurple()
        )
        
        commands_list = [
            "`/ticket create [razón]` - Crear ticket de soporte",
            "`/ticket close` - Cerrar ticket actual",
            "`/ticket add [usuario]` - Añadir usuario al ticket",
            "`/ticket remove [usuario]` - Quitar usuario del ticket",
            "`/ticket setup` - Configurar sistema (admin)",
            "`/transcript` - Generar transcripción"
        ]
        
        embed.add_field(
            name="🎯 Comandos Disponibles",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.add_field(
            name="📝 Características",
            value="• Transcripciones automáticas\n• Gestión de permisos\n• Logs completos\n• Interfaz intuitiva",
            inline=False
        )
        
        return embed
    
    def _get_voicemaster_help(self):
        embed = nextcord.Embed(
            title="🎙️ VoiceMaster",
            description="Sistema de canales de voz temporales personalizables",
            color=nextcord.Color.dark_blue()
        )
        
        commands_list = [
            "`/voice setup` - Configurar VoiceMaster (admin)",
            "`/voice lock` - Bloquear tu canal",
            "`/voice unlock` - Desbloquear tu canal",
            "`/voice limit [número]` - Límite de usuarios",
            "`/voice name [nombre]` - Cambiar nombre",
            "`/voice transfer [usuario]` - Transferir propiedad"
        ]
        
        embed.add_field(
            name="🔧 Comandos Disponibles",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.add_field(
            name="⚡ Funcionamiento",
            value="1. Únete al canal **➕ Crear Canal**\n2. Se crea automáticamente tu canal\n3. Gestiona con botones o comandos",
            inline=False
        )
        
        return embed
    
    def _get_server_help(self):
        embed = nextcord.Embed(
            title="🏗️ Configuración de Servidor",
            description="Plantillas y configuraciones automáticas",
            color=nextcord.Color.teal()
        )
        
        commands_list = [
            "`/server template` - Crear plantilla de servidor",
            "`/server stats` - Configurar estadísticas automáticas",
            "`/verificacion setup` - Sistema de verificación",
            "`/confesiones setup` - Configurar confesiones",
            "`/niveles config` - Configurar sistema de niveles"
        ]
        
        embed.add_field(
            name="🛠️ Comandos Disponibles",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.add_field(
            name="🎨 Plantillas Disponibles",
            value="• Gaming (esports y clanes)\n• Comunidad (chat general)\n• Estudio (académico)\n• Empresarial (corporativo)\n• Tech (programación)",
            inline=False
        )
        
        return embed
    
    def _get_admin_help(self):
        embed = nextcord.Embed(
            title="⚙️ Comandos de Administración",
            description="Herramientas administrativas avanzadas",
            color=nextcord.Color.dark_red()
        )
        
        commands_list = [
            "`/say [mensaje]` - Hacer que el bot diga algo",
            "`/embed [título] [descripción]` - Crear embed personalizado",
            "`/announce [mensaje]` - Anuncio con formato especial",
            "`/config view` - Ver configuración del servidor",
            "`/logs setup` - Configurar logs de moderación"
        ]
        
        embed.add_field(
            name="🔐 Comandos Disponibles",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Importante",
            value="Estos comandos requieren permisos de **Gestionar Servidor** o superiores",
            inline=False
        )
        
        return embed
    
    def _get_emojis_help(self):
        embed = nextcord.Embed(
            title="😀 Emojis & Stickers",
            description="Personaliza tu servidor con emojis y stickers chulos",
            color=nextcord.Color.yellow()
        )
        
        emoji_commands = [
            "`/emoji add [url] [nombre]` - Añadir emoji desde URL",
            "`/emoji pack [pack]` - Instalar pack de emojis temático",
            "`/emoji random` - Añadir emoji aleatorio popular",
            "`/emoji list` - Ver emojis del servidor",
            "`/emoji remove [nombre]` - Eliminar emoji del servidor"
        ]
        
        sticker_commands = [
            "`/sticker add [url] [nombre]` - Añadir sticker personalizado",
            "`/sticker pack [pack]` - Instalar pack de stickers",
            "`/sticker search [query]` - Buscar stickers populares",
            "`/sticker list` - Ver stickers del servidor",
            "`/sticker remove [id]` - Eliminar sticker",
            "`/sticker trending` - Ver stickers populares"
        ]
        
        embed.add_field(
            name="😀 Comandos de Emojis",
            value="\n".join(emoji_commands),
            inline=False
        )
        
        embed.add_field(
            name="📋 Comandos de Stickers",
            value="\n".join(sticker_commands),
            inline=False
        )
        
        embed.add_field(
            name="📦 Packs Disponibles",
            value="**Emojis:** pepe, kappa, discord, gaming, cute\n**Stickers:** memes, anime, cats, gaming, reactions",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Requisitos",
            value="• **Emojis:** Permisos de Gestionar Emojis\n• **Stickers:** Gestionar Servidor + Nitro Nivel 2+",
            inline=False
        )
        
        return embed

def setup(bot):
    """cargar el cog"""
    bot.add_cog(HelpSystem(bot))
