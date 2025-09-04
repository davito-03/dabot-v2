"""
Sistema de avisos para el bot
por davito
"""

import logging
import json
import os
from datetime import datetime, timedelta
import nextcord
from nextcord.ext import commands

logger = logging.getLogger(__name__)

class Warnings(commands.Cog):
    """sistema de avisos del servidor"""
    
    def __init__(self, bot):
        self.bot = bot
        self.warnings_file = "data/warnings.json"
        self.warnings_data = self.load_warnings()
        
        # crear directorio si no existe
        os.makedirs("data", exist_ok=True)
    
    def load_warnings(self):
        """carga los avisos desde el archivo"""
        try:
            if os.path.exists(self.warnings_file):
                with open(self.warnings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"error cargando avisos: {e}")
            return {}
    
    def save_warnings(self):
        """guarda los avisos en el archivo"""
        try:
            with open(self.warnings_file, 'w', encoding='utf-8') as f:
                json.dump(self.warnings_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"error guardando avisos: {e}")
    
    def get_user_warnings(self, guild_id: int, user_id: int):
        """obtiene los avisos de un usuario"""
        guild_str = str(guild_id)
        user_str = str(user_id)
        
        if guild_str not in self.warnings_data:
            self.warnings_data[guild_str] = {}
        
        if user_str not in self.warnings_data[guild_str]:
            self.warnings_data[guild_str][user_str] = []
        
        return self.warnings_data[guild_str][user_str]
    
    def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str):
        """añade un aviso a un usuario"""
        warnings = self.get_user_warnings(guild_id, user_id)
        
        warning = {
            "id": len(warnings) + 1,
            "reason": reason,
            "moderator": moderator_id,
            "timestamp": datetime.now().isoformat(),
            "active": True
        }
        
        warnings.append(warning)
        self.save_warnings()
        
        return warning
    
    def remove_warning(self, guild_id: int, user_id: int, warning_id: int):
        """elimina un aviso específico"""
        warnings = self.get_user_warnings(guild_id, user_id)
        
        for warning in warnings:
            if warning["id"] == warning_id and warning["active"]:
                warning["active"] = False
                warning["removed_at"] = datetime.now().isoformat()
                self.save_warnings()
                return True
        
        return False
    
    def clear_warnings(self, guild_id: int, user_id: int):
        """limpia todos los avisos de un usuario"""
        warnings = self.get_user_warnings(guild_id, user_id)
        
        for warning in warnings:
            if warning["active"]:
                warning["active"] = False
                warning["removed_at"] = datetime.now().isoformat()
        
        self.save_warnings()
        return len([w for w in warnings if w["active"]])
    
    @commands.command(name='warn', aliases=['avisar'])
    @commands.has_permissions(kick_members=True)
    async def warn_user(self, ctx, member: nextcord.Member, *, reason="sin razón especificada"):
        """
        avisar a un usuario
        uso: !warn @usuario razón
        """
        try:
            if member == ctx.author:
                await ctx.send("❌ no puedes avisarte a ti mismo.")
                return
            
            if member == self.bot.user:
                await ctx.send("❌ no puedes avisarme.")
                return
            
            if member.top_role >= ctx.author.top_role:
                await ctx.send("❌ no puedes avisar a alguien con un rol igual o superior.")
                return
            
            # añadir aviso
            warning = self.add_warning(ctx.guild.id, member.id, ctx.author.id, reason)
            warnings = self.get_user_warnings(ctx.guild.id, member.id)
            active_warnings = [w for w in warnings if w["active"]]
            
            # embed de confirmación
            embed = nextcord.Embed(
                title="⚠️ aviso registrado",
                color=nextcord.Color.orange()
            )
            embed.add_field(name="usuario", value=member.mention, inline=True)
            embed.add_field(name="moderador", value=ctx.author.mention, inline=True)
            embed.add_field(name="avisos totales", value=len(active_warnings), inline=True)
            embed.add_field(name="razón", value=reason, inline=False)
            embed.set_footer(text=f"id del aviso: {warning['id']}")
            
            await ctx.send(embed=embed)
            
            # enviar dm al usuario
            try:
                dm_embed = nextcord.Embed(
                    title="⚠️ has recibido un aviso",
                    description=f"servidor: **{ctx.guild.name}**",
                    color=nextcord.Color.orange()
                )
                dm_embed.add_field(name="razón", value=reason, inline=False)
                dm_embed.add_field(name="moderador", value=str(ctx.author), inline=True)
                dm_embed.add_field(name="avisos totales", value=len(active_warnings), inline=True)
                dm_embed.set_footer(text="comportate mejor para evitar sanciones")
                
                await member.send(embed=dm_embed)
            except nextcord.Forbidden:
                await ctx.send("⚠️ no se pudo enviar dm al usuario.")
            
            # auto-sanciones según avisos
            if len(active_warnings) >= 5:
                try:
                    await member.ban(reason=f"5 avisos acumulados - último: {reason}")
                    await ctx.send(f"🔨 {member.mention} ha sido baneado por acumular 5 avisos.")
                except:
                    pass
            elif len(active_warnings) >= 3:
                try:
                    await member.timeout(timedelta(hours=24), reason=f"3 avisos acumulados - último: {reason}")
                    await ctx.send(f"🔇 {member.mention} ha sido silenciado 24h por acumular 3 avisos.")
                except:
                    pass
            
            logger.info(f"aviso dado a {member} por {ctx.author}: {reason}")
            
        except Exception as e:
            logger.error(f"error en comando warn: {e}")
            await ctx.send("❌ error al procesar el aviso.")
    
    @nextcord.slash_command(name="warn", description="avisar a un usuario")
    async def slash_warn(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        reason: str = "sin razón especificada"
    ):
        """comando slash para avisar"""
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ no tienes permisos.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        class MockContext:
            def __init__(self, interaction):
                self.author = interaction.user
                self.guild = interaction.guild
                self.channel = interaction.channel
                self.send = interaction.followup.send
                
        ctx = MockContext(interaction)
        await self.warn_user(ctx, member, reason=reason)
    
    @commands.command(name='warnings', aliases=['avisos'])
    async def show_warnings(self, ctx, member: nextcord.Member = None):
        """
        ver avisos de un usuario
        uso: !warnings @usuario
        """
        try:
            if member is None:
                member = ctx.author
            
            warnings = self.get_user_warnings(ctx.guild.id, member.id)
            active_warnings = [w for w in warnings if w["active"]]
            
            if not active_warnings:
                embed = nextcord.Embed(
                    title="📋 avisos",
                    description=f"{member.mention} no tiene avisos activos.",
                    color=nextcord.Color.green()
                )
                await ctx.send(embed=embed)
                return
            
            embed = nextcord.Embed(
                title=f"📋 avisos de {member.display_name}",
                description=f"avisos activos: **{len(active_warnings)}**",
                color=nextcord.Color.orange()
            )
            
            for warning in active_warnings[:10]:  # mostrar máximo 10
                moderator = self.bot.get_user(warning["moderator"])
                mod_name = moderator.display_name if moderator else "desconocido"
                
                timestamp = datetime.fromisoformat(warning["timestamp"])
                date_str = timestamp.strftime("%d/%m/%Y %H:%M")
                
                embed.add_field(
                    name=f"aviso #{warning['id']}",
                    value=f"**razón:** {warning['reason']}\n**moderador:** {mod_name}\n**fecha:** {date_str}",
                    inline=False
                )
            
            if len(active_warnings) > 10:
                embed.set_footer(text=f"mostrando 10 de {len(active_warnings)} avisos")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error mostrando avisos: {e}")
            await ctx.send("❌ error al obtener los avisos.")
    
    @nextcord.slash_command(name="warnings", description="ver avisos de un usuario")
    async def slash_warnings(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = None
    ):
        """comando slash para ver avisos"""
        if member is None:
            member = interaction.user
            
        class MockContext:
            def __init__(self, interaction):
                self.author = interaction.user
                self.guild = interaction.guild
                self.channel = interaction.channel
                self.send = interaction.response.send_message
                
        ctx = MockContext(interaction)
        await self.show_warnings(ctx, member)
    
    @commands.command(name='removewarn', aliases=['quitaraviso'])
    @commands.has_permissions(kick_members=True)
    async def remove_warn(self, ctx, member: nextcord.Member, warning_id: int):
        """
        quitar un aviso específico
        uso: !removewarn @usuario id_aviso
        """
        try:
            if self.remove_warning(ctx.guild.id, member.id, warning_id):
                embed = nextcord.Embed(
                    title="✅ aviso eliminado",
                    description=f"aviso #{warning_id} eliminado de {member.mention}",
                    color=nextcord.Color.green()
                )
                embed.add_field(name="moderador", value=ctx.author.mention, inline=True)
                
                await ctx.send(embed=embed)
                logger.info(f"aviso {warning_id} eliminado de {member} por {ctx.author}")
            else:
                await ctx.send("❌ aviso no encontrado o ya eliminado.")
                
        except ValueError:
            await ctx.send("❌ id de aviso inválido.")
        except Exception as e:
            logger.error(f"error eliminando aviso: {e}")
            await ctx.send("❌ error al eliminar el aviso.")
    
    @commands.command(name='clearwarns', aliases=['limpiaravisos'])
    @commands.has_permissions(kick_members=True)
    async def clear_warns(self, ctx, member: nextcord.Member):
        """
        limpiar todos los avisos de un usuario
        uso: !clearwarns @usuario
        """
        try:
            count = self.clear_warnings(ctx.guild.id, member.id)
            
            embed = nextcord.Embed(
                title="🧹 avisos limpiados",
                description=f"se eliminaron {count} avisos de {member.mention}",
                color=nextcord.Color.green()
            )
            embed.add_field(name="moderador", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
            logger.info(f"{count} avisos limpiados de {member} por {ctx.author}")
            
        except Exception as e:
            logger.error(f"error limpiando avisos: {e}")
            await ctx.send("❌ error al limpiar avisos.")
    
    @commands.command(name='topwarns', aliases=['topavisos'])
    @commands.has_permissions(kick_members=True)
    async def top_warnings(self, ctx):
        """
        ver usuarios con más avisos
        uso: !topwarns
        """
        try:
            guild_str = str(ctx.guild.id)
            if guild_str not in self.warnings_data:
                await ctx.send("❌ no hay datos de avisos en este servidor.")
                return
            
            user_counts = []
            for user_id, warnings in self.warnings_data[guild_str].items():
                active_count = len([w for w in warnings if w["active"]])
                if active_count > 0:
                    user = self.bot.get_user(int(user_id))
                    user_name = user.display_name if user else f"usuario {user_id}"
                    user_counts.append((user_name, active_count))
            
            if not user_counts:
                await ctx.send("✅ no hay usuarios con avisos activos.")
                return
            
            user_counts.sort(key=lambda x: x[1], reverse=True)
            
            embed = nextcord.Embed(
                title="🏆 top usuarios con avisos",
                color=nextcord.Color.red()
            )
            
            for i, (user_name, count) in enumerate(user_counts[:10], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                embed.add_field(
                    name=f"{medal} {user_name}",
                    value=f"{count} avisos",
                    inline=True
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"error en top avisos: {e}")
            await ctx.send("❌ error al obtener estadísticas.")
