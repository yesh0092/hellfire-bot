import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state


class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

        # 🔒 NEVER reassign — only mutate
        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {}

        state.SYSTEM_FLAGS.setdefault("panic_mode", False)

    # =====================================================
    # HELP (STAFF ONLY)
    # =====================================================

    @commands.command(name="help", help="Show HellFire Hangout command list")
    @commands.guild_only()
    @require_level(1)  # Staff
    async def system_help(self, ctx: commands.Context):
        await ctx.send(
            embed=luxury_embed(
                title="🌙 HellFire Hangout — Command Codex",
                description=(
                    "**🛎️ SUPPORT (USERS)**\n"
                    "`support` → Open support via DM\n"
                    "• Button-based tickets\n"
                    "• Auto status & priority\n\n"

                    "**⚠️ MODERATION (STAFF)**\n"
                    "`!warn @user <reason>`\n"
                    "`!unwarn @user [count]`\n"
                    "`!timeout @user <minutes> <reason>`\n"
                    "`!kick @user <reason>`\n"
                    "`!ban @user <reason>`\n\n"

                    "**👮 STAFF SYSTEM**\n"
                    "• Role-tier enforcement\n"
                    "• Staff notes & workload tracking\n\n"

                    "**🔊 VOICE PRESENCE**\n"
                    "`!setvc <channel>` / `!unsetvc`\n"
                    "`!vcstatus`\n\n"

                    "**🛡️ SECURITY**\n"
                    "• Invite & spam protection\n"
                    "• Raid detection\n"
                    "• Panic mode\n\n"

                    "**⚙️ ADMIN (STAFF+++)**\n"
                    "`!setup`\n"
                    "`!welcome` / `!unwelcome`\n"
                    "`!supportlog` / `!unsupportlog`\n"
                    "`!autorole` / `!unautorole`\n\n"

                    "**📣 ANNOUNCEMENTS**\n"
                    "`!announce <message>`\n\n"

                    "**📊 SYSTEM**\n"
                    "`!status`\n"
                    "`!panic` / `!unpanic`\n\n"

                    "_Designed for silent, luxury-grade moderation._"
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================================
    # STATUS
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(1)
    async def status(self, ctx: commands.Context):
        uptime = datetime.utcnow() - self.start_time
        h, r = divmod(int(uptime.total_seconds()), 3600)
        m, s = divmod(r, 60)

        await ctx.send(
            embed=luxury_embed(
                title="📊 System Status",
                description=(
                    f"🟢 **Bot Status:** Online\n"
                    f"⏱ **Uptime:** {h}h {m}m {s}s\n"
                    f"🚨 **Panic Mode:** {'ON' if state.SYSTEM_FLAGS.get('panic_mode') else 'OFF'}\n"
                    f"🔊 **Voice Presence:** {'ON' if getattr(state, 'VOICE_STAY_ENABLED', False) else 'OFF'}\n"
                    f"🧠 **Loaded Cogs:** {len(self.bot.cogs)}\n"
                    f"📁 **Bot Logs:** {'Enabled' if state.BOT_LOG_CHANNEL_ID else 'Disabled'}"
                ),
                color=COLOR_SECONDARY
            )
        )

    # =====================================================
    # PANIC MODE
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True

        await ctx.send(
            embed=luxury_embed(
                title="🚨 PANIC MODE ENABLED",
                description=(
                    "High-risk protections are now active.\n\n"
                    "• Aggressive spam limits\n"
                    "• Elevated moderation sensitivity"
                ),
                color=COLOR_DANGER
            )
        )

        await self._log(ctx, "🚨 Panic mode enabled")

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = False

        await ctx.send(
            embed=luxury_embed(
                title="✅ Panic Mode Disabled",
                description="All systems restored to normal operation.",
                color=COLOR_GOLD
            )
        )

        await self._log(ctx, "✅ Panic mode disabled")

    # =====================================================
    # INTERNAL LOGGER
    # =====================================================

    async def _log(self, ctx: commands.Context, message: str):
        if not ctx.guild or not state.BOT_LOG_CHANNEL_ID:
            return

        channel = ctx.guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        try:
            await channel.send(
                embed=luxury_embed(
                    title="📁 System Log",
                    description=f"{message}\n\n**By:** {ctx.author.mention}",
                    color=COLOR_SECONDARY
                )
            )
        except (discord.Forbidden, discord.HTTPException):
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))
