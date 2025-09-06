"""
Sistema de logs y registros del servidor
por davito
"""

import logging
import json
import os
from datetime import datetime
import nextcord
from nextcord.ext import commands

logger = logging.getLogger(__name__)

class LoggingSystem(commands.Cog):
    """sistema de logs completo del servidor"""
    
    def __init__(self, bot):
        self.bot = bot
        self.log_channels = {}  # guild_id: channel_id
        self.config_file = "data/logging_config.json"
        self.load_config()
        
        # crear directorio si no existe
        os.makedirs("data", exist_ok=True)
    
    def load_config(self):
        """cargar configuración de logs"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.log_channels = {int(k): v for k, v in data.get('log_channels', {}).items()}
        except Exception as e:
            logger.error(f"error cargando config de logs: {e}")
    
    def save_config(self):
        """guardar configuración de logs"""
        try:
            config = {
                'log_channels': {str(k): v for k, v in self.log_channels.items()}
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando config de logs: {e}")
    
    async def send_log(self, guild_id: int, embed: nextcord.Embed):
        """enviar log al canal configurado"""
        try:
            if guild_id in self.log_channels:
                channel = self.bot.get_channel(self.log_channels[guild_id])
                if channel:
                    await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"error enviando log: {e}")
    
    @commands.command(name='setlogs')
    @commands.has_permissions(manage_guild=True)
    async def set_log_channel(self, ctx, channel: nextcord.TextChannel = None):
        """
        configurar canal de logs
        uso: !setlogs [#canal]
        """
        try:
            if channel is None:
                channel = ctx.channel
            
            # verificar permisos
            permissions = channel.permissions_for(ctx.guild.me)
            if not permissions.send_messages or not permissions.embed_links:
                await ctx.send("❌ no tengo permisos necesarios en ese canal.")
                return
            
            self.log_channels[ctx.guild.id] = channel.id
            self.save_config()
            
            embed = nextcord.Embed(
                title="📝 canal de logs configurado",
                description=f"los logs se enviarán a {channel.mention}",
                color=nextcord.Color.green()
            )
            embed.add_field(name="configurado por", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            
            # mensaje de prueba en el canal de logs
            test_embed = nextcord.Embed(
                title="✅ sistema de logs activado",
                description="este canal recibirá todos los logs del servidor",
                color=nextcord.Color.blue(),
                timestamp=datetime.now()
            )
            test_embed.set_footer(text="sistema de logs por davito")
            
            await channel.send(embed=test_embed)
            logger.info(f"canal de logs configurado en {ctx.guild.name}: {channel.name}")
            
        except Exception as e:
            logger.error(f"error configurando logs: {e}")
            await ctx.send("❌ error al configurar canal de logs.")
    
    @commands.command(name='removelogs')
    @commands.has_permissions(manage_guild=True)
    async def remove_log_channel(self, ctx):
        """
        desactivar logs
        uso: !removelogs
        """
        try:
            if ctx.guild.id in self.log_channels:
                del self.log_channels[ctx.guild.id]
                self.save_config()
                
                embed = nextcord.Embed(
                    title="📝 logs desactivados",
                    description="el sistema de logs ha sido desactivado",
                    color=nextcord.Color.orange()
                )
                embed.add_field(name="desactivado por", value=ctx.author.mention, inline=True)
                
                await ctx.send(embed=embed)
                logger.info(f"logs desactivados en {ctx.guild.name}")
            else:
                await ctx.send("❌ no hay canal de logs configurado.")
                
        except Exception as e:
            logger.error(f"error desactivando logs: {e}")
            await ctx.send("❌ error al desactivar logs.")
    
    # eventos de mensajes
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """log de mensajes eliminados"""
        if message.author.bot or not message.guild:
            return
        
        try:
            embed = nextcord.Embed(
                title="🗑️ mensaje eliminado",
                color=nextcord.Color.red(),
                timestamp=datetime.now()
            )
            embed.add_field(name="autor", value=f"{message.author.mention} ({message.author})", inline=True)
            embed.add_field(name="canal", value=message.channel.mention, inline=True)
            embed.add_field(name="id del mensaje", value=message.id, inline=True)
            
            if message.content:
                content = message.content[:1000] + "..." if len(message.content) > 1000 else message.content
                embed.add_field(name="contenido", value=f"```{content}```", inline=False)
            
            if message.attachments:
                files = [f"[{att.filename}]({att.url})" for att in message.attachments]
                embed.add_field(name="archivos", value="\n".join(files), inline=False)
            
            embed.set_footer(text=f"id del autor: {message.author.id}")
            
            await self.send_log(message.guild.id, embed)
            
        except Exception as e:
            logger.error(f"error en log de mensaje eliminado: {e}")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """log de mensajes editados"""
        if before.author.bot or not before.guild or before.content == after.content:
            return
        
        try:
            embed = nextcord.Embed(
                title="✏️ mensaje editado",
                color=nextcord.Color.orange(),
                timestamp=datetime.now()
            )
            embed.add_field(name="autor", value=f"{before.author.mention} ({before.author})", inline=True)
            embed.add_field(name="canal", value=before.channel.mention, inline=True)
            embed.add_field(name="id del mensaje", value=before.id, inline=True)
            
            if before.content:
                old_content = before.content[:500] + "..." if len(before.content) > 500 else before.content
                embed.add_field(name="contenido anterior", value=f"```{old_content}```", inline=False)
            
            if after.content:
                new_content = after.content[:500] + "..." if len(after.content) > 500 else after.content
                embed.add_field(name="contenido nuevo", value=f"```{new_content}```", inline=False)
            
            embed.set_footer(text=f"id del autor: {before.author.id}")
            
            await self.send_log(before.guild.id, embed)
            
        except Exception as e:
            logger.error(f"error en log de mensaje editado: {e}")
    
    # eventos de miembros
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """log de usuarios que se unen"""
        try:
            embed = nextcord.Embed(
                title="📥 usuario se unió",
                color=nextcord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name="usuario", value=f"{member.mention} ({member})", inline=True)
            embed.add_field(name="id", value=member.id, inline=True)
            embed.add_field(name="cuenta creada", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
            embed.add_field(name="miembros totales", value=member.guild.member_count, inline=True)
            
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)
            
            # verificar si es cuenta nueva (menos de 7 días)
            account_age = (datetime.now() - member.created_at.replace(tzinfo=None)).days
            if account_age < 7:
                embed.add_field(name="⚠️ advertencia", value=f"cuenta nueva ({account_age} días)", inline=False)
            
            embed.set_footer(text="usuario se unió al servidor")
            
            await self.send_log(member.guild.id, embed)
            
        except Exception as e:
            logger.error(f"error en log de member join: {e}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """log de usuarios que se van"""
        try:
            embed = nextcord.Embed(
                title="📤 usuario se fue",
                color=nextcord.Color.red(),
                timestamp=datetime.now()
            )
            embed.add_field(name="usuario", value=f"{member} ({member.id})", inline=True)
            embed.add_field(name="se unió", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "desconocido", inline=True)
            embed.add_field(name="miembros restantes", value=member.guild.member_count, inline=True)
            
            if member.roles and len(member.roles) > 1:  # excluir @everyone
                roles = [role.mention for role in member.roles[1:]][:10]  # máximo 10 roles
                embed.add_field(name="roles", value=" ".join(roles), inline=False)
            
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)
            
            embed.set_footer(text="usuario abandonó el servidor")
            
            await self.send_log(member.guild.id, embed)
            
        except Exception as e:
            logger.error(f"error en log de member remove: {e}")
    
    # eventos de voz
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """log de cambios en canales de voz"""
        if member.bot:
            return
        
        try:
            # usuario se conectó a un canal
            if before.channel is None and after.channel is not None:
                embed = nextcord.Embed(
                    title="🔊 conexión a canal de voz",
                    color=nextcord.Color.green(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="usuario", value=f"{member.mention} ({member})", inline=True)
                embed.add_field(name="canal", value=after.channel.name, inline=True)
                embed.set_footer(text=f"id del usuario: {member.id}")
                
                await self.send_log(member.guild.id, embed)
            
            # usuario se desconectó de un canal
            elif before.channel is not None and after.channel is None:
                embed = nextcord.Embed(
                    title="🔇 desconexión de canal de voz",
                    color=nextcord.Color.red(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="usuario", value=f"{member.mention} ({member})", inline=True)
                embed.add_field(name="canal", value=before.channel.name, inline=True)
                embed.set_footer(text=f"id del usuario: {member.id}")
                
                await self.send_log(member.guild.id, embed)
            
            # usuario cambió de canal
            elif before.channel != after.channel and before.channel is not None and after.channel is not None:
                embed = nextcord.Embed(
                    title="🔄 cambio de canal de voz",
                    color=nextcord.Color.blue(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="usuario", value=f"{member.mention} ({member})", inline=True)
                embed.add_field(name="canal anterior", value=before.channel.name, inline=True)
                embed.add_field(name="canal nuevo", value=after.channel.name, inline=True)
                embed.set_footer(text=f"id del usuario: {member.id}")
                
                await self.send_log(member.guild.id, embed)
                
        except Exception as e:
            logger.error(f"error en log de voice state: {e}")
    
    # eventos de moderación
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """log de usuarios baneados"""
        try:
            embed = nextcord.Embed(
                title="🔨 usuario baneado",
                color=nextcord.Color.dark_red(),
                timestamp=datetime.now()
            )
            embed.add_field(name="usuario", value=f"{user} ({user.id})", inline=True)
            
            # intentar obtener info del ban
            try:
                ban_info = await guild.fetch_ban(user)
                if ban_info.reason:
                    embed.add_field(name="razón", value=ban_info.reason, inline=False)
            except:
                pass
            
            if user.avatar:
                embed.set_thumbnail(url=user.avatar.url)
            
            embed.set_footer(text="usuario baneado del servidor")
            
            await self.send_log(guild.id, embed)
            
        except Exception as e:
            logger.error(f"error en log de ban: {e}")
    
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        """log de usuarios desbaneados"""
        try:
            embed = nextcord.Embed(
                title="🔓 usuario desbaneado",
                color=nextcord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name="usuario", value=f"{user} ({user.id})", inline=True)
            
            if user.avatar:
                embed.set_thumbnail(url=user.avatar.url)
            
            embed.set_footer(text="usuario desbaneado del servidor")
            
            await self.send_log(guild.id, embed)
            
        except Exception as e:
            logger.error(f"error en log de unban: {e}")
    
    # eventos de roles
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """log de cambios de roles"""
        if before.roles != after.roles:
            try:
                added_roles = set(after.roles) - set(before.roles)
                removed_roles = set(before.roles) - set(after.roles)
                
                if added_roles or removed_roles:
                    embed = nextcord.Embed(
                        title="👑 cambio de roles",
                        color=nextcord.Color.blue(),
                        timestamp=datetime.now()
                    )
                    embed.add_field(name="usuario", value=f"{after.mention} ({after})", inline=True)
                    
                    if added_roles:
                        roles = [role.mention for role in added_roles]
                        embed.add_field(name="roles añadidos", value=" ".join(roles), inline=False)
                    
                    if removed_roles:
                        roles = [role.mention for role in removed_roles]
                        embed.add_field(name="roles removidos", value=" ".join(roles), inline=False)
                    
                    embed.set_footer(text=f"id del usuario: {after.id}")
                    
                    await self.send_log(after.guild.id, embed)
                    
            except Exception as e:
                logger.error(f"error en log de role update: {e}")
    
    @commands.command(name='logstatus')
    @commands.has_permissions(manage_guild=True)
    async def log_status(self, ctx):
        """
        ver estado del sistema de logs
        uso: !logstatus
        """
        try:
            if ctx.guild.id in self.log_channels:
                channel = self.bot.get_channel(self.log_channels[ctx.guild.id])
                status = f"✅ activo en {channel.mention}" if channel else "❌ canal no encontrado"
            else:
                status = "❌ desactivado"
            
            embed = nextcord.Embed(
                title="📊 estado del sistema de logs",
                color=nextcord.Color.blue()
            )
            embed.add_field(name="estado", value=status, inline=False)
            embed.add_field(
                name="eventos registrados",
                value="• mensajes eliminados/editados\n• entradas/salidas de usuarios\n• cambios de canal de voz\n• bans/unbans\n• cambios de roles",
                inline=False
            )
            embed.add_field(
                name="comandos",
                value="• `!setlogs #canal` - activar logs\n• `!removelogs` - desactivar logs",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error en log status: {e}")
            await ctx.send("❌ error al obtener estado de logs.")

def setup(bot):
    """Función setup para cargar el cog"""
    return LoggingSystem(bot)
