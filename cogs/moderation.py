import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from utils.database import add_warning, get_warnings, clear_warnings

class Moderation(commands.Cog):
    def __init__(self, bot): self.bot=bot

    async def mod_action(self, interaction, action, member, reason):
        await interaction.response.send_message(f"**{action}** completed for {member.mention}. Reason: {reason}")

    @app_commands.command(name="ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction, member: discord.Member, reason: str="No reason provided"):
        await member.ban(reason=reason)
        await self.mod_action(interaction,"Ban",member,reason)

    @app_commands.command(name="kick")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction, member: discord.Member, reason: str="No reason provided"):
        await member.kick(reason=reason)
        await self.mod_action(interaction,"Kick",member,reason)

    @app_commands.command(name="timeout")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(self, interaction, member: discord.Member, minutes: app_commands.Range[int,1,40320], reason: str="No reason provided"):
        await member.timeout(timedelta(minutes=minutes), reason=reason)
        await self.mod_action(interaction,"Timeout",member,reason)

    @app_commands.command(name="untimeout")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def untimeout(self, interaction, member: discord.Member):
        await member.timeout(None)
        await interaction.response.send_message(f"Timeout removed for {member.mention}.")

    @app_commands.command(name="warn")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction, member: discord.Member, reason: str):
        await add_warning(interaction.guild.id, member.id, interaction.user.id, reason)
        await interaction.response.send_message(f"⚠️ {member.mention} has been warned. Reason: {reason}")

    @app_commands.command(name="warnings")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(self, interaction, member: discord.Member):
        rows=await get_warnings(interaction.guild.id,member.id)
        if not rows: return await interaction.response.send_message(f"{member.mention} has no warnings.")
        text="\n".join(f"`#{r[0]}` • {r[1]}" for r in rows[:10])
        await interaction.response.send_message(f"**Warnings for {member}:**\n{text}")

    @app_commands.command(name="clearwarnings")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def clearwarnings_cmd(self, interaction, member: discord.Member):
        await clear_warnings(interaction.guild.id,member.id)
        await interaction.response.send_message(f"Warnings cleared for {member.mention}.")

    @app_commands.command(name="clear")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction, amount: app_commands.Range[int,1,100]):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"Deleted {amount} messages.", ephemeral=True)

    @app_commands.command(name="lock")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 Channel locked.")

    @app_commands.command(name="unlock")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction):
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
        await interaction.response.send_message("🔓 Channel unlocked.")

    @app_commands.command(name="slowmode")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, interaction, seconds: app_commands.Range[int,0,21600]):
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(f"Slowmode set to {seconds} seconds.")

async def setup(bot): await bot.add_cog(Moderation(bot))
