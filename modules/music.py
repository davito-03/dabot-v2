"""
Módulo de Música para el bot de Discord
Incluye reproducción de música de YouTube con sistema de cola y búsqueda con resultados
"""

import asyncio
import datetime
import logging
import re
import subprocess
import nextcord
from nextcord.ext import commands
import yt_dlp
from collections import deque
from modules.config_manager import get_config, is_module_enabled
import requests
import json
from urllib.parse import quote

logger = logging.getLogger(__name__)

# Configuración para yt-dlp (optimizada para servidores)
ytdl_format_options = {
    'format': 'bestaudio[acodec!=opus]/bestaudio/best',  # Mejor calidad de audio disponible
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'prefer_ffmpeg': True,
    'keepvideo': False,
    # Configuración optimizada para servidores remotos
    'socket_timeout': 30,
    'http_chunk_size': 1024,
    'retries': 3,
    'fragment_retries': 3,
    'extractor_args': {
        'youtube': {
            'skip': ['hls', 'dash'],
            'player_skip': ['js']
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Connection': 'keep-alive'
    }
}

# Configurar FFmpeg optimizado para servidores remotos
def get_ffmpeg_executable():
    """Obtener la ruta del ejecutable de FFmpeg"""
    # Intentar rutas comunes (incluyendo contenedores Linux)
    ffmpeg_paths = [
        'ffmpeg',  # En PATH
        '/usr/bin/ffmpeg',  # Linux estándar
        '/usr/local/bin/ffmpeg',  # Linux local
        '/opt/render/project/.render/ffmpeg/ffmpeg',  # Render específico
        'C:/ffmpeg/bin/ffmpeg.exe',  # Windows personalizada
        'C:/Program Files/ffmpeg/bin/ffmpeg.exe',  # Windows estándar
    ]
    
    for path in ffmpeg_paths:
        try:
            subprocess.run([path, '-version'], 
                          capture_output=True, 
                          check=True,
                          timeout=5)
            logger.info(f"FFmpeg encontrado en: {path}")
            return path
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    logger.warning("FFmpeg no encontrado en rutas estándar, usando 'ffmpeg' por defecto")
    return 'ffmpeg'

# Configurar FFmpeg con opciones optimizadas para streaming
ffmpeg_executable = get_ffmpeg_executable()

# FFmpeg options optimizadas para servidores con conexiones inestables
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -http_persistent 0 -fflags +discardcorrupt',
    'options': '-vn -loglevel quiet -bufsize 64k -maxrate 128k',
    'executable': ffmpeg_executable
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
    async def from_url(cls, url, *, loop=None, stream=True):
        """Crear fuente de audio desde URL - optimizada para servidores remotos"""
        loop = loop or asyncio.get_event_loop()
        
        # Configuración específica para reproducción en servidores
        playback_opts = {
            'format': 'bestaudio[acodec!=opus]/bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'prefer_ffmpeg': True,
            'socket_timeout': 30,
            'http_chunk_size': 1024,
            'retries': 2,
            'fragment_retries': 2,
            # Forzar streaming para reducir uso de disco
            'noplaylist': True,
            'no_color': True
        }
        
        try:
            logger.info(f"Extrayendo información de: {url}")
            
            # Extraer información con timeout
            extract_task = loop.run_in_executor(
                None, 
                lambda: yt_dlp.YoutubeDL(playback_opts).extract_info(url, download=False)
            )
            
            try:
                data = await asyncio.wait_for(extract_task, timeout=30.0)
            except asyncio.TimeoutError:
                raise Exception("Timeout al extraer información del video")
            
            if 'entries' in data:
                # Tomar el primer resultado si es una playlist
                data = data['entries'][0]
            
            # Validar datos necesarios
            if not data:
                raise Exception("No se pudieron extraer datos del video")
                
            # Asegurar que tenemos una URL válida para streaming
            audio_url = data.get('url')
            if not audio_url:
                raise Exception("No se pudo obtener URL de audio")
            
            logger.info(f"URL de audio obtenida: {audio_url[:100]}...")
            
            # Crear el reproductor con opciones optimizadas
            try:
                source = nextcord.FFmpegPCMAudio(
                    audio_url,
                    **ffmpeg_options,
                    stderr=subprocess.DEVNULL  # Silenciar stderr de FFmpeg
                )
                return cls(source, data=data)
                
            except Exception as ffmpeg_error:
                logger.error(f"Error creando FFmpegPCMAudio: {ffmpeg_error}")
                # Intentar con opciones más básicas
                basic_options = {
                    'before_options': '-reconnect 1',
                    'options': '-vn -loglevel panic',
                    'executable': ffmpeg_executable
                }
                source = nextcord.FFmpegPCMAudio(audio_url, **basic_options)
                return cls(source, data=data)
            
        except Exception as e:
            logger.error(f"Error creando fuente de audio: {e}")
            raise Exception(f"No se pudo procesar el audio: {str(e)}")

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
                
                # Editar el mensaje original con el embed de confirmación
                await interaction.message.edit(content=None, embed=embed, view=None)
                
            except Exception as e:
                logger.error(f"Error al reproducir canción seleccionada: {e}")
                # Editar el mensaje original con el error
                error_embed = nextcord.Embed(
                    title="❌ Error",
                    description=f"Error al reproducir: {str(e)}",
                    color=0xff0000
                )
                await interaction.message.edit(content=None, embed=error_embed, view=None)
            
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
        
        # Usar defer() y luego editar el mensaje
        await interaction.response.defer()
        await interaction.message.edit(content=None, embed=embed, view=None)
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
        self.server_environment = self._detect_server_environment()
        
        # Advertencia para entornos de servidor
        if self.server_environment:
            logger.warning(
                f"🚨 Bot detectado en entorno de servidor ({self.server_environment}). "
                "Las funciones de voz pueden tener limitaciones."
            )
    
    def _detect_server_environment(self):
        """Detectar si estamos en un entorno de servidor hospedado"""
        import os
        
        # Detectar varios entornos de hosting
        if os.getenv('RENDER'):
            return 'Render'
        elif os.getenv('HEROKU'):
            return 'Heroku'
        elif os.getenv('RAILWAY_ENVIRONMENT'):
            return 'Railway'
        elif os.getenv('VERCEL'):
            return 'Vercel'
        elif os.getenv('FLYCTL_ORG'):
            return 'Fly.io'
        elif os.path.exists('/.dockerenv'):
            return 'Docker'
        elif os.getenv('container') == 'oci':
            return 'Container'
        
        return None
        
    def get_queue(self, guild_id):
        """Obtener cola de música para un servidor"""
        if guild_id not in self.queues:
            self.queues[guild_id] = MusicQueue()
        return self.queues[guild_id]
    
    async def get_song_info(self, url):
        """Obtener información completa de una canción"""
        try:
            # Configuración más simple para obtener info
            simple_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'worst[abr>0]/worst/best',
                'ignoreerrors': True
            }
            
            data = await self.bot.loop.run_in_executor(
                None, 
                lambda: yt_dlp.YoutubeDL(simple_opts).extract_info(url, download=False)
            )
            
            if 'entries' in data:
                data = data['entries'][0]
            
            duration_str = "N/A"
            if data.get('duration'):
                minutes, seconds = divmod(data['duration'], 60)
                duration_str = f"{int(minutes):02d}:{int(seconds):02d}"
            
            return {
                'url': data.get('url', url),  # Usar URL original como respaldo
                'title': data.get('title', 'Título desconocido'),
                'duration': data.get('duration', 0),
                'duration_str': duration_str,
                'uploader': data.get('uploader', 'Desconocido'),
                'thumbnail': data.get('thumbnail'),
                'webpage_url': data.get('webpage_url', url)
            }
        except Exception as e:
            logger.error(f"Error obteniendo información de canción: {e}")
            
            # Información básica como respaldo
            return {
                'url': url,
                'title': 'Video de YouTube',
                'duration': 0,
                'duration_str': 'N/A',
                'uploader': 'Desconocido',
                'thumbnail': None,
                'webpage_url': url
            }
    
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
        
        # Verificar si contiene errores comunes que indican que debemos usar método alternativo
        error_keywords = [
            "Sign in to confirm you're not a bot",
            "Requested format is not available",
            "This video is unavailable"
        ]
        
        # Saltar directamente al método alternativo si sabemos que yt-dlp tendrá problemas
        logger.info("Usando búsqueda alternativa directamente para mayor confiabilidad...")
        return await self._search_youtube_alternative(query, limit)
    
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
    
    async def _search_youtube_alternative(self, query: str, limit: int = 5):
        """Búsqueda alternativa usando requests cuando yt-dlp falla"""
        try:
            search_query = quote(query)
            url = f"https://www.youtube.com/results?search_query={search_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
                'Connection': 'keep-alive',
            }
            
            response = await self.bot.loop.run_in_executor(
                None,
                lambda: requests.get(url, headers=headers, timeout=10)
            )
            
            if response.status_code == 200:
                # Buscar datos JSON en la página
                pattern = r'var ytInitialData = ({.*?});'
                match = re.search(pattern, response.text)
                
                if match:
                    data = json.loads(match.group(1))
                    
                    # Extraer resultados
                    results = []
                    try:
                        contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
                        
                        for item in contents[:limit]:
                            if 'videoRenderer' in item:
                                video = item['videoRenderer']
                                
                                # Extraer información básica
                                video_id = video.get('videoId', '')
                                title = video.get('title', {}).get('runs', [{}])[0].get('text', 'Título desconocido')
                                
                                # Extraer canal
                                channel = 'Desconocido'
                                if 'ownerText' in video:
                                    channel = video['ownerText']['runs'][0]['text']
                                
                                # Extraer duración
                                duration_str = 'N/A'
                                if 'lengthText' in video:
                                    duration_str = video['lengthText']['simpleText']
                                
                                # Extraer thumbnail
                                thumbnail = None
                                if 'thumbnail' in video and 'thumbnails' in video['thumbnail']:
                                    thumbnail = video['thumbnail']['thumbnails'][-1]['url']
                                
                                results.append({
                                    'title': title,
                                    'url': f'https://www.youtube.com/watch?v={video_id}',
                                    'duration': 0,
                                    'duration_str': duration_str,
                                    'uploader': channel,
                                    'view_count': 'N/A',
                                    'thumbnail': thumbnail
                                })
                    
                    except Exception as parse_error:
                        logger.error(f"Error parseando resultados alternativos: {parse_error}")
                        return []
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Error en búsqueda alternativa: {e}")
            return []
    
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
                
                # Usar followup.send en lugar de edit_original_response
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("❌ No se pudo obtener información de la canción.")
        except Exception as e:
            logger.error(f"Error reproduciendo URL directa: {e}")
            await interaction.followup.send(f"❌ Error al reproducir: {str(e)}")

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
            # Conectar al canal de voz con manejo de errores mejorado
            voice_channel = interaction.user.voice.channel
            voice_client = None
            
            if not interaction.guild.voice_client:
                # Intentar conectar con reintentos
                for attempt in range(3):
                    try:
                        logger.info(f"Intento {attempt + 1} de conexión a canal de voz")
                        voice_client = await asyncio.wait_for(
                            voice_channel.connect(timeout=30.0, reconnect=True),
                            timeout=30.0
                        )
                        logger.info(f"Conectado exitosamente al canal: {voice_channel.name}")
                        break
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout en intento {attempt + 1} de conexión")
                        if attempt == 2:
                            await interaction.followup.send(
                                "❌ **Error de conexión de voz**\n"
                                "El bot no puede conectarse al canal de voz. Esto puede deberse a:\n"
                                "• Limitaciones del servidor de hosting\n"
                                "• Problemas de red temporales\n"
                                "• Restricciones de Discord\n\n"
                                "**Soluciones:**\n"
                                "1. Intenta de nuevo en unos minutos\n"
                                "2. Verifica los permisos del bot\n"
                                "3. Contacta al administrador del servidor"
                            )
                            return
                        await asyncio.sleep(2)  # Pausa entre intentos
                    except nextcord.errors.ConnectionClosed as e:
                        logger.error(f"Conexión cerrada en intento {attempt + 1}: {e}")
                        if attempt == 2:
                            await interaction.followup.send(
                                "❌ **Error de conexión WebSocket (Código 4006)**\n"
                                "Este error es común en servidores hospedados y significa que Discord rechazó la conexión de voz.\n\n"
                                "**Esto puede deberse a:**\n"
                                "• Limitaciones de la plataforma de hosting (Render, Heroku, etc.)\n"
                                "• Restricciones de red del servidor\n"
                                "• Configuración de firewall\n\n"
                                "**Alternativas:**\n"
                                "• Usar el bot en un servidor local\n"
                                "• Contactar al proveedor de hosting\n"
                                "• Considerar usar otros servicios de música"
                            )
                            return
                        await asyncio.sleep(3)
                    except Exception as e:
                        logger.error(f"Error inesperado en conexión {attempt + 1}: {e}")
                        if attempt == 2:
                            await interaction.followup.send(f"❌ Error de conexión: {str(e)}")
                            return
                        await asyncio.sleep(2)
            else:
                voice_client = interaction.guild.voice_client
                if voice_client.channel != voice_channel:
                    try:
                        await voice_client.move_to(voice_channel)
                        logger.info(f"Movido a canal: {voice_channel.name}")
                    except Exception as e:
                        logger.error(f"Error moviendo a canal: {e}")
                        # Intentar desconectar y reconectar
                        try:
                            await voice_client.disconnect(force=True)
                            voice_client = await voice_channel.connect(timeout=20.0)
                        except Exception as reconnect_error:
                            logger.error(f"Error en reconexión: {reconnect_error}")
                            await interaction.followup.send("❌ No se pudo cambiar de canal de voz.")
                            return
            
            # Si es una URL directa, reproducir inmediatamente
            if "youtube.com" in search or "youtu.be" in search:
                await self._play_direct_url(interaction, search)
                return
            
            # Si es una búsqueda, mostrar resultados
            search_msg = await interaction.followup.send(f"🔍 Buscando: **{search}**...")
            search_results = await self._search_youtube(search, limit=5)
            
            if not search_results:
                # Editar el mensaje de búsqueda con el error
                await search_msg.edit(content="❌ No se encontraron resultados para tu búsqueda.")
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
            # Editar el mensaje de búsqueda con el embed y los botones
            await search_msg.edit(content=None, embed=embed, view=view)
            
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

    @nextcord.slash_command(name="voice-info", description="Información sobre limitaciones de voz del bot")
    async def slash_voice_info(self, interaction: nextcord.Interaction):
        """Mostrar información sobre el sistema de voz y posibles limitaciones"""
        await interaction.response.defer()
        
        embed = nextcord.Embed(
            title="🎙️ Información del Sistema de Voz",
            color=0x00ff00 if not self.server_environment else 0xff9900
        )
        
        if self.server_environment:
            embed.add_field(
                name="⚠️ Entorno Detectado",
                value=f"**{self.server_environment}** - Pueden existir limitaciones de voz",
                inline=False
            )
            
            embed.add_field(
                name="🚨 Limitaciones Conocidas",
                value=(
                    "• **Error 4006**: Discord rechaza conexiones de voz desde algunos proveedores\n"
                    "• **Timeout**: Conexiones lentas o inestables\n"
                    "• **FFmpeg**: Posibles problemas de configuración\n"
                    "• **NAT/Firewall**: Restricciones de red del proveedor"
                ),
                inline=False
            )
            
            embed.add_field(
                name="💡 Soluciones Recomendadas",
                value=(
                    "1. **Reintentar**: Los errores pueden ser temporales\n"
                    "2. **Verificar permisos**: Asegurar permisos de voz del bot\n"
                    "3. **Contactar soporte**: Reportar problemas persistentes\n"
                    "4. **Servidor local**: Para funcionalidad completa"
                ),
                inline=False
            )
        else:
            embed.add_field(
                name="✅ Entorno Local",
                value="El bot está ejecutándose localmente, la funcionalidad de voz debería funcionar correctamente.",
                inline=False
            )
            
        # Información técnica
        embed.add_field(
            name="🔧 Información Técnica",
            value=(
                f"• **FFmpeg**: {ffmpeg_executable}\n"
                f"• **Nextcord**: {nextcord.__version__}\n"
                f"• **Python**: {__import__('sys').version.split()[0]}"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📞 Soporte",
            value=(
                "Si experimentas problemas persistentes:\n"
                "• Verifica los logs del bot\n"
                "• Reporta el error específico\n"
                "• Incluye información del entorno"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use /play para probar la funcionalidad de música")
        await interaction.followup.send(embed=embed)

def setup(bot):
    bot.add_cog(Music(bot))
