import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

# ================= INTENTS =================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True

# ================= BOT =================

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None  # we use custom help
)

# ================= COG LIST =================

COGS = [
    "cogs.core",
    "cogs.warn_system",
    "cogs.moderation",
    "cogs.support",
    "cogs.onboarding",
    "cogs.security",
    "cogs.staff",
    "cogs.audit",
    "cogs.system",
    "cogs.admin",
    "cogs.announce",
]

# ================= EVENTS =================

@bot.event
async def on_ready():
    print(f"🌙 {bot.user} | Hellfire Hangout ONLINE")

# ================= LOAD COGS =================

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed {cog}: {e}")

# ================= RUN =================

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
