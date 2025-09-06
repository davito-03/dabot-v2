"""
sistema de automod avanzado
por davito
"""

import nextcord
from nextcord.ext import commands, tasks
import json
import re
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = {}
        self.user_warnings = {}
        self.spam_tracker = {}
        self.load_config()
        self.cleanup_spam_tracker.start()
    
    def load_config(self):
        """cargar configuración de automod"""
        try:
            with open('data/automod_config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
            self.save_config()
    
    def save_config(self):
        """guardar configuración"""
        try:
            with open('data/automod_config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando config automod: {e}")
    
    def get_guild_config(self, guild_id):
        """obtener config de un servidor"""
        return self.config.get(str(guild_id), {
            'anti_spam': True,
            'anti_caps': True,
            'anti_links': True,
            'anti_invites': True,
            'anti_mentions': True,
            'max_mentions': 5,
            'max_duplicates': 3,
            'max_caps_percentage': 70,
            'punishment': 'warn',  # warn, mute, kick, ban
            'log_channel': None,
            'immune_roles': [],
            'enabled': True
        })
    
    @tasks.loop(minutes=5)
    async def cleanup_spam_tracker(self):
        """limpiar tracker de spam"""
        current_time = datetime.now()
        to_remove = []
        
        for user_id, data in self.spam_tracker.items():
            if current_time - data['last_message'] > timedelta(minutes=2):
                to_remove.append(user_id)
        
        for user_id in to_remove:
            del self.spam_tracker[user_id]
    
    @nextcord.slash_command(name="automod", description="Configurar sistema de automoderacion")
    @commands.has_permissions(manage_guild=True)
    async def automod_config(self, interaction: nextcord.Interaction):
        """comando principal de automod"""
        embed = nextcord.Embed(
            title="🛡️ Configuración de AutoMod",
            description="Selecciona qué configurar:",
            color=0x3498db
        )
        
        view = AutoModView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """verificar mensajes automáticamente"""
        if not message.guild or message.author.bot:
            return
        
        config = self.get_guild_config(message.guild.id)
        
        if not config['enabled']:
            return
        
        # verificar inmunidad
        if any(role.id in config['immune_roles'] for role in message.author.roles):
            return
        
        violations = []
        
        # anti-spam
        if config['anti_spam']:
            if await self.check_spam(message):
                violations.append("spam")
        
        # anti-caps
        if config['anti_caps']:
            if self.check_excessive_caps(message.content, config['max_caps_percentage']):
                violations.append("mayúsculas excesivas")
        
        # anti-links
        if config['anti_links']:
            if self.check_links(message.content):
                violations.append("enlaces no permitidos")
        
        # anti-invites
        if config['anti_invites']:
            if self.check_discord_invites(message.content):
                violations.append("invitaciones de Discord")
        
        # anti-mentions
        if config['anti_mentions']:
            if len(message.mentions) > config['max_mentions']:
                violations.append(f"demasiadas menciones ({len(message.mentions)})")
        
        if violations:
            await self.handle_violation(message, violations, config)
    
    async def check_spam(self, message):
        """verificar spam"""
        user_id = message.author.id
        current_time = datetime.now()
        
        if user_id not in self.spam_tracker:
            self.spam_tracker[user_id] = {
                'messages': [],
                'last_message': current_time
            }
        
        tracker = self.spam_tracker[user_id]
        tracker['messages'].append({
            'content': message.content,
            'time': current_time
        })
        tracker['last_message'] = current_time
        
        # limpiar mensajes antiguos (últimos 10 segundos)
        tracker['messages'] = [
            msg for msg in tracker['messages']
            if current_time - msg['time'] < timedelta(seconds=10)
        ]
        
        # verificar duplicados
        if len(tracker['messages']) >= 3:
            recent_contents = [msg['content'] for msg in tracker['messages'][-3:]]
            if len(set(recent_contents)) == 1:  # todos iguales
                return True
        
        # verificar velocidad
        if len(tracker['messages']) >= 5:
            return True
        
        return False
    
    def check_excessive_caps(self, content, max_percentage):
        """verificar mayúsculas excesivas"""
        if len(content) < 5:
            return False
        
        letters = sum(1 for c in content if c.isalpha())
        if letters == 0:
            return False
        
        caps = sum(1 for c in content if c.isupper())
        percentage = (caps / letters) * 100
        
        return percentage > max_percentage
    
    def check_links(self, content):
        """verificar enlaces"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return bool(re.search(url_pattern, content))
    
    def check_discord_invites(self, content):
        """verificar invitaciones de discord"""
        invite_pattern = r'(discord\.gg/|discordapp\.com/invite/|discord\.com/invite/)[a-zA-Z0-9]+'
        return bool(re.search(invite_pattern, content))
    
    async def handle_violation(self, message, violations, config):
        """manejar violación de automod"""
        try:
            # eliminar mensaje
            await message.delete()
            
            # aplicar castigo
            punishment = config['punishment']
            
            if punishment == 'warn':
                await self.warn_user(message.author, message.guild, violations)
            elif punishment == 'mute':
                await self.mute_user(message.author, message.guild, violations)
            elif punishment == 'kick':
                await message.author.kick(reason=f"AutoMod: {', '.join(violations)}")
            elif punishment == 'ban':
                await message.author.ban(reason=f"AutoMod: {', '.join(violations)}")
            
            # log
            if config['log_channel']:
                await self.log_violation(message, violations, config)
            
            # notificar al usuario
            try:
                embed = nextcord.Embed(
                    title="⚠️ Mensaje eliminado por AutoMod",
                    description=f"**Violaciones detectadas:**\n• " + "\n• ".join(violations),
                    color=0xe74c3c
                )
                embed.add_field(name="Servidor", value=message.guild.name, inline=True)
                embed.add_field(name="Canal", value=message.channel.mention, inline=True)
                await message.author.send(embed=embed)
            except:
                pass
                
        except Exception as e:
            logger.error(f"error manejando violación automod: {e}")
    
    async def warn_user(self, user, guild, violations):
        """advertir usuario"""
        # implementar sistema de warns aquí
        pass
    
    async def mute_user(self, user, guild, violations):
        """mutear usuario"""
        # buscar rol de mute
        mute_role = nextcord.utils.get(guild.roles, name="Muted")
        if mute_role:
            await user.add_roles(mute_role)
    
    async def log_violation(self, message, violations, config):
        """log de violación"""
        channel = self.bot.get_channel(config['log_channel'])
        if not channel:
            return
        
        embed = nextcord.Embed(
            title="🛡️ AutoMod - Violación detectada",
            color=0xe74c3c,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Usuario", value=f"{message.author} ({message.author.id})", inline=True)
        embed.add_field(name="Canal", value=message.channel.mention, inline=True)
        embed.add_field(name="Violaciones", value="• " + "\n• ".join(violations), inline=False)
        embed.add_field(name="Mensaje original", value=message.content[:1000], inline=False)
        
        await channel.send(embed=embed)

class AutoModView(nextcord.ui.View):
    def __init__(self, automod_cog):
        super().__init__(timeout=300)
        self.automod = automod_cog
    
    @nextcord.ui.button(label="Anti-Spam", emoji="🚫", style=nextcord.ButtonStyle.secondary)
    async def toggle_spam(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = self.automod.get_guild_config(interaction.guild.id)
        config['anti_spam'] = not config.get('anti_spam', True)
        self.automod.config[str(interaction.guild.id)] = config
        self.automod.save_config()
        
        status = "✅ Activado" if config['anti_spam'] else "❌ Desactivado"
        await interaction.response.send_message(f"Anti-Spam: {status}", ephemeral=True)
    
    @nextcord.ui.button(label="Anti-Links", emoji="🔗", style=nextcord.ButtonStyle.secondary)
    async def toggle_links(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = self.automod.get_guild_config(interaction.guild.id)
        config['anti_links'] = not config.get('anti_links', True)
        self.automod.config[str(interaction.guild.id)] = config
        self.automod.save_config()
        
        status = "✅ Activado" if config['anti_links'] else "❌ Desactivado"
        await interaction.response.send_message(f"Anti-Links: {status}", ephemeral=True)
    
    @nextcord.ui.button(label="Anti-Invites", emoji="📧", style=nextcord.ButtonStyle.secondary)
    async def toggle_invites(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        config = self.automod.get_guild_config(interaction.guild.id)
        config['anti_invites'] = not config.get('anti_invites', True)
        self.automod.config[str(interaction.guild.id)] = config
        self.automod.save_config()
        
        status = "✅ Activado" if config['anti_invites'] else "❌ Desactivado"
        await interaction.response.send_message(f"Anti-Invites: {status}", ephemeral=True)

def setup(bot):
    return AutoMod(bot)
