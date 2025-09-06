"""
Comando de prueba para verificar sistemas de mensajes persistentes
"""

import logging
import nextcord
from nextcord.ext import commands

logger = logging.getLogger(__name__)

class TestPersistentSystems(commands.Cog):
    """Comandos de prueba para sistemas persistentes"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @nextcord.slash_command(name="test", description="Comandos de prueba")
    async def test_main(self, interaction: nextcord.Interaction):
        """Comando principal de pruebas"""
        pass
    
    @test_main.subcommand(name="messages", description="Probar sistema de mensajes persistentes")
    async def test_messages(self, interaction: nextcord.Interaction):
        """Probar mensajes persistentes"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitas permisos de administrador para usar este comando.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Obtener el gestor de mensajes persistentes
        pm_manager = self.bot.get_cog('PersistentMessageManager')
        if not pm_manager:
            embed = nextcord.Embed(
                title="❌ Error",
                description="Sistema de mensajes persistentes no disponible.",
                color=nextcord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Verificar todos los paneles
        results = []
        guild = interaction.guild
        
        # Lista de paneles a verificar
        panels = ['ticket_panel', 'voicemaster_panel', 'welcome_panel']
        
        for panel_type in panels:
            try:
                success = await pm_manager.verify_and_setup_message(guild, panel_type)
                status = "✅ OK" if success else "❌ Error"
                results.append(f"**{panel_type}**: {status}")
            except Exception as e:
                results.append(f"**{panel_type}**: ❌ Error ({str(e)[:50]})")
        
        embed = nextcord.Embed(
            title="🧪 Prueba de Mensajes Persistentes",
            description="\n".join(results),
            color=nextcord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Sistemas Verificados",
            value=f"• Sistema de tickets\n• VoiceMaster\n• Panel de bienvenida",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)
    
    @test_main.subcommand(name="tickets", description="Probar sistema de tickets")
    async def test_tickets(self, interaction: nextcord.Interaction):
        """Probar sistema de tickets"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitas permisos de administrador para usar este comando.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Obtener el ticket manager
        ticket_manager = self.bot.get_cog('TicketManager')
        if not ticket_manager:
            embed = nextcord.Embed(
                title="❌ Error",
                description="Sistema de tickets no disponible.",
                color=nextcord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Configurar sistema de tickets
        success = await ticket_manager.setup_ticket_system(interaction.guild)
        
        if success:
            embed = nextcord.Embed(
                title="✅ Prueba de Tickets Exitosa",
                description="El sistema de tickets ha sido configurado y está funcionando.",
                color=nextcord.Color.green()
            )
            embed.add_field(
                name="📋 Estado",
                value="• Categoría creada/verificada\n• Panel de tickets configurado\n• Base de datos inicializada",
                inline=False
            )
        else:
            embed = nextcord.Embed(
                title="❌ Error en Prueba de Tickets",
                description="No se pudo configurar el sistema de tickets.",
                color=nextcord.Color.red()
            )
        
        await interaction.followup.send(embed=embed)
    
    @test_main.subcommand(name="voicemaster", description="Probar sistema VoiceMaster")
    async def test_voicemaster(self, interaction: nextcord.Interaction):
        """Probar VoiceMaster"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitas permisos de administrador para usar este comando.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Obtener VoiceMaster
        voicemaster = self.bot.get_cog('VoiceMaster')
        if not voicemaster:
            embed = nextcord.Embed(
                title="❌ Error",
                description="Sistema VoiceMaster no disponible.",
                color=nextcord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Configurar VoiceMaster
        success = await voicemaster.setup_voicemaster(interaction.guild)
        
        if success:
            embed = nextcord.Embed(
                title="✅ Prueba de VoiceMaster Exitosa",
                description="El sistema VoiceMaster ha sido configurado y está funcionando.",
                color=nextcord.Color.green()
            )
            embed.add_field(
                name="📋 Estado",
                value="• Categoría creada/verificada\n• Canal creador configurado\n• Panel de control configurado",
                inline=False
            )
        else:
            embed = nextcord.Embed(
                title="❌ Error en Prueba de VoiceMaster",
                description="No se pudo configurar el sistema VoiceMaster.",
                color=nextcord.Color.red()
            )
        
        await interaction.followup.send(embed=embed)
    
    @test_main.subcommand(name="all", description="Probar todos los sistemas")
    async def test_all(self, interaction: nextcord.Interaction):
        """Probar todos los sistemas de una vez"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitas permisos de administrador para usar este comando.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        embed = nextcord.Embed(
            title="🧪 Prueba Completa de Sistemas",
            description="Ejecutando pruebas de todos los sistemas...",
            color=nextcord.Color.blue()
        )
        
        results = []
        
        # Probar sistema de mensajes persistentes
        pm_manager = self.bot.get_cog('PersistentMessageManager')
        if pm_manager:
            try:
                success = await pm_manager.verify_and_setup_message(interaction.guild, 'ticket_panel')
                results.append(f"**Mensajes Persistentes**: {'✅ OK' if success else '❌ Error'}")
            except:
                results.append("**Mensajes Persistentes**: ❌ Error")
        else:
            results.append("**Mensajes Persistentes**: ❌ No disponible")
        
        # Probar tickets
        ticket_manager = self.bot.get_cog('TicketManager')
        if ticket_manager:
            try:
                success = await ticket_manager.setup_ticket_system(interaction.guild)
                results.append(f"**Sistema de Tickets**: {'✅ OK' if success else '❌ Error'}")
            except:
                results.append("**Sistema de Tickets**: ❌ Error")
        else:
            results.append("**Sistema de Tickets**: ❌ No disponible")
        
        # Probar VoiceMaster
        voicemaster = self.bot.get_cog('VoiceMaster')
        if voicemaster:
            try:
                success = await voicemaster.setup_voicemaster(interaction.guild)
                results.append(f"**VoiceMaster**: {'✅ OK' if success else '❌ Error'}")
            except:
                results.append("**VoiceMaster**: ❌ Error")
        else:
            results.append("**VoiceMaster**: ❌ No disponible")
        
        # Probar ServerManager
        server_manager = self.bot.get_cog('ServerManager')
        if server_manager:
            try:
                success = await server_manager.setup_server(interaction.guild)
                results.append(f"**Gestión de Servidor**: {'✅ OK' if success else '❌ Error'}")
            except:
                results.append("**Gestión de Servidor**: ❌ Error")
        else:
            results.append("**Gestión de Servidor**: ❌ No disponible")
        
        embed.description = "\n".join(results)
        embed.add_field(
            name="📊 Resumen",
            value="Todos los sistemas han sido probados y configurados automáticamente.",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)

def setup(bot):
    """Función para añadir el cog al bot"""
    return TestPersistentSystems(bot)
