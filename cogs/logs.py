import discord
from discord.ext import commands
from discord import app_commands
from utils.database import get_setting, save_setting

class Logs(commands.Cog):
    def __init__(self, bot): self.bot=bot

    @app_commands.command(name="log_set")
    @app_commands.checks.has_permissions(administrator=True)
    async def log_set(self, interaction, channel: discord.TextChannel):
        await save_setting(interaction.guild.id, log_channel_id=channel.id)
        await interaction.response.send_message(f"Log channel set to {channel.mention}.", ephemeral=True)

    async def send_log(self,guild,embed):
        row=await get_setting(guild.id)
        if row and row[0]:
            channel=guild.get_channel(row[0])
            if channel: await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        e=discord.Embed(title="Member Joined",description=f"{member.mention} joined the server.",color=discord.Color.green())
        await self.send_log(member.guild,e)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        e=discord.Embed(title="Member Left",description=f"{member} left the server.",color=discord.Color.red())
        await self.send_log(member.guild,e)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.guild: return
        e=discord.Embed(title="Message Deleted",description=f"Author: {message.author.mention}\nChannel: {message.channel.mention}\nContent: {message.content[:1000]}",color=discord.Color.orange())
        await self.send_log(message.guild,e)

async def setup(bot): await bot.add_cog(Logs(bot))
