"""
sistema voicemaster para canales de voz temporales
por davito
"""

import json
import logging
import asyncio
import nextcord
from nextcord.ext import commands
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class VoiceView(nextcord.ui.View):
    """vista con botones para control de canal de voz"""
    
    def __init__(self, voicemaster_cog, owner_id: int):
        super().__init__(timeout=None)
        self.voicemaster = voicemaster_cog
        self.owner_id = owner_id
    
    @nextcord.ui.button(label="🔒 cerrar", style=nextcord.ButtonStyle.danger)
    async def close_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """cerrar canal para todos excepto owner"""
        try:
            if interaction.user.id != self.owner_id:
                await interaction.response.send_message("❌ solo el dueño del canal puede usar esto.", ephemeral=True)
                return
            
            voice_channel = interaction.user.voice.channel if interaction.user.voice else None
            if not voice_channel or voice_channel.id not in self.voicemaster.temp_channels:
                await interaction.response.send_message("❌ no estás en un canal temporal.", ephemeral=True)
                return
            
            # cambiar permisos para denegar entrada
            overwrite = nextcord.PermissionOverwrite(connect=False)
            await voice_channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            
            await interaction.response.send_message("🔒 canal cerrado para nuevos usuarios.", ephemeral=True)
            logger.info(f"canal {voice_channel.name} cerrado por {interaction.user}")
            
        except Exception as e:
            logger.error(f"error cerrando canal: {e}")
            await interaction.response.send_message("❌ error al cerrar el canal.", ephemeral=True)
    
    @nextcord.ui.button(label="🔓 abrir", style=nextcord.ButtonStyle.success)
    async def open_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """abrir canal para todos"""
        try:
            if interaction.user.id != self.owner_id:
                await interaction.response.send_message("❌ solo el dueño del canal puede usar esto.", ephemeral=True)
                return
            
            voice_channel = interaction.user.voice.channel if interaction.user.voice else None
            if not voice_channel or voice_channel.id not in self.voicemaster.temp_channels:
                await interaction.response.send_message("❌ no estás en un canal temporal.", ephemeral=True)
                return
            
            # restaurar permisos normales
            await voice_channel.set_permissions(interaction.guild.default_role, overwrite=None)
            
            await interaction.response.send_message("🔓 canal abierto para todos.", ephemeral=True)
            logger.info(f"canal {voice_channel.name} abierto por {interaction.user}")
            
        except Exception as e:
            logger.error(f"error abriendo canal: {e}")
            await interaction.response.send_message("❌ error al abrir el canal.", ephemeral=True)
    
    @nextcord.ui.button(label="👥 límite", style=nextcord.ButtonStyle.primary)
    async def set_limit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """cambiar límite de usuarios"""
        try:
            if interaction.user.id != self.owner_id:
                await interaction.response.send_message("❌ solo el dueño del canal puede usar esto.", ephemeral=True)
                return
            
            voice_channel = interaction.user.voice.channel if interaction.user.voice else None
            if not voice_channel or voice_channel.id not in self.voicemaster.temp_channels:
                await interaction.response.send_message("❌ no estás en un canal temporal.", ephemeral=True)
                return
            
            # crear modal para solicitar límite
            modal = LimitModal(voice_channel)
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            logger.error(f"error configurando límite: {e}")
            await interaction.response.send_message("❌ error al configurar límite.", ephemeral=True)
    
    @nextcord.ui.button(label="📝 nombre", style=nextcord.ButtonStyle.secondary)
    async def change_name(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """cambiar nombre del canal"""
        try:
            if interaction.user.id != self.owner_id:
                await interaction.response.send_message("❌ solo el dueño del canal puede usar esto.", ephemeral=True)
                return
            
            voice_channel = interaction.user.voice.channel if interaction.user.voice else None
            if not voice_channel or voice_channel.id not in self.voicemaster.temp_channels:
                await interaction.response.send_message("❌ no estás en un canal temporal.", ephemeral=True)
                return
            
            # crear modal para solicitar nombre
            modal = NameModal(voice_channel)
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            logger.error(f"error cambiando nombre: {e}")
            await interaction.response.send_message("❌ error al cambiar nombre.", ephemeral=True)
    
    @nextcord.ui.button(label="👤 transferir", style=nextcord.ButtonStyle.secondary)
    async def transfer_ownership(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """transferir propiedad del canal"""
        try:
            if interaction.user.id != self.owner_id:
                await interaction.response.send_message("❌ solo el dueño del canal puede usar esto.", ephemeral=True)
                return
            
            voice_channel = interaction.user.voice.channel if interaction.user.voice else None
            if not voice_channel or voice_channel.id not in self.voicemaster.temp_channels:
                await interaction.response.send_message("❌ no estás en un canal temporal.", ephemeral=True)
                return
            
            # crear modal para solicitar usuario
            modal = TransferModal(voice_channel, self.voicemaster)
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            logger.error(f"error transfiriendo propiedad: {e}")
            await interaction.response.send_message("❌ error al transferir propiedad.", ephemeral=True)
    
    @nextcord.ui.button(label="🗑️ eliminar", style=nextcord.ButtonStyle.danger)
    async def delete_channel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        """eliminar canal temporal"""
        try:
            if interaction.user.id != self.owner_id:
                await interaction.response.send_message("❌ solo el dueño del canal puede usar esto.", ephemeral=True)
                return
            
            voice_channel = interaction.user.voice.channel if interaction.user.voice else None
            if not voice_channel or voice_channel.id not in self.voicemaster.temp_channels:
                await interaction.response.send_message("❌ no estás en un canal temporal.", ephemeral=True)
                return
            
            await interaction.response.send_message("🗑️ eliminando canal...", ephemeral=True)
            
            # eliminar canal y datos
            del self.voicemaster.temp_channels[voice_channel.id]
            await voice_channel.delete(reason="eliminado por el dueño")
            
            logger.info(f"canal temporal eliminado por {interaction.user}")
            
        except Exception as e:
            logger.error(f"error eliminando canal: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ error al eliminar canal.", ephemeral=True)

class LimitModal(nextcord.ui.Modal):
    """modal para cambiar límite de usuarios"""
    
    def __init__(self, voice_channel):
        super().__init__(title="cambiar límite de usuarios")
        self.voice_channel = voice_channel
        
        self.limit_input = nextcord.ui.TextInput(
            label="límite de usuarios",
            placeholder="escribe un número entre 0-99 (0 = sin límite)",
            max_length=2,
            required=True
        )
        self.add_item(self.limit_input)
    
    async def callback(self, interaction: nextcord.Interaction):
        try:
            limit = int(self.limit_input.value)
            if limit < 0 or limit > 99:
                await interaction.response.send_message("❌ el límite debe estar entre 0 y 99.", ephemeral=True)
                return
            
            await self.voice_channel.edit(user_limit=limit)
            
            if limit == 0:
                message = "🔓 límite de usuarios removido."
            else:
                message = f"👥 límite de usuarios establecido en {limit}."
            
            await interaction.response.send_message(message, ephemeral=True)
            logger.info(f"límite de {self.voice_channel.name} cambiado a {limit}")
            
        except ValueError:
            await interaction.response.send_message("❌ debes introducir un número válido.", ephemeral=True)
        except Exception as e:
            logger.error(f"error cambiando límite: {e}")
            await interaction.response.send_message("❌ error al cambiar límite.", ephemeral=True)

class NameModal(nextcord.ui.Modal):
    """modal para cambiar nombre del canal"""
    
    def __init__(self, voice_channel):
        super().__init__(title="cambiar nombre del canal")
        self.voice_channel = voice_channel
        
        self.name_input = nextcord.ui.TextInput(
            label="nuevo nombre",
            placeholder="escribe el nuevo nombre del canal",
            max_length=100,
            required=True
        )
        self.add_item(self.name_input)
    
    async def callback(self, interaction: nextcord.Interaction):
        try:
            new_name = self.name_input.value.strip()
            if not new_name:
                await interaction.response.send_message("❌ el nombre no puede estar vacío.", ephemeral=True)
                return
            
            await self.voice_channel.edit(name=new_name)
            await interaction.response.send_message(f"📝 nombre cambiado a: **{new_name}**", ephemeral=True)
            logger.info(f"nombre de canal cambiado a {new_name}")
            
        except Exception as e:
            logger.error(f"error cambiando nombre: {e}")
            await interaction.response.send_message("❌ error al cambiar nombre.", ephemeral=True)

class TransferModal(nextcord.ui.Modal):
    """modal para transferir propiedad"""
    
    def __init__(self, voice_channel, voicemaster):
        super().__init__(title="transferir propiedad")
        self.voice_channel = voice_channel
        self.voicemaster = voicemaster
        
        self.user_input = nextcord.ui.TextInput(
            label="nuevo dueño",
            placeholder="@usuario o id del usuario",
            max_length=50,
            required=True
        )
        self.add_item(self.user_input)
    
    async def callback(self, interaction: nextcord.Interaction):
        try:
            user_mention = self.user_input.value.strip()
            
            # intentar obtener usuario por mención o id
            if user_mention.startswith('<@') and user_mention.endswith('>'):
                user_id = int(user_mention[2:-1].replace('!', ''))
            else:
                user_id = int(user_mention)
            
            new_owner = interaction.guild.get_member(user_id)
            if not new_owner:
                await interaction.response.send_message("❌ usuario no encontrado.", ephemeral=True)
                return
            
            if new_owner.bot:
                await interaction.response.send_message("❌ no puedes transferir a un bot.", ephemeral=True)
                return
            
            # verificar que el usuario esté en el canal
            if new_owner not in self.voice_channel.members:
                await interaction.response.send_message("❌ el usuario debe estar en el canal.", ephemeral=True)
                return
            
            # actualizar propiedad
            self.voicemaster.temp_channels[self.voice_channel.id]['owner_id'] = new_owner.id
            
            await interaction.response.send_message(f"👤 propiedad transferida a {new_owner.mention}", ephemeral=True)
            logger.info(f"propiedad de {self.voice_channel.name} transferida a {new_owner}")
            
        except ValueError:
            await interaction.response.send_message("❌ id de usuario inválido.", ephemeral=True)
        except Exception as e:
            logger.error(f"error transfiriendo propiedad: {e}")
            await interaction.response.send_message("❌ error al transferir propiedad.", ephemeral=True)

class VoiceMaster(commands.Cog):
    """sistema de canales de voz temporales"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "data/voicemaster_config.json"
        self.temp_channels: Dict[int, dict] = {}
        self.guild_configs: Dict[int, dict] = {}
        
        # cargar configuración
        self.load_config()
    
    def load_config(self):
        """cargar configuración desde archivo"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.guild_configs = data.get('guild_configs', {})
                # convertir keys a int
                self.guild_configs = {int(k): v for k, v in self.guild_configs.items()}
        except FileNotFoundError:
            logger.info("archivo de configuración voicemaster no encontrado, creando nuevo")
            self.guild_configs = {}
        except Exception as e:
            logger.error(f"error cargando configuración voicemaster: {e}")
            self.guild_configs = {}
    
    def save_config(self):
        """guardar configuración en archivo"""
        try:
            import os
            os.makedirs("data", exist_ok=True)
            
            data = {
                'guild_configs': self.guild_configs
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"error guardando configuración voicemaster: {e}")
    
    @commands.command(name='vmsetup', aliases=['voicemastersetup'])
    @commands.has_permissions(administrator=True)
    async def setup_voicemaster(self, ctx, channel: nextcord.VoiceChannel = None):
        """
        configurar voicemaster en un canal
        uso: !vmsetup [#canal_voz]
        """
        try:
            if not channel:
                await ctx.send("❌ debes mencionar un canal de voz. uso: `!vmsetup #canal_voz`")
                return
            
            # configurar guild
            self.guild_configs[ctx.guild.id] = {
                'join_to_create_channel': channel.id,
                'category_id': channel.category_id if channel.category else None,
                'enabled': True
            }
            
            # guardar configuración
            self.save_config()
            
            embed = nextcord.Embed(
                title="🎤 voicemaster configurado",
                description=f"canal configurado: {channel.mention}",
                color=nextcord.Color.green()
            )
            embed.add_field(
                name="funcionamiento",
                value="los usuarios que se unan a este canal crearán automáticamente su propio canal temporal",
                inline=False
            )
            embed.add_field(
                name="controles",
                value="el dueño del canal podrá gestionarlo con botones en el panel de control",
                inline=False
            )
            
            await ctx.send(embed=embed)
            logger.info(f"voicemaster configurado en {ctx.guild.name}: {channel.name}")
            
        except Exception as e:
            logger.error(f"error configurando voicemaster: {e}")
            await ctx.send("❌ error al configurar voicemaster.")
    
    @commands.command(name='vmpanel', aliases=['voicemasterpanel'])
    async def voicemaster_panel(self, ctx):
        """
        mostrar panel de control de voicemaster
        uso: !vmpanel
        """
        try:
            # verificar que el usuario esté en un canal temporal
            if not ctx.author.voice or not ctx.author.voice.channel:
                await ctx.send("❌ debes estar en un canal de voz para usar el panel.")
                return
            
            voice_channel = ctx.author.voice.channel
            
            if voice_channel.id not in self.temp_channels:
                await ctx.send("❌ debes estar en un canal temporal para usar el panel.")
                return
            
            channel_data = self.temp_channels[voice_channel.id]
            
            # verificar que sea el dueño
            if ctx.author.id != channel_data['owner_id']:
                await ctx.send("❌ solo el dueño del canal puede usar el panel.")
                return
            
            # crear embed del panel
            embed = nextcord.Embed(
                title="🎤 panel de control voicemaster",
                description=f"canal: **{voice_channel.name}**",
                color=nextcord.Color.blue()
            )
            
            embed.add_field(
                name="👤 dueño",
                value=f"<@{channel_data['owner_id']}>",
                inline=True
            )
            
            embed.add_field(
                name="👥 usuarios",
                value=f"{len(voice_channel.members)}/{voice_channel.user_limit if voice_channel.user_limit else '∞'}",
                inline=True
            )
            
            embed.add_field(
                name="🔒 estado",
                value="cerrado" if voice_channel.overwrites_for(ctx.guild.default_role).connect == False else "abierto",
                inline=True
            )
            
            embed.add_field(
                name="controles disponibles",
                value="🔒 cerrar/🔓 abrir canal\n👥 cambiar límite\n📝 cambiar nombre\n👤 transferir propiedad\n🗑️ eliminar canal",
                inline=False
            )
            
            # crear vista con botones
            view = VoiceView(self, ctx.author.id)
            
            await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"error mostrando panel voicemaster: {e}")
            await ctx.send("❌ error al mostrar el panel.")
    
    @nextcord.slash_command(name="vmpanel", description="mostrar panel de control de voicemaster")
    async def slash_voicemaster_panel(self, interaction: nextcord.Interaction):
        """comando slash para panel voicemaster"""
        try:
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.response.send_message("❌ debes estar en un canal de voz para usar el panel.", ephemeral=True)
                return
            
            voice_channel = interaction.user.voice.channel
            
            if voice_channel.id not in self.temp_channels:
                await interaction.response.send_message("❌ debes estar en un canal temporal para usar el panel.", ephemeral=True)
                return
            
            channel_data = self.temp_channels[voice_channel.id]
            
            if interaction.user.id != channel_data['owner_id']:
                await interaction.response.send_message("❌ solo el dueño del canal puede usar el panel.", ephemeral=True)
                return
            
            embed = nextcord.Embed(
                title="🎤 panel de control voicemaster",
                description=f"canal: **{voice_channel.name}**",
                color=nextcord.Color.blue()
            )
            
            embed.add_field(
                name="👤 dueño",
                value=f"<@{channel_data['owner_id']}>",
                inline=True
            )
            
            embed.add_field(
                name="👥 usuarios",
                value=f"{len(voice_channel.members)}/{voice_channel.user_limit if voice_channel.user_limit else '∞'}",
                inline=True
            )
            
            embed.add_field(
                name="🔒 estado",
                value="cerrado" if voice_channel.overwrites_for(interaction.guild.default_role).connect == False else "abierto",
                inline=True
            )
            
            view = VoiceView(self, interaction.user.id)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"error en slash vmpanel: {e}")
            await interaction.response.send_message("❌ error al mostrar el panel.", ephemeral=True)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """manejar cambios en canales de voz"""
        try:
            # usuario se unió a un canal
            if after.channel and after.channel.id in self.guild_configs.get(member.guild.id, {}).get('join_to_create_channel', []):
                if not isinstance(self.guild_configs.get(member.guild.id, {}).get('join_to_create_channel'), list):
                    join_channels = [self.guild_configs[member.guild.id]['join_to_create_channel']]
                else:
                    join_channels = self.guild_configs[member.guild.id]['join_to_create_channel']
                
                if after.channel.id in join_channels:
                    await self.create_temp_channel(member, after.channel)
            
            # usuario salió de un canal temporal
            if before.channel and before.channel.id in self.temp_channels:
                await self.check_empty_temp_channel(before.channel)
                
        except Exception as e:
            logger.error(f"error en voice state update: {e}")
    
    async def create_temp_channel(self, member, join_channel):
        """crear canal temporal para usuario"""
        try:
            guild_config = self.guild_configs.get(member.guild.id, {})
            
            if not guild_config.get('enabled', False):
                return
            
            # obtener categoría
            category = None
            if guild_config.get('category_id'):
                category = member.guild.get_channel(guild_config['category_id'])
            
            if not category:
                category = join_channel.category
            
            # crear canal temporal
            temp_channel = await member.guild.create_voice_channel(
                name=f"🎤│{member.display_name}",
                category=category,
                reason=f"canal temporal creado por {member}"
            )
            
            # mover usuario al canal temporal
            await member.move_to(temp_channel)
            
            # guardar datos del canal
            self.temp_channels[temp_channel.id] = {
                'owner_id': member.id,
                'created_at': asyncio.get_event_loop().time()
            }
            
            logger.info(f"canal temporal creado: {temp_channel.name} por {member}")
            
        except Exception as e:
            logger.error(f"error creando canal temporal: {e}")
    
    async def check_empty_temp_channel(self, channel):
        """verificar si canal temporal está vacío y eliminarlo"""
        try:
            # esperar un poco para evitar eliminar prematuramente
            await asyncio.sleep(5)
            
            # verificar si el canal aún existe y está vacío
            if channel and len(channel.members) == 0:
                if channel.id in self.temp_channels:
                    del self.temp_channels[channel.id]
                
                await channel.delete(reason="canal temporal vacío")
                logger.info(f"canal temporal eliminado: {channel.name}")
                
        except Exception as e:
            logger.error(f"error verificando canal vacío: {e}")

def setup(bot):
    """función para cargar el cog"""
    return VoiceMaster(bot)
