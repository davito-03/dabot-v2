"""
Sistema de Niveles Avanzado para DaBot v2
Incluye XP por mensajes y tiempo en voz, roles de colores, privilegios
"""

import nextcord
from nextcord.ext import commands, tasks
import sqlite3
import asyncio
from datetime import datetime, timedelta
import random
import json

class AdvancedLevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_database()
        self.voice_sessions = {}  # Seguimiento de sesiones de voz
        self.voice_xp_task.start()
        
        # Configuración de XP
        self.MESSAGE_XP_MIN = 15
        self.MESSAGE_XP_MAX = 25
        self.VOICE_XP_PER_MINUTE = 2
        self.XP_MULTIPLIER_BOOST = 1.5
        
        # Colores disponibles para elegir
        self.available_colors = {
            "🔴 Rojo Fuego": 0xff4444,
            "🟠 Naranja Vibrante": 0xff8800,
            "🟡 Amarillo Dorado": 0xffdd00,
            "🟢 Verde Esmeralda": 0x00ff88,
            "🔵 Azul Océano": 0x4488ff,
            "🟣 Púrpura Real": 0x8844ff,
            "🌸 Rosa Sakura": 0xff88dd,
            "🖤 Negro Elegante": 0x2f3136,
            "🤍 Blanco Puro": 0xffffff,
            "🟤 Marrón Tierra": 0x8b4513,
            "💎 Diamante": 0xb9f2ff,
            "🌈 Arcoíris": 0xff69b4,
            "🔥 Llama": 0xff6600,
            "❄️ Hielo": 0x87ceeb,
            "🌟 Estrella": 0xffd700,
            "🌙 Luna": 0xc0c0c0,
            "☀️ Sol": 0xffa500,
            "🌊 Ola": 0x006994,
            "🍃 Hoja": 0x32cd32,
            "🌺 Flor": 0xda70d6
        }
        
    def init_database(self):
        """Inicializar base de datos para niveles"""
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_levels (
                    guild_id INTEGER,
                    user_id INTEGER,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 0,
                    messages_sent INTEGER DEFAULT 0,
                    voice_time INTEGER DEFAULT 0,
                    last_message TIMESTAMP,
                    chosen_color INTEGER,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS level_roles (
                    guild_id INTEGER,
                    level INTEGER,
                    role_id INTEGER,
                    role_name TEXT,
                    role_color INTEGER,
                    privileges TEXT,
                    PRIMARY KEY (guild_id, level)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS level_config (
                    guild_id INTEGER PRIMARY KEY,
                    enabled BOOLEAN DEFAULT 1,
                    level_up_channel INTEGER,
                    color_choice_level INTEGER DEFAULT 10,
                    privilege_levels TEXT
                )
            ''')
            conn.commit()

    async def setup_level_system(self, guild, template_type):
        """Configurar sistema de niveles para una plantilla específica"""
        level_configs = {
            "streamer": {
                "roles": [
                    (5, "🌱 Nuevo Viewer", 0x90EE90, ["basic_chat"]),
                    (10, "👀 Viewer Regular", 0x87CEEB, ["basic_chat", "nickname"]),
                    (20, "💬 Chatero Activo", 0xDDA0DD, ["basic_chat", "nickname", "media"]),
                    (35, "⭐ Fan Leal", 0xFFD700, ["basic_chat", "nickname", "media", "links"]),
                    (50, "🎭 Miembro VIP", 0xFF69B4, ["basic_chat", "nickname", "media", "links", "color_choice"]),
                    (75, "👑 Super Fan", 0xFF4500, ["all_privileges"]),
                    (100, "💎 Leyenda del Canal", 0x9932CC, ["all_privileges", "special_mention"])
                ]
            },
            "gaming": {
                "roles": [
                    (5, "🎮 Noob", 0x808080, ["basic_chat"]),
                    (15, "⚔️ Guerrero", 0x8FBC8F, ["basic_chat", "nickname"]),
                    (30, "🏆 Veterano", 0x4169E1, ["basic_chat", "nickname", "media"]),
                    (50, "🥇 Élite", 0xFFD700, ["basic_chat", "nickname", "media", "links"]),
                    (75, "💀 Leyenda", 0xFF6347, ["basic_chat", "nickname", "media", "links", "color_choice"]),
                    (100, "👑 Gran Maestro", 0x8A2BE2, ["all_privileges"]),
                    (150, "🌟 Inmortal", 0xFF1493, ["all_privileges", "special_mention"])
                ]
            },
            "desarrollo": {
                "roles": [
                    (5, "👶 Principiante", 0xA9A9A9, ["basic_chat"]),
                    (15, "🔰 Junior Dev", 0x90EE90, ["basic_chat", "nickname"]),
                    (30, "💻 Desarrollador", 0x4169E1, ["basic_chat", "nickname", "media"]),
                    (50, "🚀 Senior Dev", 0xFFD700, ["basic_chat", "nickname", "media", "links"]),
                    (75, "🧠 Arquitecto", 0xFF4500, ["basic_chat", "nickname", "media", "links", "color_choice"]),
                    (100, "👑 Tech Lead", 0x8A2BE2, ["all_privileges"]),
                    (150, "🌟 Guru", 0xFF1493, ["all_privileges", "special_mention"])
                ]
            },
            "general": {
                "roles": [
                    (5, "🌱 Recién llegado", 0xA9A9A9, ["basic_chat"]),
                    (15, "😊 Miembro", 0x87CEEB, ["basic_chat", "nickname"]),
                    (30, "💬 Conversador", 0xDDA0DD, ["basic_chat", "nickname", "media"]),
                    (50, "⭐ Miembro Activo", 0xFFD700, ["basic_chat", "nickname", "media", "links"]),
                    (75, "🎨 Creativo", 0xFF69B4, ["basic_chat", "nickname", "media", "links", "color_choice"]),
                    (100, "👑 Miembro VIP", 0xFF4500, ["all_privileges"]),
                    (150, "💎 Leyenda", 0x9932CC, ["all_privileges", "special_mention"])
                ]
            }
        }
        
        config = level_configs.get(template_type, level_configs["general"])
        
        # Crear roles de nivel
        created_roles = []
        for level, name, color, privileges in config["roles"]:
            try:
                # Verificar si el rol ya existe
                existing_role = nextcord.utils.get(guild.roles, name=name)
                if existing_role:
                    role = existing_role
                else:
                    # Crear nuevo rol
                    role = await guild.create_role(
                        name=name,
                        color=nextcord.Color(color),
                        mentionable=True,
                        hoist=True,
                        reason="Sistema de niveles automático"
                    )
                
                # Guardar en base de datos
                with sqlite3.connect('data/bot_data.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO level_roles 
                        (guild_id, level, role_id, role_name, role_color, privileges)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (guild.id, level, role.id, name, color, json.dumps(privileges)))
                    conn.commit()
                
                created_roles.append((level, role))
                
            except Exception as e:
                print(f"Error creando rol de nivel {level}: {e}")
        
        # Configurar sistema de niveles
        level_channel = None
        for channel in guild.text_channels:
            if "nivel" in channel.name.lower() or "level" in channel.name.lower():
                level_channel = channel
                break
        
        if not level_channel:
            # Buscar canal general
            for channel in guild.text_channels:
                if "general" in channel.name.lower():
                    level_channel = channel
                    break
        
        # Guardar configuración
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO level_config 
                (guild_id, enabled, level_up_channel, color_choice_level, privilege_levels)
                VALUES (?, ?, ?, ?, ?)
            ''', (guild.id, True, level_channel.id if level_channel else None, 50, json.dumps(config)))
            conn.commit()
        
        return created_roles

    async def add_message_xp(self, message):
        """Añadir XP por mensaje"""
        if message.author.bot or not message.guild:
            return
            
        # Verificar cooldown (1 minuto entre mensajes que dan XP)
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT last_message FROM user_levels 
                WHERE guild_id = ? AND user_id = ?
            ''', (message.guild.id, message.author.id))
            
            result = cursor.fetchone()
            now = datetime.now()
            
            if result and result[0]:
                last_message = datetime.fromisoformat(result[0])
                if (now - last_message).seconds < 60:
                    return
            
            # Calcular XP ganado
            base_xp = random.randint(self.MESSAGE_XP_MIN, self.MESSAGE_XP_MAX)
            
            # Multiplicador por boost de servidor
            if message.guild.premium_tier >= 1:
                base_xp = int(base_xp * self.XP_MULTIPLIER_BOOST)
            
            # Actualizar datos del usuario
            cursor.execute('''
                INSERT OR IGNORE INTO user_levels 
                (guild_id, user_id, xp, level, messages_sent, voice_time, last_message)
                VALUES (?, ?, 0, 0, 0, 0, ?)
            ''', (message.guild.id, message.author.id, now.isoformat()))
            
            cursor.execute('''
                UPDATE user_levels 
                SET xp = xp + ?, messages_sent = messages_sent + 1, last_message = ?
                WHERE guild_id = ? AND user_id = ?
            ''', (base_xp, now.isoformat(), message.guild.id, message.author.id))
            
            # Obtener datos actualizados
            cursor.execute('''
                SELECT xp, level FROM user_levels 
                WHERE guild_id = ? AND user_id = ?
            ''', (message.guild.id, message.author.id))
            
            xp, current_level = cursor.fetchone()
            
            # Calcular nuevo nivel
            new_level = self.calculate_level(xp)
            
            if new_level > current_level:
                cursor.execute('''
                    UPDATE user_levels SET level = ? 
                    WHERE guild_id = ? AND user_id = ?
                ''', (new_level, message.guild.id, message.author.id))
                
                conn.commit()
                await self.handle_level_up(message.guild, message.author, new_level, current_level)
            else:
                conn.commit()

    def calculate_level(self, xp):
        """Calcular nivel basado en XP"""
        # Fórmula: Level = sqrt(XP / 100)
        return int((xp / 100) ** 0.5)

    def calculate_xp_for_level(self, level):
        """Calcular XP necesario para un nivel"""
        return (level ** 2) * 100

    async def handle_level_up(self, guild, user, new_level, old_level):
        """Manejar subida de nivel"""
        # Buscar canal de level up
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT level_up_channel FROM level_config WHERE guild_id = ?
            ''', (guild.id,))
            
            result = cursor.fetchone()
            channel_id = result[0] if result else None
        
        channel = guild.get_channel(channel_id) if channel_id else None
        if not channel:
            # Buscar canal general
            for ch in guild.text_channels:
                if "general" in ch.name.lower():
                    channel = ch
                    break
        
        if not channel:
            return
        
        # Crear embed de level up
        embed = nextcord.Embed(
            title="🎉 ¡LEVEL UP!",
            description=f"¡Felicidades {user.mention}!\nHas subido al **Nivel {new_level}**!",
            color=0x00ff00
        )
        
        # Verificar si hay nuevo rol
        await self.assign_level_role(guild, user, new_level)
        
        # Verificar privilegios desbloqueados
        privileges = await self.get_new_privileges(guild, new_level)
        if privileges:
            embed.add_field(
                name="🔓 Nuevos Privilegios",
                value="\n".join(f"• {privilege}" for privilege in privileges),
                inline=False
            )
        
        # Calcular XP para siguiente nivel
        next_level_xp = self.calculate_xp_for_level(new_level + 1)
        current_xp = await self.get_user_xp(guild.id, user.id)
        needed_xp = next_level_xp - current_xp
        
        embed.add_field(
            name="📊 Progreso",
            value=f"**XP Actual:** {current_xp:,}\n**Siguiente Nivel:** {needed_xp:,} XP restantes",
            inline=False
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="¡Sigue participando para seguir subiendo!")
        
        await channel.send(embed=embed)

    async def assign_level_role(self, guild, user, level):
        """Asignar rol de nivel al usuario"""
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role_id FROM level_roles 
                WHERE guild_id = ? AND level <= ?
                ORDER BY level DESC LIMIT 1
            ''', (guild.id, level))
            
            result = cursor.fetchone()
            if not result:
                return
            
            role_id = result[0]
            role = guild.get_role(role_id)
            
            if role and role not in user.roles:
                # Remover roles de nivel anteriores
                cursor.execute('''
                    SELECT role_id FROM level_roles WHERE guild_id = ?
                ''', (guild.id,))
                
                all_level_roles = [guild.get_role(r[0]) for r in cursor.fetchall()]
                roles_to_remove = [r for r in all_level_roles if r and r in user.roles]
                
                try:
                    if roles_to_remove:
                        await user.remove_roles(*roles_to_remove, reason="Actualización de nivel")
                    await user.add_roles(role, reason=f"Alcanzó nivel {level}")
                except Exception as e:
                    print(f"Error asignando rol de nivel: {e}")

    async def get_new_privileges(self, guild, level):
        """Obtener nuevos privilegios desbloqueados"""
        privilege_descriptions = {
            "nickname": "Cambiar tu propio apodo",
            "media": "Enviar imágenes y archivos en chat general",
            "links": "Enviar enlaces en canales generales",
            "color_choice": "Elegir color de rol personalizado",
            "special_mention": "Menciones especiales en eventos",
            "all_privileges": "Todos los privilegios del servidor"
        }
        
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT privileges FROM level_roles 
                WHERE guild_id = ? AND level = ?
            ''', (guild.id, level))
            
            result = cursor.fetchone()
            if not result:
                return []
            
            privileges = json.loads(result[0])
            return [privilege_descriptions.get(p, p) for p in privileges]

    @tasks.loop(minutes=1)
    async def voice_xp_task(self):
        """Dar XP por tiempo en voz cada minuto"""
        for guild_id, sessions in self.voice_sessions.items():
            for user_id, start_time in sessions.items():
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    continue
                
                user = guild.get_member(user_id)
                if not user or not user.voice or user.voice.self_mute or user.voice.self_deaf:
                    continue
                
                # Dar XP por minuto en voz
                with sqlite3.connect('data/bot_data.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO user_levels 
                        (guild_id, user_id, xp, level, messages_sent, voice_time, last_message)
                        VALUES (?, ?, 0, 0, 0, 0, ?)
                    ''', (guild.id, user.id, datetime.now().isoformat()))
                    
                    cursor.execute('''
                        UPDATE user_levels 
                        SET xp = xp + ?, voice_time = voice_time + 1
                        WHERE guild_id = ? AND user_id = ?
                    ''', (self.VOICE_XP_PER_MINUTE, guild.id, user.id))
                    
                    # Verificar level up
                    cursor.execute('''
                        SELECT xp, level FROM user_levels 
                        WHERE guild_id = ? AND user_id = ?
                    ''', (guild.id, user.id))
                    
                    xp, current_level = cursor.fetchone()
                    new_level = self.calculate_level(xp)
                    
                    if new_level > current_level:
                        cursor.execute('''
                            UPDATE user_levels SET level = ? 
                            WHERE guild_id = ? AND user_id = ?
                        ''', (new_level, guild.id, user.id))
                        
                        conn.commit()
                        await self.handle_level_up(guild, user, new_level, current_level)
                    else:
                        conn.commit()

    async def voice_state_update(self, member, before, after):
        """Manejar cambios de estado de voz"""
        if member.bot:
            return
        
        guild_id = member.guild.id
        user_id = member.id
        
        if guild_id not in self.voice_sessions:
            self.voice_sessions[guild_id] = {}
        
        # Usuario se unió a canal de voz
        if after.channel and not before.channel:
            self.voice_sessions[guild_id][user_id] = datetime.now()
        
        # Usuario salió de canal de voz
        elif before.channel and not after.channel:
            if user_id in self.voice_sessions[guild_id]:
                del self.voice_sessions[guild_id][user_id]

    async def get_user_xp(self, guild_id, user_id):
        """Obtener XP de un usuario"""
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT xp FROM user_levels WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            result = cursor.fetchone()
            return result[0] if result else 0

    async def get_leaderboard(self, guild, limit=10):
        """Obtener leaderboard del servidor"""
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, xp, level, messages_sent, voice_time 
                FROM user_levels 
                WHERE guild_id = ? 
                ORDER BY xp DESC 
                LIMIT ?
            ''', (guild.id, limit))
            
            return cursor.fetchall()

def setup(bot):
    bot.add_cog(AdvancedLevelSystem(bot))
