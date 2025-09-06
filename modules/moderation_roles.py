import nextcord
from nextcord.ext import commands
import json
import os
import logging
from datetime import datetime
from modules.config_manager import config, get_config

logger = logging.getLogger(__name__)

class ModerationRoles(commands.Cog):
    """Sistema de roles de moderación con permisos específicos"""
    
    def __init__(self, bot):
        self.bot = bot
        self.roles_config = {}
        self.load_roles_config()
    
    def load_roles_config(self):
        """Cargar configuración de roles"""
        try:
            if os.path.exists('data/moderation_roles.json'):
                with open('data/moderation_roles.json', 'r', encoding='utf-8') as f:
                    self.roles_config = json.load(f)
            else:
                self.roles_config = {
                    'admin_roles': [],      # Roles con permisos completos
                    'mod_roles': [],        # Roles con permisos limitados
                    'helper_roles': []      # Roles solo para avisos
                }
                self.save_roles_config()
        except Exception as e:
            logger.error(f"Error cargando roles: {e}")
            self.roles_config = {'admin_roles': [], 'mod_roles': [], 'helper_roles': []}
    
    def save_roles_config(self):
        """Guardar configuración de roles"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/moderation_roles.json', 'w', encoding='utf-8') as f:
                json.dump(self.roles_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando roles: {e}")
    
    def get_user_mod_level(self, member: nextcord.Member) -> str:
        """Obtener nivel de moderación del usuario"""
        if member.guild_permissions.administrator:
            return 'owner'
        
        user_role_ids = [str(role.id) for role in member.roles]
        
        # Verificar roles de admin
        for role_id in self.roles_config.get('admin_roles', []):
            if role_id in user_role_ids:
                return 'admin'
        
        # Verificar roles de moderador
        for role_id in self.roles_config.get('mod_roles', []):
            if role_id in user_role_ids:
                return 'moderator'
        
        # Verificar roles de helper
        for role_id in self.roles_config.get('helper_roles', []):
            if role_id in user_role_ids:
                return 'helper'
        
        return 'none'
    
    def can_perform_action(self, member: nextcord.Member, action: str) -> bool:
        """Verificar si el usuario puede realizar una acción"""
        level = self.get_user_mod_level(member)
        
        permissions = {
            'owner': ['warn', 'unwarn', 'ban', 'unban', 'kick', 'mute', 'unmute', 'clear', 'manage_roles'],
            'admin': ['warn', 'unwarn', 'ban', 'unban', 'kick', 'mute', 'unmute', 'clear', 'manage_roles'],
            'moderator': ['warn', 'unwarn', 'ban', 'kick', 'mute', 'unmute', 'clear'],
            'helper': ['warn'],
            'none': []
        }
        
        return action in permissions.get(level, [])
    
    @nextcord.slash_command(name="mod-roles", description="Gestionar roles de moderación")
    async def mod_roles(self, interaction: nextcord.Interaction):
        """Comando principal para gestionar roles"""
        pass
    
    @mod_roles.subcommand(name="add", description="Añadir rol de moderación")
    async def add_mod_role(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = nextcord.SlashOption(description="Rol a añadir"),
        level: str = nextcord.SlashOption(
            description="Nivel de moderación",
            choices=["admin", "moderator", "helper"]
        )
    ):
        """Añadir rol de moderación"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Solo administradores pueden gestionar roles de moderación.", ephemeral=True)
            return
        
        role_id = str(role.id)
        
        # Remover de otros niveles primero
        for level_key in ['admin_roles', 'mod_roles', 'helper_roles']:
            if role_id in self.roles_config.get(level_key, []):
                self.roles_config[level_key].remove(role_id)
        
        # Añadir al nivel correspondiente
        level_key = f"{level}_roles"
        if level_key not in self.roles_config:
            self.roles_config[level_key] = []
        
        self.roles_config[level_key].append(role_id)
        self.save_roles_config()
        
        level_names = {
            'admin': 'Administrador (todos los permisos)',
            'moderator': 'Moderador (sin desbanear)',
            'helper': 'Helper (solo avisos)'
        }
        
        embed = nextcord.Embed(
            title="✅ Rol de Moderación Añadido",
            color=0x27ae60
        )
        embed.add_field(name="Rol", value=role.mention, inline=True)
        embed.add_field(name="Nivel", value=level_names[level], inline=True)
        embed.add_field(
            name="Permisos",
            value=self.get_permissions_text(level),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @mod_roles.subcommand(name="remove", description="Remover rol de moderación")
    async def remove_mod_role(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = nextcord.SlashOption(description="Rol a remover")
    ):
        """Remover rol de moderación"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Solo administradores pueden gestionar roles de moderación.", ephemeral=True)
            return
        
        role_id = str(role.id)
        removed = False
        
        for level_key in ['admin_roles', 'mod_roles', 'helper_roles']:
            if role_id in self.roles_config.get(level_key, []):
                self.roles_config[level_key].remove(role_id)
                removed = True
                break
        
        if removed:
            self.save_roles_config()
            await interaction.response.send_message(f"✅ Rol {role.mention} removido del sistema de moderación.")
        else:
            await interaction.response.send_message(f"❌ El rol {role.mention} no estaba en el sistema de moderación.", ephemeral=True)
    
    @mod_roles.subcommand(name="list", description="Ver roles de moderación configurados")
    async def list_mod_roles(self, interaction: nextcord.Interaction):
        """Listar roles de moderación"""
        embed = nextcord.Embed(
            title="🛡️ Roles de Moderación Configurados",
            color=0x3498db
        )
        
        role_types = {
            'admin_roles': ('👑 Administradores', 'Todos los permisos'),
            'mod_roles': ('🔒 Moderadores', 'Sin desbanear'),
            'helper_roles': ('🆘 Helpers', 'Solo avisos')
        }
        
        for role_type, (title, description) in role_types.items():
            role_ids = self.roles_config.get(role_type, [])
            if role_ids:
                roles_text = []
                for role_id in role_ids:
                    role = interaction.guild.get_role(int(role_id))
                    if role:
                        roles_text.append(role.mention)
                    else:
                        roles_text.append(f"Rol eliminado ({role_id})")
                
                embed.add_field(
                    name=f"{title} ({len(role_ids)})",
                    value="\n".join(roles_text) if roles_text else "Ninguno",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{title} (0)",
                    value="Ninguno configurado",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    def get_permissions_text(self, level: str) -> str:
        """Obtener texto de permisos para un nivel"""
        permissions = {
            'admin': "✅ Avisar\n✅ Quitar avisos\n✅ Banear\n✅ Desbanear\n✅ Expulsar\n✅ Mutear\n✅ Desmutear\n✅ Limpiar mensajes\n✅ Gestionar roles",
            'moderator': "✅ Avisar\n✅ Quitar avisos\n✅ Banear\n❌ Desbanear\n✅ Expulsar\n✅ Mutear\n✅ Desmutear\n✅ Limpiar mensajes",
            'helper': "✅ Avisar\n❌ Quitar avisos\n❌ Banear\n❌ Desbanear\n❌ Expulsar\n❌ Mutear\n❌ Desmutear\n❌ Limpiar mensajes"
        }
        return permissions.get(level, "Sin permisos")
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Cargar configuración al iniciar"""
        self.load_roles_config()

def setup(bot):
    """Función para cargar el cog"""
    return ModerationRoles(bot)
