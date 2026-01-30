import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ================= LOAD ENV =================

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
    help_command=None
)

# ================= STAFF ROLES =================

STAFF_ROLE_NAMES = {
    "Staff",
    "Staff+",
    "Staff++",
    "Staff+++"
}

# ================= GLOBAL STRICT GUARD =================

@bot.check
async def strict_command_guard(ctx: commands.Context) -> bool:
    """
    HARD BLOCK:
    - Normal users cannot run ANY command
    - No help, no status, no probing
    """

    # 1️⃣ Allow DMs (support system)
    if ctx.guild is None:
        return True

    # 2️⃣ Bot owner
    if await bot.is_owner(ctx.author):
        return True

    # 3️⃣ Administrator
    if ctx.author.guild_permissions.administrator:
        return True

    # 4️⃣ Moderation permissions
    perms = ctx.author.guild_permissions
    if (
        perms.manage_guild
        or perms.moderate_members
        or perms.kick_members
        or perms.ban_members
    ):
        return True

    # 5️⃣ Staff role ladder
    if any(role.name in STAFF_ROLE_NAMES for role in ctx.author.roles):
        return True

    # ❌ HARD DENY
    return False

# ================= COGS =================

COGS = [
    "cogs.system",
    "cogs.support",
    "cogs.moderation",
    "cogs.warn_system",
    "cogs.staff",
    "cogs.security",
    "cogs.onboarding",
    "cogs.audit",
    "cogs.admin",
    "cogs.announce",
    "cogs.botlog",
]

# ================= LOAD COGS =================

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed {cog}: {e}")

# ================= EVENTS =================

@bot.event
async def on_ready():
    print(f"🌙 {bot.user} | Hellfire Hangout ONLINE")

# ================= RUN =================

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())
