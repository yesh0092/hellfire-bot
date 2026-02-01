import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state


BOT_PREFIX = "&"  # 🔥 SINGLE SOURCE OF TRUTH


class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

        # 🔒 Never reassign, only mutate
        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {}

        state.SYSTEM_FLAGS.setdefault("panic_mode", False)

    # =====================================================
    # HELP (STAFF ONLY)
    # =====================================================

    @commands.command(name="help")
    @commands.guild_only()
    @require_level(1)  # Staff
    async def system_help(self, ctx: commands.Context):
        await ctx.send(
            embed=luxury_embed(
                title="🌙 HellFire Hangout — Command Codex",
                description=(
                    f"**🔑 Active Prefix:** `{BOT_PREFIX}`\n\n"

                    "**🛎️ SUPPORT (USERS)**\n"
                    "`support` → Open support via DM\n"
                    "• Button-based tickets\n"
                    "• Auto status & priority\n\n"

                    "**⚠️ MODERATION (STAFF)**\n"
                    f"`{BOT_PREFIX}warn @user <reason>`\n"
                    f"`{BOT_PREFIX}unwarn @user [count]`\n"
                    f"`{BOT_PREFIX}timeout @user <minutes> <reason>`\n"
                    f"`{BOT_PREFIX}kick @user <reason>`\n"
                    f"`{BOT_PREFIX}ban @user <reason>`\n\n"

                    "**👮 STAFF SYSTEM**\n"
                    "• Role-tier enforcement\n"
                    "• Staff notes & workload tracking\n\n"

                    "**🔊 VOICE PRESENCE**\n"
                    f"`{BOT_PREFIX}setvc <voice_channel>`\n"
                    f"`{BOT_PREFIX}unsetvc`\n"
                    f"`{BOT_PREFIX}vcstatus`\n\n"

                    "**🛡️ SECURITY**\n"
                    "• Invite & spam protection\n"
                    "• Raid detection\n"
                    "• Panic mode\n\n"

                    "**⚙️ ADMIN (STAFF+++)**\n"
                    f"`{BOT_PREFIX}setup`\n"
                    f"`{BOT_PREFIX}welcome` / `{BOT_PREFIX}unwelcome`\n"
                    f"`{BOT_PREFIX}supportlog` / `{BOT_PREFIX}unsupportlog`\n"
                    f"`{BOT_PREFIX}autorole` / `{BOT_PREFIX}unautorole`\n\n"

                    "**📣 ANNOUNCEMENTS**\n"
                    f"`{BOT_PREFIX}announce <message>`\n\n"

                    "**📊 SYSTEM**\n"
                    f"`{BOT_PREFIX}status`\n"
                    f"`{BOT_PREFIX}panic` / `{BOT_PREFIX}unpanic`\n\n"

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
                    "🟢 **Bot Status:** Online\n"
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
    # PANIC MODE (STAFF+++)
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
