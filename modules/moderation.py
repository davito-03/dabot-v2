"""
Módulo de Moderación para el bot de Discord
Incluye comandos para banear, kick, limpiar mensajes y sistema de avisos
"""

import logging
import nextcord
from nextcord.ext import commands
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    """Clase para comandos de moderación"""
    
    def __init__(self, bot):
        self.bot = bot
        self.warnings = {}
        self.load_warnings()
    
    def load_warnings(self):
        """cargar avisos desde archivo"""
        try:
            with open('data/warnings.json', 'r', encoding='utf-8') as f:
                self.warnings = json.load(f)
        except FileNotFoundError:
            self.warnings = {}
    
    def save_warnings(self):
        """guardar avisos a archivo"""
        try:
            with open('data/warnings.json', 'w', encoding='utf-8') as f:
                json.dump(self.warnings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando avisos: {e}")
    
    
    @nextcord.slash_command(name="avisar", description="Dar un aviso a un usuario")
    @commands.has_permissions(moderate_members=True)
    async def warn_user(self, interaction: nextcord.Interaction, 
                       usuario: nextcord.Member, *, razon: str = "No se especificó razón"):
        """dar aviso a un usuario"""
        if usuario.bot:
            await interaction.response.send_message("❌ No puedes avisar a un bot.", ephemeral=True)
            return
        
        if usuario == interaction.user:
            await interaction.response.send_message("❌ No puedes avisarte a ti mismo.", ephemeral=True)
            return
        
        # crear estructura de avisos
        guild_id = str(interaction.guild.id)
        user_id = str(usuario.id)
        
        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}
        
        if user_id not in self.warnings[guild_id]:
            self.warnings[guild_id][user_id] = []
        
        # crear aviso
        warning = {
            'id': len(self.warnings[guild_id][user_id]) + 1,
            'reason': razon,
            'moderator': str(interaction.user),
            'moderator_id': interaction.user.id,
            'timestamp': datetime.now().isoformat(),
            'active': True
        }
        
        self.warnings[guild_id][user_id].append(warning)
        self.save_warnings()
        
        # notificar al usuario
        try:
            dm_embed = nextcord.Embed(
                title="⚠️ Has recibido un aviso",
                description=f"Has recibido un aviso en **{interaction.guild.name}**",
                color=0xe74c3c
            )
            dm_embed.add_field(name="Razón", value=razon, inline=False)
            dm_embed.add_field(name="Moderador", value=str(interaction.user), inline=False)
            dm_embed.add_field(name="Total de avisos", value=len(self.warnings[guild_id][user_id]), inline=False)
            await usuario.send(embed=dm_embed)
        except:
            pass
        
        # respuesta en el canal
        embed = nextcord.Embed(
            title="✅ Aviso dado",
            description=f"Se ha dado un aviso a {usuario.mention}",
            color=0xe74c3c
        )
        embed.add_field(name="Razón", value=razon, inline=False)
        embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
        embed.add_field(name="Total de avisos", value=len(self.warnings[guild_id][user_id]), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="avisos", description="Ver los avisos de un usuario")
    @commands.has_permissions(moderate_members=True)
    async def view_warnings(self, interaction: nextcord.Interaction, 
                           usuario: nextcord.Member):
        """ver avisos de un usuario"""
        guild_id = str(interaction.guild.id)
        user_id = str(usuario.id)
        
        if guild_id not in self.warnings or user_id not in self.warnings[guild_id]:
            embed = nextcord.Embed(
                title="📋 Avisos del usuario",
                description=f"{usuario.mention} no tiene avisos.",
                color=0x2ecc71
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_warnings = self.warnings[guild_id][user_id]
        active_warnings = [w for w in user_warnings if w.get('active', True)]
        
        embed = nextcord.Embed(
            title=f"📋 Avisos de {usuario.display_name}",
            description=f"Total: {len(active_warnings)} avisos activos",
            color=0xe74c3c if active_warnings else 0x2ecc71
        )
        
        for warning in active_warnings[-10:]:  # últimos 10
            timestamp = datetime.fromisoformat(warning['timestamp']).strftime("%d/%m/%Y %H:%M")
            embed.add_field(
                name=f"Aviso #{warning['id']}",
                value=f"**Razón:** {warning['reason']}\n**Moderador:** {warning['moderator']}\n**Fecha:** {timestamp}",
                inline=False
            )
        
        embed.set_thumbnail(url=usuario.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @nextcord.slash_command(name="quitar-aviso", description="Quitar un aviso específico de un usuario")
    @commands.has_permissions(moderate_members=True)
    async def remove_warning(self, interaction: nextcord.Interaction, 
                            usuario: nextcord.Member, aviso_id: int):
        """quitar aviso específico"""
        guild_id = str(interaction.guild.id)
        user_id = str(usuario.id)
        
        if guild_id not in self.warnings or user_id not in self.warnings[guild_id]:
            await interaction.response.send_message("❌ Este usuario no tiene avisos.", ephemeral=True)
            return
        
        user_warnings = self.warnings[guild_id][user_id]
        
        # buscar y desactivar el aviso
        warning_found = False
        for warning in user_warnings:
            if warning['id'] == aviso_id and warning.get('active', True):
                warning['active'] = False
                warning['removed_by'] = str(interaction.user)
                warning['removed_at'] = datetime.now().isoformat()
                warning_found = True
                break
        
        if not warning_found:
            await interaction.response.send_message("❌ Aviso no encontrado o ya removido.", ephemeral=True)
            return
        
        self.save_warnings()
        
        embed = nextcord.Embed(
            title="✅ Aviso removido",
            description=f"Se removió el aviso #{aviso_id} de {usuario.mention}",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="limpiar-avisos", description="Limpiar todos los avisos de un usuario")
    @commands.has_permissions(administrator=True)
    async def clear_warnings(self, interaction: nextcord.Interaction, 
                            usuario: nextcord.Member):
        """limpiar todos los avisos de un usuario"""
        guild_id = str(interaction.guild.id)
        user_id = str(usuario.id)
        
        if guild_id not in self.warnings or user_id not in self.warnings[guild_id]:
            await interaction.response.send_message("❌ Este usuario no tiene avisos.", ephemeral=True)
            return
        
        # desactivar todos los avisos
        for warning in self.warnings[guild_id][user_id]:
            warning['active'] = False
            warning['removed_by'] = str(interaction.user)
            warning['removed_at'] = datetime.now().isoformat()
        
        self.save_warnings()
        
        embed = nextcord.Embed(
            title="✅ Avisos limpiados",
            description=f"Se limpiaron todos los avisos de {usuario.mention}",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed)

    @commands.command(name='ban')
    @commands.has_permissions(administrator=True)
    async def ban_member(self, ctx, member: nextcord.Member, *, reason="No se proporcionó razón"):
        """
        Banea a un miembro del servidor
        Uso: !ban @usuario razón
        """
        try:
            # Verificar que no se esté intentando banear al autor del comando
            if member == ctx.author:
                await ctx.send("❌ No puedes banearte a ti mismo.")
                return
            
            # Verificar que no se esté intentando banear al bot
            if member == self.bot.user:
                await ctx.send("❌ No puedo banearme a mí mismo.")
                return
            
            # Verificar jerarquía de roles
            if member.top_role >= ctx.author.top_role:
                await ctx.send("❌ No puedes banear a alguien con un rol igual o superior al tuyo.")
                return
            
            # Confirmar la acción
            embed = nextcord.Embed(
                title="⚠️ Confirmación de Baneo",
                description=f"¿Estás seguro de que quieres banear a {member.mention}?",
                color=nextcord.Color.orange()
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
            
            # Crear vista con botones de confirmación
            view = ConfirmationView(ctx.author)
            message = await ctx.send(embed=embed, view=view)
            
            # Esperar confirmación
            await view.wait()
            
            if view.confirmed:
                # Enviar mensaje privado al usuario antes del baneo
                try:
                    dm_embed = nextcord.Embed(
                        title="🔨 Has sido baneado",
                        description=f"Has sido baneado del servidor **{ctx.guild.name}**",
                        color=nextcord.Color.red()
                    )
                    dm_embed.add_field(name="Razón", value=reason, inline=False)
                    dm_embed.add_field(name="Moderador", value=str(ctx.author), inline=False)
                    await member.send(embed=dm_embed)
                except nextcord.Forbidden:
                    pass  # El usuario tiene DMs deshabilitados
                
                # Realizar el baneo
                await member.ban(reason=f"Baneado por {ctx.author} - {reason}")
                
                # Confirmar la acción
                success_embed = nextcord.Embed(
                    title="✅ Usuario Baneado",
                    description=f"{member.mention} ha sido baneado exitosamente.",
                    color=nextcord.Color.green()
                )
                success_embed.add_field(name="Razón", value=reason, inline=False)
                success_embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
                
                await message.edit(embed=success_embed, view=None)
                logger.info(f"{member} fue baneado por {ctx.author} - Razón: {reason}")
            else:
                # Cancelar la acción
                cancel_embed = nextcord.Embed(
                    title="❌ Baneo Cancelado",
                    description="La acción de baneo ha sido cancelada.",
                    color=nextcord.Color.gray()
                )
                await message.edit(embed=cancel_embed, view=None)
                
        except nextcord.Forbidden:
            await ctx.send("❌ No tengo permisos para banear a este usuario.")
        except Exception as e:
            logger.error(f"Error en comando ban: {e}")
            await ctx.send("❌ Ocurrió un error al intentar banear al usuario.")
    
    @nextcord.slash_command(name="ban", description="Banea a un miembro del servidor")
    async def slash_ban(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        reason: str = "No se proporcionó razón"
    ):
        """Comando slash para banear usuarios"""
        # Verificar permisos
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Crear un contexto simulado
        class MockContext:
            def __init__(self, interaction):
                self.author = interaction.user
                self.guild = interaction.guild
                self.channel = interaction.channel
                self.send = interaction.followup.send
                
        ctx = MockContext(interaction)
        await self.ban_member(ctx, member, reason=reason)
    
    @commands.command(name='kick')
    @commands.has_permissions(administrator=True)
    async def kick_member(self, ctx, member: nextcord.Member, *, reason="No se proporcionó razón"):
        """
        Expulsa a un miembro del servidor
        Uso: !kick @usuario razón
        """
        try:
            # Verificaciones similares al comando ban
            if member == ctx.author:
                await ctx.send("❌ No puedes expulsarte a ti mismo.")
                return
            
            if member == self.bot.user:
                await ctx.send("❌ No puedo expulsarme a mí mismo.")
                return
            
            if member.top_role >= ctx.author.top_role:
                await ctx.send("❌ No puedes expulsar a alguien con un rol igual o superior al tuyo.")
                return
            
            # Confirmar la acción
            embed = nextcord.Embed(
                title="⚠️ Confirmación de Expulsión",
                description=f"¿Estás seguro de que quieres expulsar a {member.mention}?",
                color=nextcord.Color.orange()
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
            
            view = ConfirmationView(ctx.author)
            message = await ctx.send(embed=embed, view=view)
            
            await view.wait()
            
            if view.confirmed:
                # Enviar mensaje privado
                try:
                    dm_embed = nextcord.Embed(
                        title="👢 Has sido expulsado",
                        description=f"Has sido expulsado del servidor **{ctx.guild.name}**",
                        color=nextcord.Color.orange()
                    )
                    dm_embed.add_field(name="Razón", value=reason, inline=False)
                    dm_embed.add_field(name="Moderador", value=str(ctx.author), inline=False)
                    await member.send(embed=dm_embed)
                except nextcord.Forbidden:
                    pass
                
                # Realizar la expulsión
                await member.kick(reason=f"Expulsado por {ctx.author} - {reason}")
                
                success_embed = nextcord.Embed(
                    title="✅ Usuario Expulsado",
                    description=f"{member.mention} ha sido expulsado exitosamente.",
                    color=nextcord.Color.green()
                )
                success_embed.add_field(name="Razón", value=reason, inline=False)
                success_embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
                
                await message.edit(embed=success_embed, view=None)
                logger.info(f"{member} fue expulsado por {ctx.author} - Razón: {reason}")
            else:
                cancel_embed = nextcord.Embed(
                    title="❌ Expulsión Cancelada",
                    description="La acción de expulsión ha sido cancelada.",
                    color=nextcord.Color.gray()
                )
                await message.edit(embed=cancel_embed, view=None)
                
        except nextcord.Forbidden:
            await ctx.send("❌ No tengo permisos para expulsar a este usuario.")
        except Exception as e:
            logger.error(f"Error en comando kick: {e}")
            await ctx.send("❌ Ocurrió un error al intentar expulsar al usuario.")
    
    @nextcord.slash_command(name="kick", description="Expulsa a un miembro del servidor")
    async def slash_kick(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        reason: str = "No se proporcionó razón"
    ):
        """Comando slash para expulsar usuarios"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        class MockContext:
            def __init__(self, interaction):
                self.author = interaction.user
                self.guild = interaction.guild
                self.channel = interaction.channel
                self.send = interaction.followup.send
                
        ctx = MockContext(interaction)
        await self.kick_member(ctx, member, reason=reason)
    
    @commands.command(name='clear', aliases=['purge'])
    @commands.has_permissions(administrator=True)
    async def clear_messages(self, ctx, amount: int = 5):
        """
        Elimina una cantidad específica de mensajes
        Uso: !clear [cantidad] (máximo 100)
        """
        try:
            # Verificar límites
            if amount < 1:
                await ctx.send("❌ La cantidad debe ser mayor a 0.")
                return
            
            if amount > 100:
                await ctx.send("❌ Solo puedo eliminar hasta 100 mensajes a la vez.")
                return
            
            # Confirmar la acción
            embed = nextcord.Embed(
                title="⚠️ Confirmación de Limpieza",
                description=f"¿Estás seguro de que quieres eliminar {amount} mensajes?",
                color=nextcord.Color.orange()
            )
            embed.add_field(name="Canal", value=ctx.channel.mention, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
            
            view = ConfirmationView(ctx.author)
            message = await ctx.send(embed=embed, view=view)
            
            await view.wait()
            
            if view.confirmed:
                # Eliminar el mensaje de confirmación primero
                await message.delete()
                
                # Eliminar los mensajes
                deleted = await ctx.channel.purge(limit=amount + 1)  # +1 para incluir el comando original
                
                # Confirmar la acción con un mensaje temporal
                success_embed = nextcord.Embed(
                    title="✅ Mensajes Eliminados",
                    description=f"Se eliminaron {len(deleted)-1} mensajes exitosamente.",
                    color=nextcord.Color.green()
                )
                success_embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
                
                # Mensaje temporal que se auto-elimina
                temp_msg = await ctx.send(embed=success_embed)
                await temp_msg.delete(delay=5)
                
                logger.info(f"{len(deleted)-1} mensajes eliminados por {ctx.author} en {ctx.channel}")
            else:
                cancel_embed = nextcord.Embed(
                    title="❌ Limpieza Cancelada",
                    description="La eliminación de mensajes ha sido cancelada.",
                    color=nextcord.Color.gray()
                )
                await message.edit(embed=cancel_embed, view=None)
                
        except nextcord.Forbidden:
            await ctx.send("❌ No tengo permisos para eliminar mensajes en este canal.")
        except Exception as e:
            logger.error(f"Error en comando clear: {e}")
            await ctx.send("❌ Ocurrió un error al intentar eliminar los mensajes.")
    
    @nextcord.slash_command(name="clear", description="Elimina una cantidad específica de mensajes")
    async def slash_clear(
        self,
        interaction: nextcord.Interaction,
        amount: int = nextcord.SlashOption(description="Cantidad de mensajes a eliminar", min_value=1, max_value=1000)
    ):
        """Comando slash para limpiar mensajes"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        class MockContext:
            def __init__(self, interaction):
                self.author = interaction.user
                self.guild = interaction.guild
                self.channel = interaction.channel
                self.send = interaction.followup.send
                
        ctx = MockContext(interaction)
        await self.clear_messages(ctx, amount)

class ConfirmationView(nextcord.ui.View):
    """Vista con botones de confirmación para acciones de moderación"""
    
    def __init__(self, author):
        super().__init__(timeout=30)
        self.author = author
        self.confirmed = None
    
    @nextcord.ui.button(label="✅ Confirmar", style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Solo el moderador que ejecutó el comando puede confirmar.", ephemeral=True)
            return
        
        self.confirmed = True
        self.stop()
    
    @nextcord.ui.button(label="❌ Cancelar", style=nextcord.ButtonStyle.red)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Solo el moderador que ejecutó el comando puede cancelar.", ephemeral=True)
            return
        
        self.confirmed = False
        self.stop()
    
    async def on_timeout(self):
        self.confirmed = False

def setup(bot):
    """Función setup para cargar el cog"""
    return Moderation(bot)
