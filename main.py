import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config import PREFIX, GUILD_ID, BOT_NAME
from utils.database import init_db


# Load the DISCORD_TOKEN from the .env file
load_dotenv()


# Discord intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True


class VolcanoBot(commands.Bot):
    async def setup_hook(self):
        # Initialize SQLite database
        await init_db()

        # Load all bot modules
        extensions = (
            "cogs.tickets",
            "cogs.moderation",
            "cogs.automod",
            "cogs.logs",
            "cogs.utility",
            "cogs.help",
        )

        for extension in extensions:
            try:
                await self.load_extension(extension)
                print(f"[✓] Loaded: {extension}")
            except Exception as error:
                print(f"[✗] Failed to load {extension}: {error}")

        # Sync slash commands to your VOLCANO SMP server
        guild = discord.Object(id=GUILD_ID)

        try:
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            print(f"[✓] Synced {len(synced)} slash commands to VOLCANO SMP.")
        except Exception as error:
            print(f"[✗] Failed to sync slash commands: {error}")


# Create the bot
bot = VolcanoBot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


@bot.event
async def on_ready():
    print("=" * 50)
    print(f"{BOT_NAME} is now online!")
    print(f"Logged in as: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print(f"Prefix: {PREFIX}")
    print("=" * 50)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing a required argument.")
        return

    print(f"Command error: {error}")


async def main():
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        print("[ERROR] DISCORD_TOKEN was not found.")
        print("Create a .env file and add your bot token.")
        return

    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())