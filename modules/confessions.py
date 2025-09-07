"""
Sistema de Confesiones Anónimas v2.0
Permite confesiones completamente anónimas con rastreo para moderadores
Por davito - Dabot v2
"""

import logging
import nextcord
from nextcord.ext import commands
import sqlite3
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class ConfessionDB:
    """manejo de base de datos para confesiones"""
    
    def __init__(self, db_path: str = "data/confessions.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """inicializar base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS confessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER,
                        user_id INTEGER,
                        message_id INTEGER,
                        confession_text TEXT,
                        channel_id INTEGER,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        anonymous_id TEXT
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS confession_config (
                        guild_id INTEGER PRIMARY KEY,
                        channel_id INTEGER,
                        enabled BOOLEAN DEFAULT 1,
                        anonymous_numbers BOOLEAN DEFAULT 1
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error inicializando base de datos de confesiones: {e}")
    
    def add_confession(self, guild_id: int, user_id: int, message_id: int, confession_text: str, channel_id: int, anonymous_id: str):
        """agregar nueva confesión"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO confessions (guild_id, user_id, message_id, confession_text, channel_id, anonymous_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (guild_id, user_id, message_id, confession_text, channel_id, anonymous_id)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error agregando confesión: {e}")
    
    def get_confession_by_message(self, message_id: int):
        """obtener confesión por ID de mensaje"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM confessions WHERE message_id = ?",
                    (message_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error obteniendo confesión: {e}")
            return None
    
    def get_user_confessions(self, guild_id: int, user_id: int):
        """obtener confesiones de un usuario"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM confessions WHERE guild_id = ? AND user_id = ? ORDER BY timestamp DESC",
                    (guild_id, user_id)
                )
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error obteniendo confesiones de usuario: {e}")
            return []
    
    def set_config(self, guild_id: int, channel_id: int):
        """configurar canal de confesiones"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO confession_config (guild_id, channel_id) VALUES (?, ?)",
                    (guild_id, channel_id)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error configurando confesiones: {e}")
    
    def get_config(self, guild_id: int):
        """obtener configuración de confesiones"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM confession_config WHERE guild_id = ?",
                    (guild_id,)
                )
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error obteniendo configuración: {e}")
            return None
    
    def get_next_anonymous_number(self, guild_id: int):
        """obtener siguiente número anónimo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM confessions WHERE guild_id = ?",
                    (guild_id,)
                )
                count = cursor.fetchone()[0]
                return count + 1
        except Exception as e:
            logger.error(f"Error obteniendo número anónimo: {e}")
            return 1

class ConfessionModal(nextcord.ui.Modal):
    """modal para escribir confesión"""
    
    def __init__(self, confession_cog):
        self.confession_cog = confession_cog
        super().__init__(
            title="📝 Confesión Anónima",
            timeout=300
        )
        
        self.confession_input = nextcord.ui.TextInput(
            label="Tu confesión",
            placeholder="Escribe tu confesión aquí... Será completamente anónima.",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
            max_length=1500
        )
        self.add_item(self.confession_input)
    
    async def on_submit(self, interaction: nextcord.Interaction):
        """procesar confesión enviada"""
        try:
            config = self.confession_cog.db.get_config(interaction.guild.id)
            if not config:
                await interaction.response.send_message(
                    "❌ Las confesiones no están configuradas en este servidor.",
                    ephemeral=True
                )
                return
            
            channel = interaction.guild.get_channel(config[1])
            if not channel:
                await interaction.response.send_message(
                    "❌ El canal de confesiones no está disponible.",
                    ephemeral=True
                )
                return
            
            # Generar ID anónimo
            anonymous_number = self.confession_cog.db.get_next_anonymous_number(interaction.guild.id)
            anonymous_id = f"Anónimo #{anonymous_number:03d}"
            
            # Crear embed de confesión
            embed = nextcord.Embed(
                title="🤫 Confesión Anónima",
                description=self.confession_input.value,
                color=nextcord.Color.dark_purple(),
                timestamp=nextcord.utils.utcnow()
            )
            embed.set_author(
                name=anonymous_id,
                icon_url="https://cdn.discordapp.com/emojis/845796977784815656.png?v=1"  # Icono anónimo
            )
            embed.set_footer(text="Esta confesión es completamente anónima")
            
            # Enviar confesión
            message = await channel.send(embed=embed)
            
            # Guardar en base de datos para rastreo de moderadores
            self.confession_cog.db.add_confession(
                interaction.guild.id,
                interaction.user.id,
                message.id,
                self.confession_input.value,
                channel.id,
                anonymous_id
            )
            
            # Agregar reacciones
            await message.add_reaction("❤️")
            await message.add_reaction("😢")
            await message.add_reaction("😮")
            await message.add_reaction("😡")
            
            await interaction.response.send_message(
                "✅ Tu confesión ha sido enviada de forma anónima.",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error procesando confesión: {e}")
            await interaction.response.send_message(
                "❌ Error al enviar la confesión. Inténtalo de nuevo.",
                ephemeral=True
            )

class ConfessionView(nextcord.ui.View):
    """vista para botón de confesión"""
    
    def __init__(self, confession_cog):
        super().__init__(timeout=None)
        self.confession_cog = confession_cog
    
    @nextcord.ui.button(
        label="📝 Hacer Confesión",
        style=nextcord.ButtonStyle.secondary,
        custom_id="confession_button",
        emoji="🤫"
    )
    async def confession_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """botón para abrir modal de confesión"""
        modal = ConfessionModal(self.confession_cog)
        await interaction.response.send_modal(modal)

class Confessions(commands.Cog):
    """sistema de confesiones anónimas"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = ConfessionDB()
        
        # Agregar vista persistente
        self.bot.add_view(ConfessionView(self))
    
    @nextcord.slash_command(name="confesion", description="comandos de confesiones")
    async def confession_group(self, interaction: nextcord.Interaction):
        pass
    
    @confession_group.subcommand(name="setup", description="configurar sistema de confesiones")
    async def setup_confessions(self, interaction: nextcord.Interaction, canal: nextcord.TextChannel = None):
        """configurar sistema de confesiones"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Necesitas permisos de gestionar servidor.",
                ephemeral=True
            )
            return
        
        # Usar canal actual si no se especifica
        channel = canal or interaction.channel
        
        # Configurar en base de datos
        self.db.set_config(interaction.guild.id, channel.id)
        
        # Crear panel de confesiones
        embed = nextcord.Embed(
            title="🤫 Sistema de Confesiones Anónimas",
            description="¡Comparte tus secretos de forma completamente anónima!",
            color=nextcord.Color.dark_purple()
        )
        embed.add_field(
            name="📝 ¿Cómo funciona?",
            value="• Haz clic en **📝 Hacer Confesión**\n• Escribe tu confesión en el modal\n• Se enviará de forma anónima\n• ¡Nadie sabrá que fuiste tú!",
            inline=False
        )
        embed.add_field(
            name="🔒 Privacidad",
            value="• Tu identidad permanece oculta\n• Solo los administradores pueden rastrear confesiones en casos extremos\n• Respeta las reglas del servidor",
            inline=False
        )
        embed.add_field(
            name="⚠️ Reglas",
            value="• No hagas confesiones que violen las reglas\n• No uses esto para acosar a otros\n• Mantén el respeto hacia la comunidad",
            inline=False
        )
        
        view = ConfessionView(self)
        
        message = await channel.send(embed=embed, view=view)
        
        # Confirmar configuración
        setup_embed = nextcord.Embed(
            title="✅ Confesiones Configuradas",
            description=f"Sistema de confesiones activado en {channel.mention}",
            color=nextcord.Color.green()
        )
        setup_embed.add_field(
            name="🔧 Funcionalidades",
            value="• Confesiones completamente anónimas\n• Panel interactivo\n• Rastreo para moderadores\n• Reacciones automáticas",
            inline=False
        )
        
        await interaction.response.send_message(embed=setup_embed)
    
    @confession_group.subcommand(name="enviar", description="enviar confesión anónima (alternativo)")
    async def send_confession(self, interaction: nextcord.Interaction):
        """enviar confesión usando comando (alternativo al botón)"""
        config = self.db.get_config(interaction.guild.id)
        if not config:
            await interaction.response.send_message(
                "❌ Las confesiones no están configuradas en este servidor.\nUsa `/confesion setup` para configurarlas.",
                ephemeral=True
            )
            return
        
        modal = ConfessionModal(self)
        await interaction.response.send_modal(modal)
    
    @confession_group.subcommand(name="rastrear", description="rastrear autor de confesión (solo moderadores)")
    async def track_confession(self, interaction: nextcord.Interaction, id_mensaje: str):
        """rastrear autor de confesión específica - solo para moderadores"""
        if not (interaction.user.guild_permissions.manage_messages or 
                interaction.user.guild_permissions.administrator):
            await interaction.response.send_message(
                "❌ Solo los moderadores pueden usar este comando.",
                ephemeral=True
            )
            return
        
        try:
            message_id = int(id_mensaje)
        except ValueError:
            await interaction.response.send_message(
                "❌ ID de mensaje no válido.",
                ephemeral=True
            )
            return
        
        confession = self.db.get_confession_by_message(message_id)
        if not confession:
            await interaction.response.send_message(
                "❌ Confesión no encontrada.",
                ephemeral=True
            )
            return
        
        user = interaction.guild.get_member(confession[2])  # user_id
        
        embed = nextcord.Embed(
            title="🔍 Rastreo de Confesión",
            description="Información confidencial para moderadores",
            color=nextcord.Color.red()
        )
        embed.add_field(
            name="👤 Autor",
            value=f"{user.mention} ({user.display_name})" if user else f"Usuario no encontrado (ID: {confession[2]})",
            inline=False
        )
        embed.add_field(
            name="📝 Confesión",
            value=confession[4][:500] + ("..." if len(confession[4]) > 500 else ""),
            inline=False
        )
        embed.add_field(
            name="📊 Detalles",
            value=f"**ID Anónimo:** {confession[7]}\n**Fecha:** {confession[6]}\n**Canal:** <#{confession[5]}>",
            inline=False
        )
        embed.set_footer(text="⚠️ Esta información es confidencial")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @confession_group.subcommand(name="stats", description="estadísticas de confesiones")
    async def confession_stats(self, interaction: nextcord.Interaction):
        """mostrar estadísticas de confesiones del servidor"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ Solo los moderadores pueden ver las estadísticas.",
                ephemeral=True
            )
            return
        
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                # Total de confesiones
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM confessions WHERE guild_id = ?",
                    (interaction.guild.id,)
                )
                total_confessions = cursor.fetchone()[0]
                
                # Confesiones por día (últimos 7 días)
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM confessions WHERE guild_id = ? AND timestamp > datetime('now', '-7 days')",
                    (interaction.guild.id,)
                )
                week_confessions = cursor.fetchone()[0]
                
                # Confesiones hoy
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM confessions WHERE guild_id = ? AND date(timestamp) = date('now')",
                    (interaction.guild.id,)
                )
                today_confessions = cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            await interaction.response.send_message(
                "❌ Error obteniendo estadísticas.",
                ephemeral=True
            )
            return
        
        embed = nextcord.Embed(
            title="📊 Estadísticas de Confesiones",
            color=nextcord.Color.purple()
        )
        embed.add_field(
            name="📈 Total de Confesiones",
            value=f"**{total_confessions}** confesiones",
            inline=True
        )
        embed.add_field(
            name="📅 Esta Semana",
            value=f"**{week_confessions}** confesiones",
            inline=True
        )
        embed.add_field(
            name="🗓️ Hoy",
            value=f"**{today_confessions}** confesiones",
            inline=True
        )
        embed.set_footer(text="Solo visible para moderadores")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @confession_group.subcommand(name="usuario", description="ver confesiones de un usuario específico")
    async def user_confessions(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """ver confesiones de un usuario específico - solo moderadores"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Solo los administradores pueden usar este comando.",
                ephemeral=True
            )
            return
        
        confessions = self.db.get_user_confessions(interaction.guild.id, usuario.id)
        
        if not confessions:
            await interaction.response.send_message(
                f"❌ {usuario.display_name} no ha hecho confesiones.",
                ephemeral=True
            )
            return
        
        embed = nextcord.Embed(
            title=f"📋 Confesiones de {usuario.display_name}",
            description=f"Total: {len(confessions)} confesiones",
            color=nextcord.Color.orange()
        )
        
        for i, confession in enumerate(confessions[:5]):  # Mostrar solo las últimas 5
            confession_preview = confession[4][:100] + ("..." if len(confession[4]) > 100 else "")
            embed.add_field(
                name=f"🤫 {confession[7]} - {confession[6][:10]}",
                value=confession_preview,
                inline=False
            )
        
        if len(confessions) > 5:
            embed.set_footer(text=f"Mostrando las 5 más recientes de {len(confessions)} total")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    """cargar el cog"""
    bot.add_cog(Confessions(bot))
