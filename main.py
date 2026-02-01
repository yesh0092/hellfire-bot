import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils import state

# ================= LOAD ENV =================

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("TOKEN missing")

# ================= INTENTS =================
# DO NOT request presences

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

# ================= STAFF LEVEL =================

def get_user_level(member: discord.Member) -> int:
    if member.guild_permissions.administrator:
        return 99

    for level, role_id in state.STAFF_ROLE_TIERS.items():
        if role_id and any(role.id == role_id for role in member.roles):
            return level
    return 0

# ================= GLOBAL CHECKS =================

@bot.check
async def guild_only(ctx):
    if ctx.guild is None:
        return False
    return True

@bot.check
async def staff_guard(ctx):
    if await bot.is_owner(ctx.author):
        return True

    level = get_user_level(ctx.author)
    required = getattr(ctx.command.callback, "required_level", 1)
    return level >= required

# ================= ERROR HANDLER =================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        return
    raise error

# ================= MESSAGE ROUTER =================
# ONLY PLACE process_commands IS CALLED

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

# ================= COG LOADER =================

COGS = [
    "cogs.admin",
    "cogs.system",
    "cogs.moderation",
    "cogs.botlog",
    "cogs.support",
    "cogs.security",
    "cogs.warn_system",
    "cogs.staff",
    "cogs.audit",
    "cogs.announce",
    "cogs.voice_system",
    "cogs.onboarding",
]

async def load_cogs():
    for cog in COGS:
        await bot.load_extension(cog)

# ================= READY =================

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Game("HellFire Hangout 🔥"),
        status=discord.Status.online
    )
    print(f"ONLINE: {bot.user}")

# ================= MAIN =================

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
