import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils import state

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("discord.http").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)

print(">>> PYTHON PROCESS STARTED <<<")

# =====================================================
# ENV
# =====================================================

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("❌ TOKEN missing in environment")

# =====================================================
# INTENTS (FULL & CORRECT)
# =====================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.moderation = True
intents.voice_states = True   # 🔥 REQUIRED FOR VC SYSTEM

# =====================================================
# BOT
# =====================================================

bot = commands.Bot(
    command_prefix="&",
    intents=intents,
    help_command=None
)

# =====================================================
# GLOBAL COMMAND GUARDS
# =====================================================

@bot.check
async def block_commands_in_dm(ctx: commands.Context) -> bool:
    """
    HARD BLOCK: commands never execute in DMs
    """
    if ctx.guild is None:
        try:
            await ctx.send(
                embed=discord.Embed(
                    title="🚫 Commands Disabled in DMs",
                    description=(
                        "**HellFire Hangout Support**\n\n"
                        "Commands can only be used inside the server."
                    ),
                    color=0x7c2d12
                ),
                delete_after=5
            )
        except discord.Forbidden:
            pass
        return False
    return True


@bot.check
async def staff_permission_guard(ctx: commands.Context) -> bool:
    """
    Staff level enforcement with admin & owner override
    """
    if not ctx.command:
        return True

    if await bot.is_owner(ctx.author):
        return True

    if ctx.author.guild_permissions.administrator:
        return True

    required = getattr(ctx.command.callback, "required_level", None)
    if required is None:
        return True

    highest_level = 0
    for level, role_id in state.STAFF_ROLE_TIERS.items():
        if role_id and any(role.id == role_id for role in ctx.author.roles):
            highest_level = max(highest_level, level)

    if highest_level >= required:
        return True

    await ctx.send(
        embed=discord.Embed(
            title="❌ Permission Denied",
            description="Your staff level is too low for this command.",
            color=0x7c2d12
        ),
        delete_after=5
    )
    return False

# =====================================================
# ERROR HANDLER
# =====================================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing required arguments.", delete_after=5)
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Invalid argument provided.", delete_after=5)
        return
    raise error

# =====================================================
# MESSAGE HANDLER (CRITICAL FIX)
# =====================================================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # 🔑 Allow DMs to reach onboarding/support cogs
    await bot.process_commands(message)

# =====================================================
# COG LOADER
# =====================================================

COGS = [
    "cogs.admin",
    "cogs.system",
    "cogs.moderation",
    "cogs.warn_system",
    "cogs.staff",
    "cogs.security",
    "cogs.support",
    "cogs.audit",
    "cogs.announce",
    "cogs.voice_system",
    "cogs.onboarding",
]

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")

# =====================================================
# EVENTS
# =====================================================

@bot.event
async def setup_hook():
    print(">>> SETUP_HOOK FIRED <<<")
    await load_cogs()

@bot.event
async def on_ready():
    print(">>> ON_READY FIRED <<<")
    print(f"🟢 Logged in as: {bot.user}")
    print(f"📦 Loaded cogs: {len(bot.cogs)}")
    print("🛡️ Commands locked to server only")
    print("⚙️ Prefix set to &")

# =====================================================
# MAIN
# =====================================================

async def main():
    print(">>> BOT STARTING LOGIN SEQUENCE <<<")
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
