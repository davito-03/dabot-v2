"""
Sistema de Canales de Estadísticas y Escenario v2.0
Incluye canales de voz con estadísticas automáticas y escenario
Por davito - Dabot v2
"""

import logging
import nextcord
from nextcord.ext import commands, tasks
import sqlite3
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class StatsDB:
    """manejo de base de datos para estadísticas"""
    
    def __init__(self, db_path: str = "data/stats.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """inicializar base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS stats_config (
                        guild_id INTEGER PRIMARY KEY,
                        member_count_channel INTEGER,
                        bot_count_channel INTEGER,
                        total_count_channel INTEGER,
                        invite_channel INTEGER,
                        stage_channel INTEGER,
                        enabled BOOLEAN DEFAULT 1
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS server_stats (
                        guild_id INTEGER,
                        date TEXT,
                        member_count INTEGER,
                        bot_count INTEGER,
                        total_channels INTEGER,
                        total_roles INTEGER,
                        PRIMARY KEY (guild_id, date)
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error inicializando base de datos de estadísticas: {e}")
    
    def set_config(self, guild_id: int, member_count_channel: int = None, bot_count_channel: int = None, 
                   total_count_channel: int = None, invite_channel: int = None, stage_channel: int = None):
        """configurar canales de estadísticas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO stats_config (guild_id, member_count_channel, bot_count_channel, total_count_channel, invite_channel, stage_channel) VALUES (?, ?, ?, ?, ?, ?)",
                    (guild_id, member_count_channel, bot_count_channel, total_count_channel, invite_channel, stage_channel)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error configurando estadísticas: {e}")
    
    def get_config(self, guild_id: int):
        """obtener configuración de estadísticas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM stats_config WHERE guild_id = ?",
                    (guild_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error obteniendo configuración: {e}")
            return None
    
    def save_daily_stats(self, guild_id: int, member_count: int, bot_count: int, total_channels: int, total_roles: int):
        """guardar estadísticas diarias"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO server_stats (guild_id, date, member_count, bot_count, total_channels, total_roles) VALUES (?, ?, ?, ?, ?, ?)",
                    (guild_id, today, member_count, bot_count, total_channels, total_roles)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error guardando estadísticas diarias: {e}")

class ServerStats(commands.Cog):
    """sistema de estadísticas del servidor"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = StatsDB()
        
        # Iniciar tareas
        self.update_stats.start()
        self.daily_stats_save.start()
    
    def cog_unload(self):
        """detener tareas al descargar"""
        self.update_stats.cancel()
        self.daily_stats_save.cancel()
    
    @nextcord.slash_command(name="stats", description="comandos de estadísticas del servidor")
    async def stats_group(self, interaction: nextcord.Interaction):
        pass
    
    @stats_group.subcommand(name="setup", description="configurar canales de estadísticas")
    async def setup_stats(self, interaction: nextcord.Interaction):
        """configurar canales de estadísticas automáticamente"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Necesitas permisos de gestionar servidor.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            
            # Crear categoría de estadísticas
            stats_category = await guild.create_category("📊 ESTADÍSTICAS DEL SERVIDOR")
            
            # Crear canales de estadísticas
            member_count = len([m for m in guild.members if not m.bot])
            bot_count = len([m for m in guild.members if m.bot])
            total_count = len(guild.members)
            
            # Canal de miembros
            member_channel = await guild.create_voice_channel(
                f"👥 Miembros: {member_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={
                    guild.default_role: nextcord.PermissionOverwrite(connect=False)
                }
            )
            
            # Canal de bots
            bot_channel = await guild.create_voice_channel(
                f"🤖 Bots: {bot_count}",
                category=stats_category,
                user_limit=0,
                overwrites={
                    guild.default_role: nextcord.PermissionOverwrite(connect=False)
                }
            )
            
            # Canal total
            total_channel = await guild.create_voice_channel(
                f"📈 Total: {total_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={
                    guild.default_role: nextcord.PermissionOverwrite(connect=False)
                }
            )
            
            # Canal de invitación
            try:
                invite = await interaction.channel.create_invite(
                    max_age=0,  # Sin expiración
                    max_uses=0,  # Sin límite de usos
                    reason="Canal de invitación automática"
                )
                invite_url = invite.url
            except:
                invite_url = "discord.gg/tu-servidor"
            
            invite_channel = await guild.create_voice_channel(
                f"🔗 {invite_url.split('/')[-1]}",
                category=stats_category,
                user_limit=0,
                overwrites={
                    guild.default_role: nextcord.PermissionOverwrite(connect=False)
                }
            )
            
            # Canal de escenario
            stage_channel = await guild.create_stage_channel(
                "🎭 Escenario Principal",
                category=stats_category,
                topic="Canal de escenario para eventos especiales"
            )
            
            # Configurar en base de datos
            self.db.set_config(
                guild.id,
                member_channel.id,
                bot_channel.id,
                total_channel.id,
                invite_channel.id,
                stage_channel.id
            )
            
            # Mensaje de confirmación
            embed = nextcord.Embed(
                title="📊 Estadísticas Configuradas",
                description="Canales de estadísticas creados exitosamente",
                color=nextcord.Color.green()
            )
            embed.add_field(
                name="📈 Canales Creados",
                value=f"• {member_channel.mention} - Contador de miembros\n• {bot_channel.mention} - Contador de bots\n• {total_channel.mention} - Total de usuarios\n• {invite_channel.mention} - Link de invitación\n• {stage_channel.mention} - Canal de escenario",
                inline=False
            )
            embed.add_field(
                name="🔄 Actualización",
                value="Los contadores se actualizan automáticamente cada 10 minutos",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error configurando estadísticas: {e}")
            await interaction.followup.send("❌ Error al configurar las estadísticas.")
    
    @tasks.loop(minutes=10)
    async def update_stats(self):
        """actualizar estadísticas de todos los servidores"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.execute("SELECT * FROM stats_config WHERE enabled = 1")
                configs = cursor.fetchall()
            
            for config in configs:
                guild_id = config[0]
                guild = self.bot.get_guild(guild_id)
                
                if not guild:
                    continue
                
                # Calcular estadísticas
                member_count = len([m for m in guild.members if not m.bot])
                bot_count = len([m for m in guild.members if m.bot])
                total_count = len(guild.members)
                
                # Actualizar canales
                if config[1]:  # member_count_channel
                    channel = guild.get_channel(config[1])
                    if channel:
                        try:
                            await channel.edit(name=f"👥 Miembros: {member_count:,}")
                        except:
                            pass
                
                if config[2]:  # bot_count_channel
                    channel = guild.get_channel(config[2])
                    if channel:
                        try:
                            await channel.edit(name=f"🤖 Bots: {bot_count}")
                        except:
                            pass
                
                if config[3]:  # total_count_channel
                    channel = guild.get_channel(config[3])
                    if channel:
                        try:
                            await channel.edit(name=f"📈 Total: {total_count:,}")
                        except:
                            pass
        
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
    
    @tasks.loop(hours=24)
    async def daily_stats_save(self):
        """guardar estadísticas diarias"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.execute("SELECT guild_id FROM stats_config WHERE enabled = 1")
                guild_ids = [row[0] for row in cursor.fetchall()]
            
            for guild_id in guild_ids:
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    continue
                
                member_count = len([m for m in guild.members if not m.bot])
                bot_count = len([m for m in guild.members if m.bot])
                total_channels = len(guild.channels)
                total_roles = len(guild.roles)
                
                self.db.save_daily_stats(guild_id, member_count, bot_count, total_channels, total_roles)
        
        except Exception as e:
            logger.error(f"Error guardando estadísticas diarias: {e}")
    
    @stats_group.subcommand(name="servidor", description="ver estadísticas detalladas del servidor")
    async def server_stats(self, interaction: nextcord.Interaction):
        """mostrar estadísticas detalladas del servidor"""
        guild = interaction.guild
        
        # Estadísticas de miembros
        total_members = len(guild.members)
        human_members = len([m for m in guild.members if not m.bot])
        bot_members = len([m for m in guild.members if m.bot])
        online_members = len([m for m in guild.members if m.status != nextcord.Status.offline])
        
        # Estadísticas de canales
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        stage_channels = len(guild.stage_channels)
        categories = len(guild.categories)
        
        # Estadísticas de roles
        total_roles = len(guild.roles)
        
        # Información del servidor
        created_at = guild.created_at
        owner = guild.owner
        
        embed = nextcord.Embed(
            title=f"📊 Estadísticas de {guild.name}",
            color=nextcord.Color.blue(),
            timestamp=nextcord.utils.utcnow()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Miembros
        embed.add_field(
            name="👥 Miembros",
            value=f"**Total:** {total_members:,}\n**Humanos:** {human_members:,}\n**Bots:** {bot_members}\n**En línea:** {online_members:,}",
            inline=True
        )
        
        # Canales
        embed.add_field(
            name="📺 Canales",
            value=f"**Texto:** {text_channels}\n**Voz:** {voice_channels}\n**Escenario:** {stage_channels}\n**Categorías:** {categories}",
            inline=True
        )
        
        # Otros
        embed.add_field(
            name="🎭 Servidor",
            value=f"**Roles:** {total_roles}\n**Owner:** {owner.mention if owner else 'Desconocido'}\n**Creado:** {created_at.strftime('%d/%m/%Y')}\n**Nivel:** {guild.premium_tier}",
            inline=True
        )
        
        # Características
        features = []
        if guild.features:
            feature_names = {
                'COMMUNITY': '🌟 Comunidad',
                'VERIFIED': '✅ Verificado',
                'PARTNERED': '🤝 Partner',
                'DISCOVERABLE': '🔍 Discoverable',
                'INVITE_SPLASH': '🎨 Splash de invitación',
                'BANNER': '🖼️ Banner',
                'VANITY_URL': '🔗 URL personalizada',
                'ANIMATED_ICON': '📸 Icono animado'
            }
            features = [feature_names.get(f, f) for f in guild.features[:5]]
        
        if features:
            embed.add_field(
                name="⭐ Características",
                value="\n".join(features),
                inline=False
            )
        
        embed.set_footer(text=f"ID del servidor: {guild.id}")
        
        await interaction.response.send_message(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """actualizar estadísticas cuando alguien se une"""
        await self.update_server_stats(member.guild)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """actualizar estadísticas cuando alguien se va"""
        await self.update_server_stats(member.guild)
    
    async def update_server_stats(self, guild):
        """actualizar estadísticas de un servidor específico"""
        try:
            config = self.db.get_config(guild.id)
            if not config:
                return
            
            member_count = len([m for m in guild.members if not m.bot])
            bot_count = len([m for m in guild.members if m.bot])
            total_count = len(guild.members)
            
            # Actualizar canales inmediatamente
            if config[1]:  # member_count_channel
                channel = guild.get_channel(config[1])
                if channel:
                    try:
                        await channel.edit(name=f"👥 Miembros: {member_count:,}")
                    except:
                        pass
            
            if config[2]:  # bot_count_channel
                channel = guild.get_channel(config[2])
                if channel:
                    try:
                        await channel.edit(name=f"🤖 Bots: {bot_count}")
                    except:
                        pass
            
            if config[3]:  # total_count_channel
                channel = guild.get_channel(config[3])
                if channel:
                    try:
                        await channel.edit(name=f"📈 Total: {total_count:,}")
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Error actualizando estadísticas del servidor: {e}")

def setup(bot):
    """cargar el cog"""
    bot.add_cog(ServerStats(bot))
