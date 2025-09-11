"""
Sistema de gestión de mensajes persistentes para DABOT V2
Maneja mensajes de tickets, voicemaster, y otros paneles interactivos
"""

import logging
import nextcord
from nextcord.ext import commands
from typing import Optional, Dict, Any, List
import json
import sqlite3
import os

logger = logging.getLogger(__name__)

class PersistentMessageDB:
    """Base de datos para mensajes persistentes"""
    
    def __init__(self, db_path: str = "data/persistent_messages.db"):
        self.db_path = db_path
        self.ensure_data_dir()
        self.init_database()
    
    def ensure_data_dir(self):
        """Asegura que el directorio de datos existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """Inicializa las tablas de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de mensajes persistentes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS persistent_messages (
                    guild_id TEXT,
                    message_type TEXT,
                    channel_id TEXT,
                    message_id TEXT,
                    message_data TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, message_type)
                )
            ''')
            
            # Tabla de configuraciones de mensajes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS message_configs (
                    guild_id TEXT,
                    message_type TEXT,
                    config_data TEXT,
                    PRIMARY KEY (guild_id, message_type)
                )
            ''')
            
            conn.commit()
    
    def save_message(self, guild_id: str, message_type: str, channel_id: str, message_id: str, message_data: Dict[str, Any]):
        """Guarda un mensaje persistente"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO persistent_messages 
                (guild_id, message_type, channel_id, message_id, message_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (guild_id, message_type, channel_id, message_id, json.dumps(message_data)))
            conn.commit()
    
    def get_message(self, guild_id: str, message_type: str) -> Optional[Dict[str, Any]]:
        """Obtiene información de un mensaje persistente"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT channel_id, message_id, message_data FROM persistent_messages 
                WHERE guild_id = ? AND message_type = ? AND is_active = 1
            ''', (guild_id, message_type))
            result = cursor.fetchone()
            
            if result:
                return {
                    'channel_id': result[0],
                    'message_id': result[1],
                    'message_data': json.loads(result[2])
                }
            return None
    
    def set_message_inactive(self, guild_id: str, message_type: str):
        """Marca un mensaje como inactivo"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE persistent_messages 
                SET is_active = 0 
                WHERE guild_id = ? AND message_type = ?
            ''', (guild_id, message_type))
            conn.commit()
    
    def save_config(self, guild_id: str, message_type: str, config: Dict[str, Any]):
        """Guarda configuración de mensaje"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO message_configs 
                (guild_id, message_type, config_data)
                VALUES (?, ?, ?)
            ''', (guild_id, message_type, json.dumps(config)))
            conn.commit()
    
    def get_config(self, guild_id: str, message_type: str) -> Dict[str, Any]:
        """Obtiene configuración de mensaje"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT config_data FROM message_configs 
                WHERE guild_id = ? AND message_type = ?
            ''', (guild_id, message_type))
            result = cursor.fetchone()
            
            if result:
                return json.loads(result[0])
            return {}

class PersistentMessageManager(commands.Cog):
    """Gestor de mensajes persistentes"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = PersistentMessageDB()
        
        # Configuraciones por defecto para diferentes tipos de mensajes
        self.default_configs = {
            'ticket_panel': {
                'title': '🎫 Sistema de Tickets',
                'description': 'Haz clic en el botón para crear un ticket y recibir soporte.',
                'color': 0x00ff00,
                'button_label': '🎫 Crear Ticket',
                'button_emoji': '🎫'
            },
            'voicemaster_panel': {
                'title': '🎤 VoiceMaster',
                'description': 'Únete a un canal de voz y usa los botones para controlarlo.',
                'color': 0x0099ff,
                'buttons': [
                    {'label': '🔒 Bloquear', 'emoji': '🔒', 'action': 'lock'},
                    {'label': '🔓 Desbloquear', 'emoji': '🔓', 'action': 'unlock'},
                    {'label': '👁️ Ocultar', 'emoji': '👁️', 'action': 'hide'},
                    {'label': '👀 Mostrar', 'emoji': '👀', 'action': 'show'},
                    {'label': '➕ Aumentar Límite', 'emoji': '➕', 'action': 'increase'},
                    {'label': '➖ Reducir Límite', 'emoji': '➖', 'action': 'decrease'}
                ]
            },
            'welcome_panel': {
                'title': '👋 ¡Bienvenido al servidor!',
                'description': 'Selecciona tus roles y lee las reglas.',
                'color': 0xffff00,
                'buttons': [
                    {'label': '📖 Leer Reglas', 'emoji': '📖', 'action': 'rules'},
                    {'label': '🎮 Roles de Juegos', 'emoji': '🎮', 'action': 'game_roles'}
                ]
            }
        }
    
    async def verify_and_setup_message(self, guild: nextcord.Guild, message_type: str, channel_id: Optional[int] = None) -> bool:
        """Verifica si existe un mensaje persistente y lo crea si no existe"""
        try:
            guild_id = str(guild.id)
            
            # Verificar si ya existe el mensaje
            existing = self.db.get_message(guild_id, message_type)
            
            if existing:
                # Verificar que el mensaje aún existe en Discord
                channel = guild.get_channel(int(existing['channel_id']))
                if channel:
                    try:
                        message = await channel.fetch_message(int(existing['message_id']))
                        if message:
                            logger.info(f"Mensaje {message_type} encontrado en {guild.name}")
                            return True
                    except nextcord.NotFound:
                        # El mensaje fue eliminado, marcar como inactivo
                        self.db.set_message_inactive(guild_id, message_type)
                        logger.warning(f"Mensaje {message_type} eliminado en {guild.name}, recreando...")
            
            # Crear nuevo mensaje
            return await self.create_message(guild, message_type, channel_id)
            
        except Exception as e:
            logger.error(f"Error verificando mensaje {message_type} en {guild.name}: {e}")
            return False
    
    async def create_message(self, guild: nextcord.Guild, message_type: str, channel_id: Optional[int] = None) -> bool:
        """Crea un mensaje persistente"""
        try:
            guild_id = str(guild.id)
            
            # Obtener configuración personalizada o usar por defecto
            config = self.db.get_config(guild_id, message_type)
            if not config:
                config = self.default_configs.get(message_type, {})
            
            # Determinar canal
            target_channel = None
            if channel_id:
                target_channel = guild.get_channel(channel_id)
            else:
                # Buscar canal apropiado automáticamente
                target_channel = await self.find_appropriate_channel(guild, message_type)
            
            if not target_channel:
                logger.warning(f"No se encontró canal apropiado para {message_type} en {guild.name}")
                return False
            
            # Crear embed
            embed = nextcord.Embed(
                title=config.get('title', f'Panel de {message_type}'),
                description=config.get('description', 'Panel interactivo'),
                color=config.get('color', 0x0099ff)
            )
            
            # Crear vista con botones
            view = self.create_view_for_type(message_type, config)
            
            # Enviar mensaje
            message = await target_channel.send(embed=embed, view=view)
            
            # Guardar en base de datos
            message_data = {
                'title': config.get('title'),
                'description': config.get('description'),
                'color': config.get('color'),
                'config': config
            }
            
            self.db.save_message(guild_id, message_type, str(target_channel.id), str(message.id), message_data)
            
            logger.info(f"Mensaje {message_type} creado en {guild.name} en canal {target_channel.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando mensaje {message_type} en {guild.name}: {e}")
            return False
    
    async def find_appropriate_channel(self, guild: nextcord.Guild, message_type: str) -> Optional[nextcord.TextChannel]:
        """Encuentra el canal más apropiado para un tipo de mensaje"""
        try:
            # Intentar obtener canal configurado desde el sistema de configuración
            from .server_manager import ServerConfigDB
            server_db = ServerConfigDB()
            
            # Mapeo de tipos de mensaje a tipos de canal
            channel_mappings = {
                'ticket_panel': ['tickets', 'soporte', 'support'],
                'voicemaster_panel': ['voicemaster', 'voice', 'voz'],
                'welcome_panel': ['welcome', 'bienvenida', 'general']
            }
            
            # Buscar canal configurado
            for channel_type in channel_mappings.get(message_type, []):
                channel_id = server_db.get_channel(str(guild.id), channel_type)
                if channel_id:
                    channel = guild.get_channel(int(channel_id))
                    if channel:
                        return channel
            
            # Buscar por nombre de canal
            search_names = {
                'ticket_panel': ['tickets', 'soporte', 'support', 'help'],
                'voicemaster_panel': ['voicemaster', 'voice-control', 'voz'],
                'welcome_panel': ['welcome', 'bienvenida', 'general', 'inicio']
            }
            
            for name in search_names.get(message_type, []):
                for channel in guild.text_channels:
                    if name.lower() in channel.name.lower():
                        return channel
            
            # Como último recurso, usar canal general
            general_channel = server_db.get_channel(str(guild.id), 'general')
            if general_channel:
                return guild.get_channel(int(general_channel))
            
            # Si no hay canal general configurado, buscar uno
            for channel in guild.text_channels:
                if channel.name.lower() in ['general', 'chat', 'inicio', 'main']:
                    return channel
            
            # Como último último recurso, usar el primer canal donde el bot pueda escribir
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    return channel
            
        except Exception as e:
            logger.error(f"Error buscando canal apropiado: {e}")
        
        return None
    
    def create_view_for_type(self, message_type: str, config: Dict[str, Any]):
        """Crea la vista apropiada para el tipo de mensaje"""
        if message_type == 'ticket_panel':
            return TicketPanelView(config)
        elif message_type == 'voicemaster_panel':
            from .voicemaster import VoiceMasterPanelView
            return VoiceMasterPanelView(config)
        elif message_type == 'welcome_panel':
            return WelcomePanelView(config)
        else:
            return DefaultPanelView(config)
    
    @nextcord.slash_command(name="panels", description="Gestión de paneles persistentes")
    async def panels_main(self, interaction: nextcord.Interaction):
        """Comando principal de gestión de paneles"""
        pass
    
    @panels_main.subcommand(name="create", description="Crear un panel persistente")
    async def create_panel(
        self,
        interaction: nextcord.Interaction,
        tipo: str = nextcord.SlashOption(
            description="Tipo de panel a crear",
            choices=["ticket_panel", "voicemaster_panel", "welcome_panel"]
        ),
        canal: nextcord.TextChannel = nextcord.SlashOption(description="Canal donde crear el panel", required=False)
    ):
        """Crear un panel persistente manualmente"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitas permisos de administrador para usar este comando.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        channel_id = canal.id if canal else None
        success = await self.create_message(interaction.guild, tipo, channel_id)
        
        if success:
            embed = nextcord.Embed(
                title="✅ Panel Creado",
                description=f"Panel de tipo **{tipo}** creado exitosamente.",
                color=nextcord.Color.green()
            )
            if canal:
                embed.add_field(name="Canal", value=canal.mention, inline=True)
        else:
            embed = nextcord.Embed(
                title="❌ Error",
                description=f"No se pudo crear el panel de tipo **{tipo}**.",
                color=nextcord.Color.red()
            )
        
        await interaction.followup.send(embed=embed)
    
    @panels_main.subcommand(name="verify", description="Verificar y recrear paneles faltantes")
    async def verify_panels(self, interaction: nextcord.Interaction):
        """Verificar todos los paneles del servidor"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitas permisos de administrador para usar este comando.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        guild = interaction.guild
        results = []
        
        # Verificar cada tipo de panel
        for panel_type in ['ticket_panel', 'voicemaster_panel', 'welcome_panel']:
            result = await self.verify_and_setup_message(guild, panel_type)
            status = "✅ Activo" if result else "❌ Error"
            results.append(f"**{panel_type}**: {status}")
        
        embed = nextcord.Embed(
            title="🔍 Verificación de Paneles",
            description="\n".join(results),
            color=nextcord.Color.blue()
        )
        
        await interaction.followup.send(embed=embed)

# Vistas para diferentes tipos de paneles
class TicketPanelView(nextcord.ui.View):
    """Vista para panel de tickets"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(timeout=None)
        self.config = config
        
        # Crear botón de ticket
        button = nextcord.ui.Button(
            label=config.get('button_label', '🎫 Crear Ticket'),
            emoji=config.get('button_emoji', '🎫'),
            style=nextcord.ButtonStyle.green,
            custom_id='create_ticket'
        )
        button.callback = self.create_ticket
        self.add_item(button)
    
    async def create_ticket(self, interaction: nextcord.Interaction):
        """Crear un nuevo ticket"""
        # Obtener el ticket manager
        ticket_manager = interaction.client.get_cog('TicketManager')
        if ticket_manager:
            await ticket_manager.create_ticket_interaction(interaction)
        else:
            await interaction.response.send_message(
                "❌ Sistema de tickets no disponible.", ephemeral=True
            )

class WelcomePanelView(nextcord.ui.View):
    """Vista para panel de bienvenida"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(timeout=None)
        self.config = config
        
        # Crear botones desde configuración
        buttons = config.get('buttons', [])
        for button_config in buttons:
            button = nextcord.ui.Button(
                label=button_config.get('label', 'Botón'),
                emoji=button_config.get('emoji'),
                style=nextcord.ButtonStyle.primary,
                custom_id=f"welcome_{button_config.get('action', 'action')}"
            )
            button.callback = self.handle_welcome_action
            self.add_item(button)
    
    async def handle_welcome_action(self, interaction: nextcord.Interaction):
        """Manejar acciones de bienvenida"""
        action = interaction.data['custom_id'].replace('welcome_', '')
        await interaction.response.send_message(
            f"👋 Ejecutando acción: {action}", ephemeral=True
        )

class DefaultPanelView(nextcord.ui.View):
    """Vista por defecto para paneles"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(timeout=None)
        self.config = config

def setup(bot):
    """Función para añadir el cog al bot"""
    return PersistentMessageManager(bot)
