"""
Módulo de Música para el bot de Discord
Incluye reproducción de música de YouTube con sistema de cola y búsqueda con resultados
"""

import asyncio
import datetime
import logging
import re
import nextcord
from nextcord.ext import commands
import yt_dlp
from collections import deque
from modules.config_manager import get_config, is_module_enabled

logger = logging.getLogger(__name__)

# Configuración para yt-dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(nextcord.PCMVolumeTransformer):
    """Fuente de audio para YouTube"""
    
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader')
        self.thumbnail = data.get('thumbnail')
    
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """Crear fuente de audio desde URL"""
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            # Tomar el primer resultado si es una playlist
            data = data['entries'][0]
        
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(nextcord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MusicQueue:
    """Sistema de cola para música"""
    
    def __init__(self):
        self.queue = deque()
        self.current = None
        self.loop = False
        self.volume = 0.5
    
    def add(self, song):
        """Agregar canción a la cola"""
        self.queue.append(song)
    
    def get_next(self):
        """Obtener siguiente canción"""
        if self.loop and self.current:
            return self.current
        
        if self.queue:
            self.current = self.queue.popleft()
            return self.current
        
        self.current = None
        return None
    
    def clear(self):
        """Limpiar la cola"""
        self.queue.clear()
        self.current = None
    
    def skip(self):
        """Saltar canción actual"""
        if self.queue:
            self.current = self.queue.popleft()
            return self.current
        self.current = None
        return None

class MusicSearchView(nextcord.ui.View):
    """Vista para seleccionar resultados de búsqueda musical"""
    
    def __init__(self, music_cog, search_results, user):
        super().__init__(timeout=60.0)
        self.music_cog = music_cog
        self.search_results = search_results
        self.user = user
        
        # Añadir botones para cada resultado (máximo 5)
        for i, result in enumerate(search_results[:5]):
            button = nextcord.ui.Button(
                label=f"{i+1}",
                style=nextcord.ButtonStyle.primary,
                emoji="🎵"
            )
            button.callback = self.create_callback(i)
            self.add_item(button)
        
        # Botón de cancelar
        cancel_button = nextcord.ui.Button(
            label="Cancelar",
            style=nextcord.ButtonStyle.danger,
            emoji="❌"
        )
        cancel_button.callback = self.cancel_search
        self.add_item(cancel_button)
    
    def create_callback(self, index):
        """Crear callback para botón específico"""
        async def callback(interaction: nextcord.Interaction):
            if interaction.user != self.user:
                await interaction.response.send_message("❌ Solo quien ejecutó el comando puede seleccionar.", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            selected_song = self.search_results[index]
            
            try:
                # Añadir a la cola
                queue = self.music_cog.get_queue(interaction.guild.id)
                queue.add(selected_song)
                
                # Reproducir si no hay nada sonando
                if not interaction.guild.voice_client.is_playing():
                    await self.music_cog.play_next_song(interaction.guild)
                    status = "🎵 Reproduciendo ahora"
                else:
                    status = f"📝 Añadida a la cola (posición {len(queue.queue)})"
                
                # Crear embed de confirmación
                embed = nextcord.Embed(
                    title=status,
                    description=f"**{selected_song['title']}**",
                    color=0x00ff00
                )
                embed.add_field(name="Artista", value=selected_song.get('uploader', 'Desconocido'), inline=True)
                embed.add_field(name="Duración", value=selected_song.get('duration_str', 'N/A'), inline=True)
                embed.add_field(name="URL", value=f"[Ver en YouTube]({selected_song['url']})", inline=True)
                
                if selected_song.get('thumbnail'):
                    embed.set_thumbnail(url=selected_song['thumbnail'])
                
                embed.set_footer(text=f"Solicitado por {interaction.user.display_name}")
                
                await interaction.edit_original_response(content=None, embed=embed, view=None)
                
            except Exception as e:
                logger.error(f"Error al reproducir canción seleccionada: {e}")
                await interaction.edit_original_response(
                    content=f"❌ Error al reproducir: {str(e)}",
                    embed=None,
                    view=None
                )
            
            self.stop()
        
        return callback
    
    async def cancel_search(self, interaction: nextcord.Interaction):
        """Cancelar búsqueda"""
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Solo quien ejecutó el comando puede cancelar.", ephemeral=True)
            return
        
        embed = nextcord.Embed(
            title="❌ Búsqueda Cancelada",
            description="La búsqueda de música ha sido cancelada.",
            color=0xff0000
        )
        
        await interaction.response.edit_message(content=None, embed=embed, view=None)
        self.stop()
    
    async def on_timeout(self):
        """Cuando se agota el timeout"""
        try:
            embed = nextcord.Embed(
                title="⏰ Tiempo Agotado",
                description="La búsqueda de música ha expirado. Usa `/play` nuevamente.",
                color=0xff6b00
            )
            # Intentar editar el mensaje original si existe
            if hasattr(self, 'message'):
                await self.message.edit(content=None, embed=embed, view=None)
        except:
            pass

class Music(commands.Cog):
    """Clase para comandos de música"""
    
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # Diccionario de colas por servidor
        
    def get_queue(self, guild_id):
        """Obtener cola de música para un servidor"""
        if guild_id not in self.queues:
            self.queues[guild_id] = MusicQueue()
        return self.queues[guild_id]
    
    async def get_song_info(self, url):
        """Obtener información completa de una canción"""
        try:
            data = await self.bot.loop.run_in_executor(
                None, 
                lambda: ytdl.extract_info(url, download=False)
            )
            
            if 'entries' in data:
                data = data['entries'][0]
            
            duration_str = "N/A"
            if data.get('duration'):
                minutes, seconds = divmod(data['duration'], 60)
                duration_str = f"{int(minutes):02d}:{int(seconds):02d}"
            
            return {
                'url': data['url'],
                'title': data.get('title', 'Título desconocido'),
                'duration': data.get('duration', 0),
                'duration_str': duration_str,
                'uploader': data.get('uploader', 'Desconocido'),
                'thumbnail': data.get('thumbnail'),
                'webpage_url': data.get('webpage_url', url)
            }
        except Exception as e:
            logger.error(f"Error obteniendo información de canción: {e}")
            return None
    
    async def play_next_song(self, guild):
        """Reproducir siguiente canción en la cola"""
        queue = self.get_queue(guild.id)
        next_song = queue.get_next()
        
        if next_song and guild.voice_client:
            try:
                source = await YTDLSource.from_url(next_song['url'], loop=self.bot.loop, stream=True)
                source.volume = queue.volume
                
                guild.voice_client.play(
                    source, 
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.play_next_song(guild), 
                        self.bot.loop
                    ) if not e else logger.error(f'Error en reproducción: {e}')
                )
                
            except Exception as e:
                logger.error(f"Error reproduciendo canción: {e}")
                await self.play_next_song(guild)
    
    async def _search_youtube(self, query: str, limit: int = 5):
        """Buscar videos en YouTube y devolver resultados"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'default_search': f'ytsearch{limit}:',
                'skip_download': True,
            }
            
            data = await self.bot.loop.run_in_executor(
                None,
                lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(query, download=False)
            )
            
            if 'entries' in data:
                results = []
                for entry in data['entries']:
                    if entry:
                        duration_str = "N/A"
                        if entry.get('duration'):
                            minutes, seconds = divmod(entry['duration'], 60)
                            duration_str = f"{int(minutes):02d}:{int(seconds):02d}"
                        
                        results.append({
                            'title': entry.get('title', 'Título desconocido'),
                            'url': entry.get('webpage_url', entry.get('url')),
                            'duration': entry.get('duration', 0),
                            'duration_str': duration_str,
                            'uploader': entry.get('uploader', 'Desconocido'),
                            'view_count': self._format_views(entry.get('view_count', 0)),
                            'thumbnail': entry.get('thumbnail')
                        })
                return results
            else:
                duration_str = "N/A"
                if data.get('duration'):
                    minutes, seconds = divmod(data['duration'], 60)
                    duration_str = f"{int(minutes):02d}:{int(seconds):02d}"
                
                return [{
                    'title': data.get('title', 'Título desconocido'),
                    'url': data.get('webpage_url', data.get('url')),
                    'duration': data.get('duration', 0),
                    'duration_str': duration_str,
                    'uploader': data.get('uploader', 'Desconocido'),
                    'view_count': self._format_views(data.get('view_count', 0)),
                    'thumbnail': data.get('thumbnail')
                }]
        except Exception as e:
            logger.error(f"Error en búsqueda de YouTube: {e}")
            return []
    
    def _format_views(self, views):
        """Formatear número de visualizaciones"""
        if not views:
            return "N/A"
        if views >= 1000000:
            return f"{views/1000000:.1f}M"
        elif views >= 1000:
            return f"{views/1000:.1f}K"
        else:
            return str(views)
    
    async def _play_direct_url(self, interaction, url):
        """Reproducir URL directa sin búsqueda"""
        try:
            data = await self.get_song_info(url)
            if data:
                queue = self.get_queue(interaction.guild.id)
                queue.add(data)
                
                if not interaction.guild.voice_client.is_playing():
                    await self.play_next_song(interaction.guild)
                    status = "🎵 Reproduciendo ahora"
                else:
                    status = f"📝 Añadida a la cola (posición {len(queue.queue)})"
                    
                embed = nextcord.Embed(
                    title=status,
                    description=f"**{data['title']}**",
                    color=0x00ff00
                )
                embed.add_field(name="Duración", value=data['duration_str'], inline=True)
                embed.add_field(name="URL", value=f"[Abrir en YouTube]({data['webpage_url']})", inline=True)
                
                if data.get('thumbnail'):
                    embed.set_thumbnail(url=data['thumbnail'])
                
                await interaction.edit_original_response(content=None, embed=embed)
            else:
                await interaction.edit_original_response(content="❌ No se pudo obtener información de la canción.")
        except Exception as e:
            logger.error(f"Error reproduciendo URL directa: {e}")
            await interaction.edit_original_response(content=f"❌ Error al reproducir: {str(e)}")

    @nextcord.slash_command(name="play", description="Reproduce música desde YouTube")
    async def slash_play(
        self,
        interaction: nextcord.Interaction,
        search: str = nextcord.SlashOption(description="URL de YouTube o términos de búsqueda")
    ):
        """Comando slash para reproducir música con selección de resultados"""
        await interaction.response.defer()
        
        # Verificar permisos
        if not is_module_enabled('music'):
            await interaction.followup.send("❌ El módulo de música está deshabilitado.", ephemeral=True)
            return
        
        # Verificar canal de voz
        if not interaction.user.voice:
            await interaction.followup.send("❌ Debes estar en un canal de voz para reproducir música.")
            return
        
        try:
            # Conectar al canal de voz si no está conectado
            voice_channel = interaction.user.voice.channel
            if not interaction.guild.voice_client:
                voice_client = await voice_channel.connect()
            else:
                voice_client = interaction.guild.voice_client
                if voice_client.channel != voice_channel:
                    await voice_client.move_to(voice_channel)
            
            # Si es una URL directa, reproducir inmediatamente
            if "youtube.com" in search or "youtu.be" in search:
                await self._play_direct_url(interaction, search)
                return
            
            # Si es una búsqueda, mostrar resultados
            await interaction.followup.send(f"🔍 Buscando: **{search}**...")
            search_results = await self._search_youtube(search, limit=5)
            
            if not search_results:
                await interaction.edit_original_response(content="❌ No se encontraron resultados para tu búsqueda.")
                return
            
            # Crear embed con resultados
            embed = nextcord.Embed(
                title="🎵 Resultados de Búsqueda",
                description=f"Selecciona una canción para reproducir:",
                color=0x00ff00
            )
            
            # Añadir resultados al embed
            for i, result in enumerate(search_results, 1):
                embed.add_field(
                    name=f"{i}. {result['title'][:50]}{'...' if len(result['title']) > 50 else ''}",
                    value=f"👤 **{result['uploader']}** | ⏱️ `{result['duration_str']}` | 👀 `{result['view_count']}`",
                    inline=False
                )
            
            embed.set_footer(text="Selecciona una opción o cancela la búsqueda")
            
            # Crear vista con botones de selección
            view = MusicSearchView(self, search_results, interaction.user)
            await interaction.edit_original_response(content=None, embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error en comando play: {e}")
            await interaction.followup.send(f"❌ Error al buscar música: {str(e)}")

    @nextcord.slash_command(name="skip", description="Salta la canción actual")
    async def slash_skip(self, interaction: nextcord.Interaction):
        """Saltar canción actual"""
        await interaction.response.defer()
        
        if not interaction.guild.voice_client:
            await interaction.followup.send("❌ No estoy reproduciendo música.")
            return
        
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await interaction.followup.send("⏭️ Canción saltada.")
        else:
            await interaction.followup.send("❌ No hay canción reproduciéndose.")

    @nextcord.slash_command(name="queue", description="Muestra la cola de reproducción")
    async def slash_queue(self, interaction: nextcord.Interaction):
        """Mostrar cola de reproducción"""
        await interaction.response.defer()
        
        queue = self.get_queue(interaction.guild.id)
        
        if not queue.current and not queue.queue:
            await interaction.followup.send("❌ La cola está vacía.")
            return
        
        embed = nextcord.Embed(
            title="🎵 Cola de Reproducción",
            color=0x00ff00
        )
        
        if queue.current:
            embed.add_field(
                name="🎵 Reproduciendo ahora:",
                value=f"**{queue.current['title']}**",
                inline=False
            )
        
        if queue.queue:
            queue_text = ""
            for i, song in enumerate(list(queue.queue)[:10], 1):
                queue_text += f"{i}. **{song['title'][:40]}{'...' if len(song['title']) > 40 else ''}**\n"
            
            embed.add_field(
                name=f"📝 En cola ({len(queue.queue)} canciones):",
                value=queue_text,
                inline=False
            )
            
            if len(queue.queue) > 10:
                embed.add_field(
                    name="➕ Y más...",
                    value=f"Hay {len(queue.queue) - 10} canciones más en la cola.",
                    inline=False
                )
        
        await interaction.followup.send(embed=embed)

    @nextcord.slash_command(name="stop", description="Detiene la música y limpia la cola")
    async def slash_stop(self, interaction: nextcord.Interaction):
        """Detener música y limpiar cola"""
        await interaction.response.defer()
        
        if not interaction.guild.voice_client:
            await interaction.followup.send("❌ No estoy conectado a un canal de voz.")
            return
        
        queue = self.get_queue(interaction.guild.id)
        queue.clear()
        
        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
        
        await interaction.guild.voice_client.disconnect()
        await interaction.followup.send("⏹️ Música detenida y cola limpiada.")

    @nextcord.slash_command(name="volume", description="Cambiar el volumen de la música")
    async def slash_volume(
        self, 
        interaction: nextcord.Interaction,
        volumen: int = nextcord.SlashOption(description="Volumen (0-100)", min_value=0, max_value=100)
    ):
        """Cambiar volumen"""
        await interaction.response.defer()
        
        if not interaction.guild.voice_client:
            await interaction.followup.send("❌ No estoy reproduciendo música.")
            return
        
        if not interaction.guild.voice_client.source:
            await interaction.followup.send("❌ No hay audio reproduciéndose.")
            return
        
        volume = volumen / 100
        queue = self.get_queue(interaction.guild.id)
        queue.volume = volume
        
        if hasattr(interaction.guild.voice_client.source, 'volume'):
            interaction.guild.voice_client.source.volume = volume
        
        await interaction.followup.send(f"🔊 Volumen cambiado a {volumen}%")

def setup(bot):
    bot.add_cog(Music(bot))
