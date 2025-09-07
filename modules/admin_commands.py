import nextcord
from nextcord.ext import commands
import logging

logger = logging.getLogger(__name__)

class AdminCommands(commands.Cog):
    """comandos administrativos avanzados"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command(
        name="say",
        description="Haz que el bot diga algo (solo administradores)"
    )
    async def say_command(
        self,
        interaction: nextcord.Interaction,
        mensaje: str = nextcord.SlashOption(
            description="El mensaje que quieres que diga el bot",
            required=True
        ),
        canal: nextcord.TextChannel = nextcord.SlashOption(
            description="Canal donde enviar el mensaje (opcional)",
            required=False
        ),
        embed: bool = nextcord.SlashOption(
            description="Enviar como embed elegante",
            required=False,
            default=False
        )
    ):
        """hacer que el bot diga algo"""
        
        # Verificar permisos
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Gestionar Mensajes** para usar este comando.",
                ephemeral=True
            )
            return
        
        # Determinar canal de destino
        target_channel = canal if canal else interaction.channel
        
        try:
            if embed:
                # Crear embed elegante
                embed_msg = nextcord.Embed(
                    description=mensaje,
                    color=nextcord.Color.blue()
                )
                embed_msg.set_footer(
                    text=f"Enviado por {interaction.user.display_name}",
                    icon_url=interaction.user.display_avatar.url
                )
                
                if target_channel == interaction.channel:
                    await interaction.response.send_message(embed=embed_msg)
                else:
                    await target_channel.send(embed=embed_msg)
                    await interaction.response.send_message(
                        f"✅ Mensaje enviado en {target_channel.mention}",
                        ephemeral=True
                    )
            else:
                # Enviar mensaje normal
                if target_channel == interaction.channel:
                    await interaction.response.send_message(mensaje)
                else:
                    await target_channel.send(mensaje)
                    await interaction.response.send_message(
                        f"✅ Mensaje enviado en {target_channel.mention}",
                        ephemeral=True
                    )
                    
        except Exception as e:
            logger.error(f"Error en comando say: {e}")
            await interaction.followup.send(
                "❌ Error al enviar el mensaje. Verifica que tenga permisos en el canal.",
                ephemeral=True
            )

def setup(bot):
    """cargar el cog"""
    bot.add_cog(AdminCommands(bot))
