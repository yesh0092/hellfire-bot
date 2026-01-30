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
    raise RuntimeError("❌ TOKEN not found in environment variables")

# ================= INTENTS =================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.moderation = True

# ================= BOT =================

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# ================= STAFF LEVEL RESOLUTION =================

def get_user_level(member: discord.Member) -> int:
    """
    Resolve staff level based on role hierarchy.
    """
    # Discord Administrator = absolute override
    if member.guild_permissions.administrator:
        return 99

    # Staff tiers
    for level, role_id in state.STAFF_ROLE_TIERS.items():
        if role_id and any(role.id == role_id for role in member.roles):
            return level

    return 0

# ================= GLOBAL COMMAND GUARD =================

@bot.check
async def strict_role_guard(ctx: commands.Context) -> bool:
    """
    Global command protection.
    """

    # Allow DMs (support system relies on this)
    if ctx.guild is None:
        return True

    # Bot owner override
    if await bot.is_owner(ctx.author):
        return True

    user_level = get_user_level(ctx.author)

    # 🚫 Normal users cannot use ANY command
    if user_level <= 0:
        return False

    # Command-level requirement (set by require_level)
    required_level = getattr(ctx.command.callback, "required_level", 1)

    return user_level >= required_level

# ================= ERROR HANDLER =================

@bot.event
async def on_command_error(ctx, error):
    # Silent permission denial (luxury experience)
    if isinstance(error, commands.CheckFailure):
        return

    # Missing arguments
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing required arguments.")
        return

    # Bad arguments
    if isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Invalid argument provided.")
        return

    # Unknown command (ignored)
    if isinstance(error, commands.CommandNotFound):
        return

    # Fallback (logged by BotLog cog)
    raise error

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
    "cogs.voice_system",  # 👈 ADD THIS
]

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed {cog}: {e}")

# ================= READY =================

@bot.event
async def on_ready():
    print(f"🌙 {bot.user} | Hellfire Hangout ONLINE")

# ================= MAIN =================

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())

