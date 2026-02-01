import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils import state

# ================= LOGGING =================

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s"
)

logging.getLogger("discord").setLevel(logging.DEBUG)
logging.getLogger("discord.http").setLevel(logging.DEBUG)
logging.getLogger("discord.gateway").setLevel(logging.DEBUG)

print(">>> PYTHON PROCESS STARTED <<<")

# ================= ENV =================

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("TOKEN missing")

# ================= INTENTS =================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.moderation = True

# ================= BOT =================

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

@bot.event
async def setup_hook():
    print(">>> SETUP_HOOK FIRED <<<")

@bot.event
async def on_ready():
    print(">>> ON_READY FIRED <<<")

# ================= MAIN =================

async def main():
    print(">>> BOT STARTING LOGIN SEQUENCE <<<")
    await bot.start(TOKEN)

asyncio.run(main())
