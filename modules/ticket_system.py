"""
Sistema de tickets mejorado con transcripciones y verificación
Incluye: Creación de tickets, transcripciones automáticas, canal de logs
Por davito - DaBot v2
"""

import json
import logging
import sqlite3
import nextcord
from nextcord.ext import commands
from typing import Dict, Optional, List
import os
import asyncio
import io
from datetime import datetime

logger = logging.getLogger(__name__)

class TicketDB:
    """manejo de base de datos para tickets mejorado"""
    
    def __init__(self, db_path: str = "data/tickets.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """inicializar base de datos con nuevas funcionalidades"""
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
                        closed_at TIMESTAMP,
                        transcript_saved BOOLEAN DEFAULT FALSE,
                        transcript_url TEXT
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS ticket_config (
                        guild_id INTEGER PRIMARY KEY,
                        category_id INTEGER,
                        support_role_id INTEGER,
                        log_channel_id INTEGER,
                        transcript_channel_id INTEGER,
                        verification_channel_id INTEGER,
                        verification_role_id INTEGER
                    )
                ''')
                
                # Nueva tabla para mensajes de transcripción
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS ticket_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER,
                        user_id INTEGER,
                        username TEXT,
                        message_content TEXT,
                        timestamp TIMESTAMP,
                        FOREIGN KEY (ticket_id) REFERENCES tickets (id)
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            logger.error(f"error inicializando base de datos de tickets: {e}")
    
    def create_ticket(self, guild_id: int, channel_id: int, user_id: int, reason: str = None):
        """crear nuevo ticket con numeración automática"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Obtener el próximo número de ticket para este servidor
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM tickets WHERE guild_id = ?",
                    (guild_id,)
                )
                ticket_number = cursor.fetchone()[0] + 1
                
                cursor = conn.execute(
                    "INSERT INTO tickets (guild_id, channel_id, user_id, reason) VALUES (?, ?, ?, ?)",
                    (guild_id, channel_id, user_id, reason)
                )
                conn.commit()
                return ticket_number  # Retornar número de ticket en lugar de ID
        except Exception as e:
            logger.error(f"error creando ticket: {e}")
            return None
    
    def add_message_to_transcript(self, ticket_id: int, user_id: int, username: str, content: str):
        """agregar mensaje a la transcripción"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO ticket_messages (ticket_id, user_id, username, message_content, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (ticket_id, user_id, username, content, datetime.now().isoformat())
                )
                conn.commit()
        except Exception as e:
            logger.error(f"error agregando mensaje a transcripción: {e}")
    
    def get_ticket_transcript(self, ticket_id: int) -> List[dict]:
        """obtener transcripción completa del ticket"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT username, message_content, timestamp FROM ticket_messages WHERE ticket_id = ? ORDER BY timestamp",
                    (ticket_id,)
                )
                messages = cursor.fetchall()
                return [
                    {
                        "username": msg[0],
                        "content": msg[1],
                        "timestamp": msg[2]
                    } for msg in messages
                ]
        except Exception as e:
            logger.error(f"error obteniendo transcripción: {e}")
            return []
    
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
    
    def set_config(self, guild_id: int, category_id: int = None, support_role_id: int = None, 
                   log_channel_id: int = None, transcript_channel_id: int = None, 
                   verification_channel_id: int = None, verification_role_id: int = None):
        """configurar servidor con nuevas opciones"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO ticket_config 
                    (guild_id, category_id, support_role_id, log_channel_id, transcript_channel_id, verification_channel_id, verification_role_id) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (guild_id, category_id, support_role_id, log_channel_id, transcript_channel_id, verification_channel_id, verification_role_id))
                conn.commit()
        except Exception as e:
            logger.error(f"error configurando servidor: {e}")

# Sistema de verificación mejorado
class VerificationView(nextcord.ui.View):
    """vista de verificación anti-bots"""
    
    def __init__(self, ticket_cog):
        super().__init__(timeout=None)
        self.ticket_cog = ticket_cog
    
    @nextcord.ui.button(label="✅ Verificarme", style=nextcord.ButtonStyle.success, 
                       custom_id="verify_user", emoji="🛡️")
    async def verify_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """verificar usuario"""
        await self.ticket_cog.verify_user_interaction(interaction)

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
    """vista de control mejorada para tickets activos"""
    
    def __init__(self, ticket_cog):
        super().__init__(timeout=None)
        self.ticket_cog = ticket_cog
    
    def is_staff(self, member, guild):
        """verificar si el usuario es staff (moderador, admin o owner)"""
        if member.guild_permissions.administrator:
            return True
        if member.id == guild.owner_id:
            return True
        
        # Verificar roles de staff comunes
        staff_role_names = ['staff', 'moderador', 'moderadora', 'mod', 'admin', 'administrador', 'administrator', 'helper', 'ayudante']
        for role in member.roles:
            if any(staff_name in role.name.lower() for staff_name in staff_role_names):
                return True
        
        # Verificar permisos específicos de moderación
        if (member.guild_permissions.manage_messages or 
            member.guild_permissions.kick_members or 
            member.guild_permissions.ban_members or
            member.guild_permissions.manage_roles):
            return True
            
        return False
    
    @nextcord.ui.button(label="🔒 Cerrar Ticket", style=nextcord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """cerrar ticket con transcripción automática - SOLO STAFF"""
        
        # Verificar si es staff
        if not self.is_staff(interaction.user, interaction.guild):
            embed = nextcord.Embed(
                title="❌ Sin Permisos",
                description="🚫 **Solo el staff puede cerrar tickets**\n\n👮 Roles con permisos:\n• Administradores\n• Moderadores\n• Usuarios con permisos de moderación",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await self.ticket_cog.close_ticket_interaction(interaction)
    
    @nextcord.ui.button(label="👥 Agregar Usuario", style=nextcord.ButtonStyle.primary, custom_id="add_user")
    async def add_user(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """agregar usuario al ticket - SOLO STAFF"""
        
        # Verificar si es staff
        if not self.is_staff(interaction.user, interaction.guild):
            embed = nextcord.Embed(
                title="❌ Sin Permisos",
                description="🚫 **Solo el staff puede agregar usuarios a tickets**",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await self.ticket_cog.add_user_to_ticket(interaction)

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
    
    @ticket_group.subcommand(name="setup", description="configurar sistema completo de tickets y verificación")
    async def setup_tickets_command(self, interaction: nextcord.Interaction):
        """configurar sistema completo de tickets y verificación - comando slash"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Necesitas permisos de gestionar servidor.", ephemeral=True)
            return
        
        await interaction.response.defer()
        await self.setup_tickets(interaction)
    
    async def setup_tickets(self, interaction: nextcord.Interaction, tickets_channel=None, transcript_channel=None):
        """configurar sistema de tickets con canales específicos o crear nuevos"""
        try:
            guild = interaction.guild
            
            # 1. Crear categoría para tickets si no se proporcionan canales
            if not tickets_channel:
                category = await guild.create_category("🎫 TICKETS")
            else:
                category = tickets_channel.category
            
            # 2. Crear rol de soporte
            support_role = nextcord.utils.get(guild.roles, name="🛠️ Soporte")
            if not support_role:
                support_role = await guild.create_role(
                    name="🛠️ Soporte", 
                    color=nextcord.Color.blue(),
                    permissions=nextcord.Permissions(
                        manage_channels=True,
                        manage_messages=True,
                        read_message_history=True
                    )
                )
            
            # 3. Crear rol de verificado
            verified_role = nextcord.utils.get(guild.roles, name="✅ Verificado")
            if not verified_role:
                verified_role = await guild.create_role(
                    name="✅ Verificado", 
                    color=nextcord.Color.green()
                )
            
            # 4. Usar canales proporcionados o crear nuevos
            # Canal de logs de tickets
            if not tickets_channel:
                log_channel = nextcord.utils.get(guild.text_channels, name="📋-ticket-logs")
                if not log_channel:
                    log_channel = await guild.create_text_channel(
                        "📋-ticket-logs", 
                        category=category,
                        overwrites={
                            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                            support_role: nextcord.PermissionOverwrite(read_messages=True)
                        }
                    )
            else:
                log_channel = tickets_channel
            
            # Canal de transcripciones
            if not transcript_channel:
                transcript_channel = nextcord.utils.get(guild.text_channels, name="📝-transcripciones")
                if not transcript_channel:
                    transcript_channel = await guild.create_text_channel(
                        "📝-transcripciones", 
                        category=category,
                        overwrites={
                            guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                            support_role: nextcord.PermissionOverwrite(read_messages=True)
                        }
                    )
            
            # Canal de verificación
            verification_channel = nextcord.utils.get(guild.text_channels, name="🛡️-verificación")
            if not verification_channel:
                verification_channel = await guild.create_text_channel(
                    "🛡️-verificación",
                    overwrites={
                        guild.default_role: nextcord.PermissionOverwrite(read_messages=True, send_messages=False),
                        verified_role: nextcord.PermissionOverwrite(read_messages=False)
                    }
                )
            
            # 5. Guardar configuración completa
            self.db.set_config(
                guild.id, 
                category.id, 
                support_role.id, 
                log_channel.id,
                transcript_channel.id,
                verification_channel.id,
                verified_role.id
            )
            
            # 6. Crear panel de tickets en el canal proporcionado o canal existente
            tickets_embed = nextcord.Embed(
                title="🎫 Sistema de Tickets",
                description="¿Necesitas ayuda? Crea un ticket de soporte haciendo clic en el botón.",
                color=nextcord.Color.blue()
            )
            tickets_embed.add_field(
                name="📋 ¿Cómo funciona?",
                value="• Haz clic en **🎫 Crear Ticket**\n• Describe tu problema detalladamente\n• El staff te ayudará lo antes posible\n• Al finalizar, se guardará la transcripción",
                inline=False
            )
            tickets_embed.add_field(
                name="⚙️ Características",
                value="• Transcripciones automáticas\n• Logs de actividad\n• Gestión avanzada de permisos\n• Soporte multiplataforma",
                inline=False
            )
            
            tickets_view = TicketView(self)
            
            # Enviar panel al canal correcto
            target_channel = tickets_channel or log_channel
            await target_channel.send(embed=tickets_embed, view=tickets_view)
            
            # 7. Crear panel de verificación
            verification_embed = nextcord.Embed(
                title="🛡️ Verificación de Usuario",
                description="Para acceder al servidor completo, debes verificarte como usuario real.",
                color=nextcord.Color.green()
            )
            verification_embed.add_field(
                name="🤖 ¿Por qué verificarse?",
                value="• Prevenir bots maliciosos\n• Proteger la comunidad\n• Acceso a todos los canales\n• Participar en eventos",
                inline=False
            )
            verification_embed.add_field(
                name="✅ Beneficios de la verificación",
                value="• Acceso completo al servidor\n• Rol de **Verificado**\n• Participación en chat\n• Acceso a canales especiales",
                inline=False
            )
            verification_embed.set_footer(text="Solo usuarios reales pueden verificarse")
            
            verification_view = VerificationView(self)
            await verification_channel.send(embed=verification_embed, view=verification_view)
            
            # 8. Configurar permisos del servidor para usuarios no verificados
            await self.setup_verification_permissions(guild, verified_role)
            
            # 9. Mensaje de confirmación (solo si es comando directo)
            if not tickets_channel:  # Solo mostrar si es setup completo
                setup_embed = nextcord.Embed(
                    title="✅ Sistema Configurado Exitosamente",
                    description="Se ha configurado todo el sistema de tickets y verificación.",
                    color=nextcord.Color.green()
                )
                setup_embed.add_field(
                    name="🎫 Tickets",
                    value=f"• Categoría: {category.mention}\n• Logs: {log_channel.mention}\n• Transcripciones: {transcript_channel.mention}",
                    inline=False
                )
                setup_embed.add_field(
                    name="🛡️ Verificación",
                    value=f"• Canal: {verification_channel.mention}\n• Rol verificado: {verified_role.mention}",
                    inline=False
                )
                setup_embed.add_field(
                    name="🛠️ Staff",
                    value=f"• Rol de soporte: {support_role.mention}",
                    inline=False
                )
                
                await interaction.followup.send(embed=setup_embed)
            
            logger.info(f"Sistema de tickets configurado en {guild.name}")
            
        except Exception as e:
            logger.error(f"Error configurando sistema de tickets: {e}")
            if not tickets_channel:  # Solo mostrar error si es comando directo
                await interaction.followup.send("❌ Error al configurar el sistema de tickets.")
    
    async def setup_verification(self, verification_channel):
        """configurar solo el sistema de verificación en un canal específico"""
        try:
            guild = verification_channel.guild
            
            # Obtener o crear rol verificado
            verified_role = nextcord.utils.get(guild.roles, name="✅ Verificado")
            if not verified_role:
                verified_role = await guild.create_role(
                    name="✅ Verificado", 
                    color=nextcord.Color.green()
                )
            
            # Configurar permisos del canal
            await verification_channel.set_permissions(
                guild.default_role, 
                read_messages=True, 
                send_messages=False
            )
            await verification_channel.set_permissions(
                verified_role, 
                read_messages=False
            )
            
            # Crear panel de verificación
            verification_embed = nextcord.Embed(
                title="🛡️ Verificación de Usuario",
                description="Para acceder al servidor completo, debes verificarte como usuario real.",
                color=nextcord.Color.green()
            )
            verification_embed.add_field(
                name="🤖 ¿Por qué verificarse?",
                value="• Prevenir bots maliciosos\n• Proteger la comunidad\n• Acceso a todos los canales\n• Participar en eventos",
                inline=False
            )
            verification_embed.add_field(
                name="✅ Beneficios de la verificación",
                value="• Acceso completo al servidor\n• Rol de **Verificado**\n• Participación en chat\n• Acceso a canales especiales",
                inline=False
            )
            verification_embed.set_footer(text="Solo usuarios reales pueden verificarse")
            
            verification_view = VerificationView(self)
            await verification_channel.send(embed=verification_embed, view=verification_view)
            
            # Configurar permisos del servidor
            await self.setup_verification_permissions(guild, verified_role)
            
            logger.info(f"Sistema de verificación configurado en {guild.name}")
            
        except Exception as e:
            logger.error(f"Error configurando verificación: {e}")
    
    async def setup_verification_permissions(self, guild, verified_role):
        """configurar permisos de verificación en todo el servidor"""
        try:
            # Lista de canales que requieren verificación (excluir algunos)
            excluded_channels = ["🛡️-verificación", "📋-reglas", "📢-anuncios"]
            
            for channel in guild.text_channels:
                if any(excluded in channel.name for excluded in excluded_channels):
                    continue
                
                # Restringir acceso a usuarios no verificados
                await channel.set_permissions(
                    guild.default_role,
                    read_messages=False,
                    send_messages=False
                )
                
                # Permitir acceso a usuarios verificados
                await channel.set_permissions(
                    verified_role,
                    read_messages=True,
                    send_messages=True
                )
            
            # También para canales de voz
            for channel in guild.voice_channels:
                await channel.set_permissions(
                    guild.default_role,
                    connect=False
                )
                await channel.set_permissions(
                    verified_role,
                    connect=True
                )
                
        except Exception as e:
            logger.error(f"Error configurando permisos de verificación: {e}")
    
    async def verify_user_interaction(self, interaction: nextcord.Interaction):
        """procesar verificación de usuario"""
        try:
            await interaction.response.defer(ephemeral=True)
            
            guild = interaction.guild
            user = interaction.user
            
            # Verificar si ya está verificado
            config = self.db.get_config(guild.id)
            if not config:
                await interaction.followup.send("❌ Sistema de verificación no configurado.", ephemeral=True)
                return
            
            verified_role_id = config[6] if len(config) > 6 else None
            if not verified_role_id:
                await interaction.followup.send("❌ Rol de verificación no configurado.", ephemeral=True)
                return
            
            verified_role = guild.get_role(verified_role_id)
            if not verified_role:
                await interaction.followup.send("❌ Rol de verificación no encontrado.", ephemeral=True)
                return
            
            if verified_role in user.roles:
                await interaction.followup.send("✅ Ya estás verificado.", ephemeral=True)
                return
            
            # Verificaciones adicionales anti-bot
            account_age = (datetime.utcnow() - user.created_at).days
            if account_age < 7:  # Cuenta muy nueva
                await interaction.followup.send(
                    "❌ Tu cuenta es muy nueva. Las cuentas deben tener al menos 7 días.",
                    ephemeral=True
                )
                return
            
            # Agregar rol de verificado
            await user.add_roles(verified_role, reason="Usuario verificado")
            
            # Mensaje de éxito
            await interaction.followup.send(
                "🎉 **¡Verificación exitosa!**\n\n"
                f"✅ Se te ha otorgado el rol {verified_role.mention}\n"
                "🔓 Ahora tienes acceso completo al servidor\n"
                "🎫 Puedes crear tickets de soporte si necesitas ayuda",
                ephemeral=True
            )
            
            # Log de verificación
            log_channel_id = config[3]
            if log_channel_id:
                log_channel = guild.get_channel(log_channel_id)
                if log_channel:
                    log_embed = nextcord.Embed(
                        title="✅ Usuario Verificado",
                        description=f"**Usuario:** {user.mention}\n**ID:** {user.id}\n**Cuenta creada:** {user.created_at.strftime('%d/%m/%Y')}",
                        color=nextcord.Color.green(),
                        timestamp=datetime.utcnow()
                    )
                    await log_channel.send(embed=log_embed)
            
            logger.info(f"Usuario verificado: {user} en {guild.name}")
            
        except Exception as e:
            logger.error(f"Error en verificación de usuario: {e}")
            await interaction.followup.send("❌ Error en la verificación. Contacta con el staff.", ephemeral=True)
    
    async def create_ticket_interaction(self, interaction: nextcord.Interaction):
        """manejar interacción de crear ticket"""
        try:
            # verificar si el usuario ya tiene un ticket abierto
            guild = interaction.guild
            user_tickets = [ch for ch in guild.text_channels if ch.name.startswith(f"ticket-") and f"-{interaction.user.name.lower()}" in ch.name]
            
            if user_tickets:
                await interaction.response.send_message("❌ Ya tienes un ticket abierto.", ephemeral=True)
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
            
            # Obtener número de ticket primero para el nombre del canal
            temp_ticket_number = None
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM tickets WHERE guild_id = ?",
                    (guild.id,)
                )
                temp_ticket_number = cursor.fetchone()[0] + 1
            
            # crear canal de ticket con numeración
            overwrites = {
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True),
                support_role: nextcord.PermissionOverwrite(read_messages=True, send_messages=True) if support_role else None
            }
            
            # remover overwrites nulos
            overwrites = {k: v for k, v in overwrites.items() if v is not None}
            
            channel_name = f"ticket-{temp_ticket_number:04d}-{user.name.lower()}"
            ticket_channel = await guild.create_text_channel(
                channel_name,
                category=category,
                overwrites=overwrites,
                topic=f"Ticket #{temp_ticket_number:04d} - Usuario: {user.display_name} | Motivo: {reason}"
            )
            
            # guardar en base de datos
            ticket_number = self.db.create_ticket(guild.id, ticket_channel.id, user.id, reason)
            
            # mensaje inicial mejorado
            embed = nextcord.Embed(
                title=f"🎫 Ticket #{ticket_number:04d}",
                description=f"**👤 Usuario:** {user.mention} (`{user.display_name}`)\n**📝 Motivo:** {reason}\n**🕒 Creado:** <t:{int(datetime.utcnow().timestamp())}:F>",
                color=nextcord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(
                name="📋 Información",
                value="• El staff responderá pronto\n• Solo el staff puede cerrar este ticket\n• La transcripción se guardará automáticamente",
                inline=False
            )
            embed.set_footer(text=f"Ticket ID: {ticket_number:04d}")
            
            view = TicketControlView(self)
            await ticket_channel.send(embed=embed, view=view)
            await ticket_channel.send(f"{user.mention} {support_role.mention if support_role else ''}")
            
            await interaction.followup.send(f"✅ Ticket #{ticket_number:04d} creado: {ticket_channel.mention}", ephemeral=True)
            
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
        """cerrar ticket con transcripción automática"""
        try:
            # verificar que es un canal de ticket
            ticket_info = self.db.get_ticket(interaction.channel.id)
            if not ticket_info:
                await interaction.response.send_message("❌ Este no es un canal de ticket.", ephemeral=True)
                return
            
            # verificar permisos
            if not (interaction.user.guild_permissions.manage_channels or 
                   interaction.user.id == ticket_info[3]):  # owner del ticket
                await interaction.response.send_message("❌ Sin permisos para cerrar este ticket.", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            # Generar transcripción antes de cerrar
            await self.save_ticket_transcript(interaction.channel, ticket_info[0])
            
            # cerrar en base de datos
            self.db.close_ticket(interaction.channel.id)
            
            # mensaje de cierre
            embed = nextcord.Embed(
                title="🔒 Ticket Cerrado",
                description=f"**Cerrado por:** {interaction.user.mention}\n**Transcripción:** Guardada automáticamente",
                color=nextcord.Color.red(),
                timestamp=datetime.utcnow()
            )
            await interaction.followup.send(embed=embed)
            
            # Log de cierre
            config = self.db.get_config(interaction.guild.id)
            if config and config[3]:
                log_channel = interaction.guild.get_channel(config[3])
                if log_channel:
                    user = interaction.guild.get_member(ticket_info[3])
                    log_embed = nextcord.Embed(
                        title="🔒 Ticket Cerrado",
                        description=f"**Usuario:** {user.mention if user else 'Usuario desconocido'}\n**Cerrado por:** {interaction.user.mention}\n**Canal:** {interaction.channel.name}",
                        color=nextcord.Color.red(),
                        timestamp=datetime.utcnow()
                    )
                    await log_channel.send(embed=log_embed)
            
            # eliminar canal después de 15 segundos
            await asyncio.sleep(15)
            await interaction.channel.delete(reason=f"Ticket cerrado por {interaction.user}")
            
            logger.info(f"Ticket cerrado por {interaction.user}")
            
        except Exception as e:
            logger.error(f"Error cerrando ticket: {e}")
            await interaction.followup.send("❌ Error al cerrar ticket.")
    
    async def save_ticket_transcript(self, channel, ticket_id):
        """guardar transcripción completa del ticket"""
        try:
            # Obtener todos los mensajes del canal
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                if not message.author.bot or message.embeds:  # Incluir mensajes de bot con embeds
                    timestamp = message.created_at.strftime("%d/%m/%Y %H:%M:%S")
                    content = message.content
                    
                    # Agregar información de archivos adjuntos
                    if message.attachments:
                        content += f"\n[{len(message.attachments)} archivo(s) adjunto(s)]"
                    
                    # Agregar información de embeds
                    if message.embeds:
                        content += f"\n[Embed: {message.embeds[0].title or 'Sin título'}]"
                    
                    messages.append({
                        "timestamp": timestamp,
                        "author": message.author.display_name,
                        "content": content or "[Mensaje vacío]"
                    })
            
            # Crear transcripción en formato texto mejorado
            ticket_info = self.db.get_ticket(channel.id)
            user_info = channel.guild.get_member(ticket_info[3]) if ticket_info else None
            
            transcript_content = f"=" * 70 + "\n"
            transcript_content += f"🎫 TRANSCRIPCIÓN DEL TICKET #{ticket_id:04d}\n"
            transcript_content += f"=" * 70 + "\n"
            transcript_content += f"📋 Canal: {channel.name}\n"
            transcript_content += f"👤 Usuario: {user_info.display_name if user_info else 'Desconocido'} ({user_info.id if user_info else 'N/A'})\n"
            transcript_content += f"🕒 Fecha de cierre: {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S')}\n"
            transcript_content += f"📊 Total de mensajes: {len(messages)}\n"
            transcript_content += f"=" * 70 + "\n\n"
            
            for msg in messages:
                transcript_content += f"[{msg['timestamp']}] {msg['author']}: {msg['content']}\n"
            
            transcript_content += f"\n" + "=" * 70 + "\n"
            transcript_content += f"Fin de la transcripción - Generada automáticamente por DaBot v2\n"
            transcript_content += f"=" * 70 + "\n"
            
            # Guardar en archivo
            transcript_file = io.StringIO(transcript_content)
            filename = f"ticket-{ticket_id:04d}-{user_info.name if user_info else 'unknown'}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            file = nextcord.File(transcript_file, filename=filename)
            
            # Enviar a canal de transcripciones - BUSCAR POR NOMBRE SI NO HAY ID
            config = self.db.get_config(channel.guild.id)
            transcript_sent = False
            transcript_channel = None
            
            # Método 1: Buscar por ID de configuración
            if config and len(config) > 4 and config[4]:  # transcript_channel_id
                transcript_channel = channel.guild.get_channel(config[4])
            
            # Método 2: Buscar por nombre de canal si no se encontró por ID
            if not transcript_channel:
                for ch in channel.guild.text_channels:
                    if any(name in ch.name.lower() for name in ['registro-tickets', 'transcripciones', 'ticket-logs', 'registro-ticket']):
                        transcript_channel = ch
                        break
            
            # Enviar transcripción al canal encontrado
            if transcript_channel:
                try:
                    embed = nextcord.Embed(
                        title=f"📝 Transcripción Ticket #{ticket_id:04d}",
                        description=f"**👤 Usuario:** {user_info.mention if user_info else 'Usuario desconocido'}\n**📋 Canal:** `{channel.name}`\n**📊 Mensajes:** {len(messages)}\n**🕒 Cerrado:** <t:{int(datetime.utcnow().timestamp())}:F>",
                        color=nextcord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(
                        name="📂 Archivo",
                        value=f"```{filename}```",
                        inline=False
                    )
                    embed.set_footer(text=f"Ticket ID: {ticket_id:04d} • Canal: {transcript_channel.name}")
                    
                    await transcript_channel.send(embed=embed, file=file)
                    transcript_sent = True
                    logger.info(f"Transcripción enviada a {transcript_channel.name}")
                except Exception as send_error:
                    logger.error(f"Error enviando transcripción: {send_error}")
            
            # Si no se pudo enviar al canal de transcripciones, buscar canal de logs
            if not transcript_sent:
                log_channel = None
                
                # Buscar canal de logs por ID
                if config and config[3]:
                    log_channel = channel.guild.get_channel(config[3])
                
                # Buscar canal de logs por nombre si no se encontró por ID
                if not log_channel:
                    for ch in channel.guild.text_channels:
                        if any(name in ch.name.lower() for name in ['logs', 'registro', 'moderacion']):
                            log_channel = ch
                            break
                
                if log_channel:
                    try:
                        # Crear nuevo archivo ya que el anterior se consumió
                        transcript_file = io.StringIO(transcript_content)
                        file = nextcord.File(transcript_file, filename=filename)
                        
                        embed = nextcord.Embed(
                            title=f"📝 Transcripción Ticket #{ticket_id:04d}",
                            description=f"**👤 Usuario:** {user_info.mention if user_info else 'Usuario desconocido'}\n**📋 Canal:** `{channel.name}`\n**📊 Mensajes:** {len(messages)}",
                            color=nextcord.Color.orange(),
                            timestamp=datetime.utcnow()
                        )
                        embed.set_footer(text=f"Enviado a {log_channel.name} - Canal de transcripciones no encontrado")
                        
                        await log_channel.send(embed=embed, file=file)
                        logger.info(f"Transcripción enviada a canal de logs: {log_channel.name}")
                    except Exception as log_error:
                        logger.error(f"Error enviando a logs: {log_error}")
                else:
                    logger.warning("No se encontró canal para enviar transcripción")
                    
        except Exception as e:
            logger.error(f"Error guardando transcripción: {e}")
    
    async def add_user_to_ticket(self, interaction: nextcord.Interaction):
        """agregar usuario al ticket"""
        try:
            await interaction.response.send_message("Menciona al usuario que quieres agregar:", ephemeral=True)
            
            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel and m.mentions
            
            try:
                message = await self.bot.wait_for('message', timeout=30.0, check=check)
                user = message.mentions[0]
                
                # Agregar permisos al usuario
                await interaction.channel.set_permissions(
                    user,
                    read_messages=True,
                    send_messages=True
                )
                
                embed = nextcord.Embed(
                    title="👥 Usuario Agregado",
                    description=f"{user.mention} ha sido agregado al ticket.",
                    color=nextcord.Color.blue()
                )
                await interaction.channel.send(embed=embed)
                await message.delete()
                
            except asyncio.TimeoutError:
                await interaction.edit_original_response(content="❌ Tiempo agotado. Inténtalo de nuevo.")
                
        except Exception as e:
            logger.error(f"Error agregando usuario: {e}")
    
    async def rename_ticket_interaction(self, interaction: nextcord.Interaction):
        """reclasificar ticket"""
        try:
            await interaction.response.send_message("Escribe el nuevo nombre para el ticket:", ephemeral=True)
            
            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel
            
            try:
                message = await self.bot.wait_for('message', timeout=30.0, check=check)
                new_name = f"ticket-{message.content.lower().replace(' ', '-')}"
                
                await interaction.channel.edit(name=new_name)
                
                embed = nextcord.Embed(
                    title="🔄 Ticket Reclasificado",
                    description=f"**Nuevo nombre:** {new_name}",
                    color=nextcord.Color.blue()
                )
                await interaction.channel.send(embed=embed)
                await message.delete()
                
            except asyncio.TimeoutError:
                await interaction.edit_original_response(content="❌ Tiempo agotado. Inténtalo de nuevo.")
                
        except Exception as e:
            logger.error(f"Error renombrando ticket: {e}")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """registrar mensajes para transcripciones"""
        try:
            if message.author.bot and not message.embeds:
                return
            
            # Verificar si es un canal de ticket
            if message.channel.name.startswith("ticket-"):
                ticket_info = self.db.get_ticket(message.channel.id)
                if ticket_info:
                    self.db.add_message_to_transcript(
                        ticket_info[0],  # ticket_id
                        message.author.id,
                        message.author.display_name,
                        message.content or "[Mensaje sin contenido]"
                    )
                    
        except Exception as e:
            logger.error(f"Error registrando mensaje para transcripción: {e}")
    
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
