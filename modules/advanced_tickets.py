"""
Sistema de tickets avanzado con categorías y integración web
por davito
"""

import json
import logging
import asyncio
import aiohttp
import datetime
import os
from typing import Dict, List, Optional
import nextcord
from nextcord.ext import commands
from nextcord import ChannelType, PermissionOverwrite

logger = logging.getLogger(__name__)

class AdvancedTicketSystem(commands.Cog):
    """Sistema de tickets avanzado con categorías"""
    
    def __init__(self, bot):
        self.bot = bot
        self.tickets_file = "data/tickets_advanced.json"
        self.config_file = "data/ticket_config.json"
        self.ensure_data_dir()
        self.load_data()
        
    def ensure_data_dir(self):
        """Asegurar que existe el directorio de datos"""
        os.makedirs("data", exist_ok=True)
        
    def load_data(self):
        """Cargar datos de tickets y configuración"""
        try:
            with open(self.tickets_file, 'r', encoding='utf-8') as f:
                self.tickets = json.load(f)
        except FileNotFoundError:
            self.tickets = {}
            self.save_tickets()
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
            self.save_config()
    
    def save_tickets(self):
        """Guardar datos de tickets"""
        try:
            with open(self.tickets_file, 'w', encoding='utf-8') as f:
                json.dump(self.tickets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando tickets: {e}")
    
    def save_config(self):
        """Guardar configuración"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def get_guild_config(self, guild_id):
        """Obtener configuración del servidor"""
        guild_id = str(guild_id)
        if guild_id not in self.config:
            self.config[guild_id] = {
                "ticket_channel": None,
                "ticket_category": None,
                "staff_role": None,
                "log_channel": None,
                "categories": {
                    "soporte": {
                        "name": "💡 Soporte General",
                        "description": "Ayuda general con el servidor",
                        "emoji": "💡",
                        "staff_ping": True
                    },
                    "reporte": {
                        "name": "🚨 Reportar Usuario",
                        "description": "Reportar comportamiento inapropiado",
                        "emoji": "🚨",
                        "staff_ping": True
                    },
                    "sugerencia": {
                        "name": "💭 Sugerencias",
                        "description": "Sugerir mejoras para el servidor",
                        "emoji": "💭",
                        "staff_ping": False
                    },
                    "apelacion": {
                        "name": "📋 Apelación",
                        "description": "Apelar una sanción",
                        "emoji": "📋",
                        "staff_ping": True
                    },
                    "otro": {
                        "name": "❓ Otros",
                        "description": "Cualquier otro tema",
                        "emoji": "❓",
                        "staff_ping": False
                    }
                }
            }
            self.save_config()
        return self.config[guild_id]

    @nextcord.slash_command(name="ticket_setup", description="Configurar el sistema de tickets")
    async def ticket_setup(
        self,
        interaction: nextcord.Interaction,
        canal_tickets: nextcord.TextChannel = nextcord.SlashOption(description="Canal donde aparecerá el panel de tickets"),
        categoria_tickets: nextcord.CategoryChannel = nextcord.SlashOption(description="Categoría donde se crearán los tickets"),
        rol_staff: nextcord.Role = nextcord.SlashOption(description="Rol que puede gestionar tickets"),
        canal_logs: nextcord.TextChannel = nextcord.SlashOption(description="Canal para logs de tickets", required=False)
    ):
        """Configurar el sistema de tickets"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ No tienes permisos para configurar tickets.", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        config["ticket_channel"] = canal_tickets.id
        config["ticket_category"] = categoria_tickets.id
        config["staff_role"] = rol_staff.id
        if canal_logs:
            config["log_channel"] = canal_logs.id
        
        self.save_config()
        
        # Crear panel de tickets
        embed = nextcord.Embed(
            title="🎫 Sistema de Tickets",
            description="Selecciona el tipo de ticket que necesitas crear:",
            color=0x7289DA
        )
        
        embed.add_field(
            name="Tipos disponibles:",
            value="\n".join([
                f"{cat['emoji']} **{cat['name']}** - {cat['description']}"
                for cat in config["categories"].values()
            ]),
            inline=False
        )
        
        embed.add_field(
            name="📋 Instrucciones:",
            value="1. Selecciona el tipo de ticket\n2. Rellena la información solicitada\n3. Espera a que el staff te atienda",
            inline=False
        )
        
        embed.set_footer(text=f"Staff: {rol_staff.name}")
        
        view = TicketPanelView(self)
        
        await canal_tickets.send(embed=embed, view=view)
        
        await interaction.response.send_message(
            f"✅ Sistema de tickets configurado exitosamente en {canal_tickets.mention}",
            ephemeral=True
        )

    async def create_ticket(self, guild, user, category, subject, description, priority="media"):
        """Crear un nuevo ticket"""
        try:
            config = self.get_guild_config(guild.id)
            
            if not config["ticket_category"]:
                raise Exception("Sistema de tickets no configurado")
            
            category_channel = guild.get_channel(config["ticket_category"])
            if not category_channel:
                raise Exception("Categoría de tickets no encontrada")
            
            # Verificar si ya tiene ticket abierto
            existing_ticket = await self.get_user_active_ticket(user.id, guild.id)
            if existing_ticket:
                raise Exception(f"Ya tienes un ticket abierto: <#{existing_ticket['channel_id']}>")
            
            # Crear canal del ticket
            ticket_number = len([t for t in self.tickets.values() if t.get('guild_id') == guild.id]) + 1
            channel_name = f"ticket-{ticket_number:04d}-{user.name}"
            
            # Configurar permisos
            overwrites = {
                guild.default_role: PermissionOverwrite(view_channel=False),
                user: PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                )
            }
            
            # Añadir permisos para staff
            if config["staff_role"]:
                staff_role = guild.get_role(config["staff_role"])
                if staff_role:
                    overwrites[staff_role] = PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True,
                        manage_messages=True,
                        attach_files=True,
                        embed_links=True
                    )
            
            # Crear canal
            ticket_channel = await category_channel.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                reason=f"Ticket creado por {user.name}"
            )
            
            # Guardar datos del ticket
            ticket_id = f"{guild.id}_{ticket_channel.id}"
            ticket_data = {
                "id": ticket_id,
                "number": ticket_number,
                "guild_id": guild.id,
                "channel_id": ticket_channel.id,
                "user_id": user.id,
                "user_name": user.display_name,
                "category": category,
                "subject": subject,
                "description": description,
                "priority": priority,
                "status": "open",
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat(),
                "messages": [],
                "staff_assigned": None
            }
            
            self.tickets[ticket_id] = ticket_data
            self.save_tickets()
            
            # Crear embed inicial
            category_info = config["categories"].get(category, config["categories"]["otro"])
            embed = nextcord.Embed(
                title=f"{category_info['emoji']} Ticket #{ticket_number:04d}",
                description=f"**Tipo:** {category_info['name']}\n**Usuario:** {user.mention}\n**Asunto:** {subject}",
                color=self.get_priority_color(priority)
            )
            
            embed.add_field(name="📝 Descripción", value=description, inline=False)
            embed.add_field(name="⏰ Creado", value=f"<t:{int(datetime.datetime.now().timestamp())}:R>", inline=True)
            embed.add_field(name="🔹 Prioridad", value=priority.title(), inline=True)
            embed.add_field(name="📊 Estado", value="Abierto", inline=True)
            
            embed.set_thumbnail(url=user.display_avatar.url)
            embed.set_footer(text=f"ID: {ticket_id}")
            
            # Botones de gestión
            view = TicketManageView(self, ticket_id)
            
            message = await ticket_channel.send(
                content=f"👋 Hola {user.mention}! Tu ticket ha sido creado.",
                embed=embed,
                view=view
            )
            
            # Mensaje de bienvenida
            welcome_embed = nextcord.Embed(
                title="📋 Información del Ticket",
                description="El staff ha sido notificado y te atenderá lo antes posible.",
                color=0x00FF00
            )
            
            welcome_embed.add_field(
                name="⚠️ Importante:",
                value="• Mantén la conversación respetuosa\n• Proporciona toda la información necesaria\n• No hagas spam en el ticket\n• El staff puede tardar en responder",
                inline=False
            )
            
            await ticket_channel.send(embed=welcome_embed)
            
            # Notificar al staff si está configurado
            if category_info.get("staff_ping") and config["staff_role"]:
                staff_role = guild.get_role(config["staff_role"])
                if staff_role:
                    await ticket_channel.send(f"📢 {staff_role.mention} - Nuevo ticket de {category_info['name']}")
            
            # Log en canal de logs
            if config.get("log_channel"):
                log_channel = guild.get_channel(config["log_channel"])
                if log_channel:
                    log_embed = nextcord.Embed(
                        title="🎫 Ticket Creado",
                        description=f"**Usuario:** {user.mention}\n**Canal:** {ticket_channel.mention}\n**Tipo:** {category_info['name']}",
                        color=0x00FF00,
                        timestamp=datetime.datetime.now()
                    )
                    log_embed.add_field(name="Asunto", value=subject, inline=False)
                    await log_channel.send(embed=log_embed)
            
            return ticket_data
            
        except Exception as e:
            logger.error(f"Error creando ticket: {e}")
            raise
    
    def get_priority_color(self, priority):
        """Obtener color según prioridad"""
        colors = {
            "baja": 0x00FF00,
            "media": 0xFFFF00,
            "alta": 0xFF0000
        }
        return colors.get(priority, 0x7289DA)
    
    async def get_user_active_ticket(self, user_id, guild_id):
        """Verificar si el usuario tiene un ticket activo"""
        for ticket in self.tickets.values():
            if (ticket.get('user_id') == user_id and 
                ticket.get('guild_id') == guild_id and 
                ticket.get('status') == 'open'):
                return ticket
        return None
    
    async def close_ticket(self, ticket_id, closed_by, reason="No especificado"):
        """Cerrar un ticket"""
        try:
            if ticket_id not in self.tickets:
                raise Exception("Ticket no encontrado")
            
            ticket = self.tickets[ticket_id]
            ticket["status"] = "closed"
            ticket["closed_by"] = closed_by.id
            ticket["closed_by_name"] = closed_by.display_name
            ticket["closed_at"] = datetime.datetime.now().isoformat()
            ticket["close_reason"] = reason
            
            self.save_tickets()
            
            # Obtener canal
            guild = self.bot.get_guild(ticket["guild_id"])
            if guild:
                channel = guild.get_channel(ticket["channel_id"])
                if channel:
                    # Crear transcript básico
                    transcript = await self.create_transcript(channel)
                    
                    # Mensaje de cierre
                    embed = nextcord.Embed(
                        title="🔒 Ticket Cerrado",
                        description=f"**Cerrado por:** {closed_by.mention}\n**Razón:** {reason}",
                        color=0xFF0000,
                        timestamp=datetime.datetime.now()
                    )
                    
                    await channel.send(embed=embed)
                    
                    # Programar eliminación del canal
                    await asyncio.sleep(30)  # Esperar 30 segundos
                    try:
                        await channel.delete(reason=f"Ticket cerrado por {closed_by.name}")
                    except:
                        pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error cerrando ticket: {e}")
            return False
    
    async def create_transcript(self, channel):
        """Crear transcript básico del ticket"""
        try:
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                if not message.author.bot or message.embeds:
                    msg_data = {
                        "author": message.author.display_name,
                        "content": message.content,
                        "timestamp": message.created_at.isoformat(),
                        "attachments": [att.url for att in message.attachments]
                    }
                    messages.append(msg_data)
            
            return messages
            
        except Exception as e:
            logger.error(f"Error creando transcript: {e}")
            return []

class TicketPanelView(nextcord.ui.View):
    """Panel principal de tickets con categorías"""
    
    def __init__(self, ticket_system):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
    
    @nextcord.ui.select(
        placeholder="Selecciona el tipo de ticket...",
        options=[
            nextcord.SelectOption(label="💡 Soporte General", value="soporte", emoji="💡"),
            nextcord.SelectOption(label="🚨 Reportar Usuario", value="reporte", emoji="🚨"),
            nextcord.SelectOption(label="💭 Sugerencias", value="sugerencia", emoji="💭"),
            nextcord.SelectOption(label="📋 Apelación", value="apelacion", emoji="📋"),
            nextcord.SelectOption(label="❓ Otros", value="otro", emoji="❓")
        ]
    )
    async def select_ticket_type(self, select, interaction):
        category = select.values[0]
        
        # Verificar si ya tiene ticket abierto
        existing_ticket = await self.ticket_system.get_user_active_ticket(interaction.user.id, interaction.guild.id)
        if existing_ticket:
            await interaction.response.send_message(
                f"❌ Ya tienes un ticket abierto: <#{existing_ticket['channel_id']}>",
                ephemeral=True
            )
            return
        
        # Abrir modal específico para la categoría
        modal = TicketCreationModal(self.ticket_system, category)
        await interaction.response.send_modal(modal)

class TicketCreationModal(nextcord.ui.Modal):
    """Modal para crear ticket con categoría específica"""
    
    def __init__(self, ticket_system, category):
        self.ticket_system = ticket_system
        self.category = category
        
        # Títulos específicos por categoría
        titles = {
            "soporte": "Solicitar Soporte",
            "reporte": "Reportar Usuario",
            "sugerencia": "Enviar Sugerencia",
            "apelacion": "Solicitar Apelación",
            "otro": "Crear Ticket"
        }
        
        super().__init__(title=titles.get(category, "Crear Ticket"))
        
        # Campos específicos por categoría
        if category == "reporte":
            self.subject_input = nextcord.ui.TextInput(
                label="Usuario a reportar",
                placeholder="@usuario o ID del usuario",
                max_length=100,
                required=True
            )
            self.description_input = nextcord.ui.TextInput(
                label="Descripción del problema",
                placeholder="Describe qué hizo mal el usuario...",
                style=nextcord.TextInputStyle.paragraph,
                max_length=1000,
                required=True
            )
        elif category == "sugerencia":
            self.subject_input = nextcord.ui.TextInput(
                label="Título de la sugerencia",
                placeholder="Breve título de tu sugerencia",
                max_length=100,
                required=True
            )
            self.description_input = nextcord.ui.TextInput(
                label="Descripción detallada",
                placeholder="Explica tu sugerencia en detalle...",
                style=nextcord.TextInputStyle.paragraph,
                max_length=1000,
                required=True
            )
        elif category == "apelacion":
            self.subject_input = nextcord.ui.TextInput(
                label="Tipo de sanción",
                placeholder="Ban, kick, mute, warning...",
                max_length=100,
                required=True
            )
            self.description_input = nextcord.ui.TextInput(
                label="Razón de la apelación",
                placeholder="Explica por qué consideras injusta la sanción...",
                style=nextcord.TextInputStyle.paragraph,
                max_length=1000,
                required=True
            )
        else:
            self.subject_input = nextcord.ui.TextInput(
                label="Asunto",
                placeholder="Describe brevemente tu consulta...",
                max_length=100,
                required=True
            )
            self.description_input = nextcord.ui.TextInput(
                label="Descripción detallada",
                placeholder="Explica tu problema con detalle...",
                style=nextcord.TextInputStyle.paragraph,
                max_length=1000,
                required=True
            )
        
        self.add_item(self.subject_input)
        self.add_item(self.description_input)
        
        # Campo de prioridad solo para ciertos tipos
        if category in ["soporte", "reporte", "apelacion"]:
            self.priority_input = nextcord.ui.TextInput(
                label="Prioridad (baja/media/alta)",
                placeholder="media",
                max_length=10,
                required=False
            )
            self.add_item(self.priority_input)
    
    async def callback(self, interaction: nextcord.Interaction):
        try:
            subject = self.subject_input.value.strip()
            description = self.description_input.value.strip()
            priority = getattr(self, 'priority_input', None)
            priority = priority.value.strip().lower() if priority else "media"
            
            if priority not in ["baja", "media", "alta"]:
                priority = "media"
            
            # Crear ticket
            ticket_data = await self.ticket_system.create_ticket(
                interaction.guild,
                interaction.user,
                self.category,
                subject,
                description,
                priority
            )
            
            await interaction.response.send_message(
                f"✅ Ticket creado exitosamente: <#{ticket_data['channel_id']}>",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error en callback del modal: {e}")
            await interaction.response.send_message(f"❌ Error al crear ticket: {str(e)}", ephemeral=True)

class TicketManageView(nextcord.ui.View):
    """Botones de gestión del ticket"""
    
    def __init__(self, ticket_system, ticket_id):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
    
    @nextcord.ui.button(label="🔒 Cerrar Ticket", style=nextcord.ButtonStyle.danger)
    async def close_ticket(self, button, interaction):
        # Verificar permisos
        config = self.ticket_system.get_guild_config(interaction.guild.id)
        has_permission = False
        
        if interaction.user.guild_permissions.manage_channels:
            has_permission = True
        elif config.get("staff_role"):
            staff_role = interaction.guild.get_role(config["staff_role"])
            if staff_role and staff_role in interaction.user.roles:
                has_permission = True
        
        # También permitir al creador del ticket
        if self.ticket_id in self.ticket_system.tickets:
            ticket = self.ticket_system.tickets[self.ticket_id]
            if ticket.get("user_id") == interaction.user.id:
                has_permission = True
        
        if not has_permission:
            await interaction.response.send_message("❌ No tienes permisos para cerrar este ticket.", ephemeral=True)
            return
        
        # Modal para razón de cierre
        modal = CloseTicketModal(self.ticket_system, self.ticket_id)
        await interaction.response.send_modal(modal)
    
    @nextcord.ui.button(label="📋 Transcript", style=nextcord.ButtonStyle.secondary)
    async def create_transcript(self, button, interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            transcript = await self.ticket_system.create_transcript(interaction.channel)
            
            # Crear archivo de transcript
            transcript_text = f"TRANSCRIPT - TICKET {self.ticket_id}\n"
            transcript_text += f"Generado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            transcript_text += "=" * 50 + "\n\n"
            
            for msg in transcript:
                transcript_text += f"[{msg['timestamp']}] {msg['author']}: {msg['content']}\n"
                if msg['attachments']:
                    transcript_text += f"  Archivos: {', '.join(msg['attachments'])}\n"
                transcript_text += "\n"
            
            # Enviar como archivo
            file = nextcord.File(
                fp=bytes(transcript_text, 'utf-8'),
                filename=f"transcript_{self.ticket_id}.txt"
            )
            
            await interaction.followup.send("📋 Transcript generado:", file=file, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error generando transcript: {e}")
            await interaction.followup.send("❌ Error generando transcript.", ephemeral=True)

class CloseTicketModal(nextcord.ui.Modal):
    """Modal para cerrar ticket con razón"""
    
    def __init__(self, ticket_system, ticket_id):
        super().__init__(title="Cerrar Ticket")
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
        
        self.reason_input = nextcord.ui.TextInput(
            label="Razón de cierre",
            placeholder="¿Por qué se cierra este ticket?",
            max_length=500,
            required=False,
            default="Resuelto"
        )
        self.add_item(self.reason_input)
    
    async def callback(self, interaction: nextcord.Interaction):
        reason = self.reason_input.value.strip() or "No especificado"
        
        success = await self.ticket_system.close_ticket(self.ticket_id, interaction.user, reason)
        
        if success:
            await interaction.response.send_message(
                f"✅ Ticket cerrado. Razón: {reason}\nEste canal se eliminará en 30 segundos.",
                ephemeral=False
            )
        else:
            await interaction.response.send_message("❌ Error al cerrar el ticket.", ephemeral=True)

def setup(bot):
    """Función setup para cargar el cog"""
    return AdvancedTicketSystem(bot)
