import os
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

COGS = [
    "cogs.core",
    "cogs.warn_system",
    "cogs.moderation",
    "cogs.support",
    "cogs.onboarding",
    "cogs.audit",
    "cogs.security",
    "cogs.staff",
    "cogs.admin",
    "cogs.announce",
    "cogs.system",
]

@bot.event
async def on_ready():
    print(f"🌙 {bot.user} | Hellfire Hangout ONLINE")

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed {cog}: {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
