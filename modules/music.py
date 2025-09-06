"""
Módulo de Música para el bot de Discord
Incluye reproducción de música de YouTube con sistema de cola
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
    
    async def play_next(self, ctx):
        """Reproducir siguiente canción en la cola"""
        queue = self.get_queue(ctx.guild.id)
        next_song = queue.get_next()
        
        if next_song and ctx.voice_client:
            try:
                source = await YTDLSource.from_url(next_song['url'], loop=self.bot.loop, stream=True)
                source.volume = queue.volume
                
                ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop) if not e else logger.error(f'Error en reproducción: {e}'))
                
                # Enviar información de la canción actual
                embed = nextcord.Embed(
                    title="🎵 Reproduciendo",
                    description=f"**{source.title}**",
                    color=nextcord.Color.green()
                )
                
                if source.uploader:
                    embed.add_field(name="Canal", value=source.uploader, inline=True)
                
                if source.duration:
                    minutes, seconds = divmod(source.duration, 60)
                    embed.add_field(name="Duración", value=f"{int(minutes):02d}:{int(seconds):02d}", inline=True)
                
                embed.add_field(name="Volumen", value=f"{int(source.volume * 100)}%", inline=True)
                
                if source.thumbnail:
                    embed.set_thumbnail(url=source.thumbnail)
                
                embed.set_footer(text=f"En cola: {len(queue.queue)} canciones")
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Error reproduciendo canción: {e}")
                await ctx.send(f"❌ Error reproduciendo: {str(e)}")
                await self.play_next(ctx)
        
        elif not next_song:
            # No hay más canciones
            embed = nextcord.Embed(
                title="🎵 Cola terminada",
                description="No hay más canciones en la cola.",
                color=nextcord.Color.blue()
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='play', aliases=['p'])
    async def play_music(self, ctx, *, search):
        """
        Reproduce música desde YouTube
        Uso: !play <URL o búsqueda>
        """
        try:
            # Verificar si el usuario está en un canal de voz
            if not ctx.author.voice:
                await ctx.send("❌ Debes estar en un canal de voz para usar este comando.")
                return
            
            # Conectar al canal de voz si no está conectado
            if not ctx.voice_client:
                channel = ctx.author.voice.channel
                await channel.connect()
                await ctx.send(f"🔗 Conectado a **{channel.name}**")
            
            # Verificar si es una URL válida
            url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
            
            if not url_pattern.match(search):
                search = f"ytsearch:{search}"
            
            # Enviar mensaje de búsqueda
            search_embed = nextcord.Embed(
                title="🔍 Buscando...",
                description=f"Buscando: **{search.replace('ytsearch:', '')}**",
                color=nextcord.Color.yellow()
            )
            search_msg = await ctx.send(embed=search_embed)
            
            # Extraer información del video
            try:
                data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
                
                if 'entries' in data and data['entries']:
                    data = data['entries'][0]
                
                # Agregar a la cola
                queue = self.get_queue(ctx.guild.id)
                song_info = {
                    'url': data['url'],
                    'title': data.get('title', 'Título desconocido'),
                    'duration': data.get('duration'),
                    'uploader': data.get('uploader'),
                    'thumbnail': data.get('thumbnail'),
                    'requester': ctx.author
                }
                
                queue.add(song_info)
                
                # Actualizar mensaje de búsqueda
                embed = nextcord.Embed(
                    title="✅ Agregado a la cola",
                    description=f"**{song_info['title']}**",
                    color=nextcord.Color.green()
                )
                
                if song_info['uploader']:
                    embed.add_field(name="Canal", value=song_info['uploader'], inline=True)
                
                if song_info['duration']:
                    minutes, seconds = divmod(song_info['duration'], 60)
                    embed.add_field(name="Duración", value=f"{int(minutes):02d}:{int(seconds):02d}", inline=True)
                
                embed.add_field(name="Posición en cola", value=len(queue.queue), inline=True)
                embed.add_field(name="Solicitado por", value=ctx.author.mention, inline=True)
                
                if song_info['thumbnail']:
                    embed.set_thumbnail(url=song_info['thumbnail'])
                
                await search_msg.edit(embed=embed)
                
                # Si no se está reproduciendo nada, empezar a reproducir
                if not ctx.voice_client.is_playing():
                    await self.play_next(ctx)
                    
            except Exception as e:
                logger.error(f"Error extrayendo información de video: {e}")
                await search_msg.edit(content="❌ Error al procesar el video. Verifica que el enlace sea válido.")
                
        except Exception as e:
            logger.error(f"Error en comando play: {e}")
            await ctx.send("❌ Ocurrió un error al intentar reproducir la música.")
    
    @nextcord.slash_command(name="play", description="Reproduce música desde YouTube")
    async def slash_play(
        self,
        interaction: nextcord.Interaction,
        search: str = nextcord.SlashOption(description="URL de YouTube o términos de búsqueda")
    ):
        """Comando slash para reproducir música"""
        await interaction.response.defer()
        
        # Verificar permisos
        config = get_config()
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
            
            # Buscar y agregar música
            await interaction.followup.send(f"🔍 Buscando: **{search}**...")
            
            if "youtube.com" in search or "youtu.be" in search:
                url = search
            else:
                # Buscar en YouTube
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'default_search': 'ytsearch1:',
                    'extractaudio': True,
                    'audioformat': 'mp3',
                    'outtmpl': '%(title)s.%(ext)s',
                    'nocheckcertificate': True,
                    'ignoreerrors': False,
                    'logtostderr': False,
                    'restrictfilenames': True,
                    'noplaylist': True,
                    'extract_flat': False,
                    'writethumbnail': False,
                    'writeinfojson': False
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    search_results = ydl.extract_info(search, download=False)
                    if 'entries' in search_results and search_results['entries']:
                        url = search_results['entries'][0]['webpage_url']
                    else:
                        await interaction.followup.send("❌ No se encontraron resultados.")
                        return
            
            # Extraer información del video
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extractaudio': True,
                'audioformat': 'mp3',
                'outtmpl': '%(title)s.%(ext)s',
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'logtostderr': False,
                'restrictfilenames': True,
                'noplaylist': True,
                'extract_flat': False
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                song_info = {
                    'url': info.get('url'),
                    'title': info.get('title', 'Título desconocido'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail'),
                    'webpage_url': info.get('webpage_url', url),
                    'requester': interaction.user.mention
                }
                
                queue = self.get_queue(interaction.guild.id)
                
                if voice_client.is_playing() or voice_client.is_paused():
                    # Agregar a la cola
                    queue.add_song(song_info)
                    embed = nextcord.Embed(
                        title="🎵 Agregado a la cola",
                        description=f"**{song_info['title']}**",
                        color=nextcord.Color.green()
                    )
                    embed.add_field(name="Posición en cola", value=f"{len(queue.queue)}", inline=True)
                    if song_info['duration']:
                        duration = str(datetime.timedelta(seconds=song_info['duration']))
                        embed.add_field(name="Duración", value=duration, inline=True)
                    embed.add_field(name="Solicitado por", value=song_info['requester'], inline=True)
                    if song_info['thumbnail']:
                        embed.set_thumbnail(url=song_info['thumbnail'])
                    
                    await interaction.followup.send(embed=embed)
                else:
                    # Reproducir inmediatamente
                    queue.current = song_info
                    ffmpeg_options = {
                        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                        'options': '-vn'
                    }
                    
                    voice_client.play(
                        nextcord.FFmpegPCMAudio(song_info['url'], **ffmpeg_options),
                        after=lambda e: self.bot.loop.create_task(self.play_next(interaction.guild)) if e else None
                    )
                    
                    embed = nextcord.Embed(
                        title="🎵 Reproduciendo ahora",
                        description=f"**{song_info['title']}**",
                        color=nextcord.Color.blue()
                    )
                    if song_info['duration']:
                        duration = str(datetime.timedelta(seconds=song_info['duration']))
                        embed.add_field(name="Duración", value=duration, inline=True)
                    embed.add_field(name="Solicitado por", value=song_info['requester'], inline=True)
                    if song_info['thumbnail']:
                        embed.set_thumbnail(url=song_info['thumbnail'])
                    
                    await interaction.followup.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"Error en comando slash play: {e}")
            await interaction.followup.send("❌ Error al reproducir la música.")
    
    @commands.command(name='skip', aliases=['s'])
    async def skip_song(self, ctx):
        """
        Salta la canción actual
        Uso: !skip
        """
        try:
            if not ctx.voice_client or not ctx.voice_client.is_playing():
                await ctx.send("❌ No se está reproduciendo música.")
                return
            
            ctx.voice_client.stop()
            await ctx.send("⏭️ Canción saltada.")
            
        except Exception as e:
            logger.error(f"Error en comando skip: {e}")
            await ctx.send("❌ Error al saltar la canción.")
    
    @nextcord.slash_command(name="skip", description="Salta la canción actual")
    async def slash_skip(self, interaction: nextcord.Interaction):
        """Comando slash para saltar canción"""
        await interaction.response.defer()
        
        # Verificar módulo habilitado
        if not is_module_enabled('music'):
            await interaction.followup.send("❌ El módulo de música está deshabilitado.", ephemeral=True)
            return
        
        try:
            if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
                await interaction.followup.send("❌ No se está reproduciendo música.")
                return
            
            interaction.guild.voice_client.stop()
            await interaction.followup.send("⏭️ Canción saltada.")
            
        except Exception as e:
            logger.error(f"Error en comando slash skip: {e}")
            await interaction.followup.send("❌ Error al saltar la canción.")
    
    @commands.command(name='stop')
    async def stop_music(self, ctx):
        """
        Detiene la música y limpia la cola
        Uso: !stop
        """
        try:
            if ctx.voice_client:
                queue = self.get_queue(ctx.guild.id)
                queue.clear()
                ctx.voice_client.stop()
                await ctx.send("⏹️ Música detenida y cola limpiada.")
            else:
                await ctx.send("❌ No estoy conectado a ningún canal de voz.")
                
        except Exception as e:
            logger.error(f"Error en comando stop: {e}")
            await ctx.send("❌ Error al detener la música.")
    
    @nextcord.slash_command(name="stop", description="Detiene la música y limpia la cola")
    async def slash_stop(self, interaction: nextcord.Interaction):
        """Comando slash para detener música"""
        await interaction.response.defer()
        
        # Verificar módulo habilitado
        if not is_module_enabled('music'):
            await interaction.followup.send("❌ El módulo de música está deshabilitado.", ephemeral=True)
            return
        
        try:
            if interaction.guild.voice_client:
                queue = self.get_queue(interaction.guild.id)
                queue.clear()
                interaction.guild.voice_client.stop()
                await interaction.followup.send("⏹️ Música detenida y cola limpiada.")
            else:
                await interaction.followup.send("❌ No estoy conectado a ningún canal de voz.")
                
        except Exception as e:
            logger.error(f"Error en comando slash stop: {e}")
            await interaction.followup.send("❌ Error al detener la música.")
    
    @commands.command(name='queue', aliases=['q'])
    async def show_queue(self, ctx):
        """
        Muestra la cola de reproducción actual
        Uso: !queue
        """
        try:
            queue = self.get_queue(ctx.guild.id)
            
            if not queue.current and not queue.queue:
                await ctx.send("❌ La cola está vacía.")
                return
            
            embed = nextcord.Embed(
                title="🎵 Cola de Reproducción",
                color=nextcord.Color.blue()
            )
            
            # Canción actual
            if queue.current:
                current_title = queue.current.get('title', 'Título desconocido')
                embed.add_field(
                    name="🎵 Reproduciendo ahora:",
                    value=f"**{current_title}**",
                    inline=False
                )
            
            # Próximas canciones
            if queue.queue:
                next_songs = []
                for i, song in enumerate(list(queue.queue)[:10], 1):  # Mostrar máximo 10
                    title = song.get('title', 'Título desconocido')
                    requester = song.get('requester', 'Desconocido')
                    next_songs.append(f"`{i}.` **{title}** - {requester.mention}")
                
                embed.add_field(
                    name=f"📋 Próximas ({len(queue.queue)} en total):",
                    value='\n'.join(next_songs),
                    inline=False
                )
                
                if len(queue.queue) > 10:
                    embed.add_field(
                        name="ℹ️ Información:",
                        value=f"Y {len(queue.queue) - 10} canciones más...",
                        inline=False
                    )
            
            # Configuración actual
            embed.add_field(name="🔁 Loop", value="Activado" if queue.loop else "Desactivado", inline=True)
            embed.add_field(name="🔊 Volumen", value=f"{int(queue.volume * 100)}%", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en comando queue: {e}")
            await ctx.send("❌ Error al mostrar la cola.")
    
    @nextcord.slash_command(name="queue", description="Muestra la cola de reproducción")
    async def slash_queue(self, interaction: nextcord.Interaction):
        """Comando slash para mostrar cola"""
        await interaction.response.defer()
        
        # Verificar módulo habilitado
        if not is_module_enabled('music'):
            await interaction.followup.send("❌ El módulo de música está deshabilitado.", ephemeral=True)
            return
        
        try:
            queue = self.get_queue(interaction.guild.id)
            
            if not queue.current and not queue.queue:
                await interaction.followup.send("❌ La cola está vacía.")
                return
            
            embed = nextcord.Embed(
                title="🎵 Cola de Reproducción",
                color=nextcord.Color.blue()
            )
            
            # Canción actual
            if queue.current:
                current_title = queue.current.get('title', 'Título desconocido')
                embed.add_field(
                    name="🎵 Reproduciendo ahora:",
                    value=f"**{current_title}**\nSolicitado por: {queue.current.get('requester', 'Desconocido')}",
                    inline=False
                )
            
            # Próximas canciones en cola
            if queue.queue:
                next_songs = []
                for i, song in enumerate(list(queue.queue)[:10]):  # Mostrar máximo 10
                    title = song.get('title', 'Título desconocido')
                    requester = song.get('requester', 'Desconocido')
                    next_songs.append(f"`{i+1}.` **{title}** - {requester}")
                
                if next_songs:
                    embed.add_field(
                        name=f"📋 Próximas canciones ({len(queue.queue)} en cola):",
                        value="\n".join(next_songs),
                        inline=False
                    )
                
                if len(queue.queue) > 10:
                    embed.add_field(
                        name="📝 Nota:",
                        value=f"Y {len(queue.queue) - 10} canciones más...",
                        inline=False
                    )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en comando slash queue: {e}")
            await interaction.followup.send("❌ Error al mostrar la cola.")
    
    @commands.command(name='volume', aliases=['vol'])
    async def set_volume(self, ctx, volume: int = None):
        """
        Ajusta el volumen de reproducción
        Uso: !volume [0-100]
        """
        try:
            if volume is None:
                queue = self.get_queue(ctx.guild.id)
                await ctx.send(f"🔊 Volumen actual: {int(queue.volume * 100)}%")
                return
            
            if volume < 0 or volume > 100:
                await ctx.send("❌ El volumen debe estar entre 0 y 100.")
                return
            
            queue = self.get_queue(ctx.guild.id)
            queue.volume = volume / 100
            
            if ctx.voice_client and ctx.voice_client.source:
                ctx.voice_client.source.volume = queue.volume
            
            await ctx.send(f"🔊 Volumen ajustado a {volume}%")
            
        except ValueError:
            await ctx.send("❌ Por favor proporciona un número válido.")
        except Exception as e:
            logger.error(f"Error en comando volume: {e}")
            await ctx.send("❌ Error al ajustar el volumen.")
    
    @nextcord.slash_command(name="volume", description="Ajusta el volumen de reproducción")
    async def slash_volume(
        self,
        interaction: nextcord.Interaction,
        volume: int = nextcord.SlashOption(description="Volumen (0-100)", min_value=0, max_value=100, required=False)
    ):
        """Comando slash para ajustar volumen"""
        await interaction.response.defer()
        
        # Verificar módulo habilitado
        if not is_module_enabled('music'):
            await interaction.followup.send("❌ El módulo de música está deshabilitado.", ephemeral=True)
            return
        
        try:
            if volume is None:
                queue = self.get_queue(interaction.guild.id)
                await interaction.followup.send(f"🔊 Volumen actual: {int(queue.volume * 100)}%")
                return
            
            if not interaction.guild.voice_client:
                await interaction.followup.send("❌ No estoy conectado a ningún canal de voz.")
                return
            
            queue = self.get_queue(interaction.guild.id)
            queue.volume = volume / 100.0
            
            if hasattr(interaction.guild.voice_client.source, 'volume'):
                interaction.guild.voice_client.source.volume = queue.volume
            
            await interaction.followup.send(f"🔊 Volumen ajustado a {volume}%")
            
        except Exception as e:
            logger.error(f"Error en comando slash volume: {e}")
            await interaction.followup.send("❌ Error al ajustar el volumen.")
    
    @commands.command(name='disconnect', aliases=['dc', 'leave'])
    async def disconnect(self, ctx):
        """
        Desconecta el bot del canal de voz
        Uso: !disconnect
        """
        try:
            if ctx.voice_client:
                queue = self.get_queue(ctx.guild.id)
                queue.clear()
                await ctx.voice_client.disconnect()
                await ctx.send("👋 Desconectado del canal de voz.")
            else:
                await ctx.send("❌ No estoy conectado a ningún canal de voz.")
                
        except Exception as e:
            logger.error(f"Error en comando disconnect: {e}")
            await ctx.send("❌ Error al desconectar.")
    
    @nextcord.slash_command(name="disconnect", description="Desconecta el bot del canal de voz")
    async def slash_disconnect(self, interaction: nextcord.Interaction):
        """Comando slash para desconectar"""
        await interaction.response.defer()
        
        # Verificar módulo habilitado
        if not is_module_enabled('music'):
            await interaction.followup.send("❌ El módulo de música está deshabilitado.", ephemeral=True)
            return
        
        try:
            if interaction.guild.voice_client:
                queue = self.get_queue(interaction.guild.id)
                queue.clear()
                await interaction.guild.voice_client.disconnect()
                await interaction.followup.send("👋 Desconectado del canal de voz.")
            else:
                await interaction.followup.send("❌ No estoy conectado a ningún canal de voz.")
                
        except Exception as e:
            logger.error(f"Error en comando slash disconnect: {e}")
            await interaction.followup.send("❌ Error al desconectar.")

def setup(bot):
    """Función setup para cargar el cog"""
    return Music(bot)
