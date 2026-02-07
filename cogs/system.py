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
            discord.SelectOption(label="Moderation", emoji="🛡️", description="Bans, Kicks, Timeouts & Automod", value="mod"),
            discord.SelectOption(label="Support System", emoji="🛎️", description="Ticket system & DM interaction", value="support"),
            discord.SelectOption(label="Activity & Stats", emoji="📊", description="Profiles, MVP & Message tracking", value="stats"),
            discord.SelectOption(label="Voice System", emoji="🎙️", description="24/7 Voice & status tracking", value="voice"),
        ]
        super().__init__(placeholder="🌌 Select a Department to view commands...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        
        # Mapping categories to content
        pages = {
            "admin": {
                "title": "⚙️ Admin & Setup Commands",
                "desc": (
                    f"**{BOT_PREFIX}setup**\nRun full server environment setup.\n\n"
                    f"**{BOT_PREFIX}welcome** / **{BOT_PREFIX}unwelcome**\nToggle the automated welcome system.\n\n"
                    f"**{BOT_PREFIX}autorole <role>** / **{BOT_PREFIX}unautorole**\nManage roles assigned to joining members.\n\n"
                    f"**{BOT_PREFIX}supportlog** / **{BOT_PREFIX}unsupportlog**\nConfigure where ticket logs are sent."
                )
            },
            "mod": {
                "title": "🛡️ Moderation & Security",
                "desc": (
                    f"**{BOT_PREFIX}warn @user <reason>**\nAssign a formal warning.\n\n"
                    f"**{BOT_PREFIX}timeout @user <min> <reason>**\nTemporary mute via Discord native timeout.\n\n"
                    f"**{BOT_PREFIX}kick @user <reason>**\nRemove member from the server.\n\n"
                    f"**{BOT_PREFIX}ban @user <reason>**\nPermanent removal and blacklist.\n\n"
                    "**Hierarchy Escalation:**\n"
                    "• 3 Warnings → 24h Timeout\n"
                    "• 5 Warnings → Immediate Kick"
                )
            },
            "support": {
                "title": "🛎️ Support & System Control",
                "desc": (
                    f"**{BOT_PREFIX}status**\nCheck system uptime and module health.\n\n"
                    f"**{BOT_PREFIX}automod <on|off|status>**\nToggle the silent security layer.\n\n"
                    f"**{BOT_PREFIX}panic** / **{BOT_PREFIX}unpanic**\nEmergency lockdown protocol.\n\n"
                    "**User Support:**\n"
                    "• Users can DM the bot directly to open a ticket."
                )
            },
            "stats": {
                "title": "📊 Profile & Engagement",
                "desc": (
                    f"**{BOT_PREFIX}profile [@user]**\nView detailed activity and join stats.\n\n"
                    f"**{BOT_PREFIX}warnstats @user**\nView infraction history for a member.\n\n"
                    f"**{BOT_PREFIX}staff**\nTrack staff activity and abuse alerts.\n\n"
                    "**Automated MVP:**\n"
                    "• Weekly top-talker role is auto-assigned."
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
            description=page["desc"] + "\n\n━━━━━━━━━━━━━━━━━━━━━━\n_Silent • Intelligent • Elite Automation_",
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
            title="🌌 HellFire Hangout — COMPLETE COMMAND GUIDE",
            description=(
                "This is the **official system manual**.\n"
                "Please select a department from the dropdown menu below to view available commands.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔑 **BASIC INFORMATION**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• Prefix: `{BOT_PREFIX}`\n"
                "• Interaction Mode: `Slash & Prefix`\n"
                "• Operational Status: `🟢 Healthy`"
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
