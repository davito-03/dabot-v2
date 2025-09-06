"""
sistema de tickets para soporte
por davito
"""

import json
import logging
import sqlite3
import nextcord
from nextcord.ext import commands
from typing import Dict, Optional
import os
import asyncio
import io
from datetime import datetime

logger = logging.getLogger(__name__)

class TicketDB:
    """manejo de base de datos para tickets"""
    
    def __init__(self, db_path: str = "data/tickets.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """inicializar base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        channel_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        reason TEXT,
                        status TEXT DEFAULT 'open',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        closed_at TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS ticket_config (
                        guild_id INTEGER PRIMARY KEY,
                        category_id INTEGER,
                        support_role_id INTEGER,
                        log_channel_id INTEGER
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"error inicializando base de datos de tickets: {e}")
    
    def create_ticket(self, guild_id: int, channel_id: int, user_id: int, reason: str = None):
        """crear nuevo ticket"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO tickets (guild_id, channel_id, user_id, reason) VALUES (?, ?, ?, ?)",
                    (guild_id, channel_id, user_id, reason)
                )
                conn.commit()
                return conn.lastrowid
        except Exception as e:
            logger.error(f"error creando ticket: {e}")
            return None
    
    def close_ticket(self, channel_id: int):
        """cerrar ticket"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE tickets SET status = 'closed', closed_at = CURRENT_TIMESTAMP WHERE channel_id = ?",
                    (channel_id,)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"error cerrando ticket: {e}")
    
    def get_ticket(self, channel_id: int):
        """obtener información de ticket"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM tickets WHERE channel_id = ?",
                    (channel_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"error obteniendo ticket: {e}")
            return None
    
    def get_config(self, guild_id: int):
        """obtener configuración del servidor"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM ticket_config WHERE guild_id = ?",
                    (guild_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"error obteniendo configuración: {e}")
            return None
    
    def set_config(self, guild_id: int, category_id: int = None, support_role_id: int = None, log_channel_id: int = None):
        """configurar servidor"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO ticket_config 
                    (guild_id, category_id, support_role_id, log_channel_id) 
                    VALUES (?, ?, ?, ?)
                ''', (guild_id, category_id, support_role_id, log_channel_id))
                conn.commit()
        except Exception as e:
            logger.error(f"error configurando servidor: {e}")

class TicketView(nextcord.ui.View):
    """vista con botones para tickets"""
    
    def __init__(self, ticket_cog):
        super().__init__(timeout=None)
        self.ticket_cog = ticket_cog
    
    @nextcord.ui.button(label="🎫 crear ticket", style=nextcord.ButtonStyle.primary, custom_id="create_ticket")
    async def create_ticket(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """crear nuevo ticket"""
        await self.ticket_cog.create_ticket_interaction(interaction)

class TicketModal(nextcord.ui.Modal):
    """modal para crear ticket"""
    
    def __init__(self, ticket_cog):
        super().__init__(title="crear ticket de soporte")
        self.ticket_cog = ticket_cog
        
        self.reason = nextcord.ui.TextInput(
            label="motivo del ticket",
            placeholder="describe tu problema o consulta...",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
            max_length=1000
        )
        self.add_item(self.reason)
    
    async def callback(self, interaction: nextcord.Interaction):
        """procesar creación de ticket"""
        await self.ticket_cog.process_ticket_creation(interaction, self.reason.value)

class TicketControlView(nextcord.ui.View):
    """vista de control para tickets activos"""
    
    def __init__(self, ticket_cog):
        super().__init__(timeout=None)
        self.ticket_cog = ticket_cog
    
    @nextcord.ui.button(label="🔒 cerrar ticket", style=nextcord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """cerrar ticket"""
        await self.ticket_cog.close_ticket_interaction(interaction)
    
    @nextcord.ui.button(label="📋 transcript", style=nextcord.ButtonStyle.secondary, custom_id="ticket_transcript")
    async def transcript(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """generar transcript"""
        await self.ticket_cog.generate_transcript(interaction)

class TicketManager(commands.Cog):
    """sistema de tickets"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = TicketDB()
        self.ticket_channels = {}
        
        # agregar vistas persistentes
        self.bot.add_view(TicketView(self))
        self.bot.add_view(TicketControlView(self))
    
    @nextcord.slash_command(name="ticket", description="comandos de tickets")
    async def ticket_group(self, interaction: nextcord.Interaction):
        pass
    
    @ticket_group.subcommand(name="setup", description="configurar sistema de tickets")
    async def setup_tickets(self, interaction: nextcord.Interaction):
        """configurar sistema de tickets"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ necesitas permisos de gestionar servidor.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            
            # crear categoría para tickets
            category = await guild.create_category("🎫 tickets")
            
            # buscar o crear rol de soporte
            support_role = nextcord.utils.get(guild.roles, name="soporte")
            if not support_role:
                support_role = await guild.create_role(name="soporte", color=nextcord.Color.blue())
            
            # buscar canal de logs
            log_channel = nextcord.utils.get(guild.text_channels, name="ticket-logs")
            if not log_channel:
                log_channel = await guild.create_text_channel("ticket-logs", category=category)
            
            # guardar configuración
            self.db.set_config(guild.id, category.id, support_role.id, log_channel.id)
            
            # crear panel de tickets
            embed = nextcord.Embed(
                title="🎫 sistema de tickets",
                description="haz clic en el botón para crear un ticket de soporte.",
                color=nextcord.Color.blue()
            )
            embed.add_field(
                name="📋 instrucciones",
                value="• haz clic en '🎫 crear ticket'\n• describe tu problema\n• espera respuesta del staff",
                inline=False
            )
            
            view = TicketView(self)
            await interaction.followup.send(embed=embed, view=view)
            
            logger.info(f"sistema de tickets configurado en {guild.name}")
            
        except Exception as e:
            logger.error(f"error configurando tickets: {e}")
            await interaction.followup.send("❌ error al configurar el sistema de tickets.")
    
    async def create_ticket_interaction(self, interaction: nextcord.Interaction):
        """manejar interacción de crear ticket"""
        try:
            # verificar si el usuario ya tiene un ticket abierto
            guild = interaction.guild
            user_tickets = [ch for ch in guild.text_channels if ch.name.startswith(f"ticket-{interaction.user.name.lower()}")]
            
            if user_tickets:
                await interaction.response.send_message("❌ ya tienes un ticket abierto.", ephemeral=True)
                return
            
            # mostrar modal
            modal = TicketModal(self)
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            logger.error(f"error en interacción crear ticket: {e}")
            await interaction.response.send_message("❌ error al crear ticket.", ephemeral=True)
    
    async def process_ticket_creation(self, interaction: nextcord.Interaction, reason: str):
        """procesar creación de ticket"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            guild = interaction.guild
            user = interaction.user
            
            # obtener configuración
            config = self.db.get_config(guild.id)
            if not config:
                await interaction.followup.send("❌ sistema de tickets no configurado.", ephemeral=True)
                return
            
            category_id, support_role_id, log_channel_id = config[1], config[2], config[3]
            category = guild.get_channel(category_id)
            support_role = guild.get_role(support_role_id)
            
            # crear canal de ticket
            overwrites = {
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True),
                support_role: nextcord.PermissionOverwrite(read_messages=True, send_messages=True) if support_role else None
            }
            
            # remover overwrites nulos
            overwrites = {k: v for k, v in overwrites.items() if v is not None}
            
            channel_name = f"ticket-{user.name.lower()}"
            ticket_channel = await guild.create_text_channel(
                channel_name,
                category=category,
                overwrites=overwrites
            )
            
            # guardar en base de datos
            ticket_id = self.db.create_ticket(guild.id, ticket_channel.id, user.id, reason)
            
            # mensaje inicial
            embed = nextcord.Embed(
                title=f"🎫 ticket #{ticket_id}",
                description=f"**usuario:** {user.mention}\n**motivo:** {reason}",
                color=nextcord.Color.green()
            )
            embed.add_field(
                name="📋 información",
                value="• el staff responderá pronto\n• usa los botones para gestionar el ticket",
                inline=False
            )
            
            view = TicketControlView(self)
            await ticket_channel.send(embed=embed, view=view)
            await ticket_channel.send(f"{user.mention} {support_role.mention if support_role else ''}")
            
            await interaction.followup.send(f"✅ ticket creado: {ticket_channel.mention}", ephemeral=True)
            
            # log
            if log_channel_id:
                log_channel = guild.get_channel(log_channel_id)
                if log_channel:
                    log_embed = nextcord.Embed(
                        title="🎫 nuevo ticket",
                        description=f"**usuario:** {user.mention}\n**canal:** {ticket_channel.mention}\n**motivo:** {reason}",
                        color=nextcord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    await log_channel.send(embed=log_embed)
            
            logger.info(f"ticket creado por {user} en {guild.name}")
            
        except Exception as e:
            logger.error(f"error procesando creación de ticket: {e}")
            await interaction.followup.send("❌ error al crear el ticket.", ephemeral=True)
    
    async def close_ticket_interaction(self, interaction: nextcord.Interaction):
        """cerrar ticket"""
        try:
            # verificar que es un canal de ticket
            ticket_info = self.db.get_ticket(interaction.channel.id)
            if not ticket_info:
                await interaction.response.send_message("❌ este no es un canal de ticket.", ephemeral=True)
                return
            
            # verificar permisos
            if not (interaction.user.guild_permissions.manage_channels or 
                   interaction.user.id == ticket_info[3]):  # owner del ticket
                await interaction.response.send_message("❌ sin permisos para cerrar este ticket.", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            # cerrar en base de datos
            self.db.close_ticket(interaction.channel.id)
            
            # mensaje de cierre
            embed = nextcord.Embed(
                title="🔒 ticket cerrado",
                description=f"ticket cerrado por {interaction.user.mention}",
                color=nextcord.Color.red(),
                timestamp=datetime.utcnow()
            )
            await interaction.followup.send(embed=embed)
            
            # eliminar canal después de 10 segundos
            await asyncio.sleep(10)
            await interaction.channel.delete(reason="ticket cerrado")
            
            logger.info(f"ticket cerrado por {interaction.user}")
            
        except Exception as e:
            logger.error(f"error cerrando ticket: {e}")
            await interaction.followup.send("❌ error al cerrar ticket.")
    
    async def generate_transcript(self, interaction: nextcord.Interaction):
        """generar transcript del ticket"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            channel = interaction.channel
            messages = []
            
            async for message in channel.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                content = message.content if message.content else "[archivo/embed]"
                messages.append(f"[{timestamp}] {message.author}: {content}")
            
            transcript_content = "\n".join(messages)
            
            # crear archivo
            file = nextcord.File(
                io.StringIO(transcript_content), 
                filename=f"transcript-{channel.name}.txt"
            )
            
            await interaction.followup.send("📋 transcript generado:", file=file, ephemeral=True)
            
        except Exception as e:
            logger.error(f"error generando transcript: {e}")
            await interaction.followup.send("❌ error generando transcript.", ephemeral=True)

def setup(bot):
    """función para cargar el cog"""
    return TicketManager(bot)
