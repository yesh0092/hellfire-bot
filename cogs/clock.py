import os
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import pytz

from utils import state
from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER

# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

for noisy in ("discord", "discord.http", "discord.gateway"):
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
# INTENTS
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
    help_command=None,
    activity=discord.Activity(type=discord.ActivityType.watching, name="System Booting... ⛩️")
)

# =====================================================
# GLOBAL COMMAND GUARDS
# =====================================================

@bot.check
async def block_commands_in_dm(ctx: commands.Context) -> bool:
    if ctx.guild is None:
        try:
            await ctx.send(
                embed=luxury_embed(
                    title="🚫 Commands Disabled in DMs",
                    description="Commands can only be used **inside the server**.",
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
    if not ctx.command: return True
    if await bot.is_owner(ctx.author): return True
    if ctx.author.guild_permissions.administrator: return True

    required_level = getattr(ctx.command.callback, "required_level", None)
    if required_level is None: return True

    highest_level = 0
    tiers = getattr(state, "STAFF_ROLE_TIERS", {})
    for level, role_id in tiers.items():
        if role_id and any(role.id == role_id for role in ctx.author.roles):
            highest_level = max(highest_level, level)

    if highest_level >= required_level: return True

    await ctx.send(
        embed=luxury_embed(title="❌ Permission Denied", description="Level too low.", color=COLOR_DANGER),
        delete_after=5
    )
    return False

# =====================================================
# ERROR HANDLER
# =====================================================

@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)): return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing required arguments.", delete_after=5)
        return
    raise error

# =====================================================
# MESSAGE ROUTER
# =====================================================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot: return
    await bot.process_commands(message)

# =====================================================
# COG LOADER
# =====================================================

COGS = [
    "cogs.admin", "cogs.system", "cogs.botlog", "cogs.audit",
    "cogs.moderation", "cogs.warnsystem", "cogs.security", "cogs.automod",
    "cogs.staff", "cogs.support", "cogs.onboarding", "cogs.announce",
    "cogs.message_tracker", "cogs.profile", "cogs.weeklymvp", "cogs.dashboard",
    "cogs.voice_system", "cogs.clock"
]

async def load_cogs():
    for cog in COGS:
        if cog in bot.extensions: continue
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
    await load_cogs()

@bot.event
async def on_ready():
    print("---" * 10)
    print(f"🟢 BOT ONLINE: {bot.user}")
    
    # ENHANCEMENT: Force Clock Update immediately on Ready
    try:
        tz = pytz.timezone('UTC') # Change to your timezone
        time_str = datetime.now(tz).strftime("%I:%M %p")
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name=f"⛩️ {time_str} | HellFire"
            )
        )
        print(f"🕒 Clock Synced: {time_str}")
    except Exception as e:
        print(f"⚠️ Clock Sync Failed: {e}")

    print("---" * 10)

# =====================================================
# ENTRYPOINT
# =====================================================

async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Terminated.")
