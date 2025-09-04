"""
Sistema anti-spam y anti-raids
por davito
"""

import logging
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, deque
import nextcord
from nextcord.ext import commands, tasks

logger = logging.getLogger(__name__)

class AntiSpam(commands.Cog):
    """sistema anti-spam y anti-raids"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # configuración anti-spam
        self.message_counts = defaultdict(lambda: deque())
        self.spam_threshold = 5  # mensajes
        self.spam_window = 10  # segundos
        self.muted_users = defaultdict(lambda: None)
        
        # configuración anti-raid
        self.join_counts = defaultdict(lambda: deque())
        self.raid_threshold = 10  # usuarios
        self.raid_window = 60  # segundos
        self.lockdown_channels = set()
        
        # configuración detección
        self.spam_patterns = [
            r'(.)\1{10,}',  # caracteres repetidos
            r'[A-Z]{10,}',  # mayúsculas excesivas
            r'[@]{3,}',     # menciones spam
            r'[!?]{5,}',    # signos excesivos
        ]
        
        # limpieza automática cada 5 minutos
        self.cleanup_task.start()
    
    def cog_unload(self):
        """detener tareas al descargar"""
        self.cleanup_task.cancel()
    
    @tasks.loop(minutes=5)
    async def cleanup_task(self):
        """limpiar datos antiguos"""
        now = datetime.now()
        
        # limpiar conteos de mensajes
        for user_id in list(self.message_counts.keys()):
            timestamps = self.message_counts[user_id]
            while timestamps and (now - timestamps[0]).seconds > self.spam_window:
                timestamps.popleft()
            
            if not timestamps:
                del self.message_counts[user_id]
        
        # limpiar conteos de joins
        for guild_id in list(self.join_counts.keys()):
            timestamps = self.join_counts[guild_id]
            while timestamps and (now - timestamps[0]).seconds > self.raid_window:
                timestamps.popleft()
            
            if not timestamps:
                del self.join_counts[guild_id]
    
    @cleanup_task.before_loop
    async def before_cleanup(self):
        """esperar a que el bot esté listo"""
        await self.bot.wait_until_ready()
    
    def is_spam(self, message):
        """detectar si un mensaje es spam"""
        import re
        
        # verificar patrones de spam
        content = message.content.lower()
        
        for pattern in self.spam_patterns:
            if re.search(pattern, content):
                return True
        
        # verificar enlaces sospechosos
        suspicious_domains = [
            'discord.gg/', 'discordapp.com/invite/',
            'bit.ly/', 'tinyurl.com/', 'shorturl.at/'
        ]
        
        for domain in suspicious_domains:
            if domain in content:
                return True
        
        # verificar contenido duplicado reciente
        user_id = message.author.id
        now = datetime.now()
        
        # añadir timestamp actual
        self.message_counts[user_id].append(now)
        
        # contar mensajes en ventana de tiempo
        recent_messages = [
            ts for ts in self.message_counts[user_id]
            if (now - ts).seconds <= self.spam_window
        ]
        
        return len(recent_messages) > self.spam_threshold
    
    def is_raid(self, guild):
        """detectar si hay un raid en curso"""
        now = datetime.now()
        
        # contar joins recientes
        recent_joins = [
            ts for ts in self.join_counts[guild.id]
            if (now - ts).seconds <= self.raid_window
        ]
        
        return len(recent_joins) > self.raid_threshold
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """procesar mensajes para detectar spam"""
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        try:
            # verificar si el usuario está silenciado
            if self.muted_users[message.author.id]:
                mute_end = self.muted_users[message.author.id]
                if datetime.now() < mute_end:
                    try:
                        await message.delete()
                        return
                    except:
                        pass
                else:
                    self.muted_users[message.author.id] = None
            
            # detectar spam
            if self.is_spam(message):
                await self.handle_spam(message)
                
        except Exception as e:
            logger.error(f"error procesando mensaje para spam: {e}")
    
    async def handle_spam(self, message):
        """manejar detección de spam"""
        try:
            # borrar mensaje
            await message.delete()
            
            # silenciar usuario temporalmente
            mute_duration = timedelta(minutes=10)
            self.muted_users[message.author.id] = datetime.now() + mute_duration
            
            # intentar timeout si es posible
            try:
                await message.author.timeout(mute_duration, reason="spam detectado")
                action = "silenciado"
            except:
                action = "mensaje eliminado"
            
            # notificar
            embed = nextcord.Embed(
                title="🚫 spam detectado",
                description=f"{message.author.mention} ha sido {action} por spam.",
                color=nextcord.Color.red()
            )
            embed.add_field(name="duración", value="10 minutos", inline=True)
            embed.add_field(name="razón", value="comportamiento de spam", inline=True)
            embed.set_footer(text="sistema anti-spam automático")
            
            await message.channel.send(embed=embed, delete_after=10)
            
            logger.info(f"spam detectado de {message.author} en {message.guild}")
            
        except Exception as e:
            logger.error(f"error manejando spam: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """detectar raids por joins masivos"""
        try:
            now = datetime.now()
            self.join_counts[member.guild.id].append(now)
            
            if self.is_raid(member.guild):
                await self.handle_raid(member.guild)
                
        except Exception as e:
            logger.error(f"error detectando raid: {e}")
    
    async def handle_raid(self, guild):
        """manejar detección de raid"""
        try:
            # bloquear canales principales
            channels_locked = []
            
            for channel in guild.text_channels:
                if channel.name in ['general', 'chat', 'bienvenida', 'principal']:
                    try:
                        # denegar envío de mensajes para @everyone
                        overwrite = nextcord.PermissionOverwrite(send_messages=False)
                        await channel.set_permissions(guild.default_role, overwrite=overwrite)
                        channels_locked.append(channel.name)
                        self.lockdown_channels.add(channel.id)
                    except:
                        pass
            
            # notificar a moderadores
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    embed = nextcord.Embed(
                        title="🚨 raid detectado",
                        description="se han detectado joins masivos sospechosos.",
                        color=nextcord.Color.red()
                    )
                    embed.add_field(
                        name="acción tomada",
                        value=f"canales bloqueados: {', '.join(channels_locked) if channels_locked else 'ninguno'}",
                        inline=False
                    )
                    embed.add_field(
                        name="recomendación",
                        value="revisar miembros recientes y usar `!unlockdown` cuando sea seguro",
                        inline=False
                    )
                    embed.set_footer(text="sistema anti-raid automático")
                    
                    await channel.send(embed=embed)
                    break
            
            logger.warning(f"raid detectado en {guild.name}")
            
        except Exception as e:
            logger.error(f"error manejando raid: {e}")
    
    @commands.command(name='antispam')
    @commands.has_permissions(manage_guild=True)
    async def toggle_antispam(self, ctx, estado: str = None):
        """
        configurar sistema anti-spam
        uso: !antispam [on/off]
        """
        try:
            if estado is None:
                embed = nextcord.Embed(
                    title="🛡️ configuración anti-spam",
                    color=nextcord.Color.blue()
                )
                embed.add_field(name="umbral de spam", value=f"{self.spam_threshold} mensajes", inline=True)
                embed.add_field(name="ventana de tiempo", value=f"{self.spam_window} segundos", inline=True)
                embed.add_field(name="duración silencio", value="10 minutos", inline=True)
                embed.add_field(name="estado", value="✅ activo", inline=False)
                
                await ctx.send(embed=embed)
                return
            
            await ctx.send("ℹ️ el sistema anti-spam está siempre activo. usa `!antispam` para ver configuración.")
            
        except Exception as e:
            logger.error(f"error en comando antispam: {e}")
            await ctx.send("❌ error al configurar anti-spam.")
    
    @commands.command(name='lockdown')
    @commands.has_permissions(manage_guild=True)
    async def lockdown(self, ctx, *channels: nextcord.TextChannel):
        """
        bloquear canales manualmente
        uso: !lockdown [#canal1 #canal2...]
        """
        try:
            if not channels:
                channels = [ctx.channel]
            
            locked = []
            for channel in channels:
                try:
                    overwrite = nextcord.PermissionOverwrite(send_messages=False)
                    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                    self.lockdown_channels.add(channel.id)
                    locked.append(channel.mention)
                except:
                    pass
            
            if locked:
                embed = nextcord.Embed(
                    title="🔒 canales bloqueados",
                    description=f"canales bloqueados: {', '.join(locked)}",
                    color=nextcord.Color.orange()
                )
                embed.add_field(name="moderador", value=ctx.author.mention, inline=True)
                embed.set_footer(text="usa !unlockdown para desbloquear")
                
                await ctx.send(embed=embed)
                logger.info(f"lockdown activado por {ctx.author} en {len(locked)} canales")
            else:
                await ctx.send("❌ no se pudieron bloquear canales.")
                
        except Exception as e:
            logger.error(f"error en lockdown: {e}")
            await ctx.send("❌ error al bloquear canales.")
    
    @commands.command(name='unlockdown')
    @commands.has_permissions(manage_guild=True)
    async def unlockdown(self, ctx):
        """
        desbloquear todos los canales
        uso: !unlockdown
        """
        try:
            unlocked = []
            
            for channel_id in list(self.lockdown_channels):
                channel = self.bot.get_channel(channel_id)
                if channel and channel.guild == ctx.guild:
                    try:
                        overwrite = nextcord.PermissionOverwrite(send_messages=None)
                        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
                        unlocked.append(channel.mention)
                        self.lockdown_channels.remove(channel_id)
                    except:
                        pass
            
            if unlocked:
                embed = nextcord.Embed(
                    title="🔓 canales desbloqueados",
                    description=f"canales desbloqueados: {', '.join(unlocked)}",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="moderador", value=ctx.author.mention, inline=True)
                
                await ctx.send(embed=embed)
                logger.info(f"unlockdown activado por {ctx.author}")
            else:
                await ctx.send("ℹ️ no hay canales bloqueados.")
                
        except Exception as e:
            logger.error(f"error en unlockdown: {e}")
            await ctx.send("❌ error al desbloquear canales.")
    
    @commands.command(name='unmute')
    @commands.has_permissions(moderate_members=True)
    async def unmute_user(self, ctx, member: nextcord.Member):
        """
        quitar silencio manual de un usuario
        uso: !unmute @usuario
        """
        try:
            # quitar del sistema interno
            if self.muted_users[member.id]:
                self.muted_users[member.id] = None
            
            # quitar timeout de discord
            try:
                await member.edit(timed_out_until=None, reason=f"unmuteado por {ctx.author}")
                
                embed = nextcord.Embed(
                    title="🔊 usuario desmuteado",
                    description=f"{member.mention} ya puede hablar.",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="moderador", value=ctx.author.mention, inline=True)
                
                await ctx.send(embed=embed)
                logger.info(f"{member} desmuteado por {ctx.author}")
                
            except Exception as e:
                await ctx.send(f"⚠️ eliminado del sistema interno, pero error con timeout: {str(e)}")
                
        except Exception as e:
            logger.error(f"error en unmute: {e}")
            await ctx.send("❌ error al desmutear usuario.")
