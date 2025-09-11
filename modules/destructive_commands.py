"""
Sistema de Comandos Destructivos para DaBot v2
Incluye verificación de owner y sistema de seguridad
"""

import nextcord
from nextcord.ext import commands
import asyncio
from datetime import datetime, timedelta

class DestructiveCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.unauthorized_attempts = {}  # guild_id: {user_id: last_attempt}
        self.timeout_users = {}  # user_id: timeout_until
        
    async def is_owner_verified(self, interaction, guild):
        """Verificar si el usuario es el propietario del servidor"""
        return interaction.user.id == guild.owner_id
    
    async def handle_unauthorized_attempt(self, interaction, guild):
        """Manejar intento no autorizado de comando destructivo"""
        user_id = interaction.user.id
        guild_id = guild.id
        current_time = datetime.now()
        
        # Registrar intento no autorizado
        if guild_id not in self.unauthorized_attempts:
            self.unauthorized_attempts[guild_id] = {}
        
        self.unauthorized_attempts[guild_id][user_id] = current_time
        
        # Aplicar timeout de 10 minutos
        timeout_until = current_time + timedelta(minutes=10)
        self.timeout_users[user_id] = timeout_until
        
        # Notificar al usuario
        embed = nextcord.Embed(
            title="🚨 Acceso Denegado",
            description=f"❌ **Solo el propietario del servidor puede usar este comando.**\n\n⏱️ **Has sido bloqueado por 10 minutos** por intento no autorizado.\n\n👑 **Propietario:** <@{guild.owner_id}>",
            color=0xff0000,
            timestamp=current_time
        )
        
        try:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except:
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Notificar al staff (enviar a canal de logs si existe)
        staff_notification = nextcord.Embed(
            title="⚠️ Intento de Comando Destructivo",
            description=f"🚨 **Usuario:** {interaction.user.mention} (`{interaction.user.id}`)\n🔧 **Comando:** `{interaction.data.get('name', 'Desconocido')}`\n⏰ **Tiempo:** {current_time.strftime('%H:%M:%S')}\n\n❌ **Acceso denegado** - No es el propietario del servidor.",
            color=0xff6b00,
            timestamp=current_time
        )
        
        # Buscar canal de logs
        log_channel = None
        for channel in guild.text_channels:
            if 'log' in channel.name.lower() or 'audit' in channel.name.lower():
                log_channel = channel
                break
        
        if log_channel:
            try:
                await log_channel.send(embed=staff_notification)
            except:
                pass
    
    async def check_user_timeout(self, interaction):
        """Verificar si el usuario está en timeout"""
        user_id = interaction.user.id
        if user_id in self.timeout_users:
            timeout_until = self.timeout_users[user_id]
            if datetime.now() < timeout_until:
                remaining = timeout_until - datetime.now()
                minutes = int(remaining.total_seconds() // 60)
                
                embed = nextcord.Embed(
                    title="⏱️ Usuario en Timeout",
                    description=f"🚫 **Estás bloqueado por intento no autorizado.**\n\n⏰ **Tiempo restante:** {minutes} minutos\n\n💡 **Razón:** Intento de usar comando destructivo sin ser propietario.",
                    color=0xff6b00
                )
                
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except:
                    await interaction.followup.send(embed=embed, ephemeral=True)
                
                return True
            else:
                # Timeout expirado, remover
                del self.timeout_users[user_id]
        
        return False
    
    async def nuclear_reset(self, interaction, guild):
        """Comando para eliminar todos los canales, categorías y roles"""
        
        # Crear embed de confirmación
        embed = nextcord.Embed(
            title="☢️ COMANDO NUCLEAR ACTIVADO",
            description="⚠️ **ADVERTENCIA CRÍTICA** ⚠️\n\n🚨 **Este comando eliminará:**\n• Todos los canales de texto\n• Todos los canales de voz\n• Todas las categorías\n• Todos los roles (excepto @everyone)\n• Toda la configuración del servidor\n\n❌ **ESTA ACCIÓN NO SE PUEDE DESHACER**\n\n⏰ **Tienes 30 segundos para confirmar**",
            color=0xff0000
        )
        
        # Crear vista con botones de confirmación
        view = ConfirmResetView(self, interaction.user)
        
        try:
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            message = await interaction.original_response()
            view.set_message(message)
        except:
            message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            view.set_message(message)
    
    async def execute_nuclear_reset(self, interaction, guild):
        """Ejecutar el reset nuclear del servidor"""
        
        # Embed de progreso
        progress_embed = nextcord.Embed(
            title="☢️ Ejecutando Reset Nuclear...",
            description="🔄 **Procesando destrucción del servidor...**\n\n⏳ Por favor espera...",
            color=0xff6b00
        )
        
        # Editar el mensaje original con el progreso
        try:
            await interaction.edit_original_message(embed=progress_embed, view=None)
        except:
            try:
                await interaction.followup.send(embed=progress_embed, ephemeral=True)
            except:
                print("❌ No se pudo mostrar el progreso del reset")
        
        deleted_count = {
            'channels': 0,
            'categories': 0,
            'roles': 0
        }
        
        try:
            # 1. Eliminar todos los canales de texto
            for channel in guild.text_channels:
                try:
                    await channel.delete(reason="Reset nuclear del servidor")
                    deleted_count['channels'] += 1
                    await asyncio.sleep(0.5)  # Evitar rate limits
                except:
                    pass
            
            # 2. Eliminar todos los canales de voz
            for channel in guild.voice_channels:
                try:
                    await channel.delete(reason="Reset nuclear del servidor")
                    deleted_count['channels'] += 1
                    await asyncio.sleep(0.5)
                except:
                    pass
            
            # 3. Eliminar todas las categorías
            for category in guild.categories:
                try:
                    await category.delete(reason="Reset nuclear del servidor")
                    deleted_count['categories'] += 1
                    await asyncio.sleep(0.5)
                except:
                    pass
            
            # 4. Eliminar todos los roles (excepto @everyone y roles del bot)
            for role in guild.roles:
                if role.name != "@everyone" and not role.managed:
                    try:
                        await role.delete(reason="Reset nuclear del servidor")
                        deleted_count['roles'] += 1
                        await asyncio.sleep(0.5)
                    except:
                        pass
            
            # 5. Crear canal de confirmación
            try:
                new_channel = await guild.create_text_channel(
                    name="🚨-reset-completado",
                    reason="Canal de confirmación post-reset"
                )
                
                # Embed de confirmación
                completion_embed = nextcord.Embed(
                    title="☢️ Reset Nuclear Completado",
                    description=f"✅ **Destrucción del servidor completada exitosamente**\n\n📊 **Estadísticas:**\n• 📺 **Canales eliminados:** {deleted_count['channels']}\n• 📁 **Categorías eliminadas:** {deleted_count['categories']}\n• 👥 **Roles eliminados:** {deleted_count['roles']}\n\n🔄 **El servidor ha sido restaurado a su estado inicial.**\n\n💡 **Puedes usar `/servidor-completo` para reconfigurar el servidor rápidamente.**",
                    color=0x00ff00,
                    timestamp=datetime.now()
                )
                
                await new_channel.send(embed=completion_embed)
                
            except Exception as e:
                print(f"Error creando canal de confirmación: {e}")
        
        except Exception as e:
            # Error durante el reset
            error_embed = nextcord.Embed(
                title="❌ Error en Reset Nuclear",
                description=f"🚨 **Ocurrió un error durante el reset:**\n\n```\n{str(e)}\n```\n\n⚠️ **El reset puede estar incompleto.**",
                color=0xff0000
            )
            
            # Intentar enviar el error por cualquier medio disponible
            try:
                await interaction.edit_original_message(embed=error_embed, view=None)
            except:
                try:
                    await interaction.followup.send(embed=error_embed, ephemeral=True)
                except:
                    print(f"❌ Error crítico en reset nuclear: {e}")

    @nextcord.slash_command(
        name="reset-servidor",
        description="🚨 PELIGROSO: Elimina todos los canales, categorías y roles del servidor"
    )
    async def nuclear_reset_command(self, interaction: nextcord.Interaction):
        """Comando slash para reset nuclear del servidor"""
        
        # VERIFICACIÓN CRÍTICA: Solo el owner puede ejecutar esto
        if interaction.user.id != interaction.guild.owner_id:
            embed = nextcord.Embed(
                title="🚨 Acceso Denegado",
                description=f"❌ **Solo el propietario del servidor puede usar este comando.**\n\n👑 **Propietario:** <@{interaction.guild.owner_id}>",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Verificar timeout del usuario
        if await self.check_user_timeout(interaction):
            return
        
        await self.nuclear_reset(interaction, interaction.guild)


class ConfirmResetView(nextcord.ui.View):
    def __init__(self, cog, user):
        super().__init__(timeout=30.0)
        self.cog = cog
        self.user = user
        self.confirmed = False
        self.message = None  # Para guardar referencia al mensaje
    
    def set_message(self, message):
        """Establecer la referencia al mensaje"""
        self.message = message
    
    @nextcord.ui.button(
        label="✅ CONFIRMAR RESET",
        style=nextcord.ButtonStyle.danger,
        emoji="☢️"
    )
    async def confirm_reset(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Solo quien ejecutó el comando puede confirmar.", ephemeral=True)
            return
        
        self.confirmed = True
        
        # Diferir la respuesta inmediatamente para evitar timeouts
        await interaction.response.defer()
        
        try:
            await self.cog.execute_nuclear_reset(interaction, interaction.guild)
        except Exception as e:
            error_embed = nextcord.Embed(
                title="❌ Error en Reset Nuclear",
                description=f"🚨 **Error durante la ejecución:**\n\n```\n{str(e)}\n```",
                color=0xff0000
            )
            try:
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            except:
                print(f"❌ Error crítico: {e}")
        
        self.stop()
    
    @nextcord.ui.button(
        label="❌ CANCELAR",
        style=nextcord.ButtonStyle.secondary,
        emoji="🛑"
    )
    async def cancel_reset(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Solo quien ejecutó el comando puede cancelar.", ephemeral=True)
            return
        
        embed = nextcord.Embed(
            title="🛑 Reset Cancelado",
            description="✅ **Reset nuclear cancelado exitosamente.**\n\n🔒 **El servidor permanece intacto.**",
            color=0x00ff00
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()
    
    async def on_timeout(self):
        if not self.confirmed:
            embed = nextcord.Embed(
                title="⏰ Tiempo Agotado",
                description="🕐 **El tiempo para confirmar el reset ha expirado.**\n\n🔒 **Reset cancelado automáticamente por seguridad.**",
                color=0xff6b00
            )
            
            try:
                await self.message.edit(embed=embed, view=None)
            except:
                pass

def setup(bot):
    bot.add_cog(DestructiveCommands(bot))
