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

        # =========================
        # CORE SYSTEM FLAGS
        # =========================
        state.SYSTEM_FLAGS.setdefault("panic_mode", False)
        state.SYSTEM_FLAGS.setdefault("automod_enabled", True)

        # =========================
        # FEATURE FLAGS (INFO ONLY)
        # =========================
        state.SYSTEM_FLAGS.setdefault("mvp_system", True)
        state.SYSTEM_FLAGS.setdefault("profile_stats", True)
        state.SYSTEM_FLAGS.setdefault("message_tracking", True)

    # =====================================================
    # HELP / FEATURE GUIDE (STAFF)
    # =====================================================

    @commands.command(name="help")
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
                    "• Shows weekly message count\n"
                    "• Displays activity ranking\n"
                    "• Anyone can use this command\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**🏆 WEEKLY TEXT MVP SYSTEM**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Tracks weekly messages automatically\n"
                    "• Top chatter receives **Text MVP** role\n"
                    "• Role rotates every week\n"
                    "• Fully automatic (no staff action)\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**⚠️ MODERATION COMMANDS (STAFF)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}warn @user <reason>`\n"
                    "• Issues a warning\n"
                    "• Warnings auto-escalate\n\n"

                    f"`{BOT_PREFIX}timeout @user <minutes> <reason>`\n"
                    "• Temporarily mutes a user\n\n"

                    f"`{BOT_PREFIX}kick @user <reason>`\n"
                    "• Removes user from server\n\n"

                    f"`{BOT_PREFIX}ban @user <reason>`\n"
                    "• Permanently bans user\n\n"

                    "⚙️ **Auto Escalation Rules:**\n"
                    "• 3 warnings → 24h timeout\n"
                    "• 5 warnings → auto kick\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**🛡️ AUTOMOD SYSTEM (SILENT)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Detects message spam\n"
                    "• No slowmode used\n"
                    "• Applies user-level timeouts\n"
                    "• DM warning → timeout → escalation\n\n"

                    f"`{BOT_PREFIX}automod on`\n"
                    f"`{BOT_PREFIX}automod off`\n"
                    f"`{BOT_PREFIX}automod status`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**🧩 ROLE MANAGEMENT (STAFF++)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}role @user @role`\n"
                    "• Assigns a role manually\n"
                    "• Respects role hierarchy\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**🚨 PANIC MODE (STAFF+++)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}panic`\n"
                    "• Tightens spam thresholds\n"
                    "• Aggressive protection\n\n"

                    f"`{BOT_PREFIX}unpanic`\n"
                    "• Restores normal operation\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**📊 SYSTEM STATUS & LOGS**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}status`\n"
                    "• Bot uptime\n"
                    "• Feature states\n"
                    "• Loaded systems\n\n"

                    "📁 **Bot Logs**\n"
                    "• All actions logged silently\n"
                    "• Visible only to staff\n\n"

                    "_Luxury-grade, silent, enterprise moderation system._"
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
                    f"⏱ **Uptime:** {h}h {m}m {s}s\n\n"

                    f"🏆 **Weekly MVP:** {'ON' if state.SYSTEM_FLAGS.get('mvp_system') else 'OFF'}\n"
                    f"📊 **Message Tracking:** {'ON' if state.SYSTEM_FLAGS.get('message_tracking') else 'OFF'}\n"
                    f"🛡️ **AutoMod:** {'ON' if state.SYSTEM_FLAGS.get('automod_enabled') else 'OFF'}\n"
                    f"🚨 **Panic Mode:** {'ON' if state.SYSTEM_FLAGS.get('panic_mode') else 'OFF'}\n\n"

                    f"🧠 **Loaded Cogs:** {len(self.bot.cogs)}\n"
                    f"📁 **Bot Logs:** {'Enabled' if state.BOT_LOG_CHANNEL_ID else 'Disabled'}"
                ),
                color=COLOR_SECONDARY
            )
        )

    # =====================================================
    # AUTOMOD TOGGLE (STAFF+++)
    # =====================================================

    @commands.command()
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
            enabled = state.SYSTEM_FLAGS.get("automod_enabled", True)
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

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(luxury_embed(
            title="🚨 PANIC MODE ENABLED",
            description="Aggressive protection is now active.",
            color=COLOR_DANGER
        ))
        await self._log(ctx, "🚨 Panic mode enabled")

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = False
        await ctx.send(luxury_embed(
            title="✅ Panic Mode Disabled",
            description="System returned to normal operation.",
            color=COLOR_GOLD
        ))
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
