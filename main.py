import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils import state
from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER

# =====================================================
# LOAD ENV
# =====================================================

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("❌ TOKEN not found in environment variables")

# =====================================================
# INTENTS (DO NOT REQUEST PRESENCES)
# =====================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.moderation = True
# ❌ DO NOT enable intents.presences

# =====================================================
# BOT
# =====================================================

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# =====================================================
# STAFF LEVEL RESOLUTION
# =====================================================

def get_user_level(member: discord.Member) -> int:
    if member.guild_permissions.administrator:
        return 99

    for level, role_id in state.STAFF_ROLE_TIERS.items():
        if role_id and any(role.id == role_id for role in member.roles):
            return level

    return 0

# =====================================================
# GLOBAL COMMAND GUARDS
# =====================================================

@bot.check
async def block_commands_in_dm(ctx: commands.Context) -> bool:
    if ctx.guild is None:
        try:
            await ctx.send(
                embed=luxury_embed(
                    title="❌ Commands Disabled",
                    description="Commands can only be used inside the server.",
                    color=COLOR_DANGER
                )
            )
        except discord.Forbidden:
            pass
        return False
    return True


@bot.check
async def strict_role_guard(ctx: commands.Context) -> bool:
    if await bot.is_owner(ctx.author):
        return True

    if not ctx.guild:
        return False

    user_level = get_user_level(ctx.author)
    if user_level <= 0:
        await ctx.send(
            embed=luxury_embed(
                title="❌ Permission Denied",
                description="You are not authorized to use this command.",
                color=COLOR_DANGER
            )
        )
        return False

    required_level = getattr(ctx.command.callback, "required_level", 1)
    if user_level < required_level:
        await ctx.send(
            embed=luxury_embed(
                title="❌ Insufficient Staff Level",
                description="Your staff level is too low for this command.",
                color=COLOR_DANGER
            )
        )
        return False

    return True

# =====================================================
# ERROR HANDLER
# =====================================================

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CheckFailure):
        return
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing required arguments.")
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Invalid argument provided.")
        return
    raise error

# =====================================================
# MESSAGE ROUTER (NO DOUBLE EXEC)
# =====================================================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    await bot.process_commands(message)

# =====================================================
# COG LOADER
# =====================================================

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
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed {cog}: {e}")

# =====================================================
# READY (THIS WILL NOW FIRE)
# =====================================================

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="HellFire Hangout 🔥"
        )
    )

    print(f"🌙 {bot.user} | HellFire Hangout ONLINE")
    print("🔒 Commands locked to server only")
    print("🛡 Staff guard active")
    print("⚙️ Single-pass command execution")
    print("🔊 Voice + Support systems active")

# =====================================================
# MAIN (RAILWAY SAFE)
# =====================================================

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
