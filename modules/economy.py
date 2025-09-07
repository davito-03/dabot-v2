"""
Sistema de economía con minijuegos y apuestas
por davito
"""

import logging
import json
import os
import random
import asyncio
from datetime import datetime, timedelta
import nextcord
from nextcord.ext import commands, tasks
import aiohttp

logger = logging.getLogger(__name__)

class Economy(commands.Cog):
    """sistema de economía completo"""
    
    def __init__(self, bot):
        self.bot = bot
        self.economy_file = "data/economy.json"
        self.economy_data = self.load_economy()
        self.daily_cooldowns = {}
        self.gambling_sessions = {}
        
        # crear directorio si no existe
        os.makedirs("data", exist_ok=True)
        
        # iniciar tareas
        self.save_task.start()
        self.interest_task.start()
    
    def cog_unload(self):
        """detener tareas al descargar"""
        self.save_task.cancel()
        self.interest_task.cancel()
    
    def load_economy(self):
        """cargar datos de economía"""
        try:
            if os.path.exists(self.economy_file):
                with open(self.economy_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"error cargando economía: {e}")
            return {}
    
    def save_economy(self):
        """guardar datos de economía"""
        try:
            with open(self.economy_file, 'w', encoding='utf-8') as f:
                json.dump(self.economy_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando economía: {e}")
    
    @tasks.loop(minutes=30)
    async def save_task(self):
        """guardar datos cada 30 minutos"""
        self.save_economy()
    
    @tasks.loop(hours=24)
    async def interest_task(self):
        """aplicar intereses diarios al banco"""
        try:
            for guild_data in self.economy_data.values():
                for user_data in guild_data.values():
                    if 'bank' in user_data and user_data['bank'] > 0:
                        interest = int(user_data['bank'] * 0.02)  # 2% de interés
                        user_data['bank'] += interest
            
            self.save_economy()
            logger.info("intereses aplicados a todas las cuentas bancarias")
            
        except Exception as e:
            logger.error(f"error aplicando intereses: {e}")
    
    @save_task.before_loop
    @interest_task.before_loop
    async def before_tasks(self):
        """esperar a que el bot esté listo"""
        await self.bot.wait_until_ready()
    
    def get_user_data(self, guild_id: int, user_id: int):
        """obtener datos de usuario"""
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        if guild_str not in self.economy_data:
            self.economy_data[guild_str] = {}
        
        if user_str not in self.economy_data[guild_str]:
            self.economy_data[guild_str][user_str] = {
                'balance': 1000,  # dinero inicial
                'bank': 0,
                'daily_streak': 0,
                'last_daily': None,
                'total_earned': 1000,
                'total_spent': 0,
                'level': 1,
                'xp': 0,
                'inventory': {},
                'achievements': []
            }
        
        return self.economy_data[guild_str][user_str]
    
    def add_money(self, guild_id: int, user_id: int, amount: int, source: str = "unknown"):
        """añadir dinero a un usuario"""
        user_data = self.get_user_data(guild_id, user_id)
        user_data['balance'] += amount
        user_data['total_earned'] += amount
        
        # añadir xp por ganar dinero
        xp_gain = max(1, amount // 100)
        self.add_xp(guild_id, user_id, xp_gain)
        
        logger.info(f"dinero añadido: {amount} a usuario {user_id} por {source}")
        return user_data['balance']
    
    def remove_money(self, guild_id: int, user_id: int, amount: int, source: str = "unknown"):
        """quitar dinero a un usuario"""
        user_data = self.get_user_data(guild_id, user_id)
        if user_data['balance'] >= amount:
            user_data['balance'] -= amount
            user_data['total_spent'] += amount
            logger.info(f"dinero quitado: {amount} de usuario {user_id} por {source}")
            return True
        return False
    
    def add_xp(self, guild_id: int, user_id: int, amount: int):
        """añadir experiencia a un usuario"""
        user_data = self.get_user_data(guild_id, user_id)
        user_data['xp'] += amount
        
        # calcular si sube de nivel
        level_up_xp = user_data['level'] * 1000
        if user_data['xp'] >= level_up_xp:
            user_data['level'] += 1
            user_data['xp'] = 0
            
            # bonificación por subir de nivel
            bonus = user_data['level'] * 500
            user_data['balance'] += bonus
            
            return True, bonus  # subió de nivel, bonificación
        
        return False, 0
    
    @commands.command(name='balance', aliases=['bal', 'dinero'])
    async def balance(self, ctx, member: nextcord.Member = None):
        """
        ver el dinero de un usuario
        uso: !balance [@usuario]
        """
        await self._show_balance(ctx, member)
    
    @nextcord.slash_command(name="balance", description="Ver el balance de monedas de un usuario")
    async def balance_slash(
        self, 
        interaction: nextcord.Interaction,
        usuario: nextcord.Member = nextcord.SlashOption(
            description="Usuario a consultar (opcional)",
            required=False
        )
    ):
        """Ver el balance de monedas de un usuario"""
        await self._show_balance(interaction, usuario)
    
    async def _show_balance(self, ctx_or_interaction, member=None):
        """función interna para mostrar balance"""
        try:
            # Determinar si es command o slash command
            if hasattr(ctx_or_interaction, 'response'):
                # Es slash command
                author = ctx_or_interaction.user
                guild = ctx_or_interaction.guild
                send_func = ctx_or_interaction.response.send_message
            else:
                # Es command tradicional
                author = ctx_or_interaction.author
                guild = ctx_or_interaction.guild
                send_func = ctx_or_interaction.send
            
            if member is None:
                member = author
            
            user_data = self.get_user_data(guild.id, member.id)
            
            embed = nextcord.Embed(
                title=f"💰 cartera de {member.display_name}",
                color=nextcord.Color.gold()
            )
            
            embed.add_field(name="💵 efectivo", value=f"€{user_data['balance']:,}", inline=True)
            embed.add_field(name="🏦 banco", value=f"€{user_data['bank']:,}", inline=True)
            embed.add_field(name="💎 total", value=f"€{user_data['balance'] + user_data['bank']:,}", inline=True)
            
            embed.add_field(name="📊 nivel", value=f"nivel {user_data['level']}", inline=True)
            embed.add_field(name="⭐ experiencia", value=f"{user_data['xp']}/{user_data['level'] * 1000} xp", inline=True)
            embed.add_field(name="🔥 racha diaria", value=f"{user_data['daily_streak']} días", inline=True)
            
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)
            
            embed.set_footer(text="usa /daily para obtener dinero diario")
            
            await send_func(embed=embed)
            
        except Exception as e:
            logger.error(f"error en balance: {e}")
            error_msg = "❌ error al obtener el balance."
            if hasattr(ctx_or_interaction, 'response'):
                await ctx_or_interaction.response.send_message(error_msg, ephemeral=True)
            else:
                await ctx_or_interaction.send(error_msg)
    
    @commands.command(name='daily', aliases=['diario'])
    async def daily_reward(self, ctx):
        """
        reclamar recompensa diaria
        uso: !daily
        """
        await self._claim_daily(ctx)
    
    @nextcord.slash_command(name="daily", description="Reclamar tu recompensa diaria de monedas")
    async def daily_slash(self, interaction: nextcord.Interaction):
        """Reclamar recompensa diaria"""
        await self._claim_daily(interaction)
    
    async def _claim_daily(self, ctx_or_interaction):
        """función interna para reclamar daily"""
        try:
            # Determinar si es command o slash command
            if hasattr(ctx_or_interaction, 'response'):
                # Es slash command
                author = ctx_or_interaction.user
                guild = ctx_or_interaction.guild
                send_func = ctx_or_interaction.response.send_message
            else:
                # Es command tradicional
                author = ctx_or_interaction.author
                guild = ctx_or_interaction.guild
                send_func = ctx_or_interaction.send
            
            user_data = self.get_user_data(guild.id, author.id)
            now = datetime.now()
            
            # verificar cooldown
            last_daily = user_data.get('last_daily')
            if last_daily:
                last_daily_dt = datetime.fromisoformat(last_daily)
                if (now - last_daily_dt).days < 1:
                    next_daily = last_daily_dt + timedelta(days=1)
                    remaining = next_daily - now
                    hours, remainder = divmod(remaining.seconds, 3600)
                    minutes, _ = divmod(remainder, 60)
                    
                    error_msg = f"⏰ ya reclamaste tu recompensa diaria. vuelve en {hours}h {minutes}m."
                    await send_func(error_msg)
                    return
            
            # calcular recompensa base
            base_reward = 500
            
            # bonificación por racha
            if last_daily:
                last_daily_dt = datetime.fromisoformat(last_daily)
                if (now - last_daily_dt).days == 1:
                    user_data['daily_streak'] += 1
                else:
                    user_data['daily_streak'] = 1
            else:
                user_data['daily_streak'] = 1
            
            # calcular bonificaciones
            streak_bonus = min(user_data['daily_streak'] * 50, 1000)  # máximo 1000 de bonus
            level_bonus = user_data['level'] * 25
            random_bonus = random.randint(0, 200)
            
            total_reward = base_reward + streak_bonus + level_bonus + random_bonus
            
            # añadir dinero
            self.add_money(guild.id, author.id, total_reward, "daily reward")
            user_data['last_daily'] = now.isoformat()
            
            # embed de recompensa
            embed = nextcord.Embed(
                title="🎁 recompensa diaria reclamada",
                color=nextcord.Color.green()
            )
            
            embed.add_field(name="💰 recompensa base", value=f"€{base_reward}", inline=True)
            embed.add_field(name="🔥 bonus racha", value=f"€{streak_bonus}", inline=True)
            embed.add_field(name="📊 bonus nivel", value=f"€{level_bonus}", inline=True)
            embed.add_field(name="🎲 bonus aleatorio", value=f"€{random_bonus}", inline=True)
            embed.add_field(name="💎 total recibido", value=f"€{total_reward}", inline=True)
            embed.add_field(name="🔥 racha actual", value=f"{user_data['daily_streak']} días", inline=True)
            
            embed.add_field(name="💵 nuevo balance", value=f"€{user_data['balance']:,}", inline=False)
            
            await send_func(embed=embed)
            
        except Exception as e:
            logger.error(f"error en daily: {e}")
            error_msg = "❌ error al reclamar recompensa diaria."
            if hasattr(ctx_or_interaction, 'response'):
                await ctx_or_interaction.response.send_message(error_msg, ephemeral=True)
            else:
                await ctx_or_interaction.send(error_msg)
    
    @commands.command(name='work', aliases=['trabajar'])
    async def work(self, ctx):
        """
        trabajar para ganar dinero
        uso: !work
        """
        try:
            # cooldown de 30 minutos
            cooldown_key = f"{ctx.guild.id}_{ctx.author.id}_work"
            now = datetime.now()
            
            if cooldown_key in self.daily_cooldowns:
                last_work = self.daily_cooldowns[cooldown_key]
                if (now - last_work).seconds < 1800:  # 30 minutos
                    remaining = 1800 - (now - last_work).seconds
                    minutes, seconds = divmod(remaining, 60)
                    await ctx.send(f"😴 estás cansado. descansa {minutes}m {seconds}s más.")
                    return
            
            # trabajos disponibles
            jobs = [
                {"name": "programador", "min": 200, "max": 800, "emoji": "💻"},
                {"name": "chef", "min": 150, "max": 600, "emoji": "👨‍🍳"},
                {"name": "médico", "min": 300, "max": 900, "emoji": "👩‍⚕️"},
                {"name": "profesor", "min": 180, "max": 650, "emoji": "👨‍🏫"},
                {"name": "mecánico", "min": 160, "max": 550, "emoji": "🔧"},
                {"name": "policía", "min": 250, "max": 750, "emoji": "👮"},
                {"name": "bombero", "min": 280, "max": 800, "emoji": "🚒"},
                {"name": "artista", "min": 100, "max": 1000, "emoji": "🎨"},
                {"name": "músico", "min": 120, "max": 900, "emoji": "🎵"},
                {"name": "escritor", "min": 150, "max": 700, "emoji": "✍️"}
            ]
            
            # seleccionar trabajo aleatorio
            job = random.choice(jobs)
            user_data = self.get_user_data(ctx.guild.id, ctx.author.id)
            
            # calcular ganancia (bonificación por nivel)
            base_earning = random.randint(job["min"], job["max"])
            level_multiplier = 1 + (user_data['level'] * 0.1)
            total_earning = int(base_earning * level_multiplier)
            
            # añadir dinero y xp
            self.add_money(ctx.guild.id, ctx.author.id, total_earning, "work")
            level_up, bonus = self.add_xp(ctx.guild.id, ctx.author.id, random.randint(10, 50))
            
            self.daily_cooldowns[cooldown_key] = now
            
            embed = nextcord.Embed(
                title=f"{job['emoji']} trabajo completado",
                description=f"trabajaste como **{job['name']}** y ganaste €{total_earning}!",
                color=nextcord.Color.green()
            )
            
            if level_up:
                embed.add_field(
                    name="🎉 subiste de nivel!",
                    value=f"nivel {user_data['level']} | bonus: €{bonus}",
                    inline=False
                )
            
            embed.add_field(name="💰 nuevo balance", value=f"€{user_data['balance']:,}", inline=True)
            embed.set_footer(text="puedes trabajar cada 30 minutos")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error en work: {e}")
            await ctx.send("❌ error al trabajar.")
    
    @commands.command(name='rob', aliases=['robar'])
    async def rob_user(self, ctx, member: nextcord.Member):
        """
        intentar robar a otro usuario
        uso: !rob @usuario
        """
        try:
            if member == ctx.author:
                await ctx.send("❌ no puedes robarte a ti mismo.")
                return
            
            if member.bot:
                await ctx.send("❌ no puedes robar a un bot.")
                return
            
            # cooldown de 1 hora
            cooldown_key = f"{ctx.guild.id}_{ctx.author.id}_rob"
            now = datetime.now()
            
            if cooldown_key in self.daily_cooldowns:
                last_rob = self.daily_cooldowns[cooldown_key]
                if (now - last_rob).seconds < 3600:  # 1 hora
                    remaining = 3600 - (now - last_rob).seconds
                    minutes, _ = divmod(remaining, 60)
                    await ctx.send(f"🚔 la policía te está vigilando. espera {minutes} minutos más.")
                    return
            
            robber_data = self.get_user_data(ctx.guild.id, ctx.author.id)
            victim_data = self.get_user_data(ctx.guild.id, member.id)
            
            # verificar que ambos tengan dinero
            if robber_data['balance'] < 100:
                await ctx.send("❌ necesitas al menos €100 para intentar robar.")
                return
            
            if victim_data['balance'] < 50:
                await ctx.send(f"❌ {member.display_name} no tiene suficiente dinero para robar.")
                return
            
            # probabilidad de éxito (40%)
            success_chance = 0.4
            
            # bonificación por nivel del ladrón
            robber_bonus = robber_data['level'] * 0.02
            
            # penalización por nivel de la víctima
            victim_defense = victim_data['level'] * 0.01
            
            final_chance = max(0.1, min(0.8, success_chance + robber_bonus - victim_defense))
            
            if random.random() < final_chance:
                # robo exitoso
                max_steal = min(victim_data['balance'] // 4, 1000)  # máximo 25% o 1000
                stolen_amount = random.randint(50, max_steal)
                
                # transferir dinero
                victim_data['balance'] -= stolen_amount
                self.add_money(ctx.guild.id, ctx.author.id, stolen_amount, "robbery")
                
                embed = nextcord.Embed(
                    title="🎭 robo exitoso!",
                    description=f"robaste €{stolen_amount} a {member.display_name}!",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="💰 nuevo balance", value=f"€{robber_data['balance']:,}", inline=True)
                
                # notificar a la víctima por dm
                try:
                    dm_embed = nextcord.Embed(
                        title="😱 has sido robado!",
                        description=f"{ctx.author.display_name} te robó €{stolen_amount} en {ctx.guild.name}",
                        color=nextcord.Color.red()
                    )
                    await member.send(embed=dm_embed)
                except:
                    pass
                
            else:
                # robo fallido
                fine = random.randint(100, 300)
                self.remove_money(ctx.guild.id, ctx.author.id, fine, "failed robbery")
                
                embed = nextcord.Embed(
                    title="🚔 robo fallido!",
                    description=f"la policía te atrapó! multa: €{fine}",
                    color=nextcord.Color.red()
                )
                embed.add_field(name="💸 nuevo balance", value=f"€{robber_data['balance']:,}", inline=True)
            
            self.daily_cooldowns[cooldown_key] = now
            embed.set_footer(text="puedes intentar robar cada hora")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error en rob: {e}")
            await ctx.send("❌ error al intentar robar.")
    
    @commands.command(name='gamble', aliases=['apostar'])
    async def gamble(self, ctx, amount: str):
        """
        apostar dinero en el casino
        uso: !gamble [cantidad/all]
        """
        await self._gamble_money(ctx, amount)
    
    @nextcord.slash_command(name="casino", description="Apostar dinero en juegos de casino")
    async def casino_slash(
        self, 
        interaction: nextcord.Interaction,
        cantidad: str = nextcord.SlashOption(
            description="Cantidad a apostar o 'todo' para apostar todo tu dinero"
        )
    ):
        """Apostar dinero en el casino"""
        await self._gamble_money(interaction, cantidad)
    
    async def _gamble_money(self, ctx_or_interaction, amount):
        """función interna para apostar dinero"""
        try:
            # Determinar si es command o slash command
            if hasattr(ctx_or_interaction, 'response'):
                # Es slash command
                author = ctx_or_interaction.user
                guild = ctx_or_interaction.guild
                send_func = ctx_or_interaction.response.send_message
            else:
                # Es command tradicional
                author = ctx_or_interaction.author
                guild = ctx_or_interaction.guild
                send_func = ctx_or_interaction.send
            
            user_data = self.get_user_data(guild.id, author.id)
            
            # parsear cantidad
            if amount.lower() in ['all', 'todo', 'everything']:
                bet_amount = user_data['balance']
            else:
                try:
                    bet_amount = int(amount)
                except ValueError:
                    await send_func("❌ cantidad inválida. usa un número o 'todo'.")
                    return
            
            # verificaciones
            if bet_amount <= 0:
                await send_func("❌ debes apostar una cantidad positiva.")
                return
            
            if bet_amount > user_data['balance']:
                await send_func("❌ no tienes suficiente dinero.")
                return
            
            if bet_amount < 10:
                await send_func("❌ la apuesta mínima es €10.")
                return
            
            # juegos de casino
            games = [
                {"name": "ruleta", "emoji": "🎰", "win_chance": 0.47, "multiplier": 2.0},
                {"name": "blackjack", "emoji": "🃏", "win_chance": 0.49, "multiplier": 2.0},
                {"name": "dados", "emoji": "🎲", "win_chance": 0.45, "multiplier": 2.2},
                {"name": "slot machine", "emoji": "🎰", "win_chance": 0.35, "multiplier": 3.0},
                {"name": "coin flip", "emoji": "🪙", "win_chance": 0.50, "multiplier": 1.9}
            ]
            
            game = random.choice(games)
            
            # quitar dinero apostado
            self.remove_money(guild.id, author.id, bet_amount, "gambling")
            
            # determinar resultado
            if random.random() < game["win_chance"]:
                # ganó
                winnings = int(bet_amount * game["multiplier"])
                self.add_money(guild.id, author.id, winnings, "gambling win")
                
                embed = nextcord.Embed(
                    title=f"{game['emoji']} ¡ganaste!",
                    description=f"jugaste **{game['name']}** y ganaste €{winnings}!",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="💰 ganancia neta", value=f"+€{winnings - bet_amount:,}", inline=True)
                
            else:
                # perdió
                embed = nextcord.Embed(
                    title=f"{game['emoji']} perdiste...",
                    description=f"jugaste **{game['name']}** y perdiste €{bet_amount}.",
                    color=nextcord.Color.red()
                )
                embed.add_field(name="💸 pérdida", value=f"-€{bet_amount:,}", inline=True)
            
            embed.add_field(name="💵 nuevo balance", value=f"€{user_data['balance']:,}", inline=True)
            embed.set_footer(text="juega responsablemente")
            
            await send_func(embed=embed)
            
        except Exception as e:
            logger.error(f"error en gamble: {e}")
            error_msg = "❌ error en el casino."
            if hasattr(ctx_or_interaction, 'response'):
                await ctx_or_interaction.response.send_message(error_msg, ephemeral=True)
            else:
                await ctx_or_interaction.send(error_msg)
    
    @commands.command(name='duel', aliases=['duelo'])
    async def duel(self, ctx, member: nextcord.Member, amount: int):
        """
        duelo de apuestas contra otro usuario
        uso: !duel @usuario cantidad
        """
        try:
            if member == ctx.author:
                await ctx.send("❌ no puedes retarte a ti mismo.")
                return
            
            if member.bot:
                await ctx.send("❌ no puedes retar a un bot.")
                return
            
            challenger_data = self.get_user_data(ctx.guild.id, ctx.author.id)
            opponent_data = self.get_user_data(ctx.guild.id, member.id)
            
            # verificaciones
            if amount <= 0:
                await ctx.send("❌ la cantidad debe ser positiva.")
                return
            
            if amount < 50:
                await ctx.send("❌ la apuesta mínima para duelos es €50.")
                return
            
            if challenger_data['balance'] < amount:
                await ctx.send("❌ no tienes suficiente dinero.")
                return
            
            if opponent_data['balance'] < amount:
                await ctx.send(f"❌ {member.display_name} no tiene suficiente dinero.")
                return
            
            # crear embed de desafío
            embed = nextcord.Embed(
                title="⚔️ desafío de duelo",
                description=f"{ctx.author.mention} desafía a {member.mention} a un duelo por €{amount}!",
                color=nextcord.Color.orange()
            )
            embed.add_field(name="reglas", value="el ganador se lleva todo\ntienes 60 segundos para aceptar", inline=False)
            embed.set_footer(text="reacciona con ✅ para aceptar o ❌ para rechazar")
            
            duel_msg = await ctx.send(embed=embed)
            await duel_msg.add_reaction("✅")
            await duel_msg.add_reaction("❌")
            
            # esperar respuesta
            def check(reaction, user):
                return user == member and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == duel_msg.id
            
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                
                if str(reaction.emoji) == "❌":
                    embed.description = f"{member.display_name} rechazó el duelo."
                    embed.color = nextcord.Color.red()
                    await duel_msg.edit(embed=embed)
                    return
                
                # duelo aceptado - quitar dinero a ambos
                self.remove_money(ctx.guild.id, ctx.author.id, amount, "duel")
                self.remove_money(ctx.guild.id, member.id, amount, "duel")
                
                # determinar ganador (50/50 base + bonificación por nivel)
                challenger_chance = 0.5 + (challenger_data['level'] * 0.01)
                opponent_chance = 1 - challenger_chance
                
                if random.random() < challenger_chance:
                    winner = ctx.author
                    loser = member
                    winner_data = challenger_data
                else:
                    winner = member
                    loser = ctx.author
                    winner_data = opponent_data
                
                # dar todo el dinero al ganador
                winnings = amount * 2
                self.add_money(ctx.guild.id, winner.id, winnings, "duel win")
                
                # embed de resultado
                embed = nextcord.Embed(
                    title="⚔️ resultado del duelo",
                    description=f"🏆 **{winner.display_name}** ganó el duelo!",
                    color=nextcord.Color.gold()
                )
                embed.add_field(name="💰 premio", value=f"€{winnings:,}", inline=True)
                embed.add_field(name="💵 nuevo balance", value=f"€{winner_data['balance']:,}", inline=True)
                embed.set_footer(text=f"{loser.display_name} perdió €{amount:,}")
                
                await duel_msg.edit(embed=embed)
                
            except asyncio.TimeoutError:
                embed.description = f"{member.display_name} no respondió a tiempo."
                embed.color = nextcord.Color.gray()
                await duel_msg.edit(embed=embed)
                
        except Exception as e:
            logger.error(f"error en duel: {e}")
            await ctx.send("❌ error en el duelo.")
    
    @commands.command(name='leaderboard', aliases=['top', 'lb'])
    async def leaderboard(self, ctx, category: str = "dinero"):
        """
        ver ranking de usuarios
        uso: !leaderboard [dinero/nivel/xp]
        """
        try:
            guild_str = str(ctx.guild.id)
            if guild_str not in self.economy_data:
                await ctx.send("❌ no hay datos de economía en este servidor.")
                return
            
            users_data = []
            for user_id, data in self.economy_data[guild_str].items():
                user = self.bot.get_user(int(user_id))
                if user and not user.bot:
                    total_money = data['balance'] + data.get('bank', 0)
                    users_data.append({
                        'user': user,
                        'money': total_money,
                        'level': data.get('level', 1),
                        'xp': data.get('xp', 0)
                    })
            
            if not users_data:
                await ctx.send("❌ no hay datos suficientes para el ranking.")
                return
            
            # ordenar según categoría
            if category.lower() in ['dinero', 'money', 'cash']:
                users_data.sort(key=lambda x: x['money'], reverse=True)
                title = "💰 ranking de dinero"
                value_key = 'money'
                value_format = lambda x: f"€{x:,}"
            elif category.lower() in ['nivel', 'level']:
                users_data.sort(key=lambda x: x['level'], reverse=True)
                title = "📊 ranking de nivel"
                value_key = 'level'
                value_format = lambda x: f"nivel {x}"
            elif category.lower() in ['xp', 'experiencia']:
                users_data.sort(key=lambda x: x['xp'], reverse=True)
                title = "⭐ ranking de experiencia"
                value_key = 'xp'
                value_format = lambda x: f"{x} xp"
            else:
                await ctx.send("❌ categoría inválida. usa: dinero, nivel o xp")
                return
            
            embed = nextcord.Embed(title=title, color=nextcord.Color.gold())
            
            for i, user_data in enumerate(users_data[:10], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                
                embed.add_field(
                    name=f"{medal} {user_data['user'].display_name}",
                    value=value_format(user_data[value_key]),
                    inline=True
                )
            
            # posición del usuario actual
            user_pos = next((i for i, u in enumerate(users_data, 1) if u['user'] == ctx.author), None)
            if user_pos and user_pos > 10:
                embed.set_footer(text=f"tu posición: #{user_pos}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error en leaderboard: {e}")
            await ctx.send("❌ error al obtener ranking.")
    
    @commands.command(name='pay', aliases=['pagar'])
    async def pay_user(self, ctx, member: nextcord.Member, amount: int):
        """
        pagar dinero a otro usuario
        uso: !pay @usuario cantidad
        """
        try:
            if member == ctx.author:
                await ctx.send("❌ no puedes pagarte a ti mismo.")
                return
            
            if member.bot:
                await ctx.send("❌ no puedes pagar a un bot.")
                return
            
            if amount <= 0:
                await ctx.send("❌ la cantidad debe ser positiva.")
                return
            
            sender_data = self.get_user_data(ctx.guild.id, ctx.author.id)
            
            if sender_data['balance'] < amount:
                await ctx.send("❌ no tienes suficiente dinero.")
                return
            
            # transferir dinero
            self.remove_money(ctx.guild.id, ctx.author.id, amount, "payment")
            self.add_money(ctx.guild.id, member.id, amount, "payment received")
            
            embed = nextcord.Embed(
                title="💸 pago realizado",
                description=f"pagaste €{amount:,} a {member.display_name}",
                color=nextcord.Color.green()
            )
            embed.add_field(name="💰 tu nuevo balance", value=f"€{sender_data['balance']:,}", inline=True)
            
            await ctx.send(embed=embed)
            
            # notificar al receptor
            try:
                dm_embed = nextcord.Embed(
                    title="💰 pago recibido",
                    description=f"recibiste €{amount:,} de {ctx.author.display_name} en {ctx.guild.name}",
                    color=nextcord.Color.green()
                )
                await member.send(embed=dm_embed)
            except:
                pass
            
        except Exception as e:
            logger.error(f"error en pay: {e}")
            await ctx.send("❌ error al realizar el pago.")
    
    @nextcord.slash_command(name="donar", description="💝 Apoya el desarrollo del bot con una donación")
    async def donar(self, interaction: nextcord.Interaction):
        """Comando para mostrar información de donaciones"""
        embed = nextcord.Embed(
            title="💝 ¡Apoya el desarrollo del bot!",
            description="¡Hola! Soy **davito**, el desarrollador de este bot. Si te gusta y quieres apoyar su desarrollo, puedes hacer una donación:",
            color=0x00ff84  # Color verde PayPal
        )
        
        embed.add_field(
            name="💳 PayPal",
            value="[🔗 **Donar por PayPal**](https://www.paypal.com/paypalme/davito03)",
            inline=False
        )
        
        embed.add_field(
            name="🎯 ¿Para qué se usan las donaciones?",
            value="• 🛠️ Desarrollo de nuevas funciones\n• 🔧 Mantenimiento del bot\n• ☁️ Hosting y servidores\n• ⚡ Mejoras de rendimiento",
            inline=False
        )
        
        embed.add_field(
            name="🎁 Beneficios de donar",
            value="• ❤️ Mi eterna gratitud\n• 🏆 Reconocimiento especial\n• 🚀 Acceso prioritario a nuevas funciones\n• 💬 Soporte directo del desarrollador",
            inline=False
        )
        
        embed.set_footer(
            text="¡Cada donación, por pequeña que sea, hace una gran diferencia! ❤️",
            icon_url="https://cdn-icons-png.flaticon.com/512/196/196561.png"  # Icono de corazón
        )
        
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/888/888879.png")  # Icono de donación
        
        # Crear botón para PayPal
        view = DonationView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @commands.command(name='donate', aliases=['donar', 'donation', 'donacion'])
    async def donate_legacy(self, ctx):
        """Comando tradicional para donaciones"""
        embed = nextcord.Embed(
            title="💝 ¡Apoya el desarrollo del bot!",
            description="¡Hola! Soy **davito**, el desarrollador de este bot. Si te gusta y quieres apoyar su desarrollo, puedes hacer una donación:",
            color=0x00ff84  # Color verde PayPal
        )
        
        embed.add_field(
            name="💳 PayPal",
            value="[🔗 **Donar por PayPal**](https://www.paypal.com/paypalme/davito03)",
            inline=False
        )
        
        embed.add_field(
            name="🎯 ¿Para qué se usan las donaciones?",
            value="• 🛠️ Desarrollo de nuevas funciones\n• 🔧 Mantenimiento del bot\n• ☁️ Hosting y servidores\n• ⚡ Mejoras de rendimiento",
            inline=False
        )
        
        embed.add_field(
            name="🎁 Beneficios de donar",
            value="• ❤️ Mi eterna gratitud\n• 🏆 Reconocimiento especial\n• 🚀 Acceso prioritario a nuevas funciones\n• 💬 Soporte directo del desarrollador",
            inline=False
        )
        
        embed.set_footer(
            text="¡Cada donación, por pequeña que sea, hace una gran diferencia! ❤️"
        )
        
        await ctx.send(embed=embed)

class DonationView(nextcord.ui.View):
    """Vista con botón para donaciones"""
    
    def __init__(self):
        super().__init__(timeout=300)
        # Añadir el botón de enlace directamente en el constructor
        self.add_item(nextcord.ui.Button(
            label="💳 Donar por PayPal",
            style=nextcord.ButtonStyle.link,
            url="https://www.paypal.com/paypalme/davito03",
            emoji="💝"
        ))

def setup(bot):
    """Función setup para cargar el cog"""
    return Economy(bot)
