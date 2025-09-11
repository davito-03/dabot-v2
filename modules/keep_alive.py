"""
Sistema de Keep-Alive para mantener el bot activo 24/7 en Render
Incluye servidor HTTP, pings internos y monitoreo de estado
"""

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from aiohttp import web, ClientSession
import json
import os

# Importación opcional de psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil no disponible - usando modo básico")

logger = logging.getLogger(__name__)

class KeepAliveSystem:
    """Sistema completo para mantener el bot activo en servicios de hosting"""
    
    def __init__(self, bot):
        self.bot = bot
        self.app = None
        self.runner = None
        self.site = None
        self.port = int(os.getenv('PORT', 8080))
        self.host = '0.0.0.0'
        
        # Estadísticas
        self.start_time = datetime.now()
        self.ping_count = 0
        self.last_ping = None
        self.health_checks = 0
        
        # URLs de ping externo (servicios gratuitos)
        self.ping_urls = [
            f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')}:{self.port}/health",
            f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')}:{self.port}/ping"
        ]
        
        # Estado del sistema
        self.is_running = False
        
    async def start(self):
        """Iniciar el sistema completo de keep-alive"""
        try:
            logger.info("🚀 Iniciando sistema Keep-Alive...")
            
            # Crear aplicación web
            self.app = web.Application()
            self.setup_routes()
            
            # Iniciar servidor HTTP
            await self.start_http_server()
            
            # Iniciar tareas de keep-alive
            await self.start_keep_alive_tasks()
            
            self.is_running = True
            logger.info(f"✅ Sistema Keep-Alive activo en http://{self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"❌ Error iniciando Keep-Alive: {e}")
            
    async def stop(self):
        """Detener el sistema keep-alive"""
        try:
            self.is_running = False
            
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
                
            logger.info("⏹️ Sistema Keep-Alive detenido")
            
        except Exception as e:
            logger.error(f"Error deteniendo Keep-Alive: {e}")
    
    def setup_routes(self):
        """Configurar rutas HTTP"""
        self.app.router.add_get('/', self.home_handler)
        self.app.router.add_get('/health', self.health_handler)
        self.app.router.add_get('/ping', self.ping_handler)
        self.app.router.add_get('/status', self.status_handler)
        self.app.router.add_get('/uptime', self.uptime_handler)
        self.app.router.add_post('/webhook', self.webhook_handler)
    
    async def start_http_server(self):
        """Iniciar servidor HTTP"""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()
            
            logger.info(f"🌐 Servidor HTTP iniciado en {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Error iniciando servidor HTTP: {e}")
            raise
    
    async def start_keep_alive_tasks(self):
        """Iniciar tareas en background para mantener activo"""
        # Tarea de ping interno cada 5 minutos
        asyncio.create_task(self.internal_ping_task())
        
        # Tarea de auto-ping cada 10 minutos (solo en Render)
        if os.getenv('RENDER'):
            asyncio.create_task(self.external_ping_task())
        
        # Tarea de limpieza cada hora
        asyncio.create_task(self.cleanup_task())
        
        logger.info("🔄 Tareas de Keep-Alive iniciadas")
    
    async def internal_ping_task(self):
        """Tarea interna de ping cada 5 minutos"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # 5 minutos
                
                self.ping_count += 1
                self.last_ping = datetime.now()
                
                # Log ping interno
                logger.info(f"💓 Ping interno #{self.ping_count} - Bot activo")
                
                # Verificar estado del bot
                if self.bot.is_ready():
                    latency = round(self.bot.latency * 1000, 2)
                    logger.debug(f"🏓 Latencia Discord: {latency}ms")
                
            except Exception as e:
                logger.error(f"Error en ping interno: {e}")
                await asyncio.sleep(60)  # Reintentar en 1 minuto
    
    async def external_ping_task(self):
        """Tarea de ping externo para mantener el servicio activo"""
        await asyncio.sleep(600)  # Esperar 10 minutos antes del primer ping
        
        while self.is_running:
            try:
                # Hacer ping a nosotros mismos
                async with ClientSession() as session:
                    for url in self.ping_urls:
                        try:
                            async with session.get(url, timeout=30) as response:
                                if response.status == 200:
                                    logger.info(f"🌐 Ping externo exitoso: {url}")
                                    break
                        except Exception as e:
                            logger.warning(f"Ping externo falló: {url} - {e}")
                
                # Esperar 10 minutos antes del siguiente ping
                await asyncio.sleep(600)
                
            except Exception as e:
                logger.error(f"Error en ping externo: {e}")
                await asyncio.sleep(300)  # Reintentar en 5 minutos
    
    async def cleanup_task(self):
        """Tarea de limpieza cada hora"""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # 1 hora
                
                # Limpiar logs antiguos, caché, etc.
                logger.info("🧹 Ejecutando limpieza de sistema...")
                
                # Información de memoria (si psutil disponible)
                if PSUTIL_AVAILABLE:
                    memory = psutil.virtual_memory()
                    logger.info(f"💾 Memoria: {memory.percent}% usada")
                else:
                    logger.info("💾 Memoria: Monitoreo no disponible")
                
            except Exception as e:
                logger.error(f"Error en limpieza: {e}")
    
    # ===== HANDLERS HTTP =====
    
    async def home_handler(self, request):
        """Página principal"""
        uptime = datetime.now() - self.start_time
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DaBot v2 - Keep Alive</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #2c2f33; color: #ffffff; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .status {{ padding: 20px; background: #23272a; border-radius: 8px; margin: 20px 0; }}
                .online {{ border-left: 4px solid #43b581; }}
                .info {{ padding: 10px; background: #36393f; border-radius: 4px; margin: 10px 0; }}
                h1 {{ color: #7289da; }}
                .ping-btn {{ background: #7289da; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 DaBot v2 - Keep Alive System</h1>
                
                <div class="status online">
                    <h2>✅ Bot Status: ONLINE</h2>
                    <div class="info">Uptime: {uptime}</div>
                    <div class="info">Pings internos: {self.ping_count}</div>
                    <div class="info">Health checks: {self.health_checks}</div>
                    <div class="info">Último ping: {self.last_ping or 'N/A'}</div>
                </div>
                
                <div class="info">
                    <strong>Endpoints disponibles:</strong><br>
                    • <a href="/health">/health</a> - Health check<br>
                    • <a href="/ping">/ping</a> - Ping simple<br>
                    • <a href="/status">/status</a> - Estado detallado<br>
                    • <a href="/uptime">/uptime</a> - Tiempo activo
                </div>
                
                <button class="ping-btn" onclick="fetch('/ping').then(r => alert('Ping enviado!'))">
                    Enviar Ping Manual
                </button>
            </div>
        </body>
        </html>
        """
        
        return web.Response(text=html, content_type='text/html')
    
    async def health_handler(self, request):
        """Endpoint de health check para Render"""
        self.health_checks += 1
        
        health_data = {
            "status": "healthy",
            "uptime": str(datetime.now() - self.start_time),
            "bot_ready": self.bot.is_ready(),
            "ping_count": self.ping_count,
            "health_checks": self.health_checks,
            "timestamp": datetime.now().isoformat(),
            "memory_usage": psutil.virtual_memory().percent if PSUTIL_AVAILABLE else "N/A"
        }
        
        if self.bot.is_ready():
            health_data["latency_ms"] = round(self.bot.latency * 1000, 2)
            health_data["guilds"] = len(self.bot.guilds)
        
        return web.json_response(health_data)
    
    async def ping_handler(self, request):
        """Endpoint simple de ping"""
        return web.json_response({
            "pong": True,
            "timestamp": datetime.now().isoformat(),
            "uptime": str(datetime.now() - self.start_time)
        })
    
    async def status_handler(self, request):
        """Endpoint de estado detallado"""
        status = {
            "bot": {
                "ready": self.bot.is_ready(),
                "latency": round(self.bot.latency * 1000, 2) if self.bot.is_ready() else None,
                "guilds": len(self.bot.guilds) if self.bot.is_ready() else 0,
                "users": sum(guild.member_count for guild in self.bot.guilds) if self.bot.is_ready() else 0
            },
            "system": {
                "uptime": str(datetime.now() - self.start_time),
                "ping_count": self.ping_count,
                "health_checks": self.health_checks,
                "last_ping": self.last_ping.isoformat() if self.last_ping else None,
                "memory_percent": psutil.virtual_memory().percent if PSUTIL_AVAILABLE else "N/A",
                "is_render": bool(os.getenv('RENDER'))
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return web.json_response(status)
    
    async def uptime_handler(self, request):
        """Endpoint simple de uptime"""
        uptime = datetime.now() - self.start_time
        return web.Response(text=str(uptime))
    
    async def webhook_handler(self, request):
        """Endpoint para webhooks externos (UptimeRobot, etc.)"""
        try:
            data = await request.json()
            logger.info(f"📡 Webhook recibido: {data}")
            
            return web.json_response({"received": True, "timestamp": datetime.now().isoformat()})
        except:
            return web.json_response({"received": True, "timestamp": datetime.now().isoformat()})

# Instancia global
keep_alive_system = None

async def setup_keep_alive(bot):
    """Configurar sistema keep-alive"""
    global keep_alive_system
    
    try:
        keep_alive_system = KeepAliveSystem(bot)
        await keep_alive_system.start()
        
        return keep_alive_system
        
    except Exception as e:
        logger.error(f"Error configurando Keep-Alive: {e}")
        return None

async def shutdown_keep_alive():
    """Cerrar sistema keep-alive"""
    global keep_alive_system
    
    if keep_alive_system:
        await keep_alive_system.stop()
        keep_alive_system = None
