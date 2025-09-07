import nextcord
from nextcord.ext import commands
import sqlite3
import logging

logger = logging.getLogger(__name__)

class VoiceMasterDB:
    """base de datos para voicemaster"""
    
    def __init__(self, db_path="data/voicemaster.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """inicializar base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla de configuración de guilds
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS guild_config (
                        guild_id INTEGER PRIMARY KEY,
                        create_channel_id INTEGER,
                        category_id INTEGER,
                        controls_channel_id INTEGER
                    )
                """)
                
                # Tabla de canales temporales
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS temp_channels (
                        channel_id INTEGER PRIMARY KEY,
                        guild_id INTEGER,
                        owner_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Base de datos VoiceMaster inicializada")
                
        except Exception as e:
            logger.error(f"Error inicializando base de datos VoiceMaster: {e}")
    
    def set_config(self, guild_id, create_channel_id, category_id, controls_channel_id):
        """configurar voicemaster para un servidor"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO guild_config 
                    (guild_id, create_channel_id, category_id, controls_channel_id)
                    VALUES (?, ?, ?, ?)
                """, (guild_id, create_channel_id, category_id, controls_channel_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error configurando VoiceMaster: {e}")
    
    def get_config(self, guild_id):
        """obtener configuración de un servidor"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error obteniendo configuración VoiceMaster: {e}")
            return None
    
    def add_temp_channel(self, channel_id, guild_id, owner_id):
        """registrar canal temporal"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO temp_channels (channel_id, guild_id, owner_id)
                    VALUES (?, ?, ?)
                """, (channel_id, guild_id, owner_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error registrando canal temporal: {e}")
    
    def remove_temp_channel(self, channel_id):
        """quitar canal temporal"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM temp_channels WHERE channel_id = ?", (channel_id,))
                conn.commit()
        except Exception as e:
            logger.error(f"Error quitando canal temporal: {e}")
    
    def get_temp_channel_owner(self, channel_id):
        """obtener dueño de canal temporal"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT owner_id FROM temp_channels WHERE channel_id = ?", (channel_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error obteniendo dueño de canal: {e}")
            return None

class VoiceControlView(nextcord.ui.View):
    """vista de control de voz"""
    
    def __init__(self, voicemaster_cog):
        super().__init__(timeout=None)
        self.voicemaster = voicemaster_cog
    
    @nextcord.ui.button(label="🔒 Bloquear", style=nextcord.ButtonStyle.red, custom_id="voice_lock")
    async def lock_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.voicemaster.lock_channel_interaction(interaction)
    
    @nextcord.ui.button(label="🔓 Desbloquear", style=nextcord.ButtonStyle.green, custom_id="voice_unlock")
    async def unlock_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.voicemaster.unlock_channel_interaction(interaction)
    
    @nextcord.ui.button(label="👥 Límite", style=nextcord.ButtonStyle.blurple, custom_id="voice_limit")
    async def set_limit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.voicemaster.limit_channel_interaction(interaction)
    
    @nextcord.ui.button(label="📝 Nombre", style=nextcord.ButtonStyle.gray, custom_id="voice_name")
    async def change_name(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.voicemaster.name_channel_interaction(interaction)

class VoiceMaster(commands.Cog):
    """sistema de canales de voz temporales"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = VoiceMasterDB()
    
    @nextcord.slash_command(
        name="voice",
        description="Comandos de VoiceMaster"
    )
    async def voice(self, interaction: nextcord.Interaction):
        pass
    
    @voice.subcommand(
        name="setup",
        description="Configurar VoiceMaster (admin)"
    )
    async def setup_voicemaster(
        self,
        interaction: nextcord.Interaction,
        create_channel: nextcord.VoiceChannel = nextcord.SlashOption(
            description="Canal para crear canales temporales"
        ),
        category: nextcord.CategoryChannel = nextcord.SlashOption(
            description="Categoría donde crear los canales"
        ),
        controls_channel: nextcord.TextChannel = nextcord.SlashOption(
            description="Canal de controles"
        )
    ):
        """configurar voicemaster"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Gestionar Servidor**.",
                ephemeral=True
            )
            return
        
        # Configurar en base de datos
        self.db.set_config(
            interaction.guild.id,
            create_channel.id,
            category.id,
            controls_channel.id
        )
        
        # Crear embed de controles
        embed = nextcord.Embed(
            title="🎙️ VoiceMaster - Panel de Control",
            description="Gestiona tu canal de voz temporal con los botones de abajo.",
            color=nextcord.Color.purple()
        )
        embed.add_field(
            name="📋 ¿Cómo usar?",
            value="1. Únete al canal **➕ Crear Canal**\n2. Se creará tu canal personal automáticamente\n3. Usa estos botones para gestionarlo",
            inline=False
        )
        
        view = VoiceControlView(self)
        await controls_channel.send(embed=embed, view=view)
        
        embed_response = nextcord.Embed(
            title="✅ VoiceMaster Configurado",
            description="Sistema configurado exitosamente.",
            color=nextcord.Color.green()
        )
        embed_response.add_field(
            name="Configuración",
            value=f"**Canal Crear**: {create_channel.mention}\n**Categoría**: {category.name}\n**Controles**: {controls_channel.mention}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed_response)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """manejar cambios de estado de voz"""
        if member.bot:
            return
        
        guild_config = self.db.get_config(member.guild.id)
        if not guild_config:
            return
        
        create_channel_id = guild_config[1]
        category_id = guild_config[2]
        
        # Si se une al canal de crear
        if after.channel and after.channel.id == create_channel_id:
            await self.create_temp_channel(member, category_id)
        
        # Si sale de un canal temporal y queda vacío
        if before.channel:
            owner_id = self.db.get_temp_channel_owner(before.channel.id)
            if owner_id and len(before.channel.members) == 0:
                await before.channel.delete(reason="Canal temporal vacío")
                self.db.remove_temp_channel(before.channel.id)
    
    async def create_temp_channel(self, member, category_id):
        """crear canal temporal"""
        try:
            category = self.bot.get_channel(category_id)
            if not category:
                return
            
            # Crear canal temporal
            channel = await member.guild.create_voice_channel(
                name=f"🎙️ {member.display_name}",
                category=category,
                overwrites={
                    member: nextcord.PermissionOverwrite(
                        manage_channels=True,
                        manage_permissions=True,
                        move_members=True
                    )
                }
            )
            
            # Mover al usuario
            await member.move_to(channel)
            
            # Registrar en base de datos
            self.db.add_temp_channel(channel.id, member.guild.id, member.id)
            
        except Exception as e:
            logger.error(f"Error creando canal temporal: {e}")
    
    async def lock_channel_interaction(self, interaction: nextcord.Interaction):
        """bloquear canal vía interacción"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Debes estar en un canal de voz.", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        owner_id = self.db.get_temp_channel_owner(channel.id)
        
        if owner_id != interaction.user.id:
            await interaction.response.send_message("❌ No eres el dueño de este canal.", ephemeral=True)
            return
        
        await channel.set_permissions(
            interaction.guild.default_role,
            connect=False
        )
        
        await interaction.response.send_message("🔒 Canal bloqueado.", ephemeral=True)
    
    async def unlock_channel_interaction(self, interaction: nextcord.Interaction):
        """desbloquear canal vía interacción"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Debes estar en un canal de voz.", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        owner_id = self.db.get_temp_channel_owner(channel.id)
        
        if owner_id != interaction.user.id:
            await interaction.response.send_message("❌ No eres el dueño de este canal.", ephemeral=True)
            return
        
        await channel.set_permissions(
            interaction.guild.default_role,
            connect=True
        )
        
        await interaction.response.send_message("🔓 Canal desbloqueado.", ephemeral=True)
    
    async def limit_channel_interaction(self, interaction: nextcord.Interaction):
        """establecer límite vía interacción"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Debes estar en un canal de voz.", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        owner_id = self.db.get_temp_channel_owner(channel.id)
        
        if owner_id != interaction.user.id:
            await interaction.response.send_message("❌ No eres el dueño de este canal.", ephemeral=True)
            return
        
        # Aquí podrías implementar un modal para pedir el límite
        await interaction.response.send_message("🔧 Usa `/voice limit [número]` para establecer el límite.", ephemeral=True)
    
    async def name_channel_interaction(self, interaction: nextcord.Interaction):
        """cambiar nombre vía interacción"""
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Debes estar en un canal de voz.", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        owner_id = self.db.get_temp_channel_owner(channel.id)
        
        if owner_id != interaction.user.id:
            await interaction.response.send_message("❌ No eres el dueño de este canal.", ephemeral=True)
            return
        
        # Aquí podrías implementar un modal para pedir el nombre
        await interaction.response.send_message("🔧 Usa `/voice name [nombre]` para cambiar el nombre.", ephemeral=True)

def setup(bot):
    """cargar el cog"""
    bot.add_cog(VoiceMaster(bot))
