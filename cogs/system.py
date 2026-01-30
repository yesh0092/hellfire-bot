import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_DANGER, COLOR_SECONDARY
from utils import state


class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

    # ================= HELP =================

    @commands.command()
    async def help(self, ctx):
        await ctx.send(
            embed=luxury_embed(
                title="🌙 Hellfire Hangout — Command Guide",
                description=(
                    "**🛎️ SUPPORT**\n"
                    "`support` → Open support via DM\n\n"
                    "**🛡️ MODERATION**\n"
                    "`!warn @user <reason>`\n"
                    "`!timeout @user <minutes> <reason>`\n"
                    "`!kick @user <reason>`\n"
                    "`!ban @user <reason>`\n\n"
                    "**⚙️ SYSTEM**\n"
                    "`!status` → Bot health\n"
                    "`!panic` / `!unpanic`\n\n"
                    "**📣 ADMIN**\n"
                    "`!welcome`\n"
                    "`!supportlog`\n"
                    "`!autorole @role`\n"
                    "`!announce <message>`"
                ),
                color=COLOR_GOLD
            )
        )

    # ================= STATUS =================

    @commands.command()
    async def status(self, ctx):
        uptime = datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)

        await ctx.send(
            embed=luxury_embed(
                title="📊 System Status",
                description=(
                    f"🟢 **Status:** Online\n"
                    f"⏱ **Uptime:** {hours}h {minutes}m {seconds}s\n"
                    f"🚨 **Panic Mode:** {'ON' if state.SYSTEM_FLAGS['panic_mode'] else 'OFF'}\n"
                    f"🧠 **Loaded Cogs:** {len(self.bot.cogs)}"
                ),
                color=COLOR_SECONDARY
            )
        )

    # ================= PANIC =================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def panic(self, ctx):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(
            embed=luxury_embed(
                title="🚨 PANIC MODE ENABLED",
                description="All non-critical systems are now restricted.",
                color=COLOR_DANGER
            )
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unpanic(self, ctx):
        state.SYSTEM_FLAGS["panic_mode"] = False
        await ctx.send(
            embed=luxury_embed(
                title="✅ Panic Mode Disabled",
                description="Systems restored to normal operation.",
                color=COLOR_GOLD
            )
        )


async def setup(bot):
    await bot.add_cog(System(bot))
