"""
Módulo de Tareas Programadas para el bot de Discord
Incluye comandos para configurar mensajes diarios automáticos
"""

import os
import logging
from datetime import time
import nextcord
from nextcord.ext import commands, tasks

logger = logging.getLogger(__name__)

class ScheduledTasks(commands.Cog):
    """Clase para tareas programadas y automatizadas"""
    
    def __init__(self, bot):
        self.bot = bot
        self.daily_channels = {}  # Diccionario de canales diarios por servidor
        
    def cog_unload(self):
        """Detener tareas al descargar el módulo"""
        if hasattr(self, 'daily_message_task'):
            self.daily_message_task.cancel()
    
    @commands.command(name='setdaily')
    @commands.has_permissions(administrator=True)
    async def set_daily_channel(self, ctx, channel: nextcord.TextChannel = None):
        """
        Configura el canal para mensajes diarios automáticos
        Uso: !setdaily #canal
        """
        try:
            if channel is None:
                channel = ctx.channel
            
            # Verificar permisos del bot en el canal
            permissions = channel.permissions_for(ctx.guild.me)
            if not permissions.send_messages:
                await ctx.send(f"❌ No tengo permisos para enviar mensajes en {channel.mention}")
                return
            
            # Guardar configuración
            self.daily_channels[ctx.guild.id] = channel.id
            
            # Crear embed de confirmación
            embed = nextcord.Embed(
                title="✅ Canal Diario Configurado",
                description=f"Los mensajes diarios se enviarán a {channel.mention} todos los días a las 8:00 AM.",
                color=nextcord.Color.green()
            )
            embed.add_field(name="Configurado por", value=ctx.author.mention, inline=True)
            embed.add_field(name="Hora", value="8:00 AM (hora del servidor)", inline=True)
            
            await ctx.send(embed=embed)
            
            # Iniciar tarea diaria si no está activa
            if not hasattr(self, 'daily_message_task') or self.daily_message_task.is_being_cancelled():
                self.daily_message_task = self.daily_message.start()
                logger.info(f"Tarea diaria iniciada para el servidor {ctx.guild.name}")
            
            logger.info(f"Canal diario configurado en {ctx.guild.name}: {channel.name}")
            
        except Exception as e:
            logger.error(f"Error configurando canal diario: {e}")
            await ctx.send("❌ Error al configurar el canal diario.")
    
    @nextcord.slash_command(name="setdaily", description="Configura el canal para mensajes diarios automáticos")
    async def slash_set_daily(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(description="Canal donde enviar los mensajes diarios", required=False)
    ):
        """Comando slash para configurar canal diario"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return
        
        ctx = await commands.Context.from_interaction(interaction)
        await self.set_daily_channel(ctx, channel)
    
    @commands.command(name='removedaily')
    @commands.has_permissions(administrator=True)
    async def remove_daily_channel(self, ctx):
        """
        Desactiva los mensajes diarios automáticos
        Uso: !removedaily
        """
        try:
            if ctx.guild.id in self.daily_channels:
                del self.daily_channels[ctx.guild.id]
                
                embed = nextcord.Embed(
                    title="✅ Mensajes Diarios Desactivados",
                    description="Los mensajes diarios automáticos han sido desactivados para este servidor.",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="Desactivado por", value=ctx.author.mention, inline=True)
                
                await ctx.send(embed=embed)
                logger.info(f"Mensajes diarios desactivados en {ctx.guild.name}")
            else:
                await ctx.send("❌ No hay mensajes diarios configurados en este servidor.")
                
        except Exception as e:
            logger.error(f"Error desactivando mensajes diarios: {e}")
            await ctx.send("❌ Error al desactivar los mensajes diarios.")
    
    @nextcord.slash_command(name="removedaily", description="Desactiva los mensajes diarios automáticos")
    async def slash_remove_daily(self, interaction: nextcord.Interaction):
        """Comando slash para desactivar mensajes diarios"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return
        
        ctx = await commands.Context.from_interaction(interaction)
        await self.remove_daily_channel(ctx)
    
    @commands.command(name='dailystatus')
    async def daily_status(self, ctx):
        """
        Muestra el estado de los mensajes diarios
        Uso: !dailystatus
        """
        try:
            if ctx.guild.id in self.daily_channels:
                channel_id = self.daily_channels[ctx.guild.id]
                channel = self.bot.get_channel(channel_id)
                
                if channel:
                    embed = nextcord.Embed(
                        title="📅 Estado de Mensajes Diarios",
                        description="Los mensajes diarios están **activados**",
                        color=nextcord.Color.green()
                    )
                    embed.add_field(name="Canal", value=channel.mention, inline=True)
                    embed.add_field(name="Hora", value="8:00 AM", inline=True)
                    embed.add_field(name="Estado", value="✅ Activo", inline=True)
                else:
                    embed = nextcord.Embed(
                        title="📅 Estado de Mensajes Diarios",
                        description="❌ El canal configurado no existe o no es accesible",
                        color=nextcord.Color.red()
                    )
            else:
                embed = nextcord.Embed(
                    title="📅 Estado de Mensajes Diarios",
                    description="Los mensajes diarios están **desactivados**",
                    color=nextcord.Color.orange()
                )
                embed.add_field(name="Configurar", value="Usa `!setdaily #canal` para activar", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error verificando estado diario: {e}")
            await ctx.send("❌ Error al verificar el estado de los mensajes diarios.")
    
    @nextcord.slash_command(name="dailystatus", description="Muestra el estado de los mensajes diarios")
    async def slash_daily_status(self, interaction: nextcord.Interaction):
        """Comando slash para mostrar estado de mensajes diarios"""
        ctx = await commands.Context.from_interaction(interaction)
        await self.daily_status(ctx)
    
    @tasks.loop(time=time(8, 0))  # 8:00 AM
    async def daily_message(self):
        """Envía mensajes diarios a los canales configurados"""
        try:
            for guild_id, channel_id in self.daily_channels.items():
                try:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        # Lista de mensajes motivacionales
                        messages = [
                            "¡Buenos días! 🌅 ¡Que tengas un día increíble!",
                            "¡Nuevo día, nuevas oportunidades! 🌟 ¡A darle con todo!",
                            "☀️ ¡Buenos días! Recuerda que eres increíble.",
                            "🌈 ¡Que este día esté lleno de sonrisas y buenas vibras!",
                            "💪 ¡Buenos días, campeón! ¡Hoy vas a lograr cosas grandiosas!",
                            "🌺 ¡Un nuevo amanecer, una nueva oportunidad de brillar!",
                            "⭐ ¡Buenos días! Recuerda que cada día es una nueva aventura.",
                            "🦋 ¡Que tengas un día tan hermoso como tu sonrisa!",
                            "🌞 ¡Buenos días! El mundo es mejor contigo en él.",
                            "🎯 ¡Nuevo día, nuevas metas! ¡Tú puedes con todo!"
                        ]
                        
                        import random
                        daily_message = random.choice(messages)
                        
                        embed = nextcord.Embed(
                            title="🌅 ¡Mensaje Diario!",
                            description=daily_message,
                            color=nextcord.Color.gold()
                        )
                        
                        # Agregar imagen aleatoria de buen día
                        images = [
                            "https://media.giphy.com/media/l0HlBO7eyXzSZkJri/giphy.gif",
                            "https://media.giphy.com/media/3oz8xLlw6GHVfokaNW/giphy.gif",
                            "https://media.giphy.com/media/5Zesu5VPNGJlm/giphy.gif"
                        ]
                        
                        embed.set_image(url=random.choice(images))
                        embed.set_footer(text="🤖 Mensaje automático diario")
                        
                        await channel.send(embed=embed)
                        logger.info(f"Mensaje diario enviado a {channel.name} en {channel.guild.name}")
                        
                except Exception as e:
                    logger.error(f"Error enviando mensaje diario al canal {channel_id}: {e}")
                    # Remover canal si no es accesible
                    if guild_id in self.daily_channels:
                        del self.daily_channels[guild_id]
                        
        except Exception as e:
            logger.error(f"Error en tarea de mensaje diario: {e}")
    
    @daily_message.before_loop
    async def before_daily_message(self):
        """Esperar a que el bot esté listo antes de iniciar la tarea"""
        await self.bot.wait_until_ready()
    
    @commands.command(name='testdaily')
    @commands.has_permissions(administrator=True)
    async def test_daily_message(self, ctx):
        """
        Envía un mensaje diario de prueba
        Uso: !testdaily
        """
        try:
            if ctx.guild.id not in self.daily_channels:
                await ctx.send("❌ No hay canal diario configurado. Usa `!setdaily #canal` primero.")
                return
            
            channel_id = self.daily_channels[ctx.guild.id]
            channel = self.bot.get_channel(channel_id)
            
            if not channel:
                await ctx.send("❌ El canal configurado no existe o no es accesible.")
                return
            
            # Enviar mensaje de prueba
            embed = nextcord.Embed(
                title="🧪 Mensaje Diario de Prueba",
                description="¡Este es un mensaje de prueba para verificar que todo funciona correctamente!",
                color=nextcord.Color.blue()
            )
            embed.add_field(name="Solicitado por", value=ctx.author.mention, inline=True)
            embed.set_footer(text="🤖 Mensaje de prueba")
            
            await channel.send(embed=embed)
            await ctx.send(f"✅ Mensaje de prueba enviado a {channel.mention}")
            
        except Exception as e:
            logger.error(f"Error en mensaje diario de prueba: {e}")
            await ctx.send("❌ Error al enviar el mensaje de prueba.")
    
    @nextcord.slash_command(name="testdaily", description="Envía un mensaje diario de prueba")
    async def slash_test_daily(self, interaction: nextcord.Interaction):
        """Comando slash para mensaje diario de prueba"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
            return
        
        try:
            if interaction.guild.id not in self.daily_channels:
                await interaction.response.send_message("❌ No hay canal diario configurado. Usa `/setdaily` primero.", ephemeral=True)
                return
            
            channel_id = self.daily_channels[interaction.guild.id]
            channel = self.bot.get_channel(channel_id)
            
            if not channel:
                await interaction.response.send_message("❌ El canal configurado no existe o no es accesible.", ephemeral=True)
                return
            
            # Enviar mensaje de prueba
            embed = nextcord.Embed(
                title="🧪 Mensaje Diario de Prueba",
                description="¡Este es un mensaje de prueba para verificar que todo funciona correctamente!",
                color=nextcord.Color.blue()
            )
            embed.add_field(name="Solicitado por", value=interaction.user.mention, inline=True)
            embed.set_footer(text="🤖 Mensaje de prueba")
            
            await channel.send(embed=embed)
            await interaction.response.send_message(f"✅ Mensaje de prueba enviado a {channel.mention}")
            
        except Exception as e:
            logger.error(f"Error en mensaje diario de prueba: {e}")
            await interaction.response.send_message("❌ Error al enviar el mensaje de prueba.", ephemeral=True)
