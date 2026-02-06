import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils import state
from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER

# =====================================================
# LOGGING (CLEAN & QUIET)
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

for noisy in (
    "discord",
    "discord.http",
    "discord.gateway",
):
    logging.getLogger(noisy).setLevel(logging.WARNING)

print("🔥 HellFire Hangout | Python Process Started")

# =====================================================
# ENVIRONMENT
# =====================================================

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("❌ TOKEN missing in environment")

# =====================================================
# INTENTS (FULL — NO SHORTCUTS)
# =====================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.moderation = True
intents.voice_states = True
intents.dm_messages = True

# =====================================================
# BOT INITIALIZATION
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
    HARD BLOCK:
    - No commands in DMs
    - DM messages still reach onboarding/support via on_message
    """
    if ctx.guild is None:
        try:
            await ctx.send(
                embed=luxury_embed(
                    title="🚫 Commands Disabled in DMs",
                    description=(
                        "Commands can only be used **inside the server**.\n\n"
                        "💬 If you need help, just send a message — the support system will respond automatically."
                    ),
                    color=COLOR_DANGER
                ),
                delete_after=6
            )
        except discord.Forbidden:
            pass
        return False
    return True


@bot.check
async def staff_permission_guard(ctx: commands.Context) -> bool:
    """
    Enforces staff hierarchy using @require_level
    Owner & Administrator override always allowed
    """
    if not ctx.command:
        return True

    if await bot.is_owner(ctx.author):
        return True

    if ctx.author.guild_permissions.administrator:
        return True

    required_level = getattr(ctx.command.callback, "required_level", None)
    if required_level is None:
        return True

    highest_level = 0
    for level, role_id in state.STAFF_ROLE_TIERS.items():
        if role_id and any(role.id == role_id for role in ctx.author.roles):
            highest_level = max(highest_level, level)

    if highest_level >= required_level:
        return True

    await ctx.send(
        embed=luxury_embed(
            title="❌ Permission Denied",
            description="Your staff level is too low for this command.",
            color=COLOR_DANGER
        ),
        delete_after=5
    )
    return False

# =====================================================
# ERROR HANDLER (SAFE & SILENT)
# =====================================================

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.CheckFailure):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing required arguments.", delete_after=5)
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Invalid argument provided.", delete_after=5)
        return

    # Log unexpected errors (do NOT swallow)
    raise error

# =====================================================
# MESSAGE ROUTER (CRITICAL)
# =====================================================

@bot.event
async def on_message(message: discord.Message):
    """
    This is the CORE MESSAGE PIPELINE.
    DO NOT block anything here.
    """
    if message.author.bot:
        return

    # DM messages must reach:
    # - Support system
    # - Onboarding
    # - Future DM features
    await bot.process_commands(message)

# =====================================================
# COG LOADER (ORDER MATTERS)
# =====================================================

COGS = [
    # Core infrastructure
    "cogs.admin",
    "cogs.system",
    "cogs.botlog",
    "cogs.audit",

    # Moderation & security
    "cogs.moderation",
    "cogs.warnsystem",
    "cogs.security",
    "cogs.automod",

    # Staff intelligence
    "cogs.staff",

    # Support & onboarding
    "cogs.support",
    "cogs.onboarding",
    "cogs.announce",

    # Activity & engagement
    "cogs.message_tracker",
    "cogs.profile",
    "cogs.weeklymvp",

    # Voice
    "cogs.voice_system",
]

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")

# =====================================================
# LIFECYCLE EVENTS
# =====================================================

@bot.event
async def setup_hook():
    print("⚙️ setup_hook started")
    await load_cogs()

@bot.event
async def on_ready():
    print("🟢 BOT ONLINE")
    print(f"👤 Logged in as: {bot.user}")
    print(f"📦 Loaded cogs: {len(bot.cogs)}")
    print("🛡️ Staff permission system active")
    print("💬 DM support system online")
    print("🔊 Voice system ready")
    print("🔥 HellFire Hangout is LIVE")

# =====================================================
# ENTRYPOINT
# =====================================================

async def main():
    print("🚀 Starting bot login sequence")
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
