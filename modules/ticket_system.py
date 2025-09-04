"""
sistema de tickets con integración web
por davito
"""

import json
import logging
import asyncio
import aiohttp
import datetime
from typing import Dict, List, Optional
import nextcord
from nextcord.ext import commands

logger = logging.getLogger(__name__)

class TicketCreateView(nextcord.ui.View):
    """vista para crear tickets"""
    
    def __init__(self, ticket_system):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
    
    @nextcord.ui.button(label="🎫 crear ticket", style=nextcord.ButtonStyle.primary, emoji="🎫")
    async def create_ticket(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """crear nuevo ticket"""
        try:
            # verificar si ya tiene ticket abierto
            existing_ticket = await self.ticket_system.get_user_active_ticket(interaction.user.id, interaction.guild.id)
            if existing_ticket:
                await interaction.response.send_message(
                    f"❌ ya tienes un ticket abierto: <#{existing_ticket['channel_id']}>",
                    ephemeral=True
                )
                return
            
            # crear modal para solicitar información
            modal = TicketModal(self.ticket_system)
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            logger.error(f"error creando ticket: {e}")
            await interaction.response.send_message("❌ error al crear ticket.", ephemeral=True)

class TicketModal(nextcord.ui.Modal):
    """modal para crear ticket"""
    
    def __init__(self, ticket_system):
        super().__init__(title="crear nuevo ticket")
        self.ticket_system = ticket_system
        
        self.subject_input = nextcord.ui.TextInput(
            label="asunto",
            placeholder="describe brevemente tu problema...",
            max_length=100,
            required=True
        )
        self.add_item(self.subject_input)
        
        self.description_input = nextcord.ui.TextInput(
            label="descripción detallada",
            placeholder="explica tu problema con detalle...",
            style=nextcord.TextInputStyle.paragraph,
            max_length=1000,
            required=True
        )
        self.add_item(self.description_input)
        
        self.priority_input = nextcord.ui.TextInput(
            label="prioridad (baja/media/alta)",
            placeholder="baja",
            max_length=10,
            required=False
        )
        self.add_item(self.priority_input)
    
    async def callback(self, interaction: nextcord.Interaction):
        try:
            subject = self.subject_input.value.strip()
            description = self.description_input.value.strip()
            priority = self.priority_input.value.strip().lower() or "baja"
            
            if priority not in ["baja", "media", "alta"]:
                priority = "baja"
            
            # crear ticket
            ticket_data = await self.ticket_system.create_ticket(
                interaction.guild,
                interaction.user,
                subject,
                description,
                priority
            )
            
            await interaction.response.send_message(
                f"✅ ticket creado exitosamente: <#{ticket_data['channel_id']}>",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"error en callback ticket modal: {e}")
            await interaction.response.send_message("❌ error al crear ticket.", ephemeral=True)

class TicketControlView(nextcord.ui.View):
    """vista de control para tickets"""
    
    def __init__(self, ticket_system, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
    
    @nextcord.ui.button(label="🔒 cerrar", style=nextcord.ButtonStyle.danger)
    async def close_ticket(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """cerrar ticket"""
        try:
            # verificar permisos
            if not (interaction.user.guild_permissions.manage_channels or 
                   await self.ticket_system.is_ticket_owner(self.ticket_id, interaction.user.id)):
                await interaction.response.send_message("❌ no tienes permisos para cerrar este ticket.", ephemeral=True)
                return
            
            # confirmar cierre
            confirm_view = ConfirmCloseView(self.ticket_system, self.ticket_id)
            
            embed = nextcord.Embed(
                title="⚠️ confirmar cierre",
                description="¿estás seguro de que quieres cerrar este ticket?",
                color=nextcord.Color.orange()
            )
            
            await interaction.response.send_message(embed=embed, view=confirm_view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"error cerrando ticket: {e}")
            await interaction.response.send_message("❌ error al cerrar ticket.", ephemeral=True)
    
    @nextcord.ui.button(label="📊 estado", style=nextcord.ButtonStyle.secondary)
    async def ticket_status(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """mostrar estado del ticket"""
        try:
            ticket_data = await self.ticket_system.get_ticket_data(self.ticket_id)
            if not ticket_data:
                await interaction.response.send_message("❌ ticket no encontrado.", ephemeral=True)
                return
            
            embed = nextcord.Embed(
                title="📊 información del ticket",
                color=nextcord.Color.blue()
            )
            
            embed.add_field(name="🆔 id", value=ticket_data['id'], inline=True)
            embed.add_field(name="👤 usuario", value=f"<@{ticket_data['user_id']}>", inline=True)
            embed.add_field(name="📋 asunto", value=ticket_data['subject'], inline=True)
            embed.add_field(name="⚡ prioridad", value=ticket_data['priority'], inline=True)
            embed.add_field(name="📅 creado", value=f"<t:{int(ticket_data['created_at'])}:R>", inline=True)
            embed.add_field(name="🔗 web", value=f"[ver en dashboard]({self.ticket_system.get_web_url(ticket_data['id'])})", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"error mostrando estado ticket: {e}")
            await interaction.response.send_message("❌ error al obtener estado.", ephemeral=True)
    
    @nextcord.ui.button(label="🏷️ asignar", style=nextcord.ButtonStyle.primary)
    async def assign_ticket(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """asignar ticket a staff"""
        try:
            if not interaction.user.guild_permissions.manage_channels:
                await interaction.response.send_message("❌ no tienes permisos para asignar tickets.", ephemeral=True)
                return
            
            modal = AssignModal(self.ticket_system, self.ticket_id)
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            logger.error(f"error asignando ticket: {e}")
            await interaction.response.send_message("❌ error al asignar ticket.", ephemeral=True)

class ConfirmCloseView(nextcord.ui.View):
    """vista de confirmación para cerrar ticket"""
    
    def __init__(self, ticket_system, ticket_id: str):
        super().__init__(timeout=30)
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
    
    @nextcord.ui.button(label="✅ sí, cerrar", style=nextcord.ButtonStyle.danger)
    async def confirm_close(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """confirmar cierre del ticket"""
        try:
            await self.ticket_system.close_ticket(self.ticket_id, interaction.user.id, "cerrado por usuario")
            await interaction.response.send_message("✅ ticket cerrado exitosamente.", ephemeral=True)
            
        except Exception as e:
            logger.error(f"error confirmando cierre: {e}")
            await interaction.response.send_message("❌ error al cerrar ticket.", ephemeral=True)
    
    @nextcord.ui.button(label="❌ cancelar", style=nextcord.ButtonStyle.secondary)
    async def cancel_close(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """cancelar cierre"""
        await interaction.response.send_message("❌ cierre cancelado.", ephemeral=True)

class AssignModal(nextcord.ui.Modal):
    """modal para asignar ticket"""
    
    def __init__(self, ticket_system, ticket_id: str):
        super().__init__(title="asignar ticket")
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
        
        self.staff_input = nextcord.ui.TextInput(
            label="miembro del staff",
            placeholder="@usuario o id del usuario",
            max_length=50,
            required=True
        )
        self.add_item(self.staff_input)
    
    async def callback(self, interaction: nextcord.Interaction):
        try:
            staff_mention = self.staff_input.value.strip()
            
            # obtener usuario
            if staff_mention.startswith('<@') and staff_mention.endswith('>'):
                user_id = int(staff_mention[2:-1].replace('!', ''))
            else:
                user_id = int(staff_mention)
            
            staff_member = interaction.guild.get_member(user_id)
            if not staff_member:
                await interaction.response.send_message("❌ miembro no encontrado.", ephemeral=True)
                return
            
            # asignar ticket
            await self.ticket_system.assign_ticket(self.ticket_id, staff_member.id)
            
            await interaction.response.send_message(
                f"✅ ticket asignado a {staff_member.mention}",
                ephemeral=True
            )
            
        except ValueError:
            await interaction.response.send_message("❌ id de usuario inválido.", ephemeral=True)
        except Exception as e:
            logger.error(f"error asignando ticket: {e}")
            await interaction.response.send_message("❌ error al asignar ticket.", ephemeral=True)

class TicketSystem(commands.Cog):
    """sistema de tickets con integración web"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/tickets_config.json"
        self.tickets_file = "data/tickets.json"
        self.guild_configs: Dict[int, dict] = {}
        self.tickets: Dict[str, dict] = {}
        self.web_api_url = "https://dashboard.davito.es/api"  # tu url de api
        self.web_dashboard_url = "https://dashboard.davito.es"
        
        # cargar datos
        self.load_config()
        self.load_tickets()
    
    def load_config(self):
        """cargar configuración"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.guild_configs = {int(k): v for k, v in data.items()}
        except FileNotFoundError:
            self.guild_configs = {}
        except Exception as e:
            logger.error(f"error cargando config tickets: {e}")
            self.guild_configs = {}
    
    def save_config(self):
        """guardar configuración"""
        try:
            import os
            os.makedirs("data", exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.guild_configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando config tickets: {e}")
    
    def load_tickets(self):
        """cargar tickets"""
        try:
            with open(self.tickets_file, 'r', encoding='utf-8') as f:
                self.tickets = json.load(f)
        except FileNotFoundError:
            self.tickets = {}
        except Exception as e:
            logger.error(f"error cargando tickets: {e}")
            self.tickets = {}
    
    def save_tickets(self):
        """guardar tickets"""
        try:
            import os
            os.makedirs("data", exist_ok=True)
            with open(self.tickets_file, 'w', encoding='utf-8') as f:
                json.dump(self.tickets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando tickets: {e}")
    
    def get_web_url(self, ticket_id: str) -> str:
        """obtener url web del ticket"""
        return f"{self.web_dashboard_url}/tickets/{ticket_id}"
    
    async def sync_to_web(self, ticket_data: dict):
        """sincronizar ticket con la web"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.bot.config.get('web_api_token', '')}"
                }
                
                async with session.post(
                    f"{self.web_api_url}/tickets",
                    json=ticket_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        logger.info(f"ticket {ticket_data['id']} sincronizado con web")
                    else:
                        logger.warning(f"error sincronizando ticket: {response.status}")
                        
        except Exception as e:
            logger.error(f"error sincronizando con web: {e}")
    
    @commands.command(name='ticketsetup')
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx, category: nextcord.CategoryChannel = None):
        """
        configurar sistema de tickets
        uso: !ticketsetup [categoría]
        """
        try:
            if not category:
                await ctx.send("❌ debes especificar una categoría. uso: `!ticketsetup [categoría]`")
                return
            
            # configurar guild
            self.guild_configs[ctx.guild.id] = {
                'category_id': category.id,
                'staff_role_id': None,
                'log_channel_id': None,
                'enabled': True
            }
            
            self.save_config()
            
            # crear embed con botón
            embed = nextcord.Embed(
                title="🎫 sistema de tickets",
                description="haz clic en el botón de abajo para crear un nuevo ticket de soporte.",
                color=nextcord.Color.blue()
            )
            embed.add_field(
                name="📋 información",
                value="• describe tu problema claramente\n• incluye toda la información relevante\n• sé paciente, te responderemos pronto",
                inline=False
            )
            embed.set_footer(text="sistema de tickets por davito")
            
            view = TicketCreateView(self)
            
            await ctx.send(embed=embed, view=view)
            
            # mensaje de confirmación
            config_embed = nextcord.Embed(
                title="✅ sistema de tickets configurado",
                description=f"categoría: {category.mention}",
                color=nextcord.Color.green()
            )
            
            await ctx.send(embed=config_embed)
            logger.info(f"sistema de tickets configurado en {ctx.guild.name}")
            
        except Exception as e:
            logger.error(f"error configurando tickets: {e}")
            await ctx.send("❌ error al configurar sistema de tickets.")
    
    async def create_ticket(self, guild, user, subject: str, description: str, priority: str = "baja"):
        """crear nuevo ticket"""
        try:
            guild_config = self.guild_configs.get(guild.id)
            if not guild_config or not guild_config.get('enabled'):
                raise Exception("sistema de tickets no configurado")
            
            # generar id único
            ticket_id = f"ticket-{guild.id}-{user.id}-{int(datetime.datetime.now().timestamp())}"
            
            # obtener categoría
            category = guild.get_channel(guild_config['category_id'])
            if not category:
                raise Exception("categoría de tickets no encontrada")
            
            # crear canal
            channel_name = f"ticket-{user.display_name}".lower().replace(" ", "-")
            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                reason=f"ticket creado por {user}"
            )
            
            # configurar permisos
            await channel.set_permissions(guild.default_role, read_messages=False)
            await channel.set_permissions(user, read_messages=True, send_messages=True)
            
            # crear datos del ticket
            ticket_data = {
                'id': ticket_id,
                'guild_id': guild.id,
                'channel_id': channel.id,
                'user_id': user.id,
                'subject': subject,
                'description': description,
                'priority': priority,
                'status': 'abierto',
                'assigned_to': None,
                'created_at': datetime.datetime.now().timestamp(),
                'closed_at': None,
                'closed_by': None,
                'close_reason': None
            }
            
            # guardar ticket
            self.tickets[ticket_id] = ticket_data
            self.save_tickets()
            
            # enviar mensaje inicial
            embed = nextcord.Embed(
                title="🎫 nuevo ticket",
                description=f"**asunto:** {subject}",
                color=nextcord.Color.blue()
            )
            embed.add_field(name="👤 usuario", value=user.mention, inline=True)
            embed.add_field(name="⚡ prioridad", value=priority, inline=True)
            embed.add_field(name="🆔 id", value=ticket_id, inline=True)
            embed.add_field(name="📝 descripción", value=description, inline=False)
            embed.add_field(name="🔗 dashboard", value=f"[ver en web]({self.get_web_url(ticket_id)})", inline=False)
            
            view = TicketControlView(self, ticket_id)
            
            await channel.send(f"¡hola {user.mention}! tu ticket ha sido creado.", embed=embed, view=view)
            
            # sincronizar con web
            await self.sync_to_web(ticket_data)
            
            logger.info(f"ticket creado: {ticket_id} por {user}")
            return ticket_data
            
        except Exception as e:
            logger.error(f"error creando ticket: {e}")
            raise
    
    async def close_ticket(self, ticket_id: str, closed_by_id: int, reason: str = "cerrado"):
        """cerrar ticket"""
        try:
            ticket_data = self.tickets.get(ticket_id)
            if not ticket_data:
                raise Exception("ticket no encontrado")
            
            # actualizar datos
            ticket_data['status'] = 'cerrado'
            ticket_data['closed_at'] = datetime.datetime.now().timestamp()
            ticket_data['closed_by'] = closed_by_id
            ticket_data['close_reason'] = reason
            
            # obtener canal
            guild = self.bot.get_guild(ticket_data['guild_id'])
            channel = guild.get_channel(ticket_data['channel_id'])
            
            if channel:
                # mensaje de cierre
                embed = nextcord.Embed(
                    title="🔒 ticket cerrado",
                    description=f"este ticket ha sido cerrado por <@{closed_by_id}>",
                    color=nextcord.Color.red()
                )
                embed.add_field(name="motivo", value=reason, inline=False)
                embed.add_field(name="cerrado en", value=f"<t:{int(ticket_data['closed_at'])}:f>", inline=False)
                
                await channel.send(embed=embed)
                
                # eliminar canal después de 5 segundos
                await asyncio.sleep(5)
                await channel.delete(reason="ticket cerrado")
            
            # guardar cambios
            self.save_tickets()
            
            # sincronizar con web
            await self.sync_to_web(ticket_data)
            
            logger.info(f"ticket cerrado: {ticket_id}")
            
        except Exception as e:
            logger.error(f"error cerrando ticket: {e}")
            raise
    
    async def get_user_active_ticket(self, user_id: int, guild_id: int) -> Optional[dict]:
        """obtener ticket activo de usuario"""
        for ticket_data in self.tickets.values():
            if (ticket_data['user_id'] == user_id and 
                ticket_data['guild_id'] == guild_id and 
                ticket_data['status'] == 'abierto'):
                return ticket_data
        return None
    
    async def get_ticket_data(self, ticket_id: str) -> Optional[dict]:
        """obtener datos de ticket"""
        return self.tickets.get(ticket_id)
    
    async def is_ticket_owner(self, ticket_id: str, user_id: int) -> bool:
        """verificar si usuario es dueño del ticket"""
        ticket_data = self.tickets.get(ticket_id)
        return ticket_data and ticket_data['user_id'] == user_id
    
    async def assign_ticket(self, ticket_id: str, staff_id: int):
        """asignar ticket a staff"""
        try:
            ticket_data = self.tickets.get(ticket_id)
            if not ticket_data:
                raise Exception("ticket no encontrado")
            
            ticket_data['assigned_to'] = staff_id
            self.save_tickets()
            
            # enviar mensaje en canal
            guild = self.bot.get_guild(ticket_data['guild_id'])
            channel = guild.get_channel(ticket_data['channel_id'])
            
            if channel:
                embed = nextcord.Embed(
                    title="🏷️ ticket asignado",
                    description=f"ticket asignado a <@{staff_id}>",
                    color=nextcord.Color.green()
                )
                await channel.send(embed=embed)
            
            # sincronizar con web
            await self.sync_to_web(ticket_data)
            
            logger.info(f"ticket {ticket_id} asignado a {staff_id}")
            
        except Exception as e:
            logger.error(f"error asignando ticket: {e}")
            raise

def setup(bot):
    """función para cargar el cog"""
    return TicketSystem(bot)
