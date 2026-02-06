import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state

BOT_PREFIX = "&"  # SINGLE SOURCE OF TRUTH


class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

        # =================================================
        # HARDEN GLOBAL STATE (NEVER REMOVE)
        # =================================================
        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {}

        state.SYSTEM_FLAGS.setdefault("panic_mode", False)
        state.SYSTEM_FLAGS.setdefault("automod_enabled", True)

        # Informational / future flags
        state.SYSTEM_FLAGS.setdefault("mvp_system", True)
        state.SYSTEM_FLAGS.setdefault("profile_stats", True)
        state.SYSTEM_FLAGS.setdefault("message_tracking", True)
        state.SYSTEM_FLAGS.setdefault("currency_system", False)
        state.SYSTEM_FLAGS.setdefault("leveling_system", False)

    # =====================================================
    # GOD-LEVEL HELP / FULL DOCUMENTATION
    # =====================================================

    @commands.command(name="help", aliases=["syshelp", "guide", "manual"])
    @commands.guild_only()
    @require_level(1)
    async def system_help(self, ctx: commands.Context):
        """
        Full interactive documentation & tutorial
        """

        await ctx.send(
            embed=luxury_embed(
                title="🌌 HellFire Hangout — SYSTEM CODEX",
                description=(

                    "Welcome to **HellFire Hangout**.\n"
                    "This is not a normal bot — this is a **silent, intelligent automation core**.\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🔑 **BASIC USAGE**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• **Prefix:** `{BOT_PREFIX}`\n"
                    "• Commands work **only inside the server**\n"
                    "• DMs are reserved for **support & onboarding**\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🛎️ **SUPPORT SYSTEM (USERS)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**How to use:**\n"
                    "1️⃣ DM the bot anything\n"
                    "2️⃣ Click **Create Ticket**\n"
                    "3️⃣ Private channel opens automatically\n\n"
                    "• One ticket per user\n"
                    "• Logged to staff & support logs\n"
                    "• Auto-closes after inactivity\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "👋 **ONBOARDING SYSTEM**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Automatic welcome message\n"
                    "• Interactive DM onboarding panel\n"
                    "• Auto role assignment (if enabled)\n"
                    "• Clean & non-intrusive\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📊 **PROFILE & ACTIVITY**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}profile [@user]`\n"
                    "• Weekly messages\n"
                    "• Lifetime messages\n"
                    "• Join date\n"
                    "• Staff notes (staff only)\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🏆 **WEEKLY TEXT MVP SYSTEM**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Fully automatic\n"
                    "• Top chatter each week wins MVP role\n"
                    "• Resets weekly\n"
                    "• No staff action required\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⚠️ **MODERATION SYSTEM (STAFF)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}warn @user <reason>`\n"
                    f"`{BOT_PREFIX}timeout @user <minutes> <reason>`\n"
                    f"`{BOT_PREFIX}kick @user <reason>`\n"
                    f"`{BOT_PREFIX}ban @user <reason>`\n\n"
                    "**Auto escalation:**\n"
                    "• 3 warns → 24h timeout\n"
                    "• 5 warns → auto kick\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🛡️ **AUTOMOD (SILENT GOD MODE)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Message spam\n"
                    "• Emoji spam\n"
                    "• Caps abuse\n"
                    "• Duplicate messages\n"
                    "• Mass mentions\n\n"
                    "⚠️ **NO SLOWMODE USED**\n"
                    "Only **user-level timeouts**\n\n"
                    f"`{BOT_PREFIX}automod on / off / status`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🚨 **PANIC MODE (STAFF+++)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}panic`\n"
                    "• Tightens all thresholds\n"
                    "• Raid & spam defense mode\n\n"
                    f"`{BOT_PREFIX}unpanic`\n"
                    "• Restores normal operation\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🎙️ **VOICE SYSTEM (24/7)**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}setvc <channel>`\n"
                    f"`{BOT_PREFIX}unsetvc`\n"
                    f"`{BOT_PREFIX}vcstatus`\n\n"
                    "• Auto reconnect\n"
                    "• Muted & deafened\n"
                    "• Never leaves unless told\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "👮 **STAFF INTELLIGENCE**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Staff action tracking\n"
                    "• Burnout detection\n"
                    "• Abuse alerts (private)\n"
                    "• Internal staff notes\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📁 **LOGGING & AUDIT**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Command logs\n"
                    "• Error logs\n"
                    "• Manual moderation detection\n"
                    "• Silent user notifications\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🔮 **UPCOMING FEATURES**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• 💰 Server currency (Inferno Coins)\n"
                    "• 📈 Leveling & prestige system\n"
                    "• 🎨 Anime visual themes\n"
                    "• 🤖 AI-assisted moderation\n"
                    "• 🧠 Smart toxicity profiling\n\n"

                    "_HellFire Hangout is not a bot.\n"
                    "It is an **autonomous system**._"
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
                    "🟢 **Status:** Online\n"
                    f"⏱ **Uptime:** {h}h {m}m {s}s\n\n"

                    f"🛡️ **AutoMod:** {'ON' if state.SYSTEM_FLAGS['automod_enabled'] else 'OFF'}\n"
                    f"🚨 **Panic Mode:** {'ON' if state.SYSTEM_FLAGS['panic_mode'] else 'OFF'}\n"
                    f"🏆 **Weekly MVP:** {'ON' if state.SYSTEM_FLAGS['mvp_system'] else 'OFF'}\n"
                    f"📊 **Message Tracking:** {'ON' if state.SYSTEM_FLAGS['message_tracking'] else 'OFF'}\n\n"

                    f"🧠 **Loaded Cogs:** {len(self.bot.cogs)}\n"
                    f"📁 **Bot Logs:** {'Configured' if state.BOT_LOG_CHANNEL_ID else 'Not Set'}"
                ),
                color=COLOR_SECONDARY
            )
        )

    # =====================================================
    # AUTOMOD TOGGLE
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

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(luxury_embed(
            title="🚨 Panic Mode Enabled",
            description="Maximum protection activated.",
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
            description="System restored to normal operation.",
            color=COLOR_GOLD
        ))
        await self._log(ctx, "✅ Panic mode disabled")

    # =====================================================
    # INTERNAL LOGGER
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
