import discord
from discord.ext import commands
from discord import ui
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state

BOT_PREFIX = "&"

# =====================================================
# THE INTERACTIVE HELP COMPONENTS
# =====================================================

class HelpDropdown(ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Admin & Setup", emoji="⚙️", description="Server configuration & auto-systems", value="admin"),
            discord.SelectOption(label="Ultimate Moderation", emoji="🛡️", description="Bans, Risk Analysis & Warn Progression", value="mod"),
            discord.SelectOption(label="Ultimate Support", emoji="🛎️", description="Transcripts, Claiming & Priority Tickets", value="support"),
            discord.SelectOption(label="Activity & Stats", emoji="📊", description="Profiles, MVP & Staff Analytics", value="stats"),
            discord.SelectOption(label="Voice System", emoji="🎙️", description="24/7 Voice & status tracking", value="voice"),
        ]
        super().__init__(placeholder="🌌 Select a Department to view commands...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        
        # Mapping categories to content (Enhanced with new features)
        pages = {
            "admin": {
                "title": "⚙️ Admin & Setup Commands",
                "desc": (
                    f"**{BOT_PREFIX}setup**\nRun full server environment setup.\n\n"
                    f"**{BOT_PREFIX}welcome** / **{BOT_PREFIX}unwelcome**\nToggle the automated welcome system.\n\n"
                    f"**{BOT_PREFIX}autorole <role>** / **{BOT_PREFIX}unautorole**\nManage roles assigned to joining members.\n\n"
                    f"**{BOT_PREFIX}supportlog**\nSet the channel for ticket transcripts & logs."
                )
            },
            "mod": {
                "title": "🛡️ Ultimate Moderation & Intelligence",
                "desc": (
                    f"**{BOT_PREFIX}warn @user <reason>**\nAssign warning with auto-escalation.\n\n"
                    f"**{BOT_PREFIX}warnstats @user**\nView **Risk Level**, **Velocity**, and **Progress Bar**.\n\n"
                    f"**{BOT_PREFIX}warnhistory @user**\nView detailed audit trail of all violations.\n\n"
                    f"**{BOT_PREFIX}timeout / kick / ban**\nStandard enforcement commands.\n\n"
                    "**God-Mode Intelligence:**\n"
                    "• Visual Progress: `🟥🟥🟥⬜⬜` (Warns/8)\n"
                    "• Velocity: Alerts staff to rapid rule-breakers."
                )
            },
            "support": {
                "title": "🛎️ Ultimate Support System",
                "desc": (
                    f"**DM the Bot**\nSelect Priority (Low/Med/High) to open a ticket.\n\n"
                    "**Ticket Controls (Buttons):**\n"
                    "• 🙋‍♂️ **Claim:** Staff can claim to manage the user.\n"
                    "• 🔒 **Close:** Generates a full **Transcript (.txt)** log.\n\n"
                    "**Automated Systems:**\n"
                    "• **Ghost-Tracking:** Updates activity on every message.\n"
                    "• **Auto-Archive:** Inactive tickets log & delete after 24h."
                )
            },
            "stats": {
                "title": "📊 Analytics & Engagement",
                "desc": (
                    f"**{BOT_PREFIX}profile [@user]**\nView activity and join stats.\n\n"
                    f"**{BOT_PREFIX}warnboard**\nTop offenders & **Staff Enforcer Metrics**.\n\n"
                    f"**{BOT_PREFIX}mywarns**\nUser-safe account health check.\n\n"
                    "**Efficiency Layer:**\n"
                    "• **Auto-Pruning:** Background cleanup of stale data."
                )
            },
            "voice": {
                "title": "🎙️ Voice System (24/7)",
                "desc": (
                    f"**{BOT_PREFIX}setvc <channel>**\nLock the bot into a 24/7 voice channel.\n\n"
                    f"**{BOT_PREFIX}unsetvc**\nRelease the voice channel lock.\n\n"
                    f"**{BOT_PREFIX}vcstatus**\nView voice stream health and connection."
                )
            }
        }

        page = pages[selection]
        embed = luxury_embed(
            title=page["title"],
            description=page["desc"] + "\n\n━━━━━━━━━━━━━━━━━━━━━━\n_Ultimate • Intelligent • Elite Automation_",
            color=COLOR_GOLD
        )
        
        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.add_item(HelpDropdown(bot))

# =====================================================
# THE SYSTEM COG (UNTRIMMED)
# =====================================================

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
    # INTERACTIVE HELP / COMMAND MANUAL
    # ==================================================

    @commands.command(
        name="help",
        aliases=["syshelp", "guide", "manual", "commands"]
    )
    @commands.guild_only()
    @require_level(1)
    async def help(self, ctx: commands.Context):
        """The New Interactive Help Dashboard"""
        embed = luxury_embed(
            title="🌌 HellFire Hangout — ULTIMATE MANUAL",
            description=(
                "Welcome to the **Unified Intelligence Dashboard**.\n"
                "The system has been upgraded with **God-Mode** analytics.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔑 **CORE STATS**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• Prefix: `{BOT_PREFIX}`\n"
                f"• Intelligence Level: `Ultimate`\n"
                "• Operational Status: `🟢 100% Functional`"
            ),
            color=COLOR_GOLD
        )
        
        view = HelpView(self.bot)
        await ctx.send(embed=embed, view=view)

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

        # Build dynamic status
        embed = luxury_embed(
            title="📊 Ultimate System Health",
            description=(
                f"⏱ **Uptime:** `{h}h {m}m {s}s`\n"
                f"🧠 **Memory Threads:** `Active`\n\n"
                f"🛡 **AutoMod:** {'`🟢 ACTIVE`' if state.SYSTEM_FLAGS['automod_enabled'] else '`🔴 DISABLED`'}\n"
                f"🚨 **Panic Mode:** {'`🔴 ON`' if state.SYSTEM_FLAGS['panic_mode'] else '`🟢 OFF`'}\n"
                f"🏆 **MVP Tracker:** {'`🟢 ON`' if state.SYSTEM_FLAGS['mvp_system'] else '`⚪ OFF`'}\n\n"
                f"🧩 **Total Modules:** `{len(self.bot.cogs)}`"
            ),
            color=COLOR_SECONDARY
        )
        await ctx.send(embed=embed)

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
                    title="⚙️ AutoMod Control",
                    description=(
                        f"`{BOT_PREFIX}automod on` - Enable shield\n"
                        f"`{BOT_PREFIX}automod off` - Disable shield\n"
                        f"`{BOT_PREFIX}automod status` - View health"
                    ),
                    color=COLOR_SECONDARY
                )
            )

        mode = mode.lower()
        if mode == "on":
            state.SYSTEM_FLAGS["automod_enabled"] = True
            await ctx.send(luxury_embed("🛡️ AutoMod Enabled", "Global security layer is now active.", color=COLOR_GOLD))
        elif mode == "off":
            state.SYSTEM_FLAGS["automod_enabled"] = False
            await ctx.send(luxury_embed("⛔ AutoMod Disabled", "Security protocol is now paused.", color=COLOR_DANGER))
        elif mode == "status":
            await ctx.send(luxury_embed("🛡️ AutoMod Status", f"Current: {'ACTIVE' if state.SYSTEM_FLAGS['automod_enabled'] else 'DISABLED'}", COLOR_SECONDARY))

    # ==================================================
    # PANIC MODE
    # ==================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(luxury_embed("🚨 PANIC MODE ACTIVATED", "Lockdown initiated. Permissions restricted.", color=COLOR_DANGER))

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = False
        await ctx.send(luxury_embed("✅ PANIC MODE DEACTIVATED", "Lockdown lifted. Resuming normal operations.", color=COLOR_GOLD))

async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))
