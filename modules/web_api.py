"""
api web para dashboard del bot
por davito
"""

import os
import json
import logging
import asyncio
import aiohttp
from aiohttp import web, ClientSession
import jwt
import datetime
from datetime import timedelta
from typing import Dict, List, Optional
import nextcord
from nextcord.ext import commands, tasks

logger = logging.getLogger(__name__)

def require_auth(func):
    """decorador para requerir autenticación"""
    async def wrapper(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return web.json_response({'error': 'token requerido'}, status=401)
        
        token = auth_header[7:]  # quitar "Bearer "
        payload = self.verify_jwt_token(token)
        
        if not payload:
            return web.json_response({'error': 'token inválido'}, status=401)
        
        request.user = payload
        return await func(self, request)
    
    return wrapper

class WebAPI(commands.Cog):
    """sistema de api web para dashboard"""
    
    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.config_file = "data/web_config.json"
        self.config = {}
        
        # obtener jwt secret de variables de entorno o usar default
        self.jwt_secret = os.getenv('JWT_SECRET', 'tu_clave_secreta_jwt_muy_segura_davito_2024')
        
        # cargar configuración
        self.load_config()
        
        # configurar rutas
        self.setup_routes()
        
        # iniciar servidor solo si el bot está listo
        self.bot.loop.create_task(self.delayed_start())
    
    async def delayed_start(self):
        """iniciar servidor después de que el bot esté listo"""
        await self.bot.wait_until_ready()
        self.start_server.start()
    
    def load_config(self):
        """cargar configuración web"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "port": 8080,
                "host": "0.0.0.0",
                "allowed_origins": ["https://dashboard.davito.es", "http://localhost:3000"],
                "api_tokens": {}
            }
            self.save_config()
        except Exception as e:
            logger.error(f"error cargando config web: {e}")
            self.config = {}
    
    def save_config(self):
        """guardar configuración web"""
        try:
            import os
            os.makedirs("data", exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando config web: {e}")
    
    def setup_routes(self):
        """configurar rutas de la api"""
        # middleware cors
        async def cors_middleware(request, handler):
            response = await handler(request)
            origin = request.headers.get('Origin')
            if origin in self.config.get('allowed_origins', []):
                response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        self.app.middlewares.append(cors_middleware)
        
        # rutas
        self.app.router.add_get('/api/status', self.api_status)
        self.app.router.add_post('/api/auth/discord', self.auth_discord)
        self.app.router.add_get('/api/guilds', self.get_guilds)
        self.app.router.add_get('/api/guilds/{guild_id}', self.get_guild_info)
        self.app.router.add_get('/api/guilds/{guild_id}/members', self.get_guild_members)
        self.app.router.add_get('/api/guilds/{guild_id}/channels', self.get_guild_channels)
        self.app.router.add_get('/api/tickets', self.get_tickets)
        self.app.router.add_get('/api/tickets/{ticket_id}', self.get_ticket)
        self.app.router.add_post('/api/tickets/{ticket_id}/close', self.close_ticket_api)
        self.app.router.add_post('/api/tickets/{ticket_id}/assign', self.assign_ticket_api)
        self.app.router.add_get('/api/economy/{guild_id}', self.get_economy_stats)
        self.app.router.add_get('/api/warnings/{guild_id}', self.get_warnings)
        self.app.router.add_post('/api/moderation/{guild_id}/action', self.moderation_action)
        
        # opciones para cors
        self.app.router.add_options('/{path:.*}', self.options_handler)
    
    async def options_handler(self, request):
        """manejar requests OPTIONS para CORS"""
        return web.Response(status=200)
    
    def generate_jwt_token(self, user_data: dict) -> str:
        """generar token jwt"""
        payload = {
            'user_id': str(user_data['id']),
            'username': user_data['username'],
            'avatar': user_data.get('avatar'),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[dict]:
        """verificar token jwt"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def api_status(self, request):
        """estado de la api"""
        return web.json_response({
            'status': 'online',
            'bot_name': self.bot.user.name if self.bot.user else 'dabot',
            'guilds': len(self.bot.guilds),
            'users': sum(guild.member_count for guild in self.bot.guilds),
            'uptime': str(datetime.datetime.now() - self.bot.start_time) if hasattr(self.bot, 'start_time') else 'unknown'
        })
    
    async def auth_discord(self, request):
        """autenticación con discord"""
        try:
            data = await request.json()
            access_token = data.get('access_token')
            
            if not access_token:
                return web.json_response({'error': 'access_token requerido'}, status=400)
            
            # obtener datos del usuario de discord
            async with ClientSession() as session:
                headers = {'Authorization': f'Bearer {access_token}'}
                
                async with session.get('https://discord.com/api/users/@me', headers=headers) as resp:
                    if resp.status != 200:
                        return web.json_response({'error': 'token inválido'}, status=401)
                    
                    user_data = await resp.json()
                
                # obtener guilds del usuario
                async with session.get('https://discord.com/api/users/@me/guilds', headers=headers) as resp:
                    user_guilds = await resp.json() if resp.status == 200 else []
            
            # verificar que el usuario esté en al menos un servidor del bot
            bot_guild_ids = {guild.id for guild in self.bot.guilds}
            user_guild_ids = {int(guild['id']) for guild in user_guilds}
            
            if not bot_guild_ids.intersection(user_guild_ids):
                return web.json_response({'error': 'no tienes acceso a ningún servidor del bot'}, status=403)
            
            # generar jwt token
            jwt_token = self.generate_jwt_token(user_data)
            
            return web.json_response({
                'token': jwt_token,
                'user': {
                    'id': user_data['id'],
                    'username': user_data['username'],
                    'discriminator': user_data['discriminator'],
                    'avatar': user_data['avatar']
                }
            })
            
        except Exception as e:
            logger.error(f"error en auth discord: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def get_guilds(self, request):
        """obtener guilds donde el usuario tiene permisos"""
        try:
            user_id = int(request.user['user_id'])
            user_guilds = []
            
            for guild in self.bot.guilds:
                member = guild.get_member(user_id)
                if member and (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                    user_guilds.append({
                        'id': str(guild.id),
                        'name': guild.name,
                        'icon': guild.icon.url if guild.icon else None,
                        'member_count': guild.member_count,
                        'owner': guild.owner_id == user_id
                    })
            
            return web.json_response({'guilds': user_guilds})
            
        except Exception as e:
            logger.error(f"error obteniendo guilds: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def get_guild_info(self, request):
        """obtener información de un guild"""
        try:
            guild_id = int(request.match_info['guild_id'])
            user_id = int(request.user['user_id'])
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return web.json_response({'error': 'servidor no encontrado'}, status=404)
            
            member = guild.get_member(user_id)
            if not member or not (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            # obtener estadísticas
            online_members = len([m for m in guild.members if m.status != nextcord.Status.offline])
            
            guild_info = {
                'id': str(guild.id),
                'name': guild.name,
                'icon': guild.icon.url if guild.icon else None,
                'banner': guild.banner.url if guild.banner else None,
                'description': guild.description,
                'member_count': guild.member_count,
                'online_members': online_members,
                'channel_count': len(guild.channels),
                'role_count': len(guild.roles),
                'owner_id': str(guild.owner_id),
                'created_at': guild.created_at.isoformat(),
                'premium_tier': guild.premium_tier,
                'features': guild.features
            }
            
            return web.json_response(guild_info)
            
        except Exception as e:
            logger.error(f"error obteniendo info guild: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def get_guild_members(self, request):
        """obtener miembros del guild"""
        try:
            guild_id = int(request.match_info['guild_id'])
            user_id = int(request.user['user_id'])
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return web.json_response({'error': 'servidor no encontrado'}, status=404)
            
            member = guild.get_member(user_id)
            if not member or not (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            # limitar a primeros 100 miembros para rendimiento
            members_data = []
            for m in list(guild.members)[:100]:
                members_data.append({
                    'id': str(m.id),
                    'username': m.name,
                    'discriminator': m.discriminator,
                    'display_name': m.display_name,
                    'avatar': m.avatar.url if m.avatar else None,
                    'status': str(m.status),
                    'joined_at': m.joined_at.isoformat() if m.joined_at else None,
                    'roles': [str(role.id) for role in m.roles if role != guild.default_role]
                })
            
            return web.json_response({'members': members_data})
            
        except Exception as e:
            logger.error(f"error obteniendo miembros: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def get_guild_channels(self, request):
        """obtener canales del guild"""
        try:
            guild_id = int(request.match_info['guild_id'])
            user_id = int(request.user['user_id'])
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return web.json_response({'error': 'servidor no encontrado'}, status=404)
            
            member = guild.get_member(user_id)
            if not member or not (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            channels_data = []
            for channel in guild.channels:
                channels_data.append({
                    'id': str(channel.id),
                    'name': channel.name,
                    'type': str(channel.type),
                    'category': channel.category.name if channel.category else None,
                    'position': channel.position,
                    'topic': getattr(channel, 'topic', None)
                })
            
            return web.json_response({'channels': channels_data})
            
        except Exception as e:
            logger.error(f"error obteniendo canales: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def get_tickets(self, request):
        """obtener tickets"""
        try:
            # obtener cog de tickets
            ticket_cog = self.bot.get_cog('TicketSystem')
            if not ticket_cog:
                return web.json_response({'error': 'sistema de tickets no disponible'}, status=503)
            
            # filtrar tickets por guilds del usuario
            user_id = int(request.user['user_id'])
            user_guild_ids = []
            
            for guild in self.bot.guilds:
                member = guild.get_member(user_id)
                if member and (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                    user_guild_ids.append(guild.id)
            
            tickets_data = []
            for ticket_id, ticket in ticket_cog.tickets.items():
                if ticket['guild_id'] in user_guild_ids:
                    # obtener información adicional
                    guild = self.bot.get_guild(ticket['guild_id'])
                    user = self.bot.get_user(ticket['user_id'])
                    
                    tickets_data.append({
                        'id': ticket_id,
                        'subject': ticket['subject'],
                        'description': ticket['description'],
                        'priority': ticket['priority'],
                        'status': ticket['status'],
                        'created_at': ticket['created_at'],
                        'closed_at': ticket.get('closed_at'),
                        'guild_name': guild.name if guild else 'desconocido',
                        'user_name': user.name if user else 'desconocido',
                        'assigned_to': ticket.get('assigned_to')
                    })
            
            return web.json_response({'tickets': tickets_data})
            
        except Exception as e:
            logger.error(f"error obteniendo tickets: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def get_ticket(self, request):
        """obtener ticket específico"""
        try:
            ticket_id = request.match_info['ticket_id']
            
            ticket_cog = self.bot.get_cog('TicketSystem')
            if not ticket_cog:
                return web.json_response({'error': 'sistema de tickets no disponible'}, status=503)
            
            ticket = ticket_cog.tickets.get(ticket_id)
            if not ticket:
                return web.json_response({'error': 'ticket no encontrado'}, status=404)
            
            # verificar permisos
            user_id = int(request.user['user_id'])
            guild = self.bot.get_guild(ticket['guild_id'])
            member = guild.get_member(user_id) if guild else None
            
            if not member or not (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            # obtener mensajes del canal
            channel = guild.get_channel(ticket['channel_id']) if guild else None
            messages_data = []
            
            if channel:
                try:
                    async for message in channel.history(limit=50):
                        messages_data.append({
                            'id': str(message.id),
                            'author': {
                                'id': str(message.author.id),
                                'name': message.author.name,
                                'avatar': message.author.avatar.url if message.author.avatar else None
                            },
                            'content': message.content,
                            'timestamp': message.created_at.isoformat(),
                            'attachments': [att.url for att in message.attachments]
                        })
                except:
                    pass
            
            ticket_data = ticket.copy()
            ticket_data['messages'] = list(reversed(messages_data))
            
            return web.json_response(ticket_data)
            
        except Exception as e:
            logger.error(f"error obteniendo ticket: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def close_ticket_api(self, request):
        """cerrar ticket via api"""
        try:
            ticket_id = request.match_info['ticket_id']
            user_id = int(request.user['user_id'])
            
            # cargar tickets
            tickets = await self.load_json('tickets.json')
            
            if ticket_id not in tickets:
                return web.json_response({'error': 'ticket no encontrado'}, status=404)
            
            ticket = tickets[ticket_id]
            
            # verificar permisos (solo el usuario o staff pueden cerrar)
            if ticket['user_id'] != user_id and not request.user.get('is_staff', False):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            # marcar como cerrado
            ticket['status'] = 'closed'
            ticket['closed_at'] = datetime.now().isoformat()
            ticket['closed_by'] = user_id
            
            # guardar
            await self.save_json('tickets.json', tickets)
            
            return web.json_response({
                'success': True,
                'message': 'ticket cerrado correctamente'
            })
            
        except Exception as e:
            logger.error(f"error cerrando ticket: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def assign_ticket_api(self, request):
        """asignar ticket a staff via api"""
        try:
            ticket_id = request.match_info['ticket_id']
            data = await request.json()
            staff_id = data.get('staff_id')
            
            if not staff_id:
                return web.json_response({'error': 'staff_id requerido'}, status=400)
            
            # cargar tickets
            tickets = await self.load_json('tickets.json')
            
            if ticket_id not in tickets:
                return web.json_response({'error': 'ticket no encontrado'}, status=404)
            
            # asignar staff
            tickets[ticket_id]['assigned_to'] = staff_id
            tickets[ticket_id]['assigned_at'] = datetime.now().isoformat()
            
            # guardar
            await self.save_json('tickets.json', tickets)
            
            return web.json_response({
                'success': True,
                'message': 'ticket asignado correctamente'
            })
            
        except Exception as e:
            logger.error(f"error asignando ticket: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def get_economy_stats(self, request):
        """obtener estadísticas de economía del guild"""
        try:
            guild_id = int(request.match_info['guild_id'])
            
            # cargar economía
            economy = await self.load_json('economy.json')
            guild_economy = economy.get(str(guild_id), {})
            
            stats = {
                'total_users': len(guild_economy),
                'total_coins': sum(user.get('coins', 0) for user in guild_economy.values()),
                'top_users': sorted(
                    [{'user_id': uid, 'coins': data.get('coins', 0)} 
                     for uid, data in guild_economy.items()],
                    key=lambda x: x['coins'], reverse=True
                )[:10]
            }
            
            return web.json_response(stats)
            
        except Exception as e:
            logger.error(f"error obteniendo stats economía: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def get_warnings(self, request):
        """obtener warnings del guild"""
        try:
            guild_id = int(request.match_info['guild_id'])
            
            # cargar warnings
            warnings = await self.load_json('warnings.json')
            guild_warnings = warnings.get(str(guild_id), {})
            
            warning_list = []
            for user_id, user_warnings in guild_warnings.items():
                for warning in user_warnings:
                    warning_list.append({
                        'user_id': user_id,
                        'reason': warning.get('reason'),
                        'moderator': warning.get('moderator'),
                        'timestamp': warning.get('timestamp')
                    })
            
            # ordenar por timestamp
            warning_list.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return web.json_response(warning_list)
            
        except Exception as e:
            logger.error(f"error obteniendo warnings: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def moderation_action(self, request):
        """ejecutar acción de moderación"""
        try:
            guild_id = int(request.match_info['guild_id'])
            data = await request.json()
            
            action = data.get('action')
            target_id = data.get('target_id')
            reason = data.get('reason', 'Sin razón especificada')
            
            if not action or not target_id:
                return web.json_response({'error': 'action y target_id requeridos'}, status=400)
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return web.json_response({'error': 'guild no encontrado'}, status=404)
            
            target = guild.get_member(int(target_id))
            if not target:
                return web.json_response({'error': 'usuario no encontrado'}, status=404)
            
            # ejecutar acción según el tipo
            if action == 'kick':
                await target.kick(reason=reason)
            elif action == 'ban':
                await target.ban(reason=reason)
            elif action == 'timeout':
                duration = data.get('duration', 3600)  # 1 hora por defecto
                await target.edit(timeout=nextcord.utils.utcnow() + timedelta(seconds=duration))
            else:
                return web.json_response({'error': 'acción no válida'}, status=400)
            
            return web.json_response({
                'success': True,
                'message': f'acción {action} ejecutada correctamente'
            })
            
        except Exception as e:
            logger.error(f"error ejecutando acción de moderación: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @tasks.loop(seconds=1, count=1)
    async def start_server(self):
        """iniciar servidor web"""
        try:
            host = self.config.get('host', '0.0.0.0')
            port = self.config.get('port', 8080)
            
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, host, port)
            await self.site.start()
            
            logger.info(f"servidor web iniciado en {host}:{port}")
            
        except Exception as e:
            logger.error(f"error iniciando servidor web: {e}")
    
    def cog_unload(self):
        """cleanup al descargar cog"""
        if self.start_server.is_running():
            self.start_server.cancel()
        
        if self.site:
            asyncio.create_task(self.site.stop())
        
        if self.runner:
            asyncio.create_task(self.runner.cleanup())

def setup(bot):
    """función para cargar el cog"""
    bot.add_cog(WebAPI(bot))
