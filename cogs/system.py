import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state

BOT_PREFIX = "&"


class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

        # ================= HARDEN STATE =================
        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {}

        state.SYSTEM_FLAGS.setdefault("panic_mode", False)
        state.SYSTEM_FLAGS.setdefault("automod_enabled", True)
        state.SYSTEM_FLAGS.setdefault("mvp_system", True)
        state.SYSTEM_FLAGS.setdefault("profile_stats", True)
        state.SYSTEM_FLAGS.setdefault("message_tracking", True)

    # ==================================================
    # COMPLETE HELP / COMMAND MANUAL
    # ==================================================

    @commands.command(
        name="help",
        aliases=["syshelp", "guide", "manual", "commands"]
    )
    @commands.guild_only()
    @require_level(1)
    async def help(self, ctx: commands.Context):
        await ctx.send(
            embed=luxury_embed(
                title="🌌 HellFire Hangout — COMPLETE COMMAND GUIDE",
                description=(

                    "This is the **official system manual**.\n"
                    "Everything this bot can do is listed below.\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🔑 BASIC INFORMATION\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• Prefix: `{BOT_PREFIX}`\n"
                    "• Commands work **inside the server only**\n"
                    "• DMs are used for **support & onboarding**\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⚙️ ADMIN / SETUP COMMANDS\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}setup`\n"
                    f"`{BOT_PREFIX}welcome` / `{BOT_PREFIX}unwelcome`\n"
                    f"`{BOT_PREFIX}autorole <role>` / `{BOT_PREFIX}unautorole`\n"
                    f"`{BOT_PREFIX}supportlog` / `{BOT_PREFIX}unsupportlog`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🛎️ SUPPORT SYSTEM (USERS)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• DM the bot **any message**\n"
                    "• Click **Create Ticket**\n"
                    "• Private staff channel opens\n"
                    "• Auto-close after inactivity\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📢 ANNOUNCEMENTS (STAFF+++)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}announce <message>`\n"
                    "• Sends DM to all members\n"
                    "• Panic-mode protected\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📊 PROFILE & USER STATS\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}profile`\n"
                    f"`{BOT_PREFIX}profile @user`\n"
                    "• Weekly messages\n"
                    "• Total messages\n"
                    "• Join date\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🏆 WEEKLY TEXT MVP (AUTO)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Highest weekly messages wins\n"
                    "• Role auto-assigned\n"
                    "• Weekly reset\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🛡️ AUTOMOD (SILENT)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Auto detects:\n"
                    "• Spam\n"
                    "• Duplicate messages\n"
                    "• Caps abuse\n"
                    "• Emoji spam\n"
                    "• Mass mentions\n\n"
                    f"`{BOT_PREFIX}automod on | off | status`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🚨 PANIC MODE (STAFF+++)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}panic`\n"
                    f"`{BOT_PREFIX}unpanic`\n"
                    "• Aggressive security thresholds\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⚠️ MODERATION COMMANDS\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}warn @user <reason>`\n"
                    f"`{BOT_PREFIX}timeout @user <minutes> <reason>`\n"
                    f"`{BOT_PREFIX}kick @user <reason>`\n"
                    f"`{BOT_PREFIX}ban @user <reason>`\n\n"
                    "Auto escalation:\n"
                    "• 3 warns → 24h timeout\n"
                    "• 5 warns → kick\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📜 WARN HISTORY (STAFF)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}warnstats @user`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "👮 STAFF SYSTEM\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}note @user <note>`\n"
                    f"`{BOT_PREFIX}notes @user`\n"
                    f"`{BOT_PREFIX}staff`\n"
                    "• Activity tracking\n"
                    "• Burnout alerts\n"
                    "• Abuse detection\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🎙️ VOICE SYSTEM (24/7)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}setvc <voice-channel>`\n"
                    f"`{BOT_PREFIX}unsetvc`\n"
                    f"`{BOT_PREFIX}vcstatus`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📁 LOGGING & AUDIT (AUTO)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Command usage logs\n"
                    "• Error logs\n"
                    "• Manual kick/ban/timeout detection\n"
                    "• Security events\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📊 SYSTEM STATUS\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}status`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🔮 UPCOMING SYSTEMS\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• 💰 Server currency & economy\n"
                    "• 📈 Leveling & prestige\n"
                    "• 🎨 Anime UI themes\n"
                    "• 🤖 AI moderation layer\n\n"

                    "_Silent • Intelligent • Elite Automation_"
                ),
                color=COLOR_GOLD
            )
        )

    # ==================================================
    # STATUS
    # ==================================================

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
                    f"🟢 Online\n"
                    f"⏱ Uptime: {h}h {m}m {s}s\n\n"
                    f"🛡 AutoMod: {'ON' if state.SYSTEM_FLAGS['automod_enabled'] else 'OFF'}\n"
                    f"🚨 Panic Mode: {'ON' if state.SYSTEM_FLAGS['panic_mode'] else 'OFF'}\n"
                    f"🏆 MVP System: {'ON' if state.SYSTEM_FLAGS['mvp_system'] else 'OFF'}\n\n"
                    f"🧠 Loaded Cogs: {len(self.bot.cogs)}"
                ),
                color=COLOR_SECONDARY
            )
        )

    # ==================================================
    # AUTOMOD CONTROL
    # ==================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def automod(self, ctx: commands.Context, mode: str = None):
        if not mode:
            return await ctx.send(
                embed=luxury_embed(
                    title="⚙️ AutoMod Usage",
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
            await ctx.send(luxury_embed("🛡️ AutoMod Enabled", "System is active.", color=COLOR_GOLD))

        elif mode == "off":
            state.SYSTEM_FLAGS["automod_enabled"] = False
            await ctx.send(luxury_embed("⛔ AutoMod Disabled", "System is paused.", color=COLOR_DANGER))

        elif mode == "status":
            await ctx.send(
                luxury_embed(
                    "🛡️ AutoMod Status",
                    f"State: {'ON' if state.SYSTEM_FLAGS['automod_enabled'] else 'OFF'}",
                    color=COLOR_SECONDARY
                )
            )

    # ==================================================
    # PANIC MODE
    # ==================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(luxury_embed("🚨 Panic Mode Enabled", "Maximum protection active.", color=COLOR_DANGER))

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = False
        await ctx.send(luxury_embed("✅ Panic Mode Disabled", "Normal operation restored.", color=COLOR_GOLD))


async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))
