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
    # FULL HELP / COMPLETE COMMAND GUIDE
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
                title="🌌 HellFire Hangout — COMPLETE SYSTEM GUIDE",
                description=(

                    "This is the **official command & feature manual**.\n"
                    "Every system running in this server is documented below.\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🔑 BASIC INFO\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• Prefix: `{BOT_PREFIX}`\n"
                    "• Commands work **only in server**\n"
                    "• DMs are reserved for **support & onboarding**\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "👋 ONBOARDING SYSTEM\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Auto welcome message\n"
                    "• Interactive DM onboarding panel\n"
                    "• Auto role assignment (if set)\n\n"
                    "**Admin commands:**\n"
                    f"`{BOT_PREFIX}welcome` → set welcome channel\n"
                    f"`{BOT_PREFIX}unwelcome`\n"
                    f"`{BOT_PREFIX}autorole <role>`\n"
                    f"`{BOT_PREFIX}unautorole`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🛎️ SUPPORT SYSTEM (DM BASED)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "**User flow:**\n"
                    "• DM bot anything → panel opens\n"
                    "• Create ticket → private channel\n\n"
                    "**Staff/Admin:**\n"
                    f"`{BOT_PREFIX}supportlog` → set log channel\n"
                    f"`{BOT_PREFIX}unsupportlog`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📢 ANNOUNCEMENT SYSTEM\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}announce <message>`\n"
                    "• Sends DM announcement to all users\n"
                    "• Panic-mode safe\n"
                    "• Rate-limited & logged\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📊 PROFILE & STATS\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}profile [@user]`\n"
                    "• Weekly messages\n"
                    "• Total messages\n"
                    "• Join date\n"
                    "• Staff notes (staff only)\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🏆 WEEKLY TEXT MVP\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Fully automatic\n"
                    "• Most messages in a week wins\n"
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
                    f"`{BOT_PREFIX}automod on`\n"
                    f"`{BOT_PREFIX}automod off`\n"
                    f"`{BOT_PREFIX}automod status`\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🚨 PANIC MODE\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}panic`\n"
                    f"`{BOT_PREFIX}unpanic`\n"
                    "• Tightens all security limits\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⚠️ MODERATION COMMANDS\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}warn @user <reason>`\n"
                    f"`{BOT_PREFIX}timeout @user <minutes> <reason>`\n"
                    f"`{BOT_PREFIX}kick @user <reason>`\n"
                    f"`{BOT_PREFIX}ban @user <reason>`\n\n"
                    "**Auto escalation:**\n"
                    "• 3 warns → 24h timeout\n"
                    "• 5 warns → kick\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📜 WARN SYSTEM (READ ONLY)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}warnstats @user`\n"
                    "• View warning history\n"
                    "• Staff-only\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "👮 STAFF SYSTEM\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}note @user <note>`\n"
                    f"`{BOT_PREFIX}notes @user`\n"
                    f"`{BOT_PREFIX}staff`\n"
                    "• Staff activity tracking\n"
                    "• Burnout detection\n"
                    "• Abuse alerts to owner\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🎙️ VOICE SYSTEM (24/7)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}setvc <voice-channel>`\n"
                    f"`{BOT_PREFIX}unsetvc`\n"
                    f"`{BOT_PREFIX}vcstatus`\n"
                    "• Auto rejoin\n"
                    "• Muted & deafened\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📁 LOGGING & AUDIT\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Command usage logs\n"
                    "• Error logs\n"
                    "• Manual ban/kick/timeout detection\n"
                    "• Security logs\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⚙️ ADMIN SETUP\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}setup`\n"
                    "• Creates staff roles\n"
                    "• Sets bot-log channel\n"
                    "• Initializes system state\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📊 SYSTEM STATUS\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"`{BOT_PREFIX}status`\n"
                    "• Uptime\n"
                    "• Loaded systems\n"
                    "• Automod & panic state\n\n"

                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "🔮 UPCOMING SYSTEMS\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• 💰 Currency / economy\n"
                    "• 📈 Leveling & prestige\n"
                    "• 🎨 Anime visual themes\n"
                    "• 🤖 AI moderation layer\n\n"

                    "_Silent • Intelligent • Elite automation_"
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
