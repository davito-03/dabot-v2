"""
Sistema Unificado de Entretenimiento y Economía
Incluye: juegos, diversión, pesca, economía básica, memes
Por: Davito
"""

import logging
import nextcord
from nextcord.ext import commands
import aiohttp
import asyncio
import random
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import time

logger = logging.getLogger(__name__)

class EntertainmentEconomy(commands.Cog):
    """Sistema unificado de entretenimiento y economía"""
    
    def __init__(self, bot):
        self.bot = bot
        self.init_database()
        
        # Configuración de la pesca
        self.fish_types = {
            "common": {
                "🐟": {"name": "Pez Común", "value": 5, "rarity": 60},
                "🐠": {"name": "Pez Tropical", "value": 8, "rarity": 55},
                "🦈": {"name": "Tiburón Bebé", "value": 15, "rarity": 45}
            },
            "rare": {
                "🐡": {"name": "Pez Globo", "value": 25, "rarity": 25},
                "🦞": {"name": "Langosta", "value": 35, "rarity": 20},
                "🦀": {"name": "Cangrejo", "value": 30, "rarity": 22}
            },
            "epic": {
                "🐙": {"name": "Pulpo", "value": 50, "rarity": 8},
                "🦑": {"name": "Calamar", "value": 60, "rarity": 6},
                "🐋": {"name": "Ballena", "value": 100, "rarity": 3}
            },
            "legendary": {
                "🦈": {"name": "Gran Tiburón", "value": 200, "rarity": 1.5},
                "🐉": {"name": "Dragón Marino", "value": 500, "rarity": 0.5}
            }
        }
        
        # Cooldowns de actividades
        self.cooldowns = {}
        
        # Frases de 8ball
        self.eightball_responses = [
            "✅ Sí, definitivamente",
            "✅ Sin duda alguna", 
            "✅ Puedes contar con ello",
            "⚡ Las perspectivas son buenas",
            "⚡ Probablemente sí",
            "🤔 Pregunta de nuevo más tarde",
            "🤔 No puedo predecirlo ahora",
            "🤔 Concentrate y pregunta de nuevo",
            "❌ No cuentes con ello",
            "❌ Mi respuesta es no",
            "❌ Muy dudoso"
        ]
    
    def init_database(self):
        """Inicializar base de datos"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            # Tabla de economía
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_economy (
                    guild_id INTEGER,
                    user_id INTEGER,
                    coins INTEGER DEFAULT 100,
                    bank INTEGER DEFAULT 0,
                    inventory TEXT DEFAULT '{}',
                    fishing_level INTEGER DEFAULT 1,
                    fishing_exp INTEGER DEFAULT 0,
                    last_daily TIMESTAMP,
                    last_work TIMESTAMP,
                    last_fish TIMESTAMP,
                    total_fish_caught INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, user_id)
                )
            ''')
            
            # Tabla de logros
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_achievements (
                    guild_id INTEGER,
                    user_id INTEGER,
                    achievement_id TEXT,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (guild_id, user_id, achievement_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Base de datos de entretenimiento y economía inicializada")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
    
    # ================================
    # COMANDOS DE ECONOMÍA
    # ================================
    
    @nextcord.slash_command(name="balance", description="Ver tu balance de monedas")
    async def balance(self, interaction: nextcord.Interaction, usuario: nextcord.Member = None):
        """Ver balance de monedas"""
        target = usuario or interaction.user
        
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT coins, bank, fishing_level, total_fish_caught
                FROM user_economy 
                WHERE guild_id = ? AND user_id = ?
            ''', (interaction.guild.id, target.id))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                coins, bank, fishing_level, fish_caught = result
            else:
                coins, bank, fishing_level, fish_caught = 100, 0, 1, 0
                await self.create_user_economy(interaction.guild.id, target.id)
            
            total = coins + bank
            
            embed = nextcord.Embed(
                title=f"💰 Balance de {target.display_name}",
                color=nextcord.Color.gold()
            )
            
            embed.add_field(
                name="💵 En Cartera",
                value=f"{coins:,} monedas",
                inline=True
            )
            
            embed.add_field(
                name="🏦 En Banco", 
                value=f"{bank:,} monedas",
                inline=True
            )
            
            embed.add_field(
                name="💎 Total",
                value=f"{total:,} monedas",
                inline=True
            )
            
            embed.add_field(
                name="🎣 Nivel de Pesca",
                value=f"Nivel {fishing_level}",
                inline=True
            )
            
            embed.add_field(
                name="🐟 Peces Pescados",
                value=f"{fish_caught:,} peces",
                inline=True
            )
            
            embed.set_thumbnail(url=target.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en balance: {e}")
            await interaction.response.send_message("❌ Error consultando balance.", ephemeral=True)
    
    @nextcord.slash_command(name="daily", description="Reclamar recompensa diaria")
    async def daily(self, interaction: nextcord.Interaction):
        """Reclamar recompensa diaria"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            # Verificar último daily
            cursor.execute('''
                SELECT last_daily FROM user_economy 
                WHERE guild_id = ? AND user_id = ?
            ''', (interaction.guild.id, interaction.user.id))
            
            result = cursor.fetchone()
            now = datetime.now()
            
            if result and result[0]:
                last_daily = datetime.fromisoformat(result[0])
                if (now - last_daily).total_seconds() < 86400:  # 24 horas
                    time_left = 86400 - (now - last_daily).total_seconds()
                    hours = int(time_left // 3600)
                    minutes = int((time_left % 3600) // 60)
                    
                    await interaction.response.send_message(
                        f"⏰ Ya reclamaste tu recompensa diaria. Vuelve en {hours}h {minutes}m",
                        ephemeral=True
                    )
                    conn.close()
                    return
            
            # Dar recompensa
            daily_amount = random.randint(50, 150)
            bonus = random.randint(1, 100)
            
            if bonus <= 10:  # 10% chance de bonus
                daily_amount *= 2
                bonus_text = "🎉 ¡BONUS x2!"
            else:
                bonus_text = ""
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_economy 
                (guild_id, user_id, coins, last_daily)
                VALUES (?, ?, COALESCE((SELECT coins FROM user_economy WHERE guild_id = ? AND user_id = ?), 100) + ?, ?)
            ''', (interaction.guild.id, interaction.user.id, interaction.guild.id, interaction.user.id, daily_amount, now.isoformat()))
            
            conn.commit()
            conn.close()
            
            embed = nextcord.Embed(
                title="💰 Recompensa Diaria",
                description=f"¡Has recibido **{daily_amount:,} monedas**!\n{bonus_text}",
                color=nextcord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en daily: {e}")
            await interaction.response.send_message("❌ Error reclamando recompensa diaria.", ephemeral=True)
    
    @nextcord.slash_command(name="work", description="Trabajar para ganar monedas")
    async def work(self, interaction: nextcord.Interaction):
        """Trabajar para ganar monedas"""
        try:
            # Verificar cooldown
            user_key = f"{interaction.guild.id}_{interaction.user.id}_work"
            if user_key in self.cooldowns:
                time_left = self.cooldowns[user_key] - time.time()
                if time_left > 0:
                    minutes = int(time_left // 60)
                    seconds = int(time_left % 60)
                    await interaction.response.send_message(
                        f"⏰ Debes esperar {minutes}m {seconds}s antes de trabajar de nuevo.",
                        ephemeral=True
                    )
                    return
            
            # Trabajos disponibles
            jobs = [
                {"name": "Programador", "min": 40, "max": 80, "emoji": "💻"},
                {"name": "Chef", "min": 30, "max": 70, "emoji": "👨‍🍳"},
                {"name": "Médico", "min": 60, "max": 100, "emoji": "👨‍⚕️"},
                {"name": "Profesor", "min": 35, "max": 65, "emoji": "👨‍🏫"},
                {"name": "Artista", "min": 25, "max": 85, "emoji": "🎨"},
                {"name": "Músico", "min": 20, "max": 90, "emoji": "🎵"}
            ]
            
            job = random.choice(jobs)
            earnings = random.randint(job["min"], job["max"])
            
            # Dar dinero
            await self.add_money(interaction.guild.id, interaction.user.id, earnings)
            
            # Setear cooldown (1 hora)
            self.cooldowns[user_key] = time.time() + 3600
            
            embed = nextcord.Embed(
                title=f"{job['emoji']} Trabajo Completado",
                description=f"Trabajaste como **{job['name']}** y ganaste **{earnings:,} monedas**!",
                color=nextcord.Color.blue()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en work: {e}")
            await interaction.response.send_message("❌ Error trabajando.", ephemeral=True)
    
    # ================================
    # SISTEMA DE PESCA
    # ================================
    
    @nextcord.slash_command(name="fish", description="Ir a pescar y ganar monedas")
    async def fish(self, interaction: nextcord.Interaction):
        """Sistema de pesca"""
        try:
            # Verificar cooldown
            user_key = f"{interaction.guild.id}_{interaction.user.id}_fish"
            if user_key in self.cooldowns:
                time_left = self.cooldowns[user_key] - time.time()
                if time_left > 0:
                    minutes = int(time_left // 60)
                    seconds = int(time_left % 60)
                    await interaction.response.send_message(
                        f"🎣 Debes esperar {minutes}m {seconds}s antes de pescar de nuevo.",
                        ephemeral=True
                    )
                    return
            
            await interaction.response.defer()
            
            # Animación de pesca
            embed = nextcord.Embed(
                title="🎣 Pescando...",
                description="🌊 Lanzaste tu caña al agua...",
                color=nextcord.Color.blue()
            )
            
            message = await interaction.followup.send(embed=embed)
            
            await asyncio.sleep(2)
            
            embed.description = "🎣 Algo está mordiendo el anzuelo..."
            await message.edit(embed=embed)
            
            await asyncio.sleep(2)
            
            # Determinar qué se pescó
            catch = self.determine_fish_catch()
            
            if catch:
                # Dar experiencia y dinero
                exp_gained = random.randint(5, 15)
                money_gained = catch["value"]
                
                await self.add_money(interaction.guild.id, interaction.user.id, money_gained)
                await self.add_fishing_exp(interaction.guild.id, interaction.user.id, exp_gained)
                await self.increment_fish_count(interaction.guild.id, interaction.user.id)
                
                # Resultado
                embed = nextcord.Embed(
                    title="🎣 ¡Pescaste algo!",
                    description=f"Pescaste un **{catch['emoji']} {catch['name']}**!\n\n"
                               f"💰 +{money_gained:,} monedas\n"
                               f"⭐ +{exp_gained} EXP de pesca",
                    color=nextcord.Color.green()
                )
                
                # Verificar subida de nivel
                level_up = await self.check_fishing_level_up(interaction.guild.id, interaction.user.id)
                if level_up:
                    embed.add_field(
                        name="🎉 ¡Subida de Nivel!",
                        value=f"¡Ahora eres nivel {level_up} en pesca!",
                        inline=False
                    )
                
            else:
                # No pescó nada
                embed = nextcord.Embed(
                    title="🎣 Sin suerte...",
                    description="No pescaste nada esta vez. ¡Inténtalo de nuevo más tarde!",
                    color=nextcord.Color.red()
                )
            
            await message.edit(embed=embed)
            
            # Setear cooldown (30 minutos)
            self.cooldowns[user_key] = time.time() + 1800
            
        except Exception as e:
            logger.error(f"Error en fish: {e}")
            await interaction.followup.send("❌ Error pescando.", ephemeral=True)
    
    def determine_fish_catch(self):
        """Determinar qué pez se pescó"""
        roll = random.randint(1, 100)
        
        # 15% chance de no pescar nada
        if roll <= 15:
            return None
        
        # Calcular probabilidades acumulativas
        all_fish = []
        for rarity, fishes in self.fish_types.items():
            for emoji, fish_data in fishes.items():
                fish_data["emoji"] = emoji
                all_fish.append(fish_data)
        
        # Ordenar por rareza (más raro = menor probabilidad)
        all_fish.sort(key=lambda x: x["rarity"], reverse=True)
        
        # Seleccionar pez basado en rareza
        total_weight = sum(fish["rarity"] for fish in all_fish)
        roll = random.randint(1, int(total_weight))
        
        current_weight = 0
        for fish in all_fish:
            current_weight += fish["rarity"]
            if roll <= current_weight:
                return fish
        
        # Fallback
        return all_fish[0]
    
    @nextcord.slash_command(name="aquarium", description="Ver tu acuario personal")
    async def aquarium(self, interaction: nextcord.Interaction):
        """Ver estadísticas de pesca"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT fishing_level, fishing_exp, total_fish_caught
                FROM user_economy 
                WHERE guild_id = ? AND user_id = ?
            ''', (interaction.guild.id, interaction.user.id))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                level, exp, total_caught = result
            else:
                level, exp, total_caught = 1, 0, 0
            
            # Calcular EXP para siguiente nivel
            exp_needed = level * 100
            exp_progress = (exp % exp_needed) if exp_needed > 0 else 0
            
            embed = nextcord.Embed(
                title=f"🏛️ Acuario de {interaction.user.display_name}",
                color=nextcord.Color.blue()
            )
            
            embed.add_field(
                name="🎣 Nivel de Pesca",
                value=f"Nivel {level}",
                inline=True
            )
            
            embed.add_field(
                name="⭐ Experiencia",
                value=f"{exp_progress}/{exp_needed} EXP",
                inline=True
            )
            
            embed.add_field(
                name="🐟 Total Pescado",
                value=f"{total_caught:,} peces",
                inline=True
            )
            
            # Mostrar tipos de peces disponibles
            fish_display = ""
            for rarity, fishes in self.fish_types.items():
                rarity_name = rarity.title()
                fish_display += f"\n**{rarity_name}:**\n"
                for emoji, fish_data in fishes.items():
                    fish_display += f"{emoji} {fish_data['name']} - {fish_data['value']} monedas\n"
            
            embed.add_field(
                name="🌊 Especies Disponibles",
                value=fish_display,
                inline=False
            )
            
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error en aquarium: {e}")
            await interaction.response.send_message("❌ Error consultando acuario.", ephemeral=True)
    
    # ================================
    # COMANDOS DE ENTRETENIMIENTO
    # ================================
    
    @nextcord.slash_command(name="8ball", description="Hazle una pregunta a la bola 8 mágica")
    async def eightball(self, interaction: nextcord.Interaction, pregunta: str):
        """Bola 8 mágica"""
        response = random.choice(self.eightball_responses)
        
        embed = nextcord.Embed(
            title="🎱 Bola 8 Mágica",
            color=nextcord.Color.purple()
        )
        
        embed.add_field(
            name="❓ Pregunta",
            value=pregunta,
            inline=False
        )
        
        embed.add_field(
            name="🔮 Respuesta",
            value=response,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="coin", description="Lanzar una moneda")
    async def coinflip(self, interaction: nextcord.Interaction):
        """Lanzar moneda"""
        result = random.choice(["Cara", "Cruz"])
        emoji = "🪙" if result == "Cara" else "⚪"
        
        embed = nextcord.Embed(
            title="🪙 Lanzamiento de Moneda",
            description=f"La moneda cayó en: **{emoji} {result}**",
            color=nextcord.Color.gold()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="dice", description="Lanzar dados")
    async def dice(self, interaction: nextcord.Interaction, caras: int = 6, cantidad: int = 1):
        """Lanzar dados"""
        if cantidad > 10:
            await interaction.response.send_message("❌ Máximo 10 dados por lanzamiento.", ephemeral=True)
            return
        
        if caras < 2 or caras > 100:
            await interaction.response.send_message("❌ Los dados deben tener entre 2 y 100 caras.", ephemeral=True)
            return
        
        results = [random.randint(1, caras) for _ in range(cantidad)]
        total = sum(results)
        
        embed = nextcord.Embed(
            title="🎲 Lanzamiento de Dados",
            color=nextcord.Color.blue()
        )
        
        if cantidad == 1:
            embed.description = f"🎲 Resultado: **{results[0]}**"
        else:
            embed.description = f"🎲 Resultados: {', '.join(map(str, results))}\n📊 Total: **{total}**"
        
        await interaction.response.send_message(embed=embed)
    
    @nextcord.slash_command(name="meme", description="Obtener un meme aleatorio")
    async def meme(self, interaction: nextcord.Interaction):
        """Obtener meme aleatorio"""
        await interaction.response.defer()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://meme-api.herokuapp.com/gimme') as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        embed = nextcord.Embed(
                            title=data['title'],
                            color=nextcord.Color.orange()
                        )
                        embed.set_image(url=data['url'])
                        embed.set_footer(text=f"👍 {data.get('ups', 0)} upvotes | r/{data.get('subreddit', 'memes')}")
                        
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ No pude obtener un meme en este momento.")
                        
        except Exception as e:
            logger.error(f"Error obteniendo meme: {e}")
            await interaction.followup.send("❌ Error obteniendo meme.")
    
    # ================================
    # FUNCIONES AUXILIARES
    # ================================
    
    async def create_user_economy(self, guild_id: int, user_id: int):
        """Crear registro de economía para usuario"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO user_economy 
                (guild_id, user_id, coins) 
                VALUES (?, ?, 100)
            ''', (guild_id, user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error creando usuario economía: {e}")
    
    async def add_money(self, guild_id: int, user_id: int, amount: int):
        """Añadir dinero a usuario"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_economy 
                (guild_id, user_id, coins)
                VALUES (?, ?, COALESCE((SELECT coins FROM user_economy WHERE guild_id = ? AND user_id = ?), 100) + ?)
            ''', (guild_id, user_id, guild_id, user_id, amount))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error añadiendo dinero: {e}")
    
    async def add_fishing_exp(self, guild_id: int, user_id: int, exp: int):
        """Añadir experiencia de pesca"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_economy 
                SET fishing_exp = fishing_exp + ?
                WHERE guild_id = ? AND user_id = ?
            ''', (exp, guild_id, user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error añadiendo EXP de pesca: {e}")
    
    async def increment_fish_count(self, guild_id: int, user_id: int):
        """Incrementar contador de peces"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_economy 
                SET total_fish_caught = total_fish_caught + 1
                WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error incrementando contador de peces: {e}")
    
    async def check_fishing_level_up(self, guild_id: int, user_id: int):
        """Verificar si el usuario subió de nivel en pesca"""
        try:
            conn = sqlite3.connect('dabot_database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT fishing_level, fishing_exp FROM user_economy 
                WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            current_level, current_exp = result
            new_level = current_level
            
            # Calcular nuevo nivel
            while current_exp >= new_level * 100:
                current_exp -= new_level * 100
                new_level += 1
            
            if new_level > current_level:
                # Actualizar nivel
                cursor.execute('''
                    UPDATE user_economy 
                    SET fishing_level = ?
                    WHERE guild_id = ? AND user_id = ?
                ''', (new_level, guild_id, user_id))
                
                conn.commit()
                conn.close()
                return new_level
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Error verificando level up: {e}")
            return None


def setup(bot):
    """Cargar el cog"""
    return EntertainmentEconomy(bot)
