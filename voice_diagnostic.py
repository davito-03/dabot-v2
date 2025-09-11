"""
Diagnóstico completo de conexión Discord Voice
Identifica la causa exacta del Error 4006
"""

import nextcord
from nextcord.ext import commands
import asyncio
import aiohttp
import logging
import os
from urllib.parse import urlparse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VoiceDiagnostic:
    def __init__(self, token):
        self.token = token
        self.intents = nextcord.Intents.default()
        self.intents.voice_states = True
        self.intents.guilds = True
        self.intents.message_content = True  # Agregar intent de contenido
        
        self.bot = commands.Bot(
            command_prefix='!',
            intents=self.intents,
            help_command=None
        )
        
        @self.bot.event
        async def on_ready():
            print(f"🤖 Bot conectado: {self.bot.user}")
            await self.run_diagnostics()
            
    async def test_network_connectivity(self):
        """Probar conectividad de red básica"""
        print("\n🌐 PROBANDO CONECTIVIDAD DE RED...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test Discord API
                async with session.get('https://discord.com/api/v10/gateway') as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"✅ Discord API: {data['url']}")
                    else:
                        print(f"❌ Discord API failed: {resp.status}")
                        
                # Test Discord CDN
                async with session.get('https://cdn.discordapp.com/') as resp:
                    print(f"✅ Discord CDN: {resp.status}" if resp.status == 200 else f"❌ Discord CDN: {resp.status}")
                    
        except Exception as e:
            print(f"❌ Error de conectividad: {e}")
            
    async def test_voice_regions(self):
        """Probar regiones de voz disponibles"""
        print("\n🌍 PROBANDO REGIONES DE VOZ...")
        
        try:
            # Obtener regiones disponibles
            voice_regions = await self.bot.fetch_voice_regions()
            print(f"✅ Regiones disponibles: {len(voice_regions)}")
            
            for region in voice_regions:
                status = "🟢 Óptima" if region.optimal else "🟡 Disponible"
                print(f"  {region.name} ({region.id}): {status}")
                
        except Exception as e:
            print(f"❌ Error obteniendo regiones: {e}")
            
    async def test_bot_permissions(self):
        """Verificar permisos del bot en servidores"""
        print("\n🔑 VERIFICANDO PERMISOS...")
        
        for guild in self.bot.guilds:
            print(f"\n🏰 Servidor: {guild.name}")
            
            # Verificar permisos del bot
            bot_member = guild.get_member(self.bot.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                
                voice_perms = {
                    "Conectar": perms.connect,
                    "Hablar": perms.speak,
                    "Usar VAD": perms.use_voice_activation,
                    "Mover miembros": perms.move_members,
                    "Ver canales": perms.view_channel
                }
                
                for perm_name, has_perm in voice_perms.items():
                    status = "✅" if has_perm else "❌"
                    print(f"  {status} {perm_name}")
                    
                # Verificar canales de voz
                voice_channels = [ch for ch in guild.channels if isinstance(ch, nextcord.VoiceChannel)]
                print(f"  📢 Canales de voz: {len(voice_channels)}")
                
                for vc in voice_channels[:3]:  # Solo primeros 3
                    perms = vc.permissions_for(bot_member)
                    can_connect = perms.connect and perms.speak
                    status = "✅" if can_connect else "❌"
                    print(f"    {status} {vc.name}")
                    
    async def test_voice_connection(self):
        """Intentar conexión de voz real"""
        print("\n🎵 PROBANDO CONEXIÓN DE VOZ...")
        
        for guild in self.bot.guilds:
            print(f"\n🏰 Probando en: {guild.name}")
            
            # Buscar canal de voz con miembros
            target_channel = None
            for channel in guild.voice_channels:
                bot_member = guild.get_member(self.bot.user.id)
                if bot_member and channel.permissions_for(bot_member).connect:
                    target_channel = channel
                    break
                    
            if not target_channel:
                print("  ❌ No hay canales de voz accesibles")
                continue
                
            print(f"  🎯 Intentando conectar a: {target_channel.name}")
            
            try:
                # Intentar conexión con timeout
                voice_client = await asyncio.wait_for(
                    target_channel.connect(),
                    timeout=30.0
                )
                
                print("  ✅ ¡CONEXIÓN EXITOSA!")
                print(f"  📊 Endpoint: {voice_client.endpoint}")
                print(f"  🌍 Región: {voice_client.server_id}")
                
                # Desconectar inmediatamente
                await voice_client.disconnect()
                print("  ✅ Desconectado correctamente")
                
                return True
                
            except asyncio.TimeoutError:
                print("  ❌ TIMEOUT - Conexión tardó más de 30 segundos")
            except nextcord.errors.ConnectionClosed as e:
                print(f"  ❌ ERROR {e.code}: {e}")
                if e.code == 4006:
                    print("  🚨 Error 4006 - Token inválido o permisos insuficientes")
            except Exception as e:
                print(f"  ❌ Error inesperado: {e}")
                
        return False
        
    async def analyze_environment(self):
        """Analizar entorno de ejecución"""
        print("\n🔍 ANALIZANDO ENTORNO...")
        
        import platform
        import sys
        
        print(f"🐍 Python: {sys.version}")
        print(f"💻 Sistema: {platform.system()} {platform.release()}")
        print(f"📦 Nextcord: {nextcord.__version__}")
        
        # Verificar variables de entorno
        env_vars = [
            'RAILWAY_ENVIRONMENT',
            'RENDER',
            'HEROKU_APP_NAME',
            'PORT',
            'MUSIC_DISABLED'
        ]
        
        print("\n🌐 Variables de entorno:")
        for var in env_vars:
            value = os.getenv(var, 'No configurada')
            print(f"  {var}: {value}")
            
        # Verificar si estamos en un contenedor
        if os.path.exists('/.dockerenv'):
            print("🐳 Ejecutándose en Docker")
        elif os.getenv('RAILWAY_ENVIRONMENT'):
            print("🚂 Ejecutándose en Railway")
        elif os.getenv('RENDER'):
            print("🎨 Ejecutándose en Render")
        else:
            print("💻 Ejecutándose localmente")
            
    async def run_diagnostics(self):
        """Ejecutar todos los diagnósticos"""
        print("🚀 INICIANDO DIAGNÓSTICO COMPLETO DE DISCORD VOICE\n")
        
        await self.analyze_environment()
        await self.test_network_connectivity()
        await self.test_voice_regions()
        await self.test_bot_permissions()
        
        # Test crítico de conexión
        success = await self.test_voice_connection()
        
        print("\n" + "="*50)
        if success:
            print("🎉 DIAGNÓSTICO: ¡Voice funciona correctamente!")
        else:
            print("❌ DIAGNÓSTICO: Voice NO funciona")
            print("\n🔧 POSIBLES SOLUCIONES:")
            print("1. Regenerar token de Discord")
            print("2. Verificar permisos del bot en servidor")
            print("3. Cambiar región del servidor Discord")
            print("4. Migrar a hosting diferente")
        print("="*50)
        
        await self.bot.close()
        
    def run(self):
        """Ejecutar diagnóstico"""
        try:
            self.bot.run(self.token)
        except Exception as e:
            print(f"❌ Error al iniciar bot: {e}")

if __name__ == "__main__":
    # Leer token desde .env
    import dotenv
    dotenv.load_dotenv()
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ No se encontró DISCORD_TOKEN en .env")
        exit(1)
        
    print("🔍 Iniciando diagnóstico de Discord Voice...")
    diagnostic = VoiceDiagnostic(token)
    diagnostic.run()
