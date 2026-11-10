import discord
from discord.ext import commands
from discord import app_commands

class Utility(commands.Cog):
    def __init__(self, bot): self.bot=bot

    @app_commands.command(name="ping")
    async def ping(self, interaction):
        await interaction.response.send_message(f"🏓 Pong! `{round(self.bot.latency*1000)}ms`")

    @app_commands.command(name="userinfo")
    async def userinfo(self, interaction, member: discord.Member=None):
        member=member or interaction.user
        e=discord.Embed(title=f"User Info • {member}",color=discord.Color.blurple())
        e.set_thumbnail(url=member.display_avatar.url)
        e.add_field(name="ID",value=member.id)
        e.add_field(name="Joined",value=discord.utils.format_dt(member.joined_at,"D"))
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="serverinfo")
    async def serverinfo(self, interaction):
        g=interaction.guild
        e=discord.Embed(title=f"{g.name} • Server Info",color=discord.Color.blurple())
        if g.icon: e.set_thumbnail(url=g.icon.url)
        e.add_field(name="Members",value=g.member_count)
        e.add_field(name="Channels",value=len(g.channels))
        e.add_field(name="Owner",value=g.owner.mention if g.owner else "Unknown")
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="avatar")
    async def avatar(self, interaction, member: discord.Member=None):
        member=member or interaction.user
        await interaction.response.send_message(member.display_avatar.url)

    @app_commands.command(name="poll")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def poll(self, interaction, question: str):
        e=discord.Embed(title="📊 Poll",description=question,color=discord.Color.blurple())
        await interaction.response.send_message(embed=e)
        msg=await interaction.original_response()
        await msg.add_reaction("👍"); await msg.add_reaction("👎")

    @app_commands.command(name="embed")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed(self, interaction, title: str, description: str):
        await interaction.response.send_message(embed=discord.Embed(title=title,description=description,color=discord.Color.blurple()))

async def setup(bot): await bot.add_cog(Utility(bot))
