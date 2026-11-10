import discord, time
from discord.ext import commands
from discord import app_commands

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot=bot
        self.bad_words={}
        self.message_times={}

    @app_commands.command(name="automod_badword")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def badword(self, interaction, word: str):
        self.bad_words.setdefault(interaction.guild.id,set()).add(word.lower())
        await interaction.response.send_message(f"Added `{word}` to the AutoMod filter.", ephemeral=True)

    @app_commands.command(name="automod_remove")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def remove(self, interaction, word: str):
        self.bad_words.setdefault(interaction.guild.id,set()).discard(word.lower())
        await interaction.response.send_message(f"Removed `{word}` from the AutoMod filter.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild: return
        words=self.bad_words.get(message.guild.id,set())
        if any(word in message.content.lower() for word in words):
            try: await message.delete()
            except discord.HTTPException: pass
            await message.channel.send(f"{message.author.mention}, that word is not allowed.", delete_after=5)
            return
        key=(message.guild.id,message.author.id)
        now=time.time()
        times=[t for t in self.message_times.get(key,[]) if now-t<5]
        times.append(now); self.message_times[key]=times
        if len(times)>=7:
            try:
                await message.author.timeout(discord.utils.utcnow()+__import__('datetime').timedelta(minutes=2), reason="AutoMod spam")
            except discord.HTTPException: pass

async def setup(bot): await bot.add_cog(AutoMod(bot))
