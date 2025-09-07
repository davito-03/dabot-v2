"""
Sistema de Reglas Automáticas para DaBot v2
Gestiona reglas específicas por canal y servidor
"""

import nextcord
from nextcord.ext import commands
import sqlite3
import asyncio
from datetime import datetime, timedelta
import re

class AutoRules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_database()
        
    def init_database(self):
        """Inicializar base de datos para reglas"""
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channel_rules (
                    guild_id INTEGER,
                    channel_id INTEGER,
                    rule_type TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    PRIMARY KEY (guild_id, channel_id, rule_type)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server_rules (
                    guild_id INTEGER PRIMARY KEY,
                    rules_channel_id INTEGER,
                    rules_content TEXT,
                    auto_rules_enabled BOOLEAN DEFAULT 1
                )
            ''')
            conn.commit()

    async def setup_server_rules(self, guild, template_type):
        """Configurar reglas automáticas según el tipo de servidor"""
        rules_templates = {
            "streamer": {
                "title": "📋 REGLAS DEL SERVIDOR - COMUNIDAD STREAMER",
                "rules": [
                    "🎭 **RESPETO Y CONVIVENCIA**",
                    "• Trata a todos con respeto y amabilidad",
                    "• No se permite spam, flood o trolling",
                    "• Prohibido el lenguaje tóxico, insultos o discriminación",
                    "• Respeta las opiniones de otros miembros",
                    "",
                    "🎮 **CONTENIDO Y CHAT**",
                    "• Mantén los temas en sus canales correspondientes",
                    "• No spoilers sin avisar previamente",
                    "• Respeta al streamer y no interrumpas con temas irrelevantes",
                    "• Los links solo en <#links-clips>",
                    "",
                    "🔊 **CANALES DE VOZ**",
                    "• No grites ni hagas ruidos molestos",
                    "• Respeta a quien esté hablando",
                    "• Usa push-to-talk si hay ruido de fondo",
                    "• No reproduzcas música sin permiso",
                    "",
                    "🎨 **CONTENIDO CREATIVO**",
                    "• El fanart va en <#fanart>",
                    "• Respeta los derechos de autor",
                    "• No resubas contenido sin dar créditos",
                    "",
                    "⚠️ **MODERACIÓN**",
                    "• Las decisiones del staff son finales",
                    "• Para apelaciones, usa el sistema de tickets",
                    "• Reporta problemas al staff mediante tickets",
                    "• Las infracciones pueden resultar en warns, timeouts o bans"
                ]
            },
            "gaming": {
                "title": "📋 REGLAS DEL SERVIDOR - GAMING",
                "rules": [
                    "🎮 **GAMING Y RESPETO**",
                    "• Respeto absoluto entre gamers",
                    "• No toxicidad en ningún juego o situación",
                    "• Ayuda a otros jugadores cuando sea posible",
                    "• Celebra las victorias, aprende de las derrotas",
                    "",
                    "🎯 **BUSCAR EQUIPO**",
                    "• Usa los canales LFG específicos para cada género",
                    "• Sé claro sobre tu nivel y disponibilidad",
                    "• Respeta los horarios acordados",
                    "• No abandones equipos sin avisar",
                    "",
                    "💬 **CHAT Y COMUNICACIÓN**",
                    "• Screenshots y clips en <#screenshots>",
                    "• Logros y achievements en <#logros>",
                    "• Links solo en canales permitidos",
                    "• No spam de invitaciones a otros servidores",
                    "",
                    "🔊 **VOZ EN GAMING**",
                    "• Comunicación clara durante partidas",
                    "• No culpes a tus compañeros por derrotas",
                    "• Usa los canales privados para conversaciones largas",
                    "• El canal competitivo es solo para partidas serias",
                    "",
                    "⚠️ **MODERACIÓN**",
                    "• No cheats, hacks o comportamiento desleal",
                    "• Reporta tramposos o tóxicos",
                    "• El staff puede mediar en disputas de equipos",
                    "• Infracciones graves = ban permanente"
                ]
            },
            "desarrollo": {
                "title": "📋 REGLAS DEL SERVIDOR - DESARROLLO",
                "rules": [
                    "💻 **PROFESIONALISMO Y RESPETO**",
                    "• Mantén un ambiente profesional y colaborativo",
                    "• Respeta todos los niveles de experiencia",
                    "• Ayuda a juniors, aprende de seniors",
                    "• No menosprecies tecnologías o lenguajes",
                    "",
                    "🔧 **DESARROLLO Y CÓDIGO**",
                    "• Usa los canales específicos para cada tecnología",
                    "• Formatea tu código con ``` bloques de código",
                    "• Explica el contexto de tu problema",
                    "• Comparte recursos útiles para la comunidad",
                    "",
                    "❓ **AYUDA Y DEBUGGING**",
                    "• Describe claramente tu problema",
                    "• Incluye código relevante y mensajes de error",
                    "• Usa <#code-review> para revisiones",
                    "• Agradece la ayuda recibida",
                    "",
                    "💼 **TRABAJOS Y PROYECTOS**",
                    "• Ofertas laborales en <#trabajos>",
                    "• Sé honesto sobre pagos y condiciones",
                    "• No spam de ofertas",
                    "• Colaboraciones en <#ideas>",
                    "",
                    "⚠️ **MODERACIÓN**",
                    "• No piratería ni contenido ilegal",
                    "• Respeta las licencias de software",
                    "• No ataques personales por preferencias técnicas",
                    "• El conocimiento se comparte, no se monopoliza"
                ]
            },
            "general": {
                "title": "📋 REGLAS DEL SERVIDOR - COMUNIDAD GENERAL",
                "rules": [
                    "🌟 **CONVIVENCIA GENERAL**",
                    "• Trata a todos con respeto y amabilidad",
                    "• Mantén conversaciones amigables y constructivas",
                    "• Acepta y respeta las diferencias de opinión",
                    "• Ayuda a crear un ambiente acogedor",
                    "",
                    "💬 **CHAT Y CONTENIDO**",
                    "• Usa los canales temáticos apropiados",
                    "• Fotos y media en <#fotos-media>",
                    "• Links interesantes en <#links>",
                    "• Comandos del bot en <#bot-zone>",
                    "",
                    "🎭 **ENTRETENIMIENTO**",
                    "• Comparte tus aficiones sin spam",
                    "• Respeta los gustos de otros",
                    "• Participa en eventos y actividades",
                    "• Sugiere ideas para el servidor",
                    "",
                    "🔊 **CANALES DE VOZ**",
                    "• Entra y sal con educación",
                    "• No monopolices la conversación",
                    "• Respeta el tema del canal",
                    "• Música con moderación",
                    "",
                    "⚠️ **MODERACIÓN**",
                    "• No contenido NSFW fuera de canales designados",
                    "• No publicidad sin permiso",
                    "• Reporta problemas al staff",
                    "• Las decisiones del staff son definitivas"
                ]
            }
        }
        
        template = rules_templates.get(template_type, rules_templates["general"])
        
        # Buscar canal de reglas
        rules_channel = None
        for channel in guild.text_channels:
            if "reglas" in channel.name.lower() or "rules" in channel.name.lower():
                rules_channel = channel
                break
        
        if not rules_channel:
            return None
            
        # Crear embed de reglas
        embed = nextcord.Embed(
            title=template["title"],
            description="Por favor, lee y respeta estas reglas para mantener una comunidad sana.",
            color=0x00ff00
        )
        
        # Añadir reglas al embed
        rules_text = "\n".join(template["rules"])
        
        # Dividir en chunks si es muy largo
        if len(rules_text) > 4000:
            chunks = [rules_text[i:i+4000] for i in range(0, len(rules_text), 4000)]
            for i, chunk in enumerate(chunks):
                embed.add_field(
                    name=f"📋 Reglas (Parte {i+1})" if i > 0 else "📋 Reglas del Servidor",
                    value=chunk,
                    inline=False
                )
        else:
            embed.add_field(
                name="📋 Reglas del Servidor",
                value=rules_text,
                inline=False
            )
        
        embed.add_field(
            name="✅ Aceptación",
            value="Al participar en este servidor, aceptas cumplir estas reglas.",
            inline=False
        )
        
        embed.set_footer(
            text=f"Servidor configurado el {datetime.now().strftime('%d/%m/%Y')} • DaBot v2"
        )
        
        # Enviar reglas
        try:
            await rules_channel.purge(limit=10)
            rules_message = await rules_channel.send(embed=embed)
            
            # Guardar en base de datos
            with sqlite3.connect('data/bot_data.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO server_rules 
                    (guild_id, rules_channel_id, rules_content, auto_rules_enabled)
                    VALUES (?, ?, ?, ?)
                ''', (guild.id, rules_channel.id, rules_text, True))
                conn.commit()
            
            return rules_channel
            
        except Exception as e:
            print(f"Error creando reglas: {e}")
            return None

    async def setup_channel_rules(self, guild, template_type):
        """Configurar reglas específicas por canal"""
        channel_rules = {
            "no_links": ["general", "chat-general", "charla-casual", "gaming-general"],
            "media_only": ["fanart", "fotos-media", "screenshots"],
            "links_only": ["links", "links-clips"],
            "no_spam": ["ayuda-general", "debug", "code-review"],
            "voice_quality": ["coding-sessions", "screen-share", "competitivo"]
        }
        
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            
            for channel in guild.text_channels:
                channel_name = channel.name.lower()
                
                # Aplicar regla de no links
                if any(name in channel_name for name in channel_rules["no_links"]):
                    cursor.execute('''
                        INSERT OR REPLACE INTO channel_rules 
                        (guild_id, channel_id, rule_type, enabled)
                        VALUES (?, ?, ?, ?)
                    ''', (guild.id, channel.id, "no_links", True))
                
                # Aplicar regla de solo media
                if any(name in channel_name for name in channel_rules["media_only"]):
                    cursor.execute('''
                        INSERT OR REPLACE INTO channel_rules 
                        (guild_id, channel_id, rule_type, enabled)
                        VALUES (?, ?, ?, ?)
                    ''', (guild.id, channel.id, "media_only", True))
                
                # Aplicar regla de solo links
                if any(name in channel_name for name in channel_rules["links_only"]):
                    cursor.execute('''
                        INSERT OR REPLACE INTO channel_rules 
                        (guild_id, channel_id, rule_type, enabled)
                        VALUES (?, ?, ?, ?)
                    ''', (guild.id, channel.id, "links_only", True))
            
            conn.commit()

    async def check_message_rules(self, message):
        """Verificar reglas en mensajes"""
        if message.author.bot or not message.guild:
            return
            
        # Verificar reglas del canal
        with sqlite3.connect('data/bot_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT rule_type FROM channel_rules 
                WHERE guild_id = ? AND channel_id = ? AND enabled = 1
            ''', (message.guild.id, message.channel.id))
            
            rules = cursor.fetchall()
            
            for rule_tuple in rules:
                rule_type = rule_tuple[0]
                
                if rule_type == "no_links":
                    await self._check_no_links(message)
                elif rule_type == "media_only":
                    await self._check_media_only(message)
                elif rule_type == "links_only":
                    await self._check_links_only(message)

    async def _check_no_links(self, message):
        """Verificar regla de no links"""
        url_pattern = r'https?://[^\s]+'
        if re.search(url_pattern, message.content):
            # Buscar canal de links
            links_channel = None
            for channel in message.guild.text_channels:
                if "links" in channel.name.lower():
                    links_channel = channel
                    break
            
            try:
                await message.delete()
                
                embed = nextcord.Embed(
                    title="🚫 Links no permitidos aquí",
                    description=f"Los links deben ir en {links_channel.mention if links_channel else 'el canal de links'}\n\nTu mensaje fue eliminado para mantener el orden.",
                    color=0xffaa00
                )
                embed.set_footer(text="Esta es una advertencia automática, no un warn oficial.")
                
                await message.author.send(embed=embed)
                
            except:
                pass

    async def _check_media_only(self, message):
        """Verificar regla de solo media"""
        if not message.attachments and not re.search(r'https?://[^\s]+\.(jpg|jpeg|png|gif|webp|mp4|mov)', message.content):
            try:
                await message.delete()
                
                embed = nextcord.Embed(
                    title="📷 Solo contenido multimedia",
                    description="Este canal es solo para fotos, videos y contenido multimedia.\n\nPara chat general, usa otros canales.",
                    color=0xffaa00
                )
                embed.set_footer(text="Esta es una advertencia automática, no un warn oficial.")
                
                await message.author.send(embed=embed)
                
            except:
                pass

    async def _check_links_only(self, message):
        """Verificar regla de solo links"""
        url_pattern = r'https?://[^\s]+'
        if not re.search(url_pattern, message.content):
            try:
                await message.delete()
                
                embed = nextcord.Embed(
                    title="🔗 Solo links permitidos",
                    description="Este canal es específicamente para compartir enlaces.\n\nPara conversaciones, usa el chat general.",
                    color=0xffaa00
                )
                embed.set_footer(text="Esta es una advertencia automática, no un warn oficial.")
                
                await message.author.send(embed=embed)
                
            except:
                pass

def setup(bot):
    bot.add_cog(AutoRules(bot))
