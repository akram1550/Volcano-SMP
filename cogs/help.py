import discord
from discord.ext import commands
from discord import app_commands
from config import PREFIX, EMBED_COLOR

class Help(commands.Cog):
    def __init__(self, bot): self.bot=bot

    @app_commands.command(name="help")
    async def help_slash(self, interaction):
        await self.send_help(interaction)

    @commands.command(name="help")
    async def help_prefix(self, ctx):
        e=self.build_embed()
        await ctx.send(embed=e)

    def build_embed(self):
        e=discord.Embed(title="🌋 VOLCANO SMP • Help",
            description=f"Every command works as a slash command. Prefix: `{PREFIX}`",
            color=EMBED_COLOR)
        e.add_field(name="🎫 Tickets",value="`/ticket panel` `category` `supportrole` `settings`",inline=False)
        e.add_field(name="📜 Logs",value="`/log_set`",inline=False)
        e.add_field(name="🛡️ Moderation",value="`/ban` `/kick` `/timeout` `/untimeout` `/warn` `/warnings` `/clearwarnings` `/clear` `/slowmode` `/lock` `/unlock`",inline=False)
        e.add_field(name="🤖 AutoMod",value="`/automod_badword` `/automod_remove`",inline=False)
        e.add_field(name="✨ Utility",value="`/ping` `/userinfo` `/serverinfo` `/avatar` `/poll` `/embed`",inline=False)
        e.set_footer(text="VOLCANO SMP • All-in-One Management Bot")
        return e

    async def send_help(self, interaction):
        await interaction.response.send_message(embed=self.build_embed())

async def setup(bot): await bot.add_cog(Help(bot))
