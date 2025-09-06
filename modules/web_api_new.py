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
        
        token = auth_header.split(' ')[1]
        user_data = self.verify_jwt_token(token)
        
        if not user_data:
            return web.json_response({'error': 'token inválido'}, status=401)
        
        request.user = user_data
        return await func(self, request)
    
    return wrapper

class WebAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.jwt_secret = os.getenv('JWT_SECRET', 'mi_secreto_super_seguro_123')
        
        # configuración
        self.config = {
            'port': int(os.getenv('WEB_PORT', '8080')),
            'host': os.getenv('WEB_HOST', 'localhost'),
            'allowed_origins': ['http://localhost:8080', 'http://127.0.0.1:8080']
        }
        
        self.setup_routes()
    
    async def load_json(self, filename: str) -> dict:
        """cargar archivo json"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"error cargando {filename}: {e}")
            return {}
    
    async def save_json(self, filename: str, data: dict):
        """guardar archivo json"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando {filename}: {e}")
    
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
        
        # rutas básicas
        self.app.router.add_get('/api/status', self.api_status)
        self.app.router.add_post('/api/auth/discord', self.auth_discord)
        self.app.router.add_get('/api/guilds', self.get_guilds)
        self.app.router.add_get('/api/guilds/{guild_id}', self.get_guild_info)
        self.app.router.add_get('/api/guilds/{guild_id}/members', self.get_guild_members)
        self.app.router.add_get('/api/guilds/{guild_id}/channels', self.get_guild_channels)
        
        # tickets endpoints
        self.app.router.add_get('/api/tickets', self.get_tickets)
        self.app.router.add_get('/api/tickets/{ticket_id}', self.get_ticket)
        self.app.router.add_post('/api/tickets/{ticket_id}/close', self.close_ticket_api)
        self.app.router.add_post('/api/tickets/{ticket_id}/assign', self.assign_ticket_api)
        self.app.router.add_get('/api/guilds/{guild_id}/tickets', self.get_guild_tickets)
        self.app.router.add_get('/api/guilds/{guild_id}/tickets/stats', self.get_tickets_stats)
        self.app.router.add_post('/api/guilds/{guild_id}/tickets/config', self.update_ticket_config)
        
        # warnings endpoints
        self.app.router.add_get('/api/warnings/{guild_id}', self.get_warnings)
        self.app.router.add_get('/api/guilds/{guild_id}/warnings', self.get_guild_warnings)
        self.app.router.add_get('/api/guilds/{guild_id}/warnings/stats', self.get_warnings_stats)
        self.app.router.add_post('/api/warnings/{guild_id}/{user_id}/add', self.add_warning_api)
        self.app.router.add_delete('/api/warnings/{guild_id}/{user_id}/{warning_id}', self.remove_warning_api)
        
        # otros endpoints
        self.app.router.add_get('/api/economy/{guild_id}', self.get_economy_stats)
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
        """obtener todos los tickets"""
        try:
            # obtener cog de tickets
            ticket_cog = self.bot.get_cog('AdvancedTickets')
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
            for ticket_id, ticket in ticket_cog.active_tickets.items():
                if ticket['guild_id'] in user_guild_ids:
                    # obtener información adicional
                    guild = self.bot.get_guild(ticket['guild_id'])
                    user = self.bot.get_user(ticket['user_id'])
                    
                    tickets_data.append({
                        'id': ticket_id,
                        'category': ticket['category'],
                        'priority': ticket['priority'],
                        'status': ticket['status'],
                        'created_at': ticket['created_at'],
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
            
            ticket_cog = self.bot.get_cog('AdvancedTickets')
            if not ticket_cog:
                return web.json_response({'error': 'sistema de tickets no disponible'}, status=503)
            
            ticket = ticket_cog.active_tickets.get(ticket_id)
            if not ticket:
                return web.json_response({'error': 'ticket no encontrado'}, status=404)
            
            # verificar permisos
            user_id = int(request.user['user_id'])
            guild = self.bot.get_guild(ticket['guild_id'])
            member = guild.get_member(user_id) if guild else None
            
            if not member or not (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            return web.json_response(ticket)
            
        except Exception as e:
            logger.error(f"error obteniendo ticket: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def close_ticket_api(self, request):
        """cerrar ticket via api"""
        try:
            ticket_id = request.match_info['ticket_id']
            user_id = int(request.user['user_id'])
            
            ticket_cog = self.bot.get_cog('AdvancedTickets')
            if not ticket_cog:
                return web.json_response({'error': 'sistema de tickets no disponible'}, status=503)
            
            ticket = ticket_cog.active_tickets.get(ticket_id)
            if not ticket:
                return web.json_response({'error': 'ticket no encontrado'}, status=404)
            
            # verificar permisos
            guild = self.bot.get_guild(ticket['guild_id'])
            member = guild.get_member(user_id) if guild else None
            
            if not member or not (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            # cerrar ticket
            ticket['status'] = 'closed'
            ticket['closed_at'] = datetime.datetime.now().isoformat()
            ticket['closed_by'] = user_id
            
            await ticket_cog.save_tickets()
            
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
            
            ticket_cog = self.bot.get_cog('AdvancedTickets')
            if not ticket_cog:
                return web.json_response({'error': 'sistema de tickets no disponible'}, status=503)
            
            ticket = ticket_cog.active_tickets.get(ticket_id)
            if not ticket:
                return web.json_response({'error': 'ticket no encontrado'}, status=404)
            
            # asignar staff
            ticket['assigned_to'] = int(staff_id)
            ticket['assigned_at'] = datetime.datetime.now().isoformat()
            
            await ticket_cog.save_tickets()
            
            return web.json_response({
                'success': True,
                'message': 'ticket asignado correctamente'
            })
            
        except Exception as e:
            logger.error(f"error asignando ticket: {e}")
            return web.json_response({'error': 'error interno'}, status=500)
    
    @require_auth
    async def get_guild_tickets(self, request):
        """obtener tickets específicos de un guild"""
        try:
            guild_id = int(request.match_info['guild_id'])
            user_id = int(request.user['user_id'])
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return web.json_response({'error': 'servidor no encontrado'}, status=404)
            
            member = guild.get_member(user_id)
            if not member or not (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            # obtener cog de tickets avanzados
            ticket_cog = self.bot.get_cog('AdvancedTickets')
            if not ticket_cog:
                return web.json_response({'error': 'sistema de tickets no disponible'}, status=503)
            
            # filtrar tickets del guild
            guild_tickets = []
            for ticket_id, ticket in ticket_cog.active_tickets.items():
                if ticket['guild_id'] == guild_id:
                    user = self.bot.get_user(ticket['user_id'])
                    assigned_user = self.bot.get_user(ticket.get('assigned_to')) if ticket.get('assigned_to') else None
                    
                    guild_tickets.append({
                        'id': ticket_id,
                        'category': ticket['category'],
                        'priority': ticket['priority'],
                        'status': ticket['status'],
                        'created_at': ticket['created_at'],
                        'user': {
                            'id': str(ticket['user_id']),
                            'name': user.name if user else 'Usuario desconocido',
                            'avatar': user.avatar.url if user and user.avatar else None
                        },
                        'assigned_to': {
                            'id': str(ticket['assigned_to']),
                            'name': assigned_user.name if assigned_user else 'Sin asignar',
                            'avatar': assigned_user.avatar.url if assigned_user and assigned_user.avatar else None
                        } if ticket.get('assigned_to') else None,
                        'transcript_url': ticket.get('transcript_url')
                    })
            
            return web.json_response({'tickets': guild_tickets})
            
        except Exception as e:
            logger.error(f"error obteniendo tickets del guild: {e}")
            return web.json_response({'error': 'error interno'}, status=500)

    @require_auth
    async def get_tickets_stats(self, request):
        """obtener estadísticas de tickets del guild"""
        try:
            guild_id = int(request.match_info['guild_id'])
            
            ticket_cog = self.bot.get_cog('AdvancedTickets')
            if not ticket_cog:
                return web.json_response({'error': 'sistema de tickets no disponible'}, status=503)
            
            # contar tickets por categoría y estado
            stats = {
                'total_tickets': 0,
                'open_tickets': 0,
                'closed_tickets': 0,
                'by_category': {
                    'soporte': 0,
                    'reporte': 0,
                    'sugerencia': 0,
                    'apelacion': 0,
                    'otro': 0
                },
                'by_priority': {
                    'baja': 0,
                    'media': 0,
                    'alta': 0
                }
            }
            
            for ticket in ticket_cog.active_tickets.values():
                if ticket['guild_id'] == guild_id:
                    stats['total_tickets'] += 1
                    
                    if ticket['status'] == 'open':
                        stats['open_tickets'] += 1
                    else:
                        stats['closed_tickets'] += 1
                    
                    stats['by_category'][ticket['category']] += 1
                    stats['by_priority'][ticket['priority']] += 1
            
            return web.json_response(stats)
            
        except Exception as e:
            logger.error(f"error obteniendo stats tickets: {e}")
            return web.json_response({'error': 'error interno'}, status=500)

    @require_auth
    async def update_ticket_config(self, request):
        """actualizar configuración de tickets del guild"""
        try:
            guild_id = int(request.match_info['guild_id'])
            user_id = int(request.user['user_id'])
            data = await request.json()
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return web.json_response({'error': 'servidor no encontrado'}, status=404)
            
            member = guild.get_member(user_id)
            if not member or not member.guild_permissions.administrator:
                return web.json_response({'error': 'sin permisos de administrador'}, status=403)
            
            ticket_cog = self.bot.get_cog('AdvancedTickets')
            if not ticket_cog:
                return web.json_response({'error': 'sistema de tickets no disponible'}, status=503)
            
            # actualizar configuración
            config = ticket_cog.config.get(str(guild_id), {})
            
            if 'panel_channel_id' in data:
                config['panel_channel_id'] = data['panel_channel_id']
            if 'category_id' in data:
                config['category_id'] = data['category_id']
            if 'staff_role_id' in data:
                config['staff_role_id'] = data['staff_role_id']
            if 'log_channel_id' in data:
                config['log_channel_id'] = data['log_channel_id']
            
            ticket_cog.config[str(guild_id)] = config
            await ticket_cog.save_config()
            
            return web.json_response({
                'success': True,
                'message': 'configuración actualizada correctamente'
            })
            
        except Exception as e:
            logger.error(f"error actualizando config tickets: {e}")
            return web.json_response({'error': 'error interno'}, status=500)

    @require_auth
    async def get_warnings(self, request):
        """obtener warnings del guild (método original)"""
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
    async def get_guild_warnings(self, request):
        """obtener warnings específicos de un guild con detalles de usuario"""
        try:
            guild_id = int(request.match_info['guild_id'])
            user_id = int(request.user['user_id'])
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return web.json_response({'error': 'servidor no encontrado'}, status=404)
            
            member = guild.get_member(user_id)
            if not member or not (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            # cargar warnings
            warnings = await self.load_json('warnings.json')
            guild_warnings = warnings.get(str(guild_id), {})
            
            warning_list = []
            for warned_user_id, user_warnings in guild_warnings.items():
                warned_user = guild.get_member(int(warned_user_id))
                
                for i, warning in enumerate(user_warnings):
                    moderator = guild.get_member(int(warning.get('moderator', 0)))
                    
                    warning_list.append({
                        'id': f"{warned_user_id}_{i}",
                        'user_id': warned_user_id,
                        'user': {
                            'name': warned_user.name if warned_user else 'Usuario desconocido',
                            'display_name': warned_user.display_name if warned_user else 'Usuario desconocido',
                            'avatar': warned_user.avatar.url if warned_user and warned_user.avatar else None
                        },
                        'reason': warning.get('reason'),
                        'moderator': {
                            'id': str(warning.get('moderator', 0)),
                            'name': moderator.name if moderator else 'Moderador desconocido',
                            'avatar': moderator.avatar.url if moderator and moderator.avatar else None
                        },
                        'timestamp': warning.get('timestamp')
                    })
            
            # ordenar por timestamp
            warning_list.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return web.json_response({'warnings': warning_list})
            
        except Exception as e:
            logger.error(f"error obteniendo warnings del guild: {e}")
            return web.json_response({'error': 'error interno'}, status=500)

    @require_auth
    async def get_warnings_stats(self, request):
        """obtener estadísticas de warnings del guild"""
        try:
            guild_id = int(request.match_info['guild_id'])
            
            # cargar warnings
            warnings = await self.load_json('warnings.json')
            guild_warnings = warnings.get(str(guild_id), {})
            
            total_warnings = sum(len(user_warnings) for user_warnings in guild_warnings.values())
            users_with_warnings = len(guild_warnings)
            
            # warnings por usuario (top 10)
            users_by_warnings = [
                {'user_id': user_id, 'count': len(user_warnings)}
                for user_id, user_warnings in guild_warnings.items()
            ]
            users_by_warnings.sort(key=lambda x: x['count'], reverse=True)
            
            stats = {
                'total_warnings': total_warnings,
                'users_with_warnings': users_with_warnings,
                'top_users': users_by_warnings[:10]
            }
            
            return web.json_response(stats)
            
        except Exception as e:
            logger.error(f"error obteniendo stats warnings: {e}")
            return web.json_response({'error': 'error interno'}, status=500)

    @require_auth
    async def add_warning_api(self, request):
        """agregar warning via api"""
        try:
            guild_id = int(request.match_info['guild_id'])
            target_user_id = int(request.match_info['user_id'])
            user_id = int(request.user['user_id'])
            data = await request.json()
            
            reason = data.get('reason', 'Sin razón especificada')
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return web.json_response({'error': 'servidor no encontrado'}, status=404)
            
            member = guild.get_member(user_id)
            if not member or not (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            # cargar warnings
            warnings = await self.load_json('warnings.json')
            guild_warnings = warnings.setdefault(str(guild_id), {})
            user_warnings = guild_warnings.setdefault(str(target_user_id), [])
            
            # agregar warning
            warning = {
                'reason': reason,
                'moderator': user_id,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            user_warnings.append(warning)
            
            # guardar
            await self.save_json('warnings.json', warnings)
            
            return web.json_response({
                'success': True,
                'message': 'warning agregado correctamente'
            })
            
        except Exception as e:
            logger.error(f"error agregando warning: {e}")
            return web.json_response({'error': 'error interno'}, status=500)

    @require_auth
    async def remove_warning_api(self, request):
        """remover warning via api"""
        try:
            guild_id = int(request.match_info['guild_id'])
            target_user_id = int(request.match_info['user_id'])
            warning_id = int(request.match_info['warning_id'])
            user_id = int(request.user['user_id'])
            
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return web.json_response({'error': 'servidor no encontrado'}, status=404)
            
            member = guild.get_member(user_id)
            if not member or not (member.guild_permissions.administrator or member.guild_permissions.manage_guild):
                return web.json_response({'error': 'sin permisos'}, status=403)
            
            # cargar warnings
            warnings = await self.load_json('warnings.json')
            guild_warnings = warnings.get(str(guild_id), {})
            user_warnings = guild_warnings.get(str(target_user_id), [])
            
            if warning_id >= len(user_warnings):
                return web.json_response({'error': 'warning no encontrado'}, status=404)
            
            # remover warning
            user_warnings.pop(warning_id)
            
            # si no hay más warnings, remover usuario
            if not user_warnings:
                del guild_warnings[str(target_user_id)]
            
            # guardar
            await self.save_json('warnings.json', warnings)
            
            return web.json_response({
                'success': True,
                'message': 'warning removido correctamente'
            })
            
        except Exception as e:
            logger.error(f"error removiendo warning: {e}")
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
            logger.error(f"error en acción moderación: {e}")
            return web.json_response({'error': 'error interno'}, status=500)

    async def start_server(self):
        """iniciar servidor web"""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(
                self.runner,
                self.config['host'],
                self.config['port']
            )
            
            await self.site.start()
            logger.info(f"servidor web iniciado en http://{self.config['host']}:{self.config['port']}")
            
        except Exception as e:
            logger.error(f"error iniciando servidor web: {e}")
    
    async def stop_server(self):
        """detener servidor web"""
        try:
            if self.site:
                await self.site.stop()
            if self.runner:
                await self.runner.cleanup()
            logger.info("servidor web detenido")
        except Exception as e:
            logger.error(f"error deteniendo servidor web: {e}")
    
    @commands.Cog.listener()
    async def on_ready(self):
        """cuando el bot esté listo, iniciar servidor web"""
        if not hasattr(self, '_server_started'):
            await self.start_server()
            self._server_started = True

def setup(bot):
    return bot.add_cog(WebAPI(bot))
