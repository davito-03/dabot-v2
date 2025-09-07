"""
Sistema de niveles avanzado y completamente configurable
Similar a AmariBot con configuración completa
Por davito
"""

import nextcord
from nextcord.ext import commands, tasks
import json
import asyncio
import random
from datetime import datetime, timedelta
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import logging
import calendar

logger = logging.getLogger(__name__)

class AdvancedLevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data = {}
        self.guild_configs = {}
        self.monthly_data = {}
        self.load_data()
        self.save_data_task.start()
        self.reset_monthly_task.start()
    
    def load_data(self):
        """Cargar todos los datos"""
        try:
            with open('data/advanced_levels.json', 'r', encoding='utf-8') as f:
                self.user_data = json.load(f)
        except FileNotFoundError:
            self.user_data = {}
        
        try:
            with open('data/advanced_level_configs.json', 'r', encoding='utf-8') as f:
                self.guild_configs = json.load(f)
        except FileNotFoundError:
            self.guild_configs = {}
        
        try:
            with open('data/monthly_levels.json', 'r', encoding='utf-8') as f:
                self.monthly_data = json.load(f)
        except FileNotFoundError:
            self.monthly_data = {}
    
    @tasks.loop(minutes=5)
    async def save_data_task(self):
        """Guardar datos periódicamente"""
        self.save_data()
    
    @tasks.loop(hours=1)
    async def reset_monthly_task(self):
        """Verificar si es necesario resetear datos mensuales"""
        now = datetime.now()
        if now.day == 1 and now.hour == 0:
            # Primer día del mes, resetear datos mensuales
            self.monthly_data = {}
            self.save_data()
    
    def save_data(self):
        """Guardar todos los datos"""
        try:
            with open('data/advanced_levels.json', 'w', encoding='utf-8') as f:
                json.dump(self.user_data, f, indent=2)
            with open('data/advanced_level_configs.json', 'w', encoding='utf-8') as f:
                json.dump(self.guild_configs, f, indent=2)
            with open('data/monthly_levels.json', 'w', encoding='utf-8') as f:
                json.dump(self.monthly_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error guardando datos de niveles: {e}")
    
    def get_default_config(self):
        """Configuración por defecto"""
        return {
            'enabled': True,
            'xp_per_message': [15, 25],  # [mínimo, máximo]
            'xp_cooldown': 60,  # segundos entre mensajes que dan XP
            'level_up_message': True,
            'level_up_channel': None,
            'no_xp_channels': [],
            'no_xp_roles': [],
            'multiplier_roles': {},  # {role_id: multiplier}
            'level_roles': {},  # {level: role_id}
            'stack_roles': False,  # Si mantener roles de niveles anteriores
            'remove_previous_roles': True,  # Si quitar roles de niveles anteriores
            'announce_channel': None,  # Canal específico para anuncios de nivel
            'custom_level_messages': {},  # {level: "mensaje personalizado"}
            'reset_on_leave': False,  # Si resetear XP al salir del servidor
            'voice_xp': {
                'enabled': False,
                'xp_per_minute': 5,
                'min_members': 2  # Mínimo de miembros en el canal para dar XP
            }
        }
    
    def get_guild_config(self, guild_id):
        """Obtener configuración del servidor"""
        guild_key = str(guild_id)
        if guild_key not in self.guild_configs:
            self.guild_configs[guild_key] = self.get_default_config()
        return self.guild_configs[guild_key]
    
    def get_user_data(self, guild_id, user_id):
        """Obtener datos del usuario"""
        guild_key = str(guild_id)
        user_key = str(user_id)
        
        if guild_key not in self.user_data:
            self.user_data[guild_key] = {}
        
        if user_key not in self.user_data[guild_key]:
            self.user_data[guild_key][user_key] = {
                'xp': 0,
                'level': 1,
                'messages': 0,
                'last_message': 0,
                'voice_time': 0,
                'joined_voice': None
            }
        
        return self.user_data[guild_key][user_key]
    
    def get_monthly_data(self, guild_id, user_id):
        """Obtener datos mensuales del usuario"""
        guild_key = str(guild_id)
        user_key = str(user_id)
        current_month = datetime.now().strftime("%Y-%m")
        
        if guild_key not in self.monthly_data:
            self.monthly_data[guild_key] = {}
        
        if current_month not in self.monthly_data[guild_key]:
            self.monthly_data[guild_key][current_month] = {}
        
        if user_key not in self.monthly_data[guild_key][current_month]:
            self.monthly_data[guild_key][current_month][user_key] = {
                'xp': 0,
                'level': 1,
                'messages': 0
            }
        
        return self.monthly_data[guild_key][current_month][user_key]
    
    def xp_to_level(self, xp):
        """Calcular nivel basado en XP (fórmula similar a MEE6)"""
        level = 0
        xp_needed = 0
        while xp_needed <= xp:
            level += 1
            xp_needed += 5 * (level ** 2) + 50 * level + 100
        return level
    
    def level_to_xp(self, level):
        """Calcular XP total necesaria para un nivel"""
        if level <= 1:
            return 0
        total_xp = 0
        for l in range(1, level):
            total_xp += 5 * (l ** 2) + 50 * l + 100
        return total_xp
    
    def xp_for_next_level(self, current_level):
        """XP necesaria para el siguiente nivel"""
        return 5 * (current_level ** 2) + 50 * current_level + 100
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Dar XP por mensajes"""
        if not message.guild or message.author.bot:
            return
        
        config = self.get_guild_config(message.guild.id)
        
        if not config['enabled']:
            return
        
        # Verificar canal bloqueado
        if message.channel.id in config['no_xp_channels']:
            return
        
        # Verificar rol bloqueado
        user_role_ids = [role.id for role in message.author.roles]
        if any(role_id in config['no_xp_roles'] for role_id in user_role_ids):
            return
        
        user_data = self.get_user_data(message.guild.id, message.author.id)
        monthly_data = self.get_monthly_data(message.guild.id, message.author.id)
        
        # Verificar cooldown
        current_time = datetime.now().timestamp()
        if current_time - user_data['last_message'] < config['xp_cooldown']:
            return
        
        # Calcular XP ganada
        base_xp = random.randint(*config['xp_per_message'])
        
        # Aplicar multiplicador por roles
        multiplier = 1.0
        for role in message.author.roles:
            if str(role.id) in config['multiplier_roles']:
                role_multiplier = config['multiplier_roles'][str(role.id)]
                multiplier = max(multiplier, role_multiplier)
        
        xp_gained = int(base_xp * multiplier)
        
        # Actualizar datos
        old_level = user_data['level']
        user_data['xp'] += xp_gained
        user_data['messages'] += 1
        user_data['last_message'] = current_time
        user_data['level'] = self.xp_to_level(user_data['xp'])
        
        # Actualizar datos mensuales
        monthly_data['xp'] += xp_gained
        monthly_data['messages'] += 1
        monthly_data['level'] = self.xp_to_level(monthly_data['xp'])
        
        # Verificar level up
        if user_data['level'] > old_level:
            await self.handle_level_up(message, user_data['level'], config)
    
    async def handle_level_up(self, message, new_level, config):
        """Manejar subida de nivel"""
        if config['level_up_message']:
            # Mensaje personalizado o por defecto
            if str(new_level) in config['custom_level_messages']:
                description = config['custom_level_messages'][str(new_level)]
            else:
                description = f"🎉 {message.author.mention} alcanzó el **nivel {new_level}**!"
            
            embed = nextcord.Embed(
                title="¡Subiste de nivel!",
                description=description,
                color=0xf1c40f,
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            embed.add_field(name="Nuevo Nivel", value=f"**{new_level}**", inline=True)
            
            # Determinar canal de anuncio
            channel = message.channel
            if config['announce_channel']:
                announce_channel = self.bot.get_channel(config['announce_channel'])
                if announce_channel:
                    channel = announce_channel
            elif config['level_up_channel']:
                level_channel = self.bot.get_channel(config['level_up_channel'])
                if level_channel:
                    channel = level_channel
            
            try:
                await channel.send(embed=embed)
            except:
                pass
        
        # Gestionar roles de nivel
        await self.manage_level_roles(message.author, new_level, config)
    
    async def manage_level_roles(self, member, new_level, config):
        """Gestionar roles por nivel"""
        try:
            # Encontrar todos los roles que debe tener
            roles_to_add = []
            roles_to_remove = []
            
            for level_str, role_id in config['level_roles'].items():
                required_level = int(level_str)
                role = member.guild.get_role(role_id)
                
                if not role:
                    continue
                
                has_role = role in member.roles
                should_have = new_level >= required_level
                
                if should_have and not has_role:
                    roles_to_add.append(role)
                elif not should_have and has_role and config['remove_previous_roles']:
                    roles_to_remove.append(role)
                elif not config['stack_roles'] and has_role and new_level > required_level:
                    # Si no apilamos roles, quitar roles de niveles anteriores
                    roles_to_remove.append(role)
            
            # Aplicar cambios de roles
            if roles_to_add:
                await member.add_roles(*roles_to_add, reason=f"Nivel {new_level} alcanzado")
            
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason=f"Gestión de roles de nivel")
        
        except Exception as e:
            logger.error(f"Error gestionando roles de nivel: {e}")
    
    # ============ COMANDOS DE CONFIGURACIÓN ============
    
    @nextcord.slash_command(name="level-config", description="Configurar sistema de niveles")
    async def level_config(self, interaction: nextcord.Interaction):
        """Comando base de configuración"""
        pass
    
    @level_config.subcommand(name="enable", description="Activar/desactivar sistema de niveles")
    async def config_enable(self, interaction: nextcord.Interaction, 
                           activar: bool = nextcord.SlashOption(description="Activar o desactivar")):
        """Activar/desactivar sistema"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Necesitas permisos de **Gestionar Servidor**.", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        config['enabled'] = activar
        self.save_data()
        
        status = "✅ **activado**" if activar else "❌ **desactivado**"
        await interaction.response.send_message(f"Sistema de niveles {status}.", ephemeral=True)
    
    @level_config.subcommand(name="xp-range", description="Configurar rango de XP por mensaje")
    async def config_xp_range(self, interaction: nextcord.Interaction,
                             minimo: int = nextcord.SlashOption(description="XP mínima por mensaje", min_value=1, max_value=100),
                             maximo: int = nextcord.SlashOption(description="XP máxima por mensaje", min_value=1, max_value=100)):
        """Configurar XP por mensaje"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Necesitas permisos de **Gestionar Servidor**.", ephemeral=True)
            return
        
        if minimo > maximo:
            await interaction.response.send_message("❌ El mínimo no puede ser mayor que el máximo.", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        config['xp_per_message'] = [minimo, maximo]
        self.save_data()
        
        await interaction.response.send_message(f"✅ XP por mensaje configurada: **{minimo}-{maximo} XP**", ephemeral=True)
    
    @level_config.subcommand(name="cooldown", description="Configurar cooldown entre mensajes")
    async def config_cooldown(self, interaction: nextcord.Interaction,
                             segundos: int = nextcord.SlashOption(description="Segundos entre mensajes que dan XP", min_value=0, max_value=300)):
        """Configurar cooldown"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Necesitas permisos de **Gestionar Servidor**.", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        config['xp_cooldown'] = segundos
        self.save_data()
        
        await interaction.response.send_message(f"✅ Cooldown configurado: **{segundos} segundos**", ephemeral=True)
    
    @level_config.subcommand(name="no-xp-channel", description="Añadir/quitar canal sin XP")
    async def config_no_xp_channel(self, interaction: nextcord.Interaction,
                                   canal: nextcord.TextChannel = nextcord.SlashOption(description="Canal a configurar"),
                                   accion: str = nextcord.SlashOption(description="Añadir o quitar", choices=["añadir", "quitar"])):
        """Configurar canales sin XP"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Necesitas permisos de **Gestionar Servidor**.", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        
        if accion == "añadir":
            if canal.id not in config['no_xp_channels']:
                config['no_xp_channels'].append(canal.id)
                await interaction.response.send_message(f"✅ {canal.mention} añadido a canales sin XP.", ephemeral=True)
            else:
                await interaction.response.send_message(f"⚠️ {canal.mention} ya está en la lista.", ephemeral=True)
        else:
            if canal.id in config['no_xp_channels']:
                config['no_xp_channels'].remove(canal.id)
                await interaction.response.send_message(f"✅ {canal.mention} quitado de canales sin XP.", ephemeral=True)
            else:
                await interaction.response.send_message(f"⚠️ {canal.mention} no está en la lista.", ephemeral=True)
        
        self.save_data()
    
    @level_config.subcommand(name="level-role", description="Configurar rol por nivel")
    async def config_level_role(self, interaction: nextcord.Interaction,
                               nivel: int = nextcord.SlashOption(description="Nivel requerido", min_value=1, max_value=1000),
                               rol: nextcord.Role = nextcord.SlashOption(description="Rol a asignar"),
                               accion: str = nextcord.SlashOption(description="Añadir o quitar", choices=["añadir", "quitar"])):
        """Configurar roles por nivel"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Necesitas permisos de **Gestionar Servidor**.", ephemeral=True)
            return
        
        config = self.get_guild_config(interaction.guild.id)
        
        if accion == "añadir":
            config['level_roles'][str(nivel)] = rol.id
            await interaction.response.send_message(f"✅ Rol {rol.mention} configurado para nivel **{nivel}**.", ephemeral=True)
        else:
            if str(nivel) in config['level_roles']:
                del config['level_roles'][str(nivel)]
                await interaction.response.send_message(f"✅ Rol para nivel **{nivel}** eliminado.", ephemeral=True)
            else:
                await interaction.response.send_message(f"⚠️ No hay rol configurado para nivel **{nivel}**.", ephemeral=True)
        
        self.save_data()
    
    # ============ COMANDOS DE GESTIÓN ============
    
    @nextcord.slash_command(name="level-manage", description="Gestionar niveles de usuarios")
    async def level_manage(self, interaction: nextcord.Interaction):
        """Comando base de gestión"""
        pass
    
    @level_manage.subcommand(name="add-xp", description="Añadir XP a un usuario")
    async def add_xp(self, interaction: nextcord.Interaction,
                     usuario: nextcord.Member = nextcord.SlashOption(description="Usuario a modificar"),
                     cantidad: int = nextcord.SlashOption(description="Cantidad de XP a añadir", min_value=1)):
        """Añadir XP"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Necesitas permisos de **Gestionar Servidor**.", ephemeral=True)
            return
        
        user_data = self.get_user_data(interaction.guild.id, usuario.id)
        old_level = user_data['level']
        user_data['xp'] += cantidad
        user_data['level'] = self.xp_to_level(user_data['xp'])
        
        self.save_data()
        
        embed = nextcord.Embed(
            title="✅ XP Añadida",
            description=f"Añadidas **{cantidad:,} XP** a {usuario.mention}",
            color=0x00ff00
        )
        embed.add_field(name="Nivel anterior", value=old_level, inline=True)
        embed.add_field(name="Nivel actual", value=user_data['level'], inline=True)
        embed.add_field(name="XP total", value=f"{user_data['xp']:,}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @level_manage.subcommand(name="remove-xp", description="Quitar XP a un usuario")
    async def remove_xp(self, interaction: nextcord.Interaction,
                        usuario: nextcord.Member = nextcord.SlashOption(description="Usuario a modificar"),
                        cantidad: int = nextcord.SlashOption(description="Cantidad de XP a quitar", min_value=1)):
        """Quitar XP"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Necesitas permisos de **Gestionar Servidor**.", ephemeral=True)
            return
        
        user_data = self.get_user_data(interaction.guild.id, usuario.id)
        old_level = user_data['level']
        user_data['xp'] = max(0, user_data['xp'] - cantidad)
        user_data['level'] = self.xp_to_level(user_data['xp'])
        
        self.save_data()
        
        embed = nextcord.Embed(
            title="✅ XP Quitada",
            description=f"Quitadas **{cantidad:,} XP** a {usuario.mention}",
            color=0xff9900
        )
        embed.add_field(name="Nivel anterior", value=old_level, inline=True)
        embed.add_field(name="Nivel actual", value=user_data['level'], inline=True)
        embed.add_field(name="XP total", value=f"{user_data['xp']:,}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @level_manage.subcommand(name="set-level", description="Establecer nivel específico")
    async def set_level(self, interaction: nextcord.Interaction,
                       usuario: nextcord.Member = nextcord.SlashOption(description="Usuario a modificar"),
                       nivel: int = nextcord.SlashOption(description="Nivel a establecer", min_value=1, max_value=1000)):
        """Establecer nivel específico"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Necesitas permisos de **Gestionar Servidor**.", ephemeral=True)
            return
        
        user_data = self.get_user_data(interaction.guild.id, usuario.id)
        old_level = user_data['level']
        required_xp = self.level_to_xp(nivel)
        
        user_data['level'] = nivel
        user_data['xp'] = required_xp
        
        self.save_data()
        
        embed = nextcord.Embed(
            title="✅ Nivel Establecido",
            description=f"Nivel de {usuario.mention} establecido a **{nivel}**",
            color=0x0099ff
        )
        embed.add_field(name="Nivel anterior", value=old_level, inline=True)
        embed.add_field(name="Nivel actual", value=nivel, inline=True)
        embed.add_field(name="XP total", value=f"{required_xp:,}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ============ COMANDOS DE CONSULTA ============
    
    @nextcord.slash_command(name="rank", description="Ver tu rango y nivel")
    async def rank_command(self, interaction: nextcord.Interaction,
                          usuario: nextcord.Member = None):
        """Ver nivel de usuario"""
        target = usuario or interaction.user
        user_data = self.get_user_data(interaction.guild.id, target.id)
        
        # Calcular progreso al siguiente nivel
        current_level = user_data['level']
        current_xp = user_data['xp']
        xp_for_current = self.level_to_xp(current_level)
        xp_for_next = self.level_to_xp(current_level + 1)
        xp_progress = current_xp - xp_for_current
        xp_needed = xp_for_next - xp_for_current
        
        # Calcular posición en el ranking
        guild_users = self.user_data.get(str(interaction.guild.id), {})
        sorted_users = sorted(guild_users.items(), key=lambda x: x[1]['xp'], reverse=True)
        rank_position = next((i + 1 for i, (uid, _) in enumerate(sorted_users) if uid == str(target.id)), 0)
        
        embed = nextcord.Embed(
            title=f"📊 Rango de {target.display_name}",
            color=0x3498db,
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=target.display_avatar.url)
        
        embed.add_field(name="🏆 Ranking", value=f"#{rank_position}", inline=True)
        embed.add_field(name="📈 Nivel", value=f"**{current_level}**", inline=True)
        embed.add_field(name="✨ XP Total", value=f"{current_xp:,}", inline=True)
        
        embed.add_field(name="💬 Mensajes", value=f"{user_data['messages']:,}", inline=True)
        embed.add_field(name="📊 Progreso", value=f"{xp_progress:,}/{xp_needed:,}", inline=True)
        embed.add_field(name="🎯 Siguiente Nivel", value=f"Nivel {current_level + 1}", inline=True)
        
        # Barra de progreso
        progress_percentage = (xp_progress / xp_needed) * 100 if xp_needed > 0 else 100
        progress_bar = self.create_progress_bar(xp_progress, xp_needed)
        embed.add_field(name="📈 Progreso al siguiente nivel", value=f"{progress_bar} {progress_percentage:.1f}%", inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="leaderboard", description="Ver tabla de líderes")
    async def leaderboard_command(self, interaction: nextcord.Interaction,
                                 tipo: str = nextcord.SlashOption(description="Tipo de ranking", 
                                                                 choices=["global", "mensual"], default="global")):
        """Ver leaderboard"""
        if tipo == "global":
            data = self.user_data.get(str(interaction.guild.id), {})
            title = "🏆 Ranking Global"
        else:
            current_month = datetime.now().strftime("%Y-%m")
            monthly_guild_data = self.monthly_data.get(str(interaction.guild.id), {})
            data = monthly_guild_data.get(current_month, {})
            title = f"📅 Ranking Mensual - {calendar.month_name[datetime.now().month]} {datetime.now().year}"
        
        if not data:
            await interaction.response.send_message("❌ No hay datos de ranking disponibles.", ephemeral=True)
            return
        
        # Ordenar usuarios por XP
        sorted_users = sorted(data.items(), key=lambda x: x[1]['xp'], reverse=True)[:10]
        
        embed = nextcord.Embed(
            title=title,
            color=0xf1c40f,
            timestamp=datetime.now()
        )
        
        description = ""
        for i, (user_id, user_data) in enumerate(sorted_users, 1):
            user = interaction.guild.get_member(int(user_id))
            if user:
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"**{i}.**"
                description += f"{medal} {user.display_name} - Nivel **{user_data['level']}** ({user_data['xp']:,} XP)\n"
        
        if description:
            embed.description = description
        else:
            embed.description = "No hay usuarios en el ranking."
        
        embed.set_footer(text=f"Servidor: {interaction.guild.name}")
        
        await interaction.response.send_message(embed=embed)
    
    def create_progress_bar(self, current, total, length=20):
        """Crear barra de progreso visual"""
        if total == 0:
            return "█" * length
        
        filled = int((current / total) * length)
        empty = length - filled
        
        return "█" * filled + "░" * empty

def setup(bot):
    return AdvancedLevelSystem(bot)
