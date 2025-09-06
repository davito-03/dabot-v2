import nextcord
from nextcord.ext import commands
import json
import os
import logging
from datetime import datetime
from .config_manager import get_config

logger = logging.getLogger(__name__)

class AppealForm(nextcord.ui.Modal):
    """Formulario de apelación para bans y warnings"""
    
    def __init__(self, appeal_type: str, guild_id: int, user_id: int):
        self.appeal_type = appeal_type  # 'ban' o 'warning'
        self.guild_id = guild_id
        self.user_id = user_id
        
        title = "Formulario de Apelación - Ban" if appeal_type == 'ban' else "Formulario de Apelación - Aviso"
        super().__init__(title=title, timeout=300.0)
        
        # Razón de la apelación
        self.reason = nextcord.ui.TextInput(
            label="¿Por qué deberíamos revocar tu sanción?",
            placeholder="Explica detalladamente por qué crees que la sanción debería ser revocada...",
            style=nextcord.TextInputStyle.paragraph,
            max_length=1000,
            required=True
        )
        self.add_item(self.reason)
        
        # Información adicional
        self.additional_info = nextcord.ui.TextInput(
            label="Información adicional",
            placeholder="Cualquier información adicional que consideres relevante...",
            style=nextcord.TextInputStyle.paragraph,
            max_length=500,
            required=False
        )
        self.add_item(self.additional_info)
        
        # Compromiso
        self.commitment = nextcord.ui.TextInput(
            label="¿Qué harás para evitar futuras infracciones?",
            placeholder="Describe qué medidas tomarás para no volver a infringir las reglas...",
            style=nextcord.TextInputStyle.paragraph,
            max_length=500,
            required=True
        )
        self.add_item(self.commitment)
    
    async def on_submit(self, interaction: nextcord.Interaction):
        """Cuando se envía el formulario"""
        try:
            # Crear embed de la apelación
            embed = nextcord.Embed(
                title=f"📋 Nueva Apelación - {'Ban' if self.appeal_type == 'ban' else 'Aviso'}",
                color=0xf39c12,
                timestamp=datetime.now()
            )
            
            # Información del usuario
            user = interaction.client.get_user(self.user_id)
            embed.add_field(
                name="👤 Usuario",
                value=f"{user.mention} ({user.name})\nID: `{self.user_id}`",
                inline=True
            )
            
            # Servidor
            guild = interaction.client.get_guild(self.guild_id)
            embed.add_field(
                name="🏠 Servidor",
                value=f"{guild.name}\nID: `{self.guild_id}`",
                inline=True
            )
            
            # Tipo de sanción
            embed.add_field(
                name="⚖️ Tipo de Sanción",
                value=self.appeal_type.capitalize(),
                inline=True
            )
            
            # Razón de la apelación
            embed.add_field(
                name="📝 Razón de la Apelación",
                value=self.reason.value,
                inline=False
            )
            
            # Información adicional
            if self.additional_info.value:
                embed.add_field(
                    name="ℹ️ Información Adicional",
                    value=self.additional_info.value,
                    inline=False
                )
            
            # Compromiso
            embed.add_field(
                name="🤝 Compromiso",
                value=self.commitment.value,
                inline=False
            )
            
            # Obtener canal de apelaciones
            appeals_channel_id = get_config('appeals.channel_id')
            if appeals_channel_id:
                appeals_channel = interaction.client.get_channel(int(appeals_channel_id))
                if appeals_channel:
                    # Crear botones para gestionar la apelación
                    view = AppealManagementView(self.appeal_type, self.guild_id, self.user_id)
                    
                    await appeals_channel.send(embed=embed, view=view)
                    
                    # Confirmar al usuario
                    await interaction.response.send_message(
                        "✅ Tu apelación ha sido enviada correctamente. El equipo de moderación la revisará pronto.",
                        ephemeral=True
                    )
                    
                    # Guardar registro de la apelación
                    self.save_appeal_record(interaction.user, embed)
                else:
                    await interaction.response.send_message(
                        "❌ Error: Canal de apelaciones no encontrado. Contacta con un administrador.",
                        ephemeral=True
                    )
            else:
                await interaction.response.send_message(
                    "❌ Error: Sistema de apelaciones no configurado. Contacta con un administrador.",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error procesando apelación: {e}")
            await interaction.response.send_message(
                "❌ Error procesando tu apelación. Inténtalo de nuevo más tarde.",
                ephemeral=True
            )
    
    def save_appeal_record(self, user: nextcord.User, embed: nextcord.Embed):
        """Guardar registro de la apelación"""
        try:
            os.makedirs('data', exist_ok=True)
            appeals_file = 'data/appeals.json'
            
            appeals = {}
            if os.path.exists(appeals_file):
                with open(appeals_file, 'r', encoding='utf-8') as f:
                    appeals = json.load(f)
            
            appeal_id = f"{self.guild_id}_{self.user_id}_{int(datetime.now().timestamp())}"
            appeals[appeal_id] = {
                'user_id': self.user_id,
                'guild_id': self.guild_id,
                'type': self.appeal_type,
                'timestamp': datetime.now().isoformat(),
                'status': 'pending',
                'reason': self.reason.value,
                'additional_info': self.additional_info.value,
                'commitment': self.commitment.value
            }
            
            with open(appeals_file, 'w', encoding='utf-8') as f:
                json.dump(appeals, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando registro de apelación: {e}")


class AppealManagementView(nextcord.ui.View):
    """Vista para gestionar apelaciones"""
    
    def __init__(self, appeal_type: str, guild_id: int, user_id: int):
        super().__init__(timeout=None)
        self.appeal_type = appeal_type
        self.guild_id = guild_id
        self.user_id = user_id
    
    @nextcord.ui.button(label="✅ Aprobar", style=nextcord.ButtonStyle.green, custom_id="approve_appeal")
    async def approve_appeal(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Aprobar la apelación"""
        # Verificar permisos
        try:
            mod_roles = interaction.client.get_cog('ModerationRoles')
            
            if mod_roles and not mod_roles.can_perform_action(interaction.user, 'unban' if self.appeal_type == 'ban' else 'unwarn'):
                await interaction.response.send_message(
                    "❌ No tienes permisos para aprobar apelaciones.",
                    ephemeral=True
                )
                return
        except:
            # Si no hay sistema de roles, verificar permisos básicos
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message(
                    "❌ No tienes permisos para aprobar apelaciones.",
                    ephemeral=True
                )
                return
        
        # Crear embed de aprobación
        embed = nextcord.Embed(
            title="✅ Apelación Aprobada",
            description=f"La apelación de {'ban' if self.appeal_type == 'ban' else 'aviso'} ha sido aprobada.",
            color=0x27ae60,
            timestamp=datetime.now()
        )
        embed.add_field(name="Aprobada por", value=interaction.user.mention, inline=True)
        embed.add_field(name="Usuario", value=f"<@{self.user_id}>", inline=True)
        
        # Deshabilitar botones
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
        
        # Notificar al usuario
        try:
            user = interaction.client.get_user(self.user_id)
            if user:
                guild = interaction.client.get_guild(self.guild_id)
                dm_embed = nextcord.Embed(
                    title="✅ Apelación Aprobada",
                    description=f"Tu apelación de {'ban' if self.appeal_type == 'ban' else 'aviso'} en **{guild.name}** ha sido aprobada.",
                    color=0x27ae60
                )
                dm_embed.add_field(
                    name="Acción Tomada",
                    value="Tu sanción ha sido revocada. Por favor, respeta las reglas del servidor.",
                    inline=False
                )
                
                await user.send(embed=dm_embed)
        except:
            pass  # No pudo enviar DM
        
        # Actualizar registro
        self.update_appeal_status('approved', interaction.user.id)
    
    @nextcord.ui.button(label="❌ Rechazar", style=nextcord.ButtonStyle.red, custom_id="reject_appeal")
    async def reject_appeal(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Rechazar la apelación"""
        # Verificar permisos
        try:
            mod_roles = interaction.client.get_cog('ModerationRoles')
            
            if mod_roles and not mod_roles.can_perform_action(interaction.user, 'unban' if self.appeal_type == 'ban' else 'unwarn'):
                await interaction.response.send_message(
                    "❌ No tienes permisos para rechazar apelaciones.",
                    ephemeral=True
                )
                return
        except:
            # Si no hay sistema de roles, verificar permisos básicos
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message(
                    "❌ No tienes permisos para rechazar apelaciones.",
                    ephemeral=True
                )
                return
        
        # Mostrar modal para razón del rechazo
        modal = RejectReasonModal(self.appeal_type, self.guild_id, self.user_id, self)
        await interaction.response.send_modal(modal)
    
    @nextcord.ui.button(label="🔍 Investigar", style=nextcord.ButtonStyle.gray, custom_id="investigate_appeal")
    async def investigate_appeal(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """Marcar como en investigación"""
        embed = nextcord.Embed(
            title="🔍 Apelación en Investigación",
            description=f"La apelación de {'ban' if self.appeal_type == 'ban' else 'aviso'} está siendo investigada.",
            color=0xf39c12,
            timestamp=datetime.now()
        )
        embed.add_field(name="Investigada por", value=interaction.user.mention, inline=True)
        embed.add_field(name="Usuario", value=f"<@{self.user_id}>", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
        
        # Actualizar registro
        self.update_appeal_status('investigating', interaction.user.id)
    
    def update_appeal_status(self, status: str, moderator_id: int):
        """Actualizar estado de la apelación"""
        try:
            appeals_file = 'data/appeals.json'
            if not os.path.exists(appeals_file):
                return
            
            with open(appeals_file, 'r', encoding='utf-8') as f:
                appeals = json.load(f)
            
            for appeal_id, appeal_data in appeals.items():
                if (appeal_data['user_id'] == self.user_id and 
                    appeal_data['guild_id'] == self.guild_id and
                    appeal_data['type'] == self.appeal_type and
                    appeal_data['status'] == 'pending'):
                    
                    appeals[appeal_id]['status'] = status
                    appeals[appeal_id]['moderator_id'] = moderator_id
                    appeals[appeal_id]['resolved_at'] = datetime.now().isoformat()
                    break
            
            with open(appeals_file, 'w', encoding='utf-8') as f:
                json.dump(appeals, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error actualizando estado de apelación: {e}")


class RejectReasonModal(nextcord.ui.Modal):
    """Modal para especificar razón del rechazo"""
    
    def __init__(self, appeal_type: str, guild_id: int, user_id: int, parent_view):
        super().__init__(title="Razón del Rechazo", timeout=300.0)
        self.appeal_type = appeal_type
        self.guild_id = guild_id
        self.user_id = user_id
        self.parent_view = parent_view
        
        self.reason = nextcord.ui.TextInput(
            label="Razón del rechazo",
            placeholder="Explica por qué se rechaza la apelación...",
            style=nextcord.TextInputStyle.paragraph,
            max_length=1000,
            required=True
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: nextcord.Interaction):
        """Procesar rechazo con razón"""
        # Crear embed de rechazo
        embed = nextcord.Embed(
            title="❌ Apelación Rechazada",
            description=f"La apelación de {'ban' if self.appeal_type == 'ban' else 'aviso'} ha sido rechazada.",
            color=0xe74c3c,
            timestamp=datetime.now()
        )
        embed.add_field(name="Rechazada por", value=interaction.user.mention, inline=True)
        embed.add_field(name="Usuario", value=f"<@{self.user_id}>", inline=True)
        embed.add_field(name="Razón del Rechazo", value=self.reason.value, inline=False)
        
        # Deshabilitar botones
        for item in self.parent_view.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
        
        # Notificar al usuario
        try:
            user = interaction.client.get_user(self.user_id)
            if user:
                guild = interaction.client.get_guild(self.guild_id)
                dm_embed = nextcord.Embed(
                    title="❌ Apelación Rechazada",
                    description=f"Tu apelación de {'ban' if self.appeal_type == 'ban' else 'aviso'} en **{guild.name}** ha sido rechazada.",
                    color=0xe74c3c
                )
                dm_embed.add_field(
                    name="Razón del Rechazo",
                    value=self.reason.value,
                    inline=False
                )
                
                await user.send(embed=dm_embed)
        except:
            pass  # No pudo enviar DM
        
        # Actualizar registro
        self.parent_view.update_appeal_status('rejected', interaction.user.id)


class Appeals(commands.Cog):
    """Sistema de apelaciones para bans y warnings"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command(name="apelar", description="Crear una apelación para ban o warning")
    async def appeal(
        self,
        interaction: nextcord.Interaction,
        tipo: str = nextcord.SlashOption(
            description="Tipo de sanción a apelar",
            choices=["ban", "warning"]
        )
    ):
        """Comando para crear apelación"""
        # Verificar si el usuario puede apelar
        if tipo == 'ban':
            # Verificar si está baneado
            try:
                await interaction.guild.fetch_ban(interaction.user)
            except nextcord.NotFound:
                await interaction.response.send_message(
                    "❌ No estás baneado en este servidor.",
                    ephemeral=True
                )
                return
        
        # Verificar cooldown de apelaciones
        if self.has_recent_appeal(interaction.guild.id, interaction.user.id, tipo):
            await interaction.response.send_message(
                "❌ Ya has enviado una apelación recientemente. Espera antes de enviar otra.",
                ephemeral=True
            )
            return
        
        # Mostrar formulario
        modal = AppealForm(tipo, interaction.guild.id, interaction.user.id)
        await interaction.response.send_modal(modal)
    
    def has_recent_appeal(self, guild_id: int, user_id: int, appeal_type: str, hours: int = 24) -> bool:
        """Verificar si tiene apelación reciente"""
        try:
            appeals_file = 'data/appeals.json'
            if not os.path.exists(appeals_file):
                return False
            
            with open(appeals_file, 'r', encoding='utf-8') as f:
                appeals = json.load(f)
            
            now = datetime.now()
            for appeal_data in appeals.values():
                if (appeal_data['user_id'] == user_id and 
                    appeal_data['guild_id'] == guild_id and
                    appeal_data['type'] == appeal_type):
                    
                    appeal_time = datetime.fromisoformat(appeal_data['timestamp'])
                    if (now - appeal_time).total_seconds() < hours * 3600:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando apelación reciente: {e}")
            return False
    
    @nextcord.slash_command(name="appeals-stats", description="Ver estadísticas de apelaciones")
    async def appeals_stats(self, interaction: nextcord.Interaction):
        """Ver estadísticas de apelaciones"""
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message(
                "❌ No tienes permisos para ver estadísticas de apelaciones.",
                ephemeral=True
            )
            return
        
        try:
            appeals_file = 'data/appeals.json'
            if not os.path.exists(appeals_file):
                await interaction.response.send_message(
                    "📊 No hay apelaciones registradas aún.",
                    ephemeral=True
                )
                return
            
            with open(appeals_file, 'r', encoding='utf-8') as f:
                appeals = json.load(f)
            
            # Filtrar por servidor
            guild_appeals = [a for a in appeals.values() if a['guild_id'] == interaction.guild.id]
            
            if not guild_appeals:
                await interaction.response.send_message(
                    "📊 No hay apelaciones registradas para este servidor.",
                    ephemeral=True
                )
                return
            
            # Calcular estadísticas
            total = len(guild_appeals)
            approved = len([a for a in guild_appeals if a['status'] == 'approved'])
            rejected = len([a for a in guild_appeals if a['status'] == 'rejected'])
            pending = len([a for a in guild_appeals if a['status'] == 'pending'])
            investigating = len([a for a in guild_appeals if a['status'] == 'investigating'])
            
            bans = len([a for a in guild_appeals if a['type'] == 'ban'])
            warnings = len([a for a in guild_appeals if a['type'] == 'warning'])
            
            embed = nextcord.Embed(
                title="📊 Estadísticas de Apelaciones",
                color=0x3498db,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📈 Total",
                value=f"{total} apelaciones",
                inline=True
            )
            embed.add_field(
                name="✅ Aprobadas",
                value=f"{approved} ({approved/total*100:.1f}%)" if total > 0 else "0",
                inline=True
            )
            embed.add_field(
                name="❌ Rechazadas",
                value=f"{rejected} ({rejected/total*100:.1f}%)" if total > 0 else "0",
                inline=True
            )
            embed.add_field(
                name="⏳ Pendientes",
                value=f"{pending}",
                inline=True
            )
            embed.add_field(
                name="🔍 En Investigación",
                value=f"{investigating}",
                inline=True
            )
            embed.add_field(
                name="📊 Por Tipo",
                value=f"Bans: {bans}\nAvisos: {warnings}",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            await interaction.response.send_message(
                "❌ Error obteniendo estadísticas de apelaciones.",
                ephemeral=True
            )

def setup(bot):
    """Función para cargar el cog"""
    return Appeals(bot)
