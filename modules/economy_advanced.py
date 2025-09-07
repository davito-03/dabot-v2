"""
Sistema de Economía Avanzado v2.0 - Estilo Mee6 Mejorado
Incluye trabajo, apuestas, robo, inversiones, criptomonedas, tienda y más
Por davito - Dabot v2
"""

import logging
import json
import os
import random
import asyncio
from datetime import datetime, timedelta
import nextcord
from nextcord.ext import commands, tasks
import sqlite3
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class EconomyDB:
    """manejo de base de datos para economía"""
    
    def __init__(self, db_path: str = "data/economy.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """inicializar base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Tabla principal de usuarios
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        guild_id INTEGER,
                        user_id INTEGER,
                        balance INTEGER DEFAULT 1000,
                        bank INTEGER DEFAULT 0,
                        total_earned INTEGER DEFAULT 1000,
                        total_spent INTEGER DEFAULT 0,
                        last_daily TIMESTAMP,
                        last_work TIMESTAMP,
                        last_rob TIMESTAMP,
                        work_streak INTEGER DEFAULT 0,
                        job TEXT DEFAULT 'Desempleado',
                        PRIMARY KEY (guild_id, user_id)
                    )
                ''')
                
                # Tabla de inversiones
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS investments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER,
                        user_id INTEGER,
                        type TEXT,
                        amount INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        mature_at TIMESTAMP,
                        active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # Tabla de criptomonedas
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS crypto (
                        guild_id INTEGER,
                        user_id INTEGER,
                        bitcoin REAL DEFAULT 0,
                        ethereum REAL DEFAULT 0,
                        dogecoin REAL DEFAULT 0,
                        PRIMARY KEY (guild_id, user_id)
                    )
                ''')
                
                # Tabla de tienda
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS shop_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER,
                        name TEXT,
                        description TEXT,
                        price INTEGER,
                        type TEXT,
                        role_id INTEGER,
                        emoji TEXT,
                        stock INTEGER DEFAULT -1,
                        active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # Tabla de inventario
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS inventory (
                        guild_id INTEGER,
                        user_id INTEGER,
                        item_id INTEGER,
                        quantity INTEGER DEFAULT 1,
                        PRIMARY KEY (guild_id, user_id, item_id)
                    )
                ''')
                
                # Tabla de transacciones
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER,
                        user_id INTEGER,
                        type TEXT,
                        amount INTEGER,
                        description TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error inicializando base de datos de economía: {e}")

class EconomyAdvanced(commands.Cog):
    """sistema de economía avanzado estilo mee6+"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = EconomyDB()
        
        # Precios de criptomonedas simulados
        self.crypto_prices = {
            'bitcoin': 45000,
            'ethereum': 3200,
            'dogecoin': 0.25
        }
        
        # Lista de trabajos disponibles
        self.jobs = {
            'programador': {'min': 800, 'max': 1500, 'description': '💻 Programador'},
            'doctor': {'min': 1000, 'max': 2000, 'description': '⚕️ Doctor'},
            'chef': {'min': 600, 'max': 1200, 'description': '👨‍🍳 Chef'},
            'youtuber': {'min': 200, 'max': 3000, 'description': '📹 YouTuber'},
            'streamer': {'min': 100, 'max': 2500, 'description': '🎮 Streamer'},
            'profesor': {'min': 700, 'max': 1300, 'description': '👨‍🏫 Profesor'},
            'abogado': {'min': 900, 'max': 1800, 'description': '⚖️ Abogado'},
            'artista': {'min': 300, 'max': 2200, 'description': '🎨 Artista'},
            'músico': {'min': 400, 'max': 1600, 'description': '🎵 Músico'},
            'piloto': {'min': 1100, 'max': 2100, 'description': '✈️ Piloto'}
        }
        
        # Iniciar tareas
        self.crypto_update.start()
        self.investment_check.start()
    
    def cog_unload(self):
        """detener tareas al descargar"""
        self.crypto_update.cancel()
        self.investment_check.cancel()
    
    def get_user_data(self, guild_id: int, user_id: int):
        """obtener datos del usuario"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM users WHERE guild_id = ? AND user_id = ?",
                    (guild_id, user_id)
                )
                result = cursor.fetchone()
                if not result:
                    # Crear usuario nuevo
                    conn.execute(
                        "INSERT INTO users (guild_id, user_id) VALUES (?, ?)",
                        (guild_id, user_id)
                    )
                    conn.commit()
                    return self.get_user_data(guild_id, user_id)
                return result
        except Exception as e:
            logger.error(f"Error obteniendo datos de usuario: {e}")
            return None
    
    def update_balance(self, guild_id: int, user_id: int, amount: int, transaction_type: str, description: str = ""):
        """actualizar balance del usuario"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                conn.execute(
                    "UPDATE users SET balance = balance + ? WHERE guild_id = ? AND user_id = ?",
                    (amount, guild_id, user_id)
                )
                
                # Registrar transacción
                conn.execute(
                    "INSERT INTO transactions (guild_id, user_id, type, amount, description) VALUES (?, ?, ?, ?, ?)",
                    (guild_id, user_id, transaction_type, amount, description)
                )
                
                # Actualizar totales
                if amount > 0:
                    conn.execute(
                        "UPDATE users SET total_earned = total_earned + ? WHERE guild_id = ? AND user_id = ?",
                        (amount, guild_id, user_id)
                    )
                else:
                    conn.execute(
                        "UPDATE users SET total_spent = total_spent + ? WHERE guild_id = ? AND user_id = ?",
                        (abs(amount), guild_id, user_id)
                    )
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error actualizando balance: {e}")
    
    @nextcord.slash_command(name="economia", description="comandos de economía")
    async def economy_group(self, interaction: nextcord.Interaction):
        pass
    
    # COMANDOS BÁSICOS
    
    @economy_group.subcommand(name="balance", description="ver tu balance")
    async def balance(self, interaction: nextcord.Interaction, usuario: nextcord.Member = None):
        """ver balance propio o de otro usuario"""
        target = usuario or interaction.user
        user_data = self.get_user_data(interaction.guild.id, target.id)
        
        if not user_data:
            await interaction.response.send_message("❌ Error obteniendo datos.", ephemeral=True)
            return
        
        # Obtener datos de crypto
        crypto_data = self.get_crypto_data(interaction.guild.id, target.id)
        crypto_value = self.calculate_crypto_value(crypto_data)
        
        embed = nextcord.Embed(
            title=f"💰 Balance de {target.display_name}",
            color=nextcord.Color.gold()
        )
        embed.add_field(
            name="💵 Efectivo",
            value=f"**${user_data[2]:,}**",
            inline=True
        )
        embed.add_field(
            name="🏦 Banco",
            value=f"**${user_data[3]:,}**",
            inline=True
        )
        embed.add_field(
            name="💎 Total",
            value=f"**${user_data[2] + user_data[3]:,}**",
            inline=True
        )
        embed.add_field(
            name="💼 Trabajo",
            value=f"**{user_data[9]}**",
            inline=True
        )
        embed.add_field(
            name="🔥 Racha de trabajo",
            value=f"**{user_data[8]} días**",
            inline=True
        )
        embed.add_field(
            name="💱 Criptomonedas",
            value=f"**${crypto_value:,.2f}**",
            inline=True
        )
        embed.add_field(
            name="📈 Estadísticas",
            value=f"**Ganado:** ${user_data[4]:,}\n**Gastado:** ${user_data[5]:,}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @economy_group.subcommand(name="daily", description="reclamar recompensa diaria")
    async def daily(self, interaction: nextcord.Interaction):
        """reclamar recompensa diaria"""
        user_data = self.get_user_data(interaction.guild.id, interaction.user.id)
        
        # Verificar cooldown
        if user_data[6]:  # last_daily
            last_daily = datetime.fromisoformat(user_data[6])
            if datetime.now() - last_daily < timedelta(hours=20):
                time_left = timedelta(hours=20) - (datetime.now() - last_daily)
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                await interaction.response.send_message(
                    f"⏰ Ya reclamaste tu recompensa diaria. Vuelve en **{hours}h {minutes}m**.",
                    ephemeral=True
                )
                return
        
        # Calcular recompensa
        base_reward = 500
        streak_bonus = min(user_data[8] * 50, 1000)  # Bonus por racha de trabajo
        total_reward = base_reward + streak_bonus
        
        # Bonus aleatorio
        if random.randint(1, 10) == 1:  # 10% chance
            total_reward *= 2
            bonus_msg = "\n🎉 **¡Bonus x2!**"
        else:
            bonus_msg = ""
        
        # Actualizar datos
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "UPDATE users SET balance = balance + ?, last_daily = ?, total_earned = total_earned + ? WHERE guild_id = ? AND user_id = ?",
                (total_reward, datetime.now().isoformat(), total_reward, interaction.guild.id, interaction.user.id)
            )
            conn.commit()
        
        embed = nextcord.Embed(
            title="💰 Recompensa Diaria",
            description=f"Has recibido **${total_reward:,}**{bonus_msg}",
            color=nextcord.Color.green()
        )
        embed.add_field(
            name="💵 Recompensa base",
            value=f"${base_reward:,}",
            inline=True
        )
        embed.add_field(
            name="🔥 Bonus por racha",
            value=f"${streak_bonus:,}",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @economy_group.subcommand(name="work", description="trabajar para ganar dinero")
    async def work(self, interaction: nextcord.Interaction):
        """trabajar para ganar dinero"""
        user_data = self.get_user_data(interaction.guild.id, interaction.user.id)
        
        # Verificar cooldown
        if user_data[7]:  # last_work
            last_work = datetime.fromisoformat(user_data[7])
            if datetime.now() - last_work < timedelta(hours=1):
                time_left = timedelta(hours=1) - (datetime.now() - last_work)
                minutes = int(time_left.total_seconds() // 60)
                await interaction.response.send_message(
                    f"⏰ Estás cansado. Descansa **{minutes} minutos** más.",
                    ephemeral=True
                )
                return
        
        # Obtener trabajo del usuario
        current_job = user_data[9] if user_data[9] != 'Desempleado' else None
        
        if not current_job or current_job not in self.jobs:
            await interaction.response.send_message(
                "❌ No tienes trabajo. Usa `/economia job` para conseguir uno.",
                ephemeral=True
            )
            return
        
        # Calcular salario
        job_info = self.jobs[current_job]
        base_salary = random.randint(job_info['min'], job_info['max'])
        
        # Bonus por racha
        streak_bonus = min(user_data[8] * 0.1, 0.5)  # Hasta 50% bonus
        total_salary = int(base_salary * (1 + streak_bonus))
        
        # Eventos aleatorios
        event_msg = ""
        if random.randint(1, 20) == 1:  # 5% chance evento positivo
            total_salary = int(total_salary * 1.5)
            event_msg = "\n🎉 **¡Buen trabajo! Bonus x1.5**"
        elif random.randint(1, 30) == 1:  # 3.3% chance evento negativo
            total_salary = int(total_salary * 0.7)
            event_msg = "\n😵 **Día malo... Salario reducido**"
        
        # Actualizar datos
        new_streak = user_data[8] + 1
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "UPDATE users SET balance = balance + ?, last_work = ?, work_streak = ?, total_earned = total_earned + ? WHERE guild_id = ? AND user_id = ?",
                (total_salary, datetime.now().isoformat(), new_streak, total_salary, interaction.guild.id, interaction.user.id)
            )
            conn.commit()
        
        embed = nextcord.Embed(
            title=f"{job_info['description']} Trabajo Completado",
            description=f"Has ganado **${total_salary:,}**{event_msg}",
            color=nextcord.Color.blue()
        )
        embed.add_field(
            name="💼 Trabajo",
            value=current_job.title(),
            inline=True
        )
        embed.add_field(
            name="🔥 Racha",
            value=f"{new_streak} días",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @economy_group.subcommand(name="job", description="conseguir o cambiar trabajo")
    async def job(self, interaction: nextcord.Interaction, trabajo: str = None):
        """conseguir o cambiar trabajo"""
        if not trabajo:
            # Mostrar trabajos disponibles
            embed = nextcord.Embed(
                title="💼 Trabajos Disponibles",
                description="Elige un trabajo para empezar a ganar dinero",
                color=nextcord.Color.blue()
            )
            
            jobs_text = ""
            for job_name, job_info in self.jobs.items():
                jobs_text += f"{job_info['description']} **{job_name.title()}**\n"
                jobs_text += f"💰 ${job_info['min']:,} - ${job_info['max']:,} por hora\n\n"
            
            embed.add_field(
                name="📋 Lista de Trabajos",
                value=jobs_text,
                inline=False
            )
            embed.add_field(
                name="ℹ️ Cómo usar",
                value="Usa `/economia job <nombre>` para conseguir un trabajo",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            return
        
        trabajo = trabajo.lower()
        if trabajo not in self.jobs:
            await interaction.response.send_message(
                "❌ Trabajo no válido. Usa `/economia job` para ver la lista.",
                ephemeral=True
            )
            return
        
        # Cambiar trabajo
        with sqlite3.connect(self.db.db_path) as conn:
            conn.execute(
                "UPDATE users SET job = ? WHERE guild_id = ? AND user_id = ?",
                (trabajo, interaction.guild.id, interaction.user.id)
            )
            conn.commit()
        
        job_info = self.jobs[trabajo]
        embed = nextcord.Embed(
            title="💼 ¡Nuevo Trabajo!",
            description=f"Ahora trabajas como {job_info['description']} **{trabajo.title()}**",
            color=nextcord.Color.green()
        )
        embed.add_field(
            name="💰 Salario",
            value=f"${job_info['min']:,} - ${job_info['max']:,} por hora",
            inline=True
        )
        embed.add_field(
            name="⏰ Cooldown",
            value="1 hora entre trabajos",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    # SISTEMA DE APUESTAS
    
    @economy_group.subcommand(name="bet", description="apostar dinero en juegos")
    async def bet(self, interaction: nextcord.Interaction, cantidad: int, juego: str = "coinflip"):
        """apostar dinero en diferentes juegos"""
        user_data = self.get_user_data(interaction.guild.id, interaction.user.id)
        
        if cantidad <= 0:
            await interaction.response.send_message("❌ La cantidad debe ser positiva.", ephemeral=True)
            return
        
        if user_data[2] < cantidad:  # balance
            await interaction.response.send_message("❌ No tienes suficiente dinero.", ephemeral=True)
            return
        
        if cantidad > 10000:
            await interaction.response.send_message("❌ La apuesta máxima es $10,000.", ephemeral=True)
            return
        
        juego = juego.lower()
        
        if juego == "coinflip":
            # Cara o cruz
            win = random.choice([True, False])
            if win:
                winnings = cantidad
                self.update_balance(interaction.guild.id, interaction.user.id, winnings, "bet_win", f"Coinflip ganado")
                embed = nextcord.Embed(
                    title="🪙 Coinflip - ¡Ganaste!",
                    description=f"**Cara** 🪙\n\nHas ganado **${winnings:,}**",
                    color=nextcord.Color.green()
                )
            else:
                self.update_balance(interaction.guild.id, interaction.user.id, -cantidad, "bet_loss", f"Coinflip perdido")
                embed = nextcord.Embed(
                    title="🪙 Coinflip - Perdiste",
                    description=f"**Cruz** 🪙\n\nHas perdido **${cantidad:,}**",
                    color=nextcord.Color.red()
                )
        
        elif juego == "dice":
            # Dados
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            total = dice1 + dice2
            
            if total >= 10:  # Ganar con 10+
                multiplier = 1.5 if total >= 11 else 1.2
                winnings = int(cantidad * multiplier)
                self.update_balance(interaction.guild.id, interaction.user.id, winnings, "bet_win", f"Dados ganado ({total})")
                embed = nextcord.Embed(
                    title="🎲 Dados - ¡Ganaste!",
                    description=f"🎲 {dice1} + 🎲 {dice2} = **{total}**\n\nHas ganado **${winnings:,}** (x{multiplier})",
                    color=nextcord.Color.green()
                )
            else:
                self.update_balance(interaction.guild.id, interaction.user.id, -cantidad, "bet_loss", f"Dados perdido ({total})")
                embed = nextcord.Embed(
                    title="🎲 Dados - Perdiste",
                    description=f"🎲 {dice1} + 🎲 {dice2} = **{total}**\n\nHas perdido **${cantidad:,}**\n\nNecesitas 10+ para ganar",
                    color=nextcord.Color.red()
                )
        
        elif juego == "slots":
            # Máquina tragamonedas
            symbols = ["🍎", "🍌", "🍇", "🍒", "💎", "⭐", "7️⃣"]
            weights = [25, 25, 20, 15, 8, 5, 2]  # Probabilidades
            
            result = random.choices(symbols, weights=weights, k=3)
            
            if result[0] == result[1] == result[2]:  # Tres iguales
                if result[0] == "7️⃣":
                    multiplier = 10
                elif result[0] == "💎":
                    multiplier = 5
                elif result[0] == "⭐":
                    multiplier = 3
                else:
                    multiplier = 2
                
                winnings = int(cantidad * multiplier)
                self.update_balance(interaction.guild.id, interaction.user.id, winnings, "bet_win", f"Slots ganado (x{multiplier})")
                embed = nextcord.Embed(
                    title="🎰 Slots - ¡JACKPOT!",
                    description=f"{result[0]} {result[1]} {result[2]}\n\nHas ganado **${winnings:,}** (x{multiplier})",
                    color=nextcord.Color.green()
                )
            elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:  # Dos iguales
                winnings = int(cantidad * 0.5)
                self.update_balance(interaction.guild.id, interaction.user.id, winnings, "bet_win", f"Slots ganado (x0.5)")
                embed = nextcord.Embed(
                    title="🎰 Slots - Mini premio",
                    description=f"{result[0]} {result[1]} {result[2]}\n\nHas ganado **${winnings:,}** (x0.5)",
                    color=nextcord.Color.orange()
                )
            else:
                self.update_balance(interaction.guild.id, interaction.user.id, -cantidad, "bet_loss", f"Slots perdido")
                embed = nextcord.Embed(
                    title="🎰 Slots - Perdiste",
                    description=f"{result[0]} {result[1]} {result[2]}\n\nHas perdido **${cantidad:,}**",
                    color=nextcord.Color.red()
                )
        
        else:
            await interaction.response.send_message(
                "❌ Juego no válido. Disponibles: `coinflip`, `dice`, `slots`",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(embed=embed)
    
    # SISTEMA DE ROBO
    
    @economy_group.subcommand(name="rob", description="robar dinero a otro usuario")
    async def rob(self, interaction: nextcord.Interaction, usuario: nextcord.Member):
        """intentar robar dinero a otro usuario"""
        if usuario.id == interaction.user.id:
            await interaction.response.send_message("❌ No puedes robarte a ti mismo.", ephemeral=True)
            return
        
        if usuario.bot:
            await interaction.response.send_message("❌ No puedes robar a un bot.", ephemeral=True)
            return
        
        user_data = self.get_user_data(interaction.guild.id, interaction.user.id)
        target_data = self.get_user_data(interaction.guild.id, usuario.id)
        
        # Verificar cooldown
        if user_data[8]:  # last_rob usando work_streak como placeholder
            # En implementación real, añadir campo last_rob
            pass
        
        # Verificar que el objetivo tenga dinero
        if target_data[2] < 500:  # balance mínimo para robar
            await interaction.response.send_message(
                f"❌ {usuario.display_name} no tiene suficiente dinero para robar (mínimo $500).",
                ephemeral=True
            )
            return
        
        # Probabilidad de éxito (50% base)
        success_chance = 50
        
        # Modificadores
        if user_data[2] > target_data[2]:  # Si tienes más dinero, menor chance
            success_chance -= 15
        
        if target_data[2] > 5000:  # Si la víctima es rica, mayor chance
            success_chance += 10
        
        success = random.randint(1, 100) <= success_chance
        
        if success:
            # Robo exitoso
            stolen_amount = random.randint(100, min(target_data[2] // 4, 2000))
            
            self.update_balance(interaction.guild.id, interaction.user.id, stolen_amount, "rob_success", f"Robado a {usuario.display_name}")
            self.update_balance(interaction.guild.id, usuario.id, -stolen_amount, "robbed", f"Robado por {interaction.user.display_name}")
            
            embed = nextcord.Embed(
                title="🥷 Robo Exitoso",
                description=f"Has robado **${stolen_amount:,}** a {usuario.display_name}",
                color=nextcord.Color.green()
            )
        else:
            # Robo fallido - multa
            fine = random.randint(200, 800)
            fine = min(fine, user_data[2])  # No puede pagar más de lo que tiene
            
            self.update_balance(interaction.guild.id, interaction.user.id, -fine, "rob_fail", f"Multa por robo fallido")
            
            embed = nextcord.Embed(
                title="🚨 Robo Fallido",
                description=f"Te han atrapado y has pagado una multa de **${fine:,}**",
                color=nextcord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed)
    
    # Continuaré con el resto de funcionalidades...
    
    def get_crypto_data(self, guild_id: int, user_id: int):
        """obtener datos de criptomonedas del usuario"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.execute(
                    "SELECT bitcoin, ethereum, dogecoin FROM crypto WHERE guild_id = ? AND user_id = ?",
                    (guild_id, user_id)
                )
                result = cursor.fetchone()
                if not result:
                    conn.execute(
                        "INSERT INTO crypto (guild_id, user_id) VALUES (?, ?)",
                        (guild_id, user_id)
                    )
                    conn.commit()
                    return (0, 0, 0)
                return result
        except Exception as e:
            logger.error(f"Error obteniendo datos de crypto: {e}")
            return (0, 0, 0)
    
    def calculate_crypto_value(self, crypto_data):
        """calcular valor total de criptomonedas"""
        bitcoin, ethereum, dogecoin = crypto_data
        return (bitcoin * self.crypto_prices['bitcoin'] + 
                ethereum * self.crypto_prices['ethereum'] + 
                dogecoin * self.crypto_prices['dogecoin'])
    
    @tasks.loop(minutes=30)
    async def crypto_update(self):
        """actualizar precios de criptomonedas"""
        for crypto in self.crypto_prices:
            # Simulación de cambio de precio ±5%
            change = random.uniform(-0.05, 0.05)
            self.crypto_prices[crypto] *= (1 + change)
            self.crypto_prices[crypto] = max(0.01, self.crypto_prices[crypto])  # Mínimo
    
    @tasks.loop(hours=24)
    async def investment_check(self):
        """verificar inversiones maduras"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                # Buscar inversiones maduras
                cursor = conn.execute(
                    "SELECT * FROM investments WHERE mature_at <= ? AND active = 1",
                    (datetime.now().isoformat(),)
                )
                mature_investments = cursor.fetchall()
                
                for investment in mature_investments:
                    guild_id, user_id, inv_type, amount = investment[1], investment[2], investment[3], investment[4]
                    
                    # Calcular retorno según tipo
                    if inv_type == "short":  # 7 días, 5-15% retorno
                        return_rate = random.uniform(0.05, 0.15)
                    elif inv_type == "medium":  # 30 días, 15-30% retorno
                        return_rate = random.uniform(0.15, 0.30)
                    elif inv_type == "long":  # 90 días, 30-60% retorno
                        return_rate = random.uniform(0.30, 0.60)
                    
                    final_amount = int(amount * (1 + return_rate))
                    
                    # Devolver dinero
                    self.update_balance(guild_id, user_id, final_amount, "investment_mature", f"Inversión {inv_type} madura")
                    
                    # Marcar como completada
                    conn.execute(
                        "UPDATE investments SET active = 0 WHERE id = ?",
                        (investment[0],)
                    )
                
                conn.commit()
        except Exception as e:
            logger.error(f"Error verificando inversiones: {e}")

def setup(bot):
    """cargar el cog"""
    bot.add_cog(EconomyAdvanced(bot))
