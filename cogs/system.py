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

        # =================================================
        # HARDEN GLOBAL STATE (CRITICAL FIX)
        # =================================================
        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {}

        state.SYSTEM_FLAGS.setdefault("panic_mode", False)
        state.SYSTEM_FLAGS.setdefault("automod_enabled", True)

        # Informational flags (read-only usage)
        state.SYSTEM_FLAGS.setdefault("mvp_system", True)
        state.SYSTEM_FLAGS.setdefault("profile_stats", True)
        state.SYSTEM_FLAGS.setdefault("message_tracking", True)

    # =====================================================
    # HELP / FEATURE GUIDE (STAFF)
    # =====================================================

    @commands.command(name="help", aliases=["syshelp"])
    @commands.guild_only()
    @require_level(1)
    async def system_help(self, ctx: commands.Context):
        """
        Complete feature & usage documentation
        """
        await ctx.send(
            embed=luxury_embed(
                title="🌙 HellFire Hangout — System Codex",
                description=(

                    f"**🔑 PREFIX**\n"
                    f"`{BOT_PREFIX}` is the global command prefix\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**🛎️ SUPPORT SYSTEM (USERS)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "`support`\n"
                    "• Opens support in DM\n"
                    "• One ticket per user\n"
                    "• Logged to support-log channel\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**📊 USER PROFILE & STATS**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}profile [@user]`\n"
                    "• Weekly message count\n"
                    "• Activity ranking\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**🏆 WEEKLY TEXT MVP**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Automatic weekly tracking\n"
                    "• Top chatter gets MVP role\n"
                    "• Auto-rotates every week\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**⚠️ MODERATION (STAFF)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}warn @user <reason>`\n"
                    f"`{BOT_PREFIX}timeout @user <minutes> <reason>`\n"
                    f"`{BOT_PREFIX}kick @user <reason>`\n"
                    f"`{BOT_PREFIX}ban @user <reason>`\n\n"

                    "⚙️ Auto escalation:\n"
                    "• 3 warns → 24h timeout\n"
                    "• 5 warns → kick\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**🛡️ AUTOMOD SYSTEM**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Spam detection\n"
                    "• No slowmode\n"
                    "• User-level timeouts\n\n"

                    f"`{BOT_PREFIX}automod on`\n"
                    f"`{BOT_PREFIX}automod off`\n"
                    f"`{BOT_PREFIX}automod status`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**🚨 PANIC MODE (STAFF+++)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}panic`\n"
                    f"`{BOT_PREFIX}unpanic`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**📊 SYSTEM**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}status`\n\n"

                    "_Silent • Clean • Enterprise-grade moderation_"
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================================
    # STATUS
    # =====================================================

    @commands.command(name="status")
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
                    "🟢 **Bot Online**\n"
                    f"⏱ **Uptime:** {h}h {m}m {s}s\n\n"
                    f"🛡️ **AutoMod:** {'ON' if state.SYSTEM_FLAGS['automod_enabled'] else 'OFF'}\n"
                    f"🚨 **Panic Mode:** {'ON' if state.SYSTEM_FLAGS['panic_mode'] else 'OFF'}\n\n"
                    f"🧠 **Loaded Cogs:** {len(self.bot.cogs)}\n"
                    f"📁 **Bot Logs:** {'Enabled' if state.BOT_LOG_CHANNEL_ID else 'Not Configured'}"
                ),
                color=COLOR_SECONDARY
            )
        )

    # =====================================================
    # AUTOMOD TOGGLE
    # =====================================================

    @commands.command(name="automod")
    @commands.guild_only()
    @require_level(4)
    async def automod(self, ctx: commands.Context, mode: str = None):
        if not mode:
            return await ctx.send(
                embed=luxury_embed(
                    title="⚙️ AutoMod Control",
                    description=(
                        f"`{BOT_PREFIX}automod on`\n"
                        f"`{BOT_PREFIX}automod off`\n"
                        f"`{BOT_PREFIX}automod status`"
                    ),
                    color=COLOR_SECONDARY
                )
            )

        mode = mode.lower()

        if mode == "on":
            state.SYSTEM_FLAGS["automod_enabled"] = True
            await ctx.send(luxury_embed(
                title="🛡️ AutoMod Enabled",
                description="Automatic moderation is now active.",
                color=COLOR_GOLD
            ))
            await self._log(ctx, "🛡️ AutoMod enabled")

        elif mode == "off":
            state.SYSTEM_FLAGS["automod_enabled"] = False
            await ctx.send(luxury_embed(
                title="⛔ AutoMod Disabled",
                description="Automatic moderation is now disabled.",
                color=COLOR_DANGER
            ))
            await self._log(ctx, "⛔ AutoMod disabled")

        elif mode == "status":
            enabled = state.SYSTEM_FLAGS["automod_enabled"]
            await ctx.send(luxury_embed(
                title="🛡️ AutoMod Status",
                description=f"State: {'ON ✅' if enabled else 'OFF ❌'}",
                color=COLOR_SECONDARY
            ))

        else:
            await ctx.send(luxury_embed(
                title="❌ Invalid Option",
                description="Use `on`, `off`, or `status`.",
                color=COLOR_DANGER
            ))

    # =====================================================
    # PANIC MODE
    # =====================================================

    @commands.command(name="panic")
    @commands.guild_only()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(luxury_embed(
            title="🚨 Panic Mode Enabled",
            description="Aggressive protection active.",
            color=COLOR_DANGER
        ))
        await self._log(ctx, "🚨 Panic mode enabled")

    @commands.command(name="unpanic")
    @commands.guild_only()
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = False
        await ctx.send(luxury_embed(
            title="✅ Panic Mode Disabled",
            description="Normal operation restored.",
            color=COLOR_GOLD
        ))
        await self._log(ctx, "✅ Panic mode disabled")

    # =====================================================
    # INTERNAL LOGGER (SAFE)
    # =====================================================

    async def _log(self, ctx: commands.Context, message: str):
        if not state.BOT_LOG_CHANNEL_ID:
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