"""
Sistema de Mensajes de Ayuda Automáticos
Crea embeds de ayuda en canales específicos y los fija automáticamente
Por: Davito
"""

import logging
import nextcord
from nextcord.ext import commands
import sqlite3
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AutoHelpSystem(commands.Cog):
    """Sistema de ayuda automática en canales"""
    
    def __init__(self, bot):
        self.bot = bot
        self.init_database()
        
        # Configuración de mensajes de ayuda por tipo de canal
        self.help_messages = {
            "comandos": {
                "title": "🤖 Canal de Comandos",
                "description": "Este canal está destinado para usar comandos del bot",
                "commands": [
                    "`/help` - Ver todos los comandos disponibles",
                    "`/ping` - Ver latencia del bot", 
                    "`/serverinfo` - Información del servidor",
                    "`/userinfo` - Información de usuario",
                    "`/avatar` - Ver avatar de usuario"
                ],
                "color": 0x3498db
            },
            "economia": {
                "title": "💰 Canal de Economía",
                "description": "Aquí puedes usar comandos relacionados con la economía del servidor",
                "commands": [
                    "`/balance` - Ver tu balance de monedas",
                    "`/daily` - Reclamar recompensa diaria",
                    "`/work` - Trabajar para ganar dinero",
                    "`/fish` - Ir a pescar",
                    "`/aquarium` - Ver tu acuario personal"
                ],
                "color": 0xf1c40f
            },
            "musica": {
                "title": "🎵 Canal de Música", 
                "description": "Controla el reproductor de música desde aquí",
                "commands": [
                    "`/play [canción]` - Reproducir música",
                    "`/pause` - Pausar reproducción",
                    "`/skip` - Saltar canción",
                    "`/queue` - Ver cola de reproducción",
                    "`/volume [0-100]` - Ajustar volumen"
                ],
                "color": 0xe91e63
            },
            "entretenimiento": {
                "title": "🎮 Canal de Entretenimiento",
                "description": "Diviértete con estos comandos de entretenimiento",
                "commands": [
                    "`/meme` - Obtener meme aleatorio",
                    "`/8ball [pregunta]` - Bola 8 mágica",
                    "`/coin` - Lanzar moneda",
                    "`/dice [caras]` - Lanzar dados",
                    "`/trivia` - Preguntas de trivia"
                ],
                "color": 0x9b59b6
            },
            "nsfw": {
                "title": "🔞 Canal NSFW",
                "description": "Comandos de contenido para adultos (Solo +18)",
                "commands": [
                    "`/nsfw waifu` - Imagen waifu aleatoria",
                    "`/nsfw neko` - Imagen neko aleatoria", 
                    "`/rule34 [tags]` - Buscar en Rule34",
                    "`/gelbooru [tags]` - Buscar en Gelbooru"
                ],
                "color": 0xe74c3c,
                "warning": "⚠️ Este contenido es solo para mayores de 18 años"
            },
            "moderacion": {
                "title": "🛡️ Canal de Moderación",
                "description": "Comandos de moderación para staff",
                "commands": [
                    "`/ban [usuario] [razón]` - Banear usuario",
                    "`/kick [usuario] [razón]` - Expulsar usuario", 
                    "`/warn [usuario] [razón]` - Advertir usuario",
                    "`/clear [cantidad]` - Limpiar mensajes",
                    "`/warnings [usuario]` - Ver warnings"
                ],
                "color": 0xf39c12,
                "warning": "🔒 Solo para miembros del staff"
            },
            "tickets": {
                "title": "🎫 Canal de Tickets",
                "description": "Crea tickets de soporte aquí",
                "commands": [
                    "`/ticket` - Crear nuevo ticket",
                    "🎫 **Botón:** Crear Ticket - Crea un ticket de soporte"
                ],
                "color": 0x00bcd4,
                "info": "Los tickets se crean como canales privados donde puedes hablar con el staff"
            },
            "autoroles": {
                "title": "🎭 Canal de Autoroles",
                "description": "Obtén roles automáticamente",
                "commands": [
                    "🎮 **Gaming:** Roles de juegos y plataformas",
                    "🎵 **Música:** Roles de géneros musicales",
                    "👥 **Comunidad:** Roles de intereses",
                    "📚 **Estudio:** Roles académicos"
                ],
                "color": 0x673ab7,
                "info": "Simplemente haz clic en los botones para obtener o quitar roles"
            },
            "voicemaster": {
                "title": "🔊 Panel de VoiceMaster",
                "description": "Controla canales de voz temporales",
                "commands": [
                    "🔒 **Lock:** Bloquear tu canal de voz",
                    "🔓 **Unlock:** Desbloquear tu canal", 
                    "👁️ **Hide:** Ocultar tu canal",
                    "👁️‍🗨️ **Show:** Mostrar tu canal",
                    "📝 **Rename:** Cambiar nombre del canal",
                    "🎯 **Limit:** Cambiar límite de usuarios"
                ],
                "color": 0x4caf50,
                "info": "Primero únete al canal 'Crear Canal de Voz' para obtener tu canal temporal"
            }
        }
    
    def init_database(self):
        """Inicializar base de datos"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_help_messages (
                    guild_id INTEGER,
                    channel_id INTEGER,
                    message_id INTEGER,
                    help_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, channel_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Base de datos de auto-help inicializada")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos auto-help: {e}")
    
    @nextcord.slash_command(name="setup-help", description="Configurar mensajes de ayuda automáticos")
    async def setup_help(self, interaction: nextcord.Interaction):
        """Configurar sistema de ayuda automática"""
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Necesitas permisos de gestionar canales.", ephemeral=True)
            return
        
        embed = nextcord.Embed(
            title="🔧 Configurar Ayuda Automática",
            description="Selecciona los canales donde configurar mensajes de ayuda automáticos",
            color=nextcord.Color.blue()
        )
        
        view = HelpSetupView(self, interaction.guild)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def create_help_message(self, channel: nextcord.TextChannel, help_type: str) -> bool:
        """Crear mensaje de ayuda en un canal"""
        try:
            if help_type not in self.help_messages:
                return False
            
            help_config = self.help_messages[help_type]
            
            embed = nextcord.Embed(
                title=help_config["title"],
                description=help_config["description"],
                color=help_config["color"]
            )
            
            # Añadir comandos
            commands_text = "\n".join(help_config["commands"])
            embed.add_field(
                name="📋 Comandos Disponibles",
                value=commands_text,
                inline=False
            )
            
            # Añadir warning si existe
            if "warning" in help_config:
                embed.add_field(
                    name="⚠️ Advertencia",
                    value=help_config["warning"],
                    inline=False
                )
            
            # Añadir info si existe
            if "info" in help_config:
                embed.add_field(
                    name="ℹ️ Información",
                    value=help_config["info"],
                    inline=False
                )
            
            embed.set_footer(text="Mensaje fijado automáticamente • DaBot v2")
            embed.timestamp = datetime.now()
            
            # Enviar mensaje
            message = await channel.send(embed=embed)
            
            # Fijar mensaje
            try:
                await message.pin()
            except:
                pass  # No se pudo fijar (tal vez ya hay muchos fijados)
            
            # Guardar en base de datos
            await self.save_help_message(channel.guild.id, channel.id, message.id, help_type)
            
            return True
            
        except Exception as e:
            logger.error(f"Error creando mensaje de ayuda: {e}")
            return False
    
    async def save_help_message(self, guild_id: int, channel_id: int, message_id: int, help_type: str):
        """Guardar mensaje de ayuda en base de datos"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO auto_help_messages
                (guild_id, channel_id, message_id, help_type)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, channel_id, message_id, help_type))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error guardando mensaje de ayuda: {e}")
    
    async def detect_channel_type(self, channel: nextcord.TextChannel) -> Optional[str]:
        """Detectar tipo de canal automáticamente"""
        name = channel.name.lower()
        
        # Detectar por nombre del canal
        if any(word in name for word in ["comando", "bot", "command"]):
            return "comandos"
        elif any(word in name for word in ["economia", "money", "coin", "dinero"]):
            return "economia"
        elif any(word in name for word in ["music", "musica", "audio", "song"]):
            return "musica"
        elif any(word in name for word in ["entretenimiento", "fun", "juego", "game"]):
            return "entretenimiento"
        elif any(word in name for word in ["nsfw", "adult", "18+"]):
            return "nsfw"
        elif any(word in name for word in ["mod", "admin", "staff"]):
            return "moderacion"
        elif any(word in name for word in ["ticket", "soporte", "support"]):
            return "tickets"
        elif any(word in name for word in ["role", "rol", "autorole"]):
            return "autoroles"
        elif any(word in name for word in ["voice", "voz", "voicemaster", "vc"]):
            return "voicemaster"
        
        return None
    
    async def auto_setup_help_messages(self, guild: nextcord.Guild):
        """Configurar mensajes de ayuda automáticamente en todo el servidor"""
        configured_count = 0
        
        for channel in guild.text_channels:
            channel_type = await self.detect_channel_type(channel)
            
            if channel_type:
                success = await self.create_help_message(channel, channel_type)
                if success:
                    configured_count += 1
                    
                # Pausa para evitar rate limits
                await asyncio.sleep(1)
        
        return configured_count


class HelpSetupView(nextcord.ui.View):
    """Vista para configurar mensajes de ayuda"""
    
    def __init__(self, cog, guild):
        super().__init__(timeout=300)
        self.cog = cog
        self.guild = guild
    
    @nextcord.ui.button(label="🔍 Detectar Automáticamente", style=nextcord.ButtonStyle.primary)
    async def auto_detect(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Detectar y configurar automáticamente"""
        await interaction.response.defer()
        
        try:
            count = await self.cog.auto_setup_help_messages(self.guild)
            
            embed = nextcord.Embed(
                title="✅ Configuración Automática Completada",
                description=f"Se configuraron mensajes de ayuda en {count} canales",
                color=nextcord.Color.green()
            )
            
            if count > 0:
                embed.add_field(
                    name="📋 Canales Configurados",
                    value=f"Se detectaron automáticamente {count} canales y se crearon mensajes de ayuda específicos",
                    inline=False
                )
            else:
                embed.add_field(
                    name="ℹ️ Sin Canales Detectados",
                    value="No se encontraron canales con nombres reconocibles. Usa la configuración manual.",
                    inline=False
                )
            
            await interaction.edit_original_response(embed=embed, view=None)
            
        except Exception as e:
            logger.error(f"Error en auto-detección: {e}")
            await interaction.edit_original_response(content="❌ Error durante la configuración automática", view=None)
    
    @nextcord.ui.button(label="⚙️ Configuración Manual", style=nextcord.ButtonStyle.secondary)
    async def manual_config(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Configuración manual por canal"""
        embed = nextcord.Embed(
            title="⚙️ Configuración Manual",
            description="Selecciona el tipo de ayuda y luego usa el comando en el canal deseado:",
            color=nextcord.Color.blue()
        )
        
        help_types = "\n".join([
            "`🤖 comandos` - Canal de comandos generales",
            "`💰 economia` - Canal de economía y pesca", 
            "`🎵 musica` - Canal de música",
            "`🎮 entretenimiento` - Canal de entretenimiento",
            "`🔞 nsfw` - Canal NSFW",
            "`🛡️ moderacion` - Canal de moderación",
            "`🎫 tickets` - Canal de tickets",
            "`🎭 autoroles` - Canal de autoroles",
            "`🔊 voicemaster` - Panel de VoiceMaster"
        ])
        
        embed.add_field(
            name="📋 Tipos Disponibles",
            value=help_types,
            inline=False
        )
        
        embed.add_field(
            name="💡 Uso",
            value="Usa `/create-help [tipo]` en el canal donde quieres el mensaje",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @nextcord.ui.button(label="❌ Cancelar", style=nextcord.ButtonStyle.danger)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Cancelar configuración"""
        embed = nextcord.Embed(
            title="❌ Configuración Cancelada",
            description="La configuración de ayuda automática ha sido cancelada",
            color=nextcord.Color.red()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)


@nextcord.slash_command(name="create-help", description="Crear mensaje de ayuda manual")
async def create_help_manual(
    interaction: nextcord.Interaction,
    tipo: str = nextcord.SlashOption(
        choices=["comandos", "economia", "musica", "entretenimiento", "nsfw", "moderacion", "tickets", "autoroles", "voicemaster"]
    )
):
    """Crear mensaje de ayuda manualmente"""
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ Necesitas permisos de gestionar canales.", ephemeral=True)
        return
    
    # Obtener instancia del cog
    auto_help_cog = None
    for cog in interaction.client.cogs.values():
        if isinstance(cog, AutoHelpSystem):
            auto_help_cog = cog
            break
    
    if not auto_help_cog:
        await interaction.response.send_message("❌ Sistema de ayuda no disponible.", ephemeral=True)
        return
    
    success = await auto_help_cog.create_help_message(interaction.channel, tipo)
    
    if success:
        await interaction.response.send_message(f"✅ Mensaje de ayuda '{tipo}' creado y fijado en este canal.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Error creando mensaje de ayuda.", ephemeral=True)


def setup(bot):
    """Cargar el cog"""
    # Registrar comando global
    bot.add_application_command(create_help_manual)
    return AutoHelpSystem(bot)
