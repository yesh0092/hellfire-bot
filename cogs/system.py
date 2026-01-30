import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

    # =====================================================
    # HELP COMMAND (ULTIMATE)
    # =====================================================

    @commands.command()
    async def help(self, ctx):
        await ctx.send(
            embed=luxury_embed(
                title="🌙 Hellfire Hangout — Command Codex",
                description=(
                    "**🛎️ SUPPORT (USERS)**\n"
                    "`support` → Open support via DM\n"
                    "• Button-based tickets\n"
                    "• Auto status & priority\n"
                    "• Ticket logs & transcripts\n\n"

                    "**⚠️ MODERATION (STAFF)**\n"
                    "`!warn @user <reason>`\n"
                    "`!unwarn @user [count]`\n"
                    "`!timeout @user <minutes> <reason>`\n"
                    "`!kick @user <reason>`\n"
                    "`!ban @user <reason>`\n"
                    "• Progressive escalation\n"
                    "• Auto-DM before actions\n\n"

                    "**👮 STAFF SYSTEM**\n"
                    "• Staff / Staff+ / Staff++ / Staff+++\n"
                    "• Permission-based power\n"
                    "• Staff notes & workload tracking\n\n"

                    "**🛡️ SECURITY**\n"
                    "• Invite & spam protection\n"
                    "• Raid detection\n"
                    "• Panic & lockdown mode\n\n"

                    "**⚙️ ADMIN CONTROLS**\n"
                    "`!welcome` / `!unwelcome`\n"
                    "`!supportlog` / `!unsupportlog`\n"
                    "`!autorole @role` / `!unautorole`\n"
                    "`!setbotlog` / `!unsetbotlog`\n\n"

                    "**📣 ANNOUNCEMENTS**\n"
                    "`!announce <message>` → DM broadcast\n\n"

                    "**📊 SYSTEM**\n"
                    "`!status` → Bot health\n"
                    "`!panic` / `!unpanic`\n\n"

                    "_Most systems work silently to keep the experience clean, "
                    "professional, and fair._"
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================================
    # STATUS
    # =====================================================

    @commands.command()
    async def status(self, ctx):
        uptime = datetime.utcnow() - self.start_time
        h, r = divmod(int(uptime.total_seconds()), 3600)
        m, s = divmod(r, 60)

        await ctx.send(
            embed=luxury_embed(
                title="📊 System Status",
                description=(
                    f"🟢 **Status:** Online\n"
                    f"⏱ **Uptime:** {h}h {m}m {s}s\n"
                    f"🚨 **Panic Mode:** {'ON' if state.SYSTEM_FLAGS.get('panic_mode') else 'OFF'}\n"
                    f"🧠 **Loaded Cogs:** {len(self.bot.cogs)}"
                ),
                color=COLOR_SECONDARY
            )
        )

    # =====================================================
    # PANIC MODE
    # =====================================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def panic(self, ctx):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(
            embed=luxury_embed(
                title="🚨 PANIC MODE ENABLED",
                description="High-risk protections are now active.",
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
                description="All systems restored to normal operation.",
                color=COLOR_GOLD
            )
        )


async def setup(bot):
    await bot.add_cog(System(bot))
