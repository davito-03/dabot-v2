"""
Sistema Unificado de Moderación
Incluye: moderación básica, warnings, appeals, roles de staff, automod
Por: Davito
"""

import logging
import nextcord
from nextcord.ext import commands
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json

logger = logging.getLogger(__name__)

class ModerationSystem(commands.Cog):
    """Sistema completo de moderación"""
    
    def __init__(self, bot):
        self.bot = bot
        self.init_database()
        
        # Cache de configuraciones de automod
        self.automod_config = {}
        
        # Filtros de palabras por defecto
        self.default_bad_words = [
            # Palabras ofensivas básicas (censuradas)
            "idiota", "estupido", "tonto", "imbecil"
        ]
    
    def init_database(self):
        """Inicializar base de datos de moderación"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            # Tabla de warnings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabla de bans temporales
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS temp_bans (
                    guild_id INTEGER,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    reason TEXT,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')
            
            # Tabla de appeals
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS appeals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER,
                    appeal_type TEXT,
                    reason TEXT,
                    status TEXT DEFAULT 'pending',
                    reviewed_by INTEGER,
                    reviewed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de configuración de automod
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS automod_config (
                    guild_id INTEGER PRIMARY KEY,
                    anti_spam BOOLEAN DEFAULT 0,
                    anti_links BOOLEAN DEFAULT 0,
                    anti_caps BOOLEAN DEFAULT 0,
                    word_filter BOOLEAN DEFAULT 0,
                    custom_words TEXT DEFAULT '[]',
                    punishment_type TEXT DEFAULT 'warn',
                    log_channel_id INTEGER,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de roles de staff
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS staff_roles (
                    guild_id INTEGER,
                    role_id INTEGER,
                    role_type TEXT,
                    permissions TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, role_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Base de datos de moderación inicializada")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos de moderación: {e}")
    
    # ================================
    # COMANDOS BÁSICOS DE MODERACIÓN
    # ================================
    
    @nextcord.slash_command(name="ban", description="Banear a un usuario")
    async def ban(
        self,
        interaction: nextcord.Interaction,
        usuario: nextcord.Member,
        razon: str = "No especificada",
        eliminar_mensajes: int = 0
    ):
        """Banear usuario"""
        if not await self.check_permissions(interaction, "ban_members"):
            return
        
        if usuario.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ No puedes banear a alguien con un rol igual o superior.", ephemeral=True)
            return
        
        try:
            # Enviar DM al usuario antes del ban
            try:
                dm_embed = nextcord.Embed(
                    title="🔨 Has sido baneado",
                    description=f"Fuiste baneado de **{interaction.guild.name}**",
                    color=nextcord.Color.red()
                )
                dm_embed.add_field(name="Razón", value=razon, inline=False)
                dm_embed.add_field(name="Moderador", value=interaction.user.mention, inline=False)
                await usuario.send(embed=dm_embed)
            except:
                pass  # No se pudo enviar DM
            
            # Banear usuario
            await usuario.ban(reason=f"{razon} | Moderador: {interaction.user}", delete_message_days=eliminar_mensajes)
            
            # Embed de confirmación
            embed = nextcord.Embed(
                title="🔨 Usuario Baneado",
                color=nextcord.Color.red()
            )
            embed.add_field(name="Usuario", value=f"{usuario} ({usuario.id})", inline=False)
            embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            embed.add_field(name="Razón", value=razon, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
            # Log del ban
            await self.log_moderation_action("ban", interaction.guild, interaction.user, usuario, razon)
            
        except Exception as e:
            logger.error(f"Error baneando usuario: {e}")
            await interaction.response.send_message("❌ Error baneando usuario.", ephemeral=True)
    
    @nextcord.slash_command(name="kick", description="Expulsar a un usuario")
    async def kick(
        self,
        interaction: nextcord.Interaction,
        usuario: nextcord.Member,
        razon: str = "No especificada"
    ):
        """Expulsar usuario"""
        if not await self.check_permissions(interaction, "kick_members"):
            return
        
        if usuario.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ No puedes expulsar a alguien con un rol igual o superior.", ephemeral=True)
            return
        
        try:
            # Enviar DM
            try:
                dm_embed = nextcord.Embed(
                    title="👢 Has sido expulsado",
                    description=f"Fuiste expulsado de **{interaction.guild.name}**",
                    color=nextcord.Color.orange()
                )
                dm_embed.add_field(name="Razón", value=razon, inline=False)
                dm_embed.add_field(name="Moderador", value=interaction.user.mention, inline=False)
                await usuario.send(embed=dm_embed)
            except:
                pass
            
            # Expulsar
            await usuario.kick(reason=f"{razon} | Moderador: {interaction.user}")
            
            embed = nextcord.Embed(
                title="👢 Usuario Expulsado",
                color=nextcord.Color.orange()
            )
            embed.add_field(name="Usuario", value=f"{usuario} ({usuario.id})", inline=False)
            embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            embed.add_field(name="Razón", value=razon, inline=True)
            
            await interaction.response.send_message(embed=embed)
            await self.log_moderation_action("kick", interaction.guild, interaction.user, usuario, razon)
            
        except Exception as e:
            logger.error(f"Error expulsando usuario: {e}")
            await interaction.response.send_message("❌ Error expulsando usuario.", ephemeral=True)
    
    @nextcord.slash_command(name="warn", description="Advertir a un usuario")
    async def warn(
        self,
        interaction: nextcord.Interaction,
        usuario: nextcord.Member,
        razon: str
    ):
        """Advertir usuario"""
        if not await self.check_permissions(interaction, "moderate_members"):
            return
        
        try:
            # Guardar warning en base de datos
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO warnings (guild_id, user_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
            ''', (interaction.guild.id, usuario.id, interaction.user.id, razon))
            
            warning_id = cursor.lastrowid
            
            # Contar warnings del usuario
            cursor.execute('''
                SELECT COUNT(*) FROM warnings 
                WHERE guild_id = ? AND user_id = ? AND active = 1
            ''', (interaction.guild.id, usuario.id))
            
            warning_count = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            
            # Enviar DM
            try:
                dm_embed = nextcord.Embed(
                    title="⚠️ Has recibido una advertencia",
                    description=f"En **{interaction.guild.name}**",
                    color=nextcord.Color.yellow()
                )
                dm_embed.add_field(name="Razón", value=razon, inline=False)
                dm_embed.add_field(name="Moderador", value=interaction.user.mention, inline=False)
                dm_embed.add_field(name="Total de Warnings", value=f"{warning_count}/3", inline=False)
                await usuario.send(embed=dm_embed)
            except:
                pass
            
            embed = nextcord.Embed(
                title="⚠️ Usuario Advertido",
                color=nextcord.Color.yellow()
            )
            embed.add_field(name="Usuario", value=f"{usuario} ({usuario.id})", inline=False)
            embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            embed.add_field(name="Razón", value=razon, inline=True)
            embed.add_field(name="Warning ID", value=f"#{warning_id}", inline=True)
            embed.add_field(name="Total Warnings", value=f"{warning_count}/3", inline=True)
            
            # Auto-ban si tiene 3 warnings
            if warning_count >= 3:
                try:
                    await usuario.ban(reason="Auto-ban: 3 warnings acumulados")
                    embed.add_field(
                        name="🔨 Auto-Ban",
                        value="Usuario baneado automáticamente por acumular 3 warnings",
                        inline=False
                    )
                except:
                    pass
            
            await interaction.response.send_message(embed=embed)
            await self.log_moderation_action("warn", interaction.guild, interaction.user, usuario, razon)
            
        except Exception as e:
            logger.error(f"Error advirtiendo usuario: {e}")
            await interaction.response.send_message("❌ Error advirtiendo usuario.", ephemeral=True)
    
    @nextcord.slash_command(name="warnings", description="Ver warnings de un usuario")
    async def warnings(
        self,
        interaction: nextcord.Interaction,
        usuario: nextcord.Member = None
    ):
        """Ver warnings de usuario"""
        if not await self.check_permissions(interaction, "moderate_members"):
            return
        
        target = usuario or interaction.user
        
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, reason, moderator_id, created_at
                FROM warnings 
                WHERE guild_id = ? AND user_id = ? AND active = 1
                ORDER BY created_at DESC
            ''', (interaction.guild.id, target.id))
            
            warnings = cursor.fetchall()
            conn.close()
            
            embed = nextcord.Embed(
                title=f"⚠️ Warnings de {target.display_name}",
                description=f"Total: {len(warnings)}/3 warnings",
                color=nextcord.Color.yellow()
            )
            
            if warnings:
                for i, (warn_id, reason, mod_id, created_at) in enumerate(warnings[:10]):
                    moderator = self.bot.get_user(mod_id)
                    mod_name = moderator.display_name if moderator else "Desconocido"
                    
                    date = datetime.fromisoformat(created_at).strftime("%d/%m/%Y")
                    
                    embed.add_field(
                        name=f"Warning #{warn_id}",
                        value=f"**Razón:** {reason}\n**Moderador:** {mod_name}\n**Fecha:** {date}",
                        inline=False
                    )
            else:
                embed.description = "Este usuario no tiene warnings activos."
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error consultando warnings: {e}")
            await interaction.response.send_message("❌ Error consultando warnings.", ephemeral=True)
    
    @nextcord.slash_command(name="clear", description="Limpiar mensajes")
    async def clear(
        self,
        interaction: nextcord.Interaction,
        cantidad: int,
        usuario: nextcord.Member = None
    ):
        """Limpiar mensajes"""
        if not await self.check_permissions(interaction, "manage_messages"):
            return
        
        if cantidad > 100:
            await interaction.response.send_message("❌ No puedes eliminar más de 100 mensajes a la vez.", ephemeral=True)
            return
        
        try:
            await interaction.response.defer(ephemeral=True)
            
            def check(message):
                if usuario:
                    return message.author == usuario
                return True
            
            deleted = await interaction.channel.purge(limit=cantidad, check=check)
            
            embed = nextcord.Embed(
                title="🧹 Mensajes Eliminados",
                description=f"Se eliminaron **{len(deleted)}** mensajes",
                color=nextcord.Color.green()
            )
            
            if usuario:
                embed.add_field(name="Usuario", value=usuario.mention, inline=True)
            
            embed.add_field(name="Canal", value=interaction.channel.mention, inline=True)
            embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error limpiando mensajes: {e}")
            await interaction.followup.send("❌ Error limpiando mensajes.")
    
    # ================================
    # SISTEMA DE APPEALS
    # ================================
    
    @nextcord.slash_command(name="appeal", description="Crear una apelación")
    async def appeal(
        self,
        interaction: nextcord.Interaction,
        tipo: str = nextcord.SlashOption(choices=["ban", "warning", "mute"]),
        razon: str = None
    ):
        """Crear apelación"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            # Verificar si ya tiene una apelación pendiente
            cursor.execute('''
                SELECT id FROM appeals 
                WHERE guild_id = ? AND user_id = ? AND status = 'pending'
            ''', (interaction.guild.id, interaction.user.id))
            
            if cursor.fetchone():
                await interaction.response.send_message("❌ Ya tienes una apelación pendiente.", ephemeral=True)
                conn.close()
                return
            
            # Crear apelación
            cursor.execute('''
                INSERT INTO appeals (guild_id, user_id, appeal_type, reason)
                VALUES (?, ?, ?, ?)
            ''', (interaction.guild.id, interaction.user.id, tipo, razon or "No especificada"))
            
            appeal_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            embed = nextcord.Embed(
                title="📝 Apelación Creada",
                description=f"Tu apelación ha sido enviada para revisión.",
                color=nextcord.Color.blue()
            )
            embed.add_field(name="ID", value=f"#{appeal_id}", inline=True)
            embed.add_field(name="Tipo", value=tipo.title(), inline=True)
            embed.add_field(name="Estado", value="Pendiente", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error creando apelación: {e}")
            await interaction.response.send_message("❌ Error creando apelación.", ephemeral=True)
    
    # ================================
    # CONFIGURACIÓN DE AUTOMOD
    # ================================
    
    @nextcord.slash_command(name="automod", description="Configurar automoderación")
    async def automod_config(self, interaction: nextcord.Interaction):
        """Configurar automod"""
        if not await self.check_permissions(interaction, "manage_guild"):
            return
        
        embed = nextcord.Embed(
            title="🤖 Configuración de Automoderación",
            description="Configura las opciones de moderación automática",
            color=nextcord.Color.blue()
        )
        
        view = AutomodConfigView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    # ================================
    # FUNCIONES AUXILIARES
    # ================================
    
    async def check_permissions(self, interaction: nextcord.Interaction, permission: str) -> bool:
        """Verificar permisos del usuario"""
        if interaction.user.guild_permissions.__getattribute__(permission):
            return True
        
        # Verificar roles de staff personalizados
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            user_role_ids = [role.id for role in interaction.user.roles]
            
            cursor.execute('''
                SELECT permissions FROM staff_roles 
                WHERE guild_id = ? AND role_id IN ({})
            '''.format(','.join('?' * len(user_role_ids))), [interaction.guild.id] + user_role_ids)
            
            for (permissions_json,) in cursor.fetchall():
                permissions = json.loads(permissions_json)
                if permission in permissions:
                    conn.close()
                    return True
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
        
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return False
    
    async def log_moderation_action(self, action: str, guild: nextcord.Guild, moderator: nextcord.Member, target: nextcord.Member, reason: str):
        """Registrar acción de moderación"""
        try:
            # Buscar canal de logs
            log_channel = None
            for channel in guild.text_channels:
                if "log" in channel.name.lower() or "audit" in channel.name.lower():
                    log_channel = channel
                    break
            
            if log_channel:
                embed = nextcord.Embed(
                    title=f"📋 {action.title()}",
                    color=nextcord.Color.red() if action == "ban" else nextcord.Color.orange() if action == "kick" else nextcord.Color.yellow()
                )
                embed.add_field(name="Usuario", value=f"{target} ({target.id})", inline=False)
                embed.add_field(name="Moderador", value=moderator.mention, inline=True)
                embed.add_field(name="Razón", value=reason, inline=True)
                embed.timestamp = datetime.now()
                
                await log_channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error registrando acción: {e}")


class AutomodConfigView(nextcord.ui.View):
    """Vista para configurar automod"""
    
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
    
    @nextcord.ui.button(label="🚫 Anti-Spam", style=nextcord.ButtonStyle.secondary)
    async def toggle_antispam(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("⚙️ Configurando anti-spam...", ephemeral=True)
    
    @nextcord.ui.button(label="🔗 Anti-Links", style=nextcord.ButtonStyle.secondary)
    async def toggle_antilinks(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("⚙️ Configurando anti-links...", ephemeral=True)
    
    @nextcord.ui.button(label="🔠 Anti-Caps", style=nextcord.ButtonStyle.secondary)
    async def toggle_anticaps(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("⚙️ Configurando anti-caps...", ephemeral=True)
    
    @nextcord.ui.button(label="🤬 Filtro de Palabras", style=nextcord.ButtonStyle.secondary)
    async def toggle_wordfilter(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_message("⚙️ Configurando filtro de palabras...", ephemeral=True)


def setup(bot):
    """Cargar el cog"""
    return ModerationSystem(bot)
