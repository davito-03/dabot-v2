"""
Plantillas de Servidor Mejoradas v2.0
Incluye canales de transcripciones de tickets, verificación anti-bot, VoiceMaster,
sistema de niveles, economía, memes, confesiones, estadísticas y más
Por davito - Dabot v2
"""

import nextcord
from nextcord.ext import commands
import logging

logger = logging.getLogger(__name__)

class NSFWConfirmView(nextcord.ui.View):
    """vista para confirmar creación de canales NSFW"""
    
    def __init__(self, template_method, *args, **kwargs):
        super().__init__(timeout=60)
        self.template_method = template_method
        self.args = args
        self.kwargs = kwargs
        self.nsfw_choice = None
    
    @nextcord.ui.button(label="✅ Sí, incluir NSFW", style=nextcord.ButtonStyle.danger)
    async def include_nsfw(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.kwargs['include_nsfw'] = True
        await interaction.response.defer()
        await self.template_method(*self.args, **self.kwargs)
        self.stop()
    
    @nextcord.ui.button(label="❌ No, omitir NSFW", style=nextcord.ButtonStyle.secondary)
    async def skip_nsfw(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        self.kwargs['include_nsfw'] = False
        await interaction.response.defer()
        await self.template_method(*self.args, **self.kwargs)
        self.stop()

class ServerTemplates(commands.Cog):
    """plantillas mejoradas de servidor"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command(name="template", description="Comandos de plantillas de servidor")
    async def template_group(self, interaction: nextcord.Interaction):
        pass
    
    @template_group.subcommand(name="gaming", description="Plantilla para servidor gaming")
    async def gaming_template(self, interaction: nextcord.Interaction):
        """crear plantilla gaming completa"""
        embed = nextcord.Embed(
            title="🎮 Configurar Servidor Gaming",
            description="¿Quieres incluir canales NSFW en tu servidor?",
            color=nextcord.Color.purple()
        )
        embed.add_field(
            name="⚠️ Contenido NSFW",
            value="Los canales NSFW están restringidos a usuarios mayores de 18 años y deben cumplir con las reglas de Discord.",
            inline=False
        )
        
        view = NSFWConfirmView(self._create_gaming_template, interaction)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @template_group.subcommand(name="community", description="Plantilla para comunidad general")
    async def community_template(self, interaction: nextcord.Interaction):
        """crear plantilla de comunidad"""
        embed = nextcord.Embed(
            title="🌟 Configurar Servidor de Comunidad",
            description="¿Quieres incluir canales NSFW en tu servidor?",
            color=nextcord.Color.purple()
        )
        embed.add_field(
            name="⚠️ Contenido NSFW",
            value="Los canales NSFW están restringidos a usuarios mayores de 18 años.",
            inline=False
        )
        
        view = NSFWConfirmView(self._create_community_template, interaction)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @template_group.subcommand(name="study", description="Plantilla para servidor de estudio")
    async def study_template(self, interaction: nextcord.Interaction):
        """crear plantilla de estudio"""
        # Para servidores de estudio, generalmente no incluimos NSFW
        await self._create_study_template(interaction, include_nsfw=False)
    
    async def _create_gaming_template(self, interaction: nextcord.Interaction, include_nsfw: bool = False):
        """crear plantilla gaming completa con nuevas funciones"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.followup.send("❌ Necesitas permisos de gestionar servidor.", ephemeral=True)
            return
        
        try:
            guild = interaction.guild
            
            # === CANALES DE VERIFICACIÓN ===
            verification_category = await guild.create_category("🛡️ VERIFICACIÓN")
            
            verification_channel = await guild.create_text_channel(
                "🔐-verificacion",
                category=verification_category,
                overwrites={
                    guild.default_role: nextcord.PermissionOverwrite(
                        send_messages=False,
                        add_reactions=False
                    )
                }
            )
            
            # === ESTADÍSTICAS DEL SERVIDOR ===
            stats_category = await guild.create_category("📊 ESTADÍSTICAS")
            
            member_count = len([m for m in guild.members if not m.bot])
            bot_count = len([m for m in guild.members if m.bot])
            total_count = len(guild.members)
            
            member_stats_channel = await guild.create_voice_channel(
                f"👥 Miembros: {member_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={guild.default_role: nextcord.PermissionOverwrite(connect=False)}
            )
            
            total_stats_channel = await guild.create_voice_channel(
                f"📈 Total: {total_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={guild.default_role: nextcord.PermissionOverwrite(connect=False)}
            )
            
            # === CANALES INFORMATIVOS ===
            info_category = await guild.create_category("📋 INFORMACIÓN")
            
            await guild.create_text_channel("📜-reglas", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            await guild.create_text_channel("📢-anuncios", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            await guild.create_text_channel("🎉-eventos", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            levels_channel = await guild.create_text_channel("📈-niveles", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            # === CANALES GENERALES ===
            general_category = await guild.create_category("💬 GENERAL")
            await guild.create_text_channel("💬-general", category=general_category)
            await guild.create_text_channel("🤖-bot-commands", category=general_category)
            
            # Publicaciones temáticas
            publications_channel = await guild.create_text_channel("📝-publicaciones", category=general_category)
            
            # Memes
            memes_channel = await guild.create_text_channel("😂-memes", category=general_category)
            
            # Confesiones
            confessions_channel = await guild.create_text_channel("🤫-confesiones", category=general_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            if include_nsfw:
                await guild.create_text_channel("🔞-nsfw", category=general_category, nsfw=True)
            
            # === ECONOMÍA Y ENTRETENIMIENTO ===
            economy_category = await guild.create_category("💰 ECONOMÍA Y JUEGOS")
            
            await guild.create_text_channel("💼-trabajos", category=economy_category)
            await guild.create_text_channel("🎰-casino", category=economy_category)
            await guild.create_text_channel("🏪-tienda", category=economy_category)
            await guild.create_text_channel("📈-inversiones", category=economy_category)
            await guild.create_text_channel("🎲-juegos", category=economy_category)
            
            # === CANALES GAMING ===
            gaming_category = await guild.create_category("🎮 GAMING")
            await guild.create_text_channel("🎮-gaming-general", category=gaming_category)
            await guild.create_text_channel("🏆-torneos", category=gaming_category)
            await guild.create_text_channel("👥-buscar-equipo", category=gaming_category)
            await guild.create_text_channel("📊-estadisticas-gaming", category=gaming_category)
            await guild.create_text_channel("🎯-competitivo", category=gaming_category)
            
            # === SISTEMA DE TICKETS MEJORADO ===
            tickets_category = await guild.create_category("🎫 SOPORTE")
            
            tickets_channel = await guild.create_text_channel(
                "🎫-crear-ticket",
                category=tickets_category,
                overwrites={
                    guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
                }
            )
            
            # Canal de transcripciones
            transcripts_channel = await guild.create_text_channel(
                "📝-transcripciones",
                category=tickets_category,
                overwrites={
                    guild.default_role: nextcord.PermissionOverwrite(read_messages=False)
                }
            )
            
            # === VOICEMASTER ===
            voice_category = await guild.create_category("🎙️ CANALES TEMPORALES")
            
            create_voice = await guild.create_voice_channel(
                "➕ Crear Canal",
                category=voice_category,
                user_limit=1
            )
            
            voice_controls = await guild.create_text_channel(
                "🎛️-voice-controls",
                category=voice_category,
                overwrites={
                    guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
                }
            )
            
            # === CANALES DE VOZ GAMING ===
            await guild.create_voice_channel("🎮 Gaming General", category=voice_category)
            await guild.create_voice_channel("🎯 Competitivo", category=voice_category)
            await guild.create_voice_channel("😎 Casual", category=voice_category)
            await guild.create_voice_channel("🎊 Party", category=voice_category)
            
            # Canal de escenario
            stage_channel = await guild.create_stage_channel(
                "🎭 Escenario Gaming",
                category=voice_category,
                topic="Eventos y competencias de gaming"
            )
            
            # === CONFIGURACIÓN AUTOMÁTICA DE SISTEMAS ===
            
            # Configurar sistema de tickets
            ticket_cog = self.bot.get_cog("TicketManager")
            if ticket_cog:
                await ticket_cog.setup_tickets(interaction, tickets_channel, transcripts_channel)
            
            # Configurar VoiceMaster
            voicemaster_cog = self.bot.get_cog("VoiceMaster")
            if voicemaster_cog:
                voicemaster_cog.db.set_config(
                    guild.id, 
                    create_voice.id, 
                    voice_category.id, 
                    voice_controls.id
                )
                
                # Enviar panel de control
                embed = nextcord.Embed(
                    title="🎙️ VoiceMaster - Panel de Control",
                    description="Gestiona tu canal de voz temporal con los botones de abajo.",
                    color=nextcord.Color.purple()
                )
                embed.add_field(
                    name="📋 ¿Cómo usar?",
                    value="1. Únete al canal **➕ Crear Canal**\n2. Se creará tu canal personal automáticamente\n3. Usa estos botones para gestionarlo",
                    inline=False
                )
                
                from modules.voicemaster import VoiceControlView
                view = VoiceControlView(voicemaster_cog)
                await voice_controls.send(embed=embed, view=view)
            
            # Configurar verificación
            ticket_cog = self.bot.get_cog("TicketManager")
            if ticket_cog and hasattr(ticket_cog, 'setup_verification'):
                await ticket_cog.setup_verification(verification_channel)
            
            # Configurar sistema de niveles
            levels_cog = self.bot.get_cog("Levels")
            if levels_cog:
                # Configurar canal de niveles
                embed = nextcord.Embed(
                    title="📈 Sistema de Niveles",
                    description="¡Gana experiencia participando en el servidor!",
                    color=nextcord.Color.gold()
                )
                embed.add_field(
                    name="🎯 ¿Cómo funciona?",
                    value="• Ganas XP enviando mensajes\n• Cada nivel te da recompensas\n• Compite en el ranking del servidor\n• Usa `/nivel` para ver tu progreso",
                    inline=False
                )
                await levels_channel.send(embed=embed)
            
            # Configurar confesiones
            confessions_cog = self.bot.get_cog("Confessions")
            if confessions_cog:
                confessions_cog.db.set_config(guild.id, confessions_channel.id)
                
                embed = nextcord.Embed(
                    title="🤫 Sistema de Confesiones Anónimas",
                    description="¡Comparte tus secretos de forma completamente anónima!",
                    color=nextcord.Color.dark_purple()
                )
                embed.add_field(
                    name="📝 ¿Cómo funciona?",
                    value="• Usa `/confesion enviar` para hacer una confesión\n• Se enviará de forma anónima\n• ¡Nadie sabrá que fuiste tú!",
                    inline=False
                )
                
                await confessions_channel.send(embed=embed)
            
            # Configurar memes
            memes_cog = self.bot.get_cog("MemesAndFun")
            if memes_cog:
                embed = nextcord.Embed(
                    title="� Canal de Memes",
                    description="¡Comparte y disfruta de los mejores memes!",
                    color=nextcord.Color.random()
                )
                embed.add_field(
                    name="🎯 Comandos disponibles",
                    value="• `/meme random` - Meme aleatorio\n• `/meme chiste` - Chiste del día\n• `/juegos verdad_o_reto` - Verdad o reto\n• `/amor` - Calculadora de amor",
                    inline=False
                )
                await memes_channel.send(embed=embed)
            
            # Configurar publicaciones
            posts_cog = self.bot.get_cog("MemesAndFun")
            if posts_cog:
                embed = nextcord.Embed(
                    title="📝 Publicaciones Temáticas",
                    description="Crea publicaciones organizadas por temas",
                    color=nextcord.Color.blue()
                )
                embed.add_field(
                    name="📋 Tipos disponibles",
                    value="💬 General • 🎯 Debate • ❓ Pregunta\n🎮 Gaming • 💼 Proyectos • 📺 Recomendaciones\n💡 Ideas • 🎨 Arte",
                    inline=False
                )
                embed.add_field(
                    name="🚀 Uso",
                    value="Usa `/publicacion` para crear una nueva publicación temática",
                    inline=False
                )
                await publications_channel.send(embed=embed)
            
            # Configurar estadísticas
            stats_cog = self.bot.get_cog("ServerStats")
            if stats_cog:
                stats_cog.db.set_config(
                    guild.id,
                    member_stats_channel.id,
                    None,  # bot_count_channel
                    total_stats_channel.id,
                    None,  # invite_channel
                    stage_channel.id
                )
            
            # === CREAR ROLES ===
            try:
                verified_role = await guild.create_role(
                    name="✅ Verificado",
                    color=nextcord.Color.green(),
                    mentionable=False
                )
                
                moderator_role = await guild.create_role(
                    name="🛡️ Moderador",
                    color=nextcord.Color.blue(),
                    permissions=nextcord.Permissions(
                        manage_messages=True,
                        kick_members=True,
                        ban_members=True,
                        manage_channels=True
                    )
                )
                
                admin_role = await guild.create_role(
                    name="👑 Administrador",
                    color=nextcord.Color.red(),
                    permissions=nextcord.Permissions(administrator=True)
                )
                
                # Roles de economía
                rich_role = await guild.create_role(
                    name="💎 Millonario",
                    color=nextcord.Color.gold(),
                    mentionable=False
                )
                
                # Configurar permisos con rol verificado
                for channel in guild.channels:
                    if channel != verification_channel and not isinstance(channel, nextcord.VoiceChannel):
                        try:
                            await channel.set_permissions(
                                guild.default_role,
                                read_messages=False
                            )
                            await channel.set_permissions(
                                verified_role,
                                read_messages=True
                            )
                        except:
                            pass
                
            except Exception as e:
                logger.error(f"Error creando roles: {e}")
            
            # === MENSAJE DE CONFIRMACIÓN ===
            embed = nextcord.Embed(
                title="🎮 Plantilla Gaming Creada",
                description="Servidor configurado con todas las funciones avanzadas de Dabot.",
                color=nextcord.Color.green()
            )
            embed.add_field(
                name="✅ Sistemas Configurados",
                value="• 🛡️ Verificación anti-bot\n• 🎫 Tickets con transcripciones\n• 🎙️ VoiceMaster con controles\n• � Sistema de niveles\n• 💰 Economía completa\n• 🤫 Confesiones anónimas\n• � Memes y entretenimiento\n• 📊 Estadísticas automáticas",
                inline=False
            )
            embed.add_field(
                name="🎯 Características Gaming",
                value="• Canales especializados para gaming\n• Sistema de equipos y torneos\n• Canales de voz organizados\n• Escenario para eventos\n• Estadísticas de gaming",
                inline=False
            )
            
            nsfw_text = " (incluye NSFW)" if include_nsfw else " (sin NSFW)"
            embed.set_footer(text=f"Plantilla gaming completa{nsfw_text}")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Plantilla gaming creada en {guild.name}")
            
        except Exception as e:
            logger.error(f"Error creando plantilla gaming: {e}")
            await interaction.followup.send("❌ Error al crear la plantilla gaming.")
    
    async def _create_community_template(self, interaction: nextcord.Interaction, include_nsfw: bool = False):
        """crear plantilla de comunidad general"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.followup.send("❌ Necesitas permisos de gestionar servidor.", ephemeral=True)
            return
        
        try:
            guild = interaction.guild
            
            # Verificación
            verification_category = await guild.create_category("🛡️ VERIFICACIÓN")
            verification_channel = await guild.create_text_channel(
                "🔐-verificacion",
                category=verification_category,
                overwrites={
                    guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
                }
            )
            
            # Estadísticas
            stats_category = await guild.create_category("📊 ESTADÍSTICAS")
            member_count = len([m for m in guild.members if not m.bot])
            total_count = len(guild.members)
            
            member_stats_channel = await guild.create_voice_channel(
                f"👥 Miembros: {member_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={guild.default_role: nextcord.PermissionOverwrite(connect=False)}
            )
            
            total_stats_channel = await guild.create_voice_channel(
                f"📈 Total: {total_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={guild.default_role: nextcord.PermissionOverwrite(connect=False)}
            )
            
            # Información
            info_category = await guild.create_category("📋 INFORMACIÓN")
            await guild.create_text_channel("📜-reglas", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            await guild.create_text_channel("📢-anuncios", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            levels_channel = await guild.create_text_channel("📈-niveles", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            # Comunidad
            community_category = await guild.create_category("🌟 COMUNIDAD")
            await guild.create_text_channel("💬-chat-general", category=community_category)
            await guild.create_text_channel("🎨-arte-y-creatividad", category=community_category)
            await guild.create_text_channel("📸-fotos", category=community_category)
            await guild.create_text_channel("🤖-bot-commands", category=community_category)
            
            # Publicaciones y entretenimiento
            publications_channel = await guild.create_text_channel("📝-publicaciones", category=community_category)
            memes_channel = await guild.create_text_channel("😂-memes", category=community_category)
            confessions_channel = await guild.create_text_channel("🤫-confesiones", category=community_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            if include_nsfw:
                await guild.create_text_channel("🔞-nsfw", category=community_category, nsfw=True)
            
            # Economía
            economy_category = await guild.create_category("💰 ECONOMÍA")
            await guild.create_text_channel("💼-trabajos", category=economy_category)
            await guild.create_text_channel("🎰-casino", category=economy_category)
            await guild.create_text_channel("🏪-tienda", category=economy_category)
            await guild.create_text_channel("🎲-juegos", category=economy_category)
            
            # Tickets
            tickets_category = await guild.create_category("🎫 SOPORTE")
            tickets_channel = await guild.create_text_channel("🎫-crear-ticket", category=tickets_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            transcripts_channel = await guild.create_text_channel("📝-transcripciones", category=tickets_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False)
            })
            
            # VoiceMaster
            voice_category = await guild.create_category("🎙️ CANALES DE VOZ")
            create_voice = await guild.create_voice_channel("➕ Crear Canal", category=voice_category, user_limit=1)
            voice_controls = await guild.create_text_channel("🎛️-voice-controls", category=voice_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            await guild.create_voice_channel("💬 Chat General", category=voice_category)
            await guild.create_voice_channel("🎵 Música", category=voice_category)
            
            # Escenario
            stage_channel = await guild.create_stage_channel(
                "🎭 Escenario Comunidad",
                category=voice_category,
                topic="Eventos y actividades de la comunidad"
            )
            
            # Configurar sistemas
            await self._configure_all_systems(
                interaction, guild, tickets_channel, transcripts_channel,
                verification_channel, create_voice, voice_category, voice_controls,
                confessions_channel, memes_channel, publications_channel,
                levels_channel, member_stats_channel, total_stats_channel, stage_channel
            )
            
            embed = nextcord.Embed(
                title="🌟 Plantilla Comunidad Creada",
                description="Servidor de comunidad configurado exitosamente con todas las funciones de Dabot.",
                color=nextcord.Color.green()
            )
            embed.add_field(
                name="✅ Sistemas Incluidos",
                value="• Verificación y estadísticas\n• Economía y entretenimiento\n• Memes y confesiones\n• Publicaciones temáticas\n• Sistema de niveles",
                inline=False
            )
            
            nsfw_text = " (incluye NSFW)" if include_nsfw else " (sin NSFW)"
            embed.set_footer(text=f"Plantilla comunidad completa{nsfw_text}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creando plantilla comunidad: {e}")
            await interaction.followup.send("❌ Error al crear la plantilla de comunidad.")
    
    async def _create_study_template(self, interaction: nextcord.Interaction, include_nsfw: bool = False):
        """crear plantilla de estudio"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Necesitas permisos de gestionar servidor.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            
            # Verificación
            verification_category = await guild.create_category("🛡️ VERIFICACIÓN")
            verification_channel = await guild.create_text_channel("🔐-verificacion", category=verification_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            # Estadísticas
            stats_category = await guild.create_category("📊 ESTADÍSTICAS")
            member_count = len([m for m in guild.members if not m.bot])
            total_count = len(guild.members)
            
            member_stats_channel = await guild.create_voice_channel(
                f"👥 Estudiantes: {member_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={guild.default_role: nextcord.PermissionOverwrite(connect=False)}
            )
            
            total_stats_channel = await guild.create_voice_channel(
                f"📈 Total: {total_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={guild.default_role: nextcord.PermissionOverwrite(connect=False)}
            )
            
            # Información académica
            info_category = await guild.create_category("📚 INFORMACIÓN ACADÉMICA")
            await guild.create_text_channel("📜-reglas-del-servidor", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            await guild.create_text_channel("📅-calendario-academico", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            levels_channel = await guild.create_text_channel("📈-niveles", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            # Estudio general
            study_category = await guild.create_category("📖 ESTUDIO GENERAL")
            await guild.create_text_channel("💬-chat-general", category=study_category)
            await guild.create_text_channel("❓-preguntas-y-dudas", category=study_category)
            await guild.create_text_channel("📚-recursos-de-estudio", category=study_category)
            await guild.create_text_channel("🤝-grupos-de-estudio", category=study_category)
            await guild.create_text_channel("🤖-bot-commands", category=study_category)
            
            # Entretenimiento educativo
            publications_channel = await guild.create_text_channel("📝-publicaciones", category=study_category)
            confessions_channel = await guild.create_text_channel("🤫-confesiones", category=study_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            # Materias específicas
            subjects_category = await guild.create_category("📝 MATERIAS ESPECÍFICAS")
            await guild.create_text_channel("🔢-matematicas", category=subjects_category)
            await guild.create_text_channel("🧪-ciencias", category=subjects_category)
            await guild.create_text_channel("🌍-historia-geografia", category=subjects_category)
            await guild.create_text_channel("📖-lengua-literatura", category=subjects_category)
            await guild.create_text_channel("💻-informatica", category=subjects_category)
            await guild.create_text_channel("🎨-arte-y-creatividad", category=subjects_category)
            
            # Sistema de economía educativa
            economy_category = await guild.create_category("🎓 SISTEMA EDUCATIVO")
            await guild.create_text_channel("🏆-logros-academicos", category=economy_category)
            await guild.create_text_channel("💎-puntos-de-estudio", category=economy_category)
            await guild.create_text_channel("🏪-tienda-educativa", category=economy_category)
            
            # Tickets de apoyo académico
            tickets_category = await guild.create_category("🎫 APOYO ACADÉMICO")
            tickets_channel = await guild.create_text_channel("🎫-solicitar-ayuda", category=tickets_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            transcripts_channel = await guild.create_text_channel("📝-registros-de-ayuda", category=tickets_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False)
            })
            
            # Salas de estudio virtuales
            voice_category = await guild.create_category("🎙️ SALAS DE ESTUDIO")
            create_voice = await guild.create_voice_channel("➕ Crear Sala de Estudio", category=voice_category, user_limit=1)
            voice_controls = await guild.create_text_channel("🎛️-control-de-salas", category=voice_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            await guild.create_voice_channel("📚 Sala de Estudio Silenciosa", category=voice_category)
            await guild.create_voice_channel("💭 Discusión Académica", category=voice_category)
            await guild.create_voice_channel("🤝 Trabajo en Grupo", category=voice_category)
            
            # Escenario para presentaciones
            stage_channel = await guild.create_stage_channel(
                "🎓 Aula Magna",
                category=voice_category,
                topic="Presentaciones y conferencias académicas"
            )
            
            # Configurar sistemas
            await self._configure_all_systems(
                interaction, guild, tickets_channel, transcripts_channel,
                verification_channel, create_voice, voice_category, voice_controls,
                confessions_channel, None, publications_channel,  # Sin memes en servidor de estudio
                levels_channel, member_stats_channel, total_stats_channel, stage_channel
            )
            
            embed = nextcord.Embed(
                title="📚 Plantilla de Estudio Creada",
                description="Servidor académico configurado para el aprendizaje colaborativo con Dabot.",
                color=nextcord.Color.green()
            )
            embed.add_field(
                name="✅ Características Académicas",
                value="• 📚 Canales organizados por materias\n• 🎫 Sistema de apoyo académico\n• 🎙️ Salas de estudio virtuales\n• 📝 Registros de ayuda\n• 🛡️ Verificación estudiantil\n• 🎓 Sistema de puntos educativos",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creando plantilla de estudio: {e}")
            await interaction.followup.send("❌ Error al crear la plantilla de estudio.")
    
    async def _configure_all_systems(self, interaction, guild, tickets_channel, transcripts_channel,
                                   verification_channel, create_voice, voice_category, voice_controls,
                                   confessions_channel, memes_channel, publications_channel,
                                   levels_channel, member_stats_channel, total_stats_channel, stage_channel):
        """configurar todos los sistemas automáticamente"""
        try:
            # Configurar sistema de tickets
            ticket_cog = self.bot.get_cog("TicketManager")
            if ticket_cog:
                await ticket_cog.setup_tickets(interaction, tickets_channel, transcripts_channel)
            
            # Configurar VoiceMaster
            voicemaster_cog = self.bot.get_cog("VoiceMaster")
            if voicemaster_cog:
                voicemaster_cog.db.set_config(guild.id, create_voice.id, voice_category.id, voice_controls.id)
                
                embed = nextcord.Embed(
                    title="🎙️ VoiceMaster - Panel de Control",
                    description="Gestiona tu canal de voz temporal con los botones de abajo.",
                    color=nextcord.Color.purple()
                )
                embed.add_field(
                    name="📋 ¿Cómo usar?",
                    value="1. Únete al canal **➕ Crear Canal**\n2. Se creará tu canal personal automáticamente\n3. Usa estos botones para gestionarlo",
                    inline=False
                )
                
                from modules.voicemaster import VoiceControlView
                view = VoiceControlView(voicemaster_cog)
                await voice_controls.send(embed=embed, view=view)
            
            # Configurar verificación
            ticket_cog = self.bot.get_cog("TicketManager")
            if ticket_cog and hasattr(ticket_cog, 'setup_verification'):
                await ticket_cog.setup_verification(verification_channel)
            
            # Configurar sistema de niveles
            if levels_channel:
                embed = nextcord.Embed(
                    title="📈 Sistema de Niveles",
                    description="¡Gana experiencia participando en el servidor!",
                    color=nextcord.Color.gold()
                )
                embed.add_field(
                    name="🎯 ¿Cómo funciona?",
                    value="• Ganas XP enviando mensajes\n• Cada nivel te da recompensas\n• Compite en el ranking del servidor\n• Usa `/nivel` para ver tu progreso",
                    inline=False
                )
                await levels_channel.send(embed=embed)
            
            # Configurar confesiones
            confessions_cog = self.bot.get_cog("Confessions")
            if confessions_cog and confessions_channel:
                confessions_cog.db.set_config(guild.id, confessions_channel.id)
                
                embed = nextcord.Embed(
                    title="🤫 Sistema de Confesiones Anónimas",
                    description="¡Comparte tus secretos de forma completamente anónima!",
                    color=nextcord.Color.dark_purple()
                )
                embed.add_field(
                    name="📝 ¿Cómo funciona?",
                    value="• Usa `/confesion enviar` para hacer una confesión\n• Se enviará de forma anónima\n• ¡Nadie sabrá que fuiste tú!",
                    inline=False
                )
                await confessions_channel.send(embed=embed)
            
            # Configurar memes (si existe el canal)
            if memes_channel:
                embed = nextcord.Embed(
                    title="😂 Canal de Memes",
                    description="¡Comparte y disfruta de los mejores memes!",
                    color=nextcord.Color.random()
                )
                embed.add_field(
                    name="🎯 Comandos disponibles",
                    value="• `/meme random` - Meme aleatorio\n• `/meme chiste` - Chiste del día\n• `/juegos verdad_o_reto` - Verdad o reto\n• `/amor` - Calculadora de amor",
                    inline=False
                )
                await memes_channel.send(embed=embed)
            
            # Configurar publicaciones
            if publications_channel:
                embed = nextcord.Embed(
                    title="📝 Publicaciones Temáticas",
                    description="Crea publicaciones organizadas por temas",
                    color=nextcord.Color.blue()
                )
                embed.add_field(
                    name="📋 Tipos disponibles",
                    value="💬 General • 🎯 Debate • ❓ Pregunta\n🎮 Gaming • � Proyectos • 📺 Recomendaciones\n💡 Ideas • 🎨 Arte",
                    inline=False
                )
                embed.add_field(
                    name="🚀 Uso",
                    value="Usa `/publicacion` para crear una nueva publicación temática",
                    inline=False
                )
                await publications_channel.send(embed=embed)
            
            # Configurar estadísticas
            stats_cog = self.bot.get_cog("ServerStats")
            if stats_cog:
                stats_cog.db.set_config(
                    guild.id,
                    member_stats_channel.id,
                    None,  # bot_count_channel
                    total_stats_channel.id,
                    None,  # invite_channel
                    stage_channel.id
                )
            
            # Crear roles básicos
            verified_role = await guild.create_role(
                name="✅ Verificado",
                color=nextcord.Color.green(),
                mentionable=False
            )
            
            # Configurar permisos básicos
            for channel in guild.channels:
                if channel != verification_channel and not isinstance(channel, nextcord.VoiceChannel):
                    try:
                        await channel.set_permissions(guild.default_role, read_messages=False)
                        await channel.set_permissions(verified_role, read_messages=True)
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Error configurando sistemas: {e}")
    
    async def _create_business_template(self, interaction: nextcord.Interaction, include_nsfw: bool = False):
        """crear plantilla de negocios/empresa"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.followup.send("❌ Necesitas permisos de gestionar servidor.", ephemeral=True)
            return
        
        try:
            guild = interaction.guild
            
            # Verificación
            verification_category = await guild.create_category("🛡️ ACCESO")
            verification_channel = await guild.create_text_channel("🔐-verificacion-empleados", category=verification_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            # Estadísticas
            stats_category = await guild.create_category("📊 ESTADÍSTICAS")
            member_count = len([m for m in guild.members if not m.bot])
            total_count = len(guild.members)
            
            member_stats_channel = await guild.create_voice_channel(
                f"👥 Empleados: {member_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={guild.default_role: nextcord.PermissionOverwrite(connect=False)}
            )
            
            total_stats_channel = await guild.create_voice_channel(
                f"📈 Total: {total_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={guild.default_role: nextcord.PermissionOverwrite(connect=False)}
            )
            
            # Información corporativa
            info_category = await guild.create_category("🏢 INFORMACIÓN CORPORATIVA")
            await guild.create_text_channel("📋-politicas-empresa", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            await guild.create_text_channel("📢-anuncios-corporativos", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            levels_channel = await guild.create_text_channel("📈-niveles", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            # Comunicación general
            communication_category = await guild.create_category("💼 COMUNICACIÓN GENERAL")
            await guild.create_text_channel("💬-chat-general", category=communication_category)
            await guild.create_text_channel("☕-break-room", category=communication_category)
            await guild.create_text_channel("🤖-bot-commands", category=communication_category)
            
            publications_channel = await guild.create_text_channel("📝-publicaciones", category=communication_category)
            confessions_channel = await guild.create_text_channel("💭-buzón-sugerencias", category=communication_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            # Departamentos
            departments_category = await guild.create_category("🏢 DEPARTAMENTOS")
            await guild.create_text_channel("💰-finanzas", category=departments_category)
            await guild.create_text_channel("👥-recursos-humanos", category=departments_category)
            await guild.create_text_channel("📈-marketing-ventas", category=departments_category)
            await guild.create_text_channel("🔧-it-soporte", category=departments_category)
            await guild.create_text_channel("📋-administracion", category=departments_category)
            
            # Sistema de incentivos (economía empresarial)
            economy_category = await guild.create_category("🏆 INCENTIVOS EMPRESARIALES")
            await guild.create_text_channel("💎-bonificaciones", category=economy_category)
            await guild.create_text_channel("🎯-objetivos", category=economy_category)
            await guild.create_text_channel("🏪-beneficios", category=economy_category)
            
            # Soporte técnico/HR
            tickets_category = await guild.create_category("🎫 SOPORTE EMPRESARIAL")
            tickets_channel = await guild.create_text_channel("🎫-soporte-tecnico", category=tickets_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            transcripts_channel = await guild.create_text_channel("📝-registros-soporte", category=tickets_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False)
            })
            
            # Salas de reuniones
            voice_category = await guild.create_category("🎙️ SALAS DE REUNIONES")
            create_voice = await guild.create_voice_channel("➕ Crear Sala Privada", category=voice_category, user_limit=1)
            voice_controls = await guild.create_text_channel("🎛️-control-salas", category=voice_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            await guild.create_voice_channel("🏢 Sala Ejecutiva", category=voice_category)
            await guild.create_voice_channel("💼 Reunión Departamental", category=voice_category)
            await guild.create_voice_channel("☕ Sala Informal", category=voice_category)
            
            # Auditorium para presentaciones
            stage_channel = await guild.create_stage_channel(
                "🎭 Auditorio Corporativo",
                category=voice_category,
                topic="Presentaciones empresariales y eventos corporativos"
            )
            
            # Configurar sistemas
            await self._configure_all_systems(
                interaction, guild, tickets_channel, transcripts_channel,
                verification_channel, create_voice, voice_category, voice_controls,
                confessions_channel, None, publications_channel,  # Sin memes en entorno empresarial
                levels_channel, member_stats_channel, total_stats_channel, stage_channel
            )
            
            embed = nextcord.Embed(
                title="🏢 Plantilla Empresarial Creada",
                description="Servidor corporativo configurado para entorno empresarial profesional.",
                color=nextcord.Color.blue()
            )
            embed.add_field(
                name="✅ Características Empresariales",
                value="• 🏢 Organización por departamentos\n• 🎫 Soporte técnico especializado\n• 🎙️ Salas de reuniones privadas\n• 💼 Sistema de incentivos\n• 📊 Estadísticas corporativas",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creando plantilla empresarial: {e}")
            await interaction.followup.send("❌ Error al crear la plantilla empresarial.")
    
    async def _create_tech_template(self, interaction: nextcord.Interaction, include_nsfw: bool = False):
        """crear plantilla de tecnología/programación"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.followup.send("❌ Necesitas permisos de gestionar servidor.", ephemeral=True)
            return
        
        try:
            guild = interaction.guild
            
            # Verificación
            verification_category = await guild.create_category("🛡️ VERIFICACIÓN")
            verification_channel = await guild.create_text_channel("🔐-verificacion-dev", category=verification_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            # Estadísticas
            stats_category = await guild.create_category("📊 ESTADÍSTICAS")
            member_count = len([m for m in guild.members if not m.bot])
            total_count = len(guild.members)
            
            member_stats_channel = await guild.create_voice_channel(
                f"👨‍💻 Developers: {member_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={guild.default_role: nextcord.PermissionOverwrite(connect=False)}
            )
            
            total_stats_channel = await guild.create_voice_channel(
                f"📈 Total: {total_count:,}",
                category=stats_category,
                user_limit=0,
                overwrites={guild.default_role: nextcord.PermissionOverwrite(connect=False)}
            )
            
            # Información del servidor
            info_category = await guild.create_category("📋 INFORMACIÓN")
            await guild.create_text_channel("📜-reglas-del-server", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            await guild.create_text_channel("📢-anuncios-tech", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            levels_channel = await guild.create_text_channel("📈-niveles", category=info_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            # Desarrollo general
            dev_category = await guild.create_category("💻 DESARROLLO GENERAL")
            await guild.create_text_channel("💬-chat-general", category=dev_category)
            await guild.create_text_channel("❓-preguntas-y-ayuda", category=dev_category)
            await guild.create_text_channel("💡-ideas-y-proyectos", category=dev_category)
            await guild.create_text_channel("🔗-recursos-utiles", category=dev_category)
            await guild.create_text_channel("🤖-bot-commands", category=dev_category)
            
            publications_channel = await guild.create_text_channel("📝-publicaciones", category=dev_category)
            memes_channel = await guild.create_text_channel("😂-memes-programacion", category=dev_category)
            confessions_channel = await guild.create_text_channel("🤫-confesiones-dev", category=dev_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            
            if include_nsfw:
                await guild.create_text_channel("🔞-nsfw", category=dev_category, nsfw=True)
            
            # Lenguajes de programación
            languages_category = await guild.create_category("🌐 LENGUAJES DE PROGRAMACIÓN")
            await guild.create_text_channel("🐍-python", category=languages_category)
            await guild.create_text_channel("☕-javascript-nodejs", category=languages_category)
            await guild.create_text_channel("🔷-typescript", category=languages_category)
            await guild.create_text_channel("☕-java", category=languages_category)
            await guild.create_text_channel("🔵-c-sharp", category=languages_category)
            await guild.create_text_channel("⚙️-c-cpp", category=languages_category)
            await guild.create_text_channel("🦀-rust", category=languages_category)
            await guild.create_text_channel("🐹-go", category=languages_category)
            
            # Tecnologías y frameworks
            tech_category = await guild.create_category("🚀 TECNOLOGÍAS & FRAMEWORKS")
            await guild.create_text_channel("⚛️-react-angular-vue", category=tech_category)
            await guild.create_text_channel("🗄️-bases-de-datos", category=tech_category)
            await guild.create_text_channel("☁️-cloud-aws-azure", category=tech_category)
            await guild.create_text_channel("🐳-docker-kubernetes", category=tech_category)
            await guild.create_text_channel("🌐-web-development", category=tech_category)
            await guild.create_text_channel("📱-mobile-dev", category=tech_category)
            
            # Sistema de reputación tech
            economy_category = await guild.create_category("🏆 REPUTACIÓN TECH")
            await guild.create_text_channel("⭐-contribuciones", category=economy_category)
            await guild.create_text_channel("🏅-logros-tech", category=economy_category)
            await guild.create_text_channel("🎯-challenges", category=economy_category)
            
            # Soporte técnico
            tickets_category = await guild.create_category("🎫 SOPORTE TÉCNICO")
            tickets_channel = await guild.create_text_channel("🎫-ayuda-tecnica", category=tickets_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            transcripts_channel = await guild.create_text_channel("📝-logs-soporte", category=tickets_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False)
            })
            
            # Salas de code review y pair programming
            voice_category = await guild.create_category("🎙️ SALAS DE DESARROLLO")
            create_voice = await guild.create_voice_channel("➕ Crear Sala Dev", category=voice_category, user_limit=1)
            voice_controls = await guild.create_text_channel("🎛️-control-salas", category=voice_category, overwrites={
                guild.default_role: nextcord.PermissionOverwrite(send_messages=False)
            })
            await guild.create_voice_channel("👥 Pair Programming", category=voice_category)
            await guild.create_voice_channel("🔍 Code Review", category=voice_category)
            await guild.create_voice_channel("☕ Coffee & Code", category=voice_category)
            
            # Escenario para presentaciones tech
            stage_channel = await guild.create_stage_channel(
                "🎭 Tech Talks",
                category=voice_category,
                topic="Presentaciones técnicas y conferencias de desarrollo"
            )
            
            # Configurar sistemas
            await self._configure_all_systems(
                interaction, guild, tickets_channel, transcripts_channel,
                verification_channel, create_voice, voice_category, voice_controls,
                confessions_channel, memes_channel, publications_channel,
                levels_channel, member_stats_channel, total_stats_channel, stage_channel
            )
            
            embed = nextcord.Embed(
                title="💻 Plantilla Tech/Programación Creada",
                description="Servidor técnico configurado para desarrolladores con Dabot.",
                color=nextcord.Color.purple()
            )
            embed.add_field(
                name="✅ Características Técnicas",
                value="• 🌐 Canales por lenguajes de programación\n• 🚀 Secciones de tecnologías y frameworks\n• 🎙️ Salas para pair programming\n• 🏆 Sistema de reputación técnica\n• 📝 Soporte especializado",
                inline=False
            )
            
            nsfw_text = " (incluye NSFW)" if include_nsfw else " (sin NSFW)"
            embed.set_footer(text=f"Plantilla técnica completa{nsfw_text}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creando plantilla tech: {e}")
            await interaction.followup.send("❌ Error al crear la plantilla tech.")

def setup(bot):
    """cargar el cog"""
    bot.add_cog(ServerTemplates(bot))
