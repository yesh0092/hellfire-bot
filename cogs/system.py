import discord
from discord.ext import commands, tasks
from discord import ui
import asyncio
import time
import platform
from datetime import datetime

# Safety import for hardware diagnostics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

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
            discord.SelectOption(label="Admin & Setup", emoji="⚙️", description="Server config & panic controls", value="admin"),
            discord.SelectOption(label="Ultimate Moderation", emoji="🛡️", description="Risk Analysis & Warn Logic", value="mod"),
            discord.SelectOption(label="Support & System", emoji="🛎️", description="Transcripts & Tickets", value="system"),
            discord.SelectOption(label="Stats & Activity", emoji="📊", description="User Intel & Profiles", value="stats"),
            discord.SelectOption(label="Voice System", emoji="🎙️", description="24/7 Voice & Health", value="voice"),
        ]
        super().__init__(placeholder="🌌 Select a Department to view commands...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        
        pages = {
            "admin": {
                "title": "⚙️ Admin & Setup Commands",
                "desc": (
                    f"**{BOT_PREFIX}setup** - Run full server sync.\n"
                    f"**{BOT_PREFIX}welcome / unwelcome** - Toggle welcome messages.\n"
                    f"**{BOT_PREFIX}autorole <role>** - Set auto-join role.\n"
                    f"**{BOT_PREFIX}supportlog** - Set support ticket logs."
                ), "color": COLOR_GOLD
            },
            "mod": {
                "title": "🛡️ Moderation & Security Intelligence",
                "desc": (
                    f"**{BOT_PREFIX}warn @user <reason>** - Assign infraction.\n"
                    f"**{BOT_PREFIX}warnstats @user** - View Risk & Progress.\n"
                    f"**{BOT_PREFIX}warnhistory @user** - Full audit trail.\n"
                    f"**{BOT_PREFIX}purge <count>** - Mass clean chat."
                ), "color": COLOR_DANGER
            },
            "system": {
                "title": "🛎️ Support & System Health",
                "desc": (
                    f"**{BOT_PREFIX}status** - Check bot/hardware health.\n"
                    f"**{BOT_PREFIX}automod <on|off>** - Toggle security shield.\n"
                    f"**{BOT_PREFIX}panic** - Emergency global lockdown.\n"
                    f"**{BOT_PREFIX}ping** - Test API/Gateway latency."
                ), "color": COLOR_SECONDARY
            },
            "stats": {
                "title": "📊 Stats & User Intelligence",
                "desc": (
                    f"**{BOT_PREFIX}profile** - View user reputation stats.\n"
                    f"**{BOT_PREFIX}whois @user** - Deep profile analysis.\n"
                    f"**{BOT_PREFIX}avatar @user** - Fetch HD profile media.\n"
                    f"**{BOT_PREFIX}staff** - View staff activity metrics."
                ), "color": COLOR_GOLD
            },
            "voice": {
                "title": "🎙️ Voice System Protocols",
                "desc": (
                    f"**{BOT_PREFIX}setvc <channel>** - Set 24/7 VC lock.\n"
                    f"**{BOT_PREFIX}unsetvc** - Remove voice lock.\n"
                    f"**{BOT_PREFIX}vcstatus** - Voice system diagnostics."
                ), "color": COLOR_SECONDARY
            }
        }

        page = pages[selection]
        embed = luxury_embed(page["title"], page["desc"] + "\n\n━━━━━━━━━━━━━━━━━━━━━━\n_Ultimate Edition • Intelligent Automation_", page["color"])
        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.add_item(HelpDropdown(bot))

# =====================================================
# THE ULTIMATE SYSTEM COG
# =====================================================

class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()

        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {}

        state.SYSTEM_FLAGS.setdefault("panic_mode", False)
        state.SYSTEM_FLAGS.setdefault("automod_enabled", True)
        state.SYSTEM_FLAGS.setdefault("mvp_system", True)

    # ---------------- MANUAL / HELP ----------------
    @commands.command(name="help", aliases=["commands", "manual"])
    @commands.guild_only()
    @require_level(1)
    async def help_command(self, ctx: commands.Context):
        """The New Interactive Help Dashboard"""
        embed = luxury_embed(
            title="🌌 HellFire Hangout — COMMAND MANUAL",
            description=(
                "Welcome to the Unified Intelligence guide.\n"
                "Select a department below to view specialized commands.\n\n"
                f"Prefix: `{BOT_PREFIX}`\n"
                "Intelligence: `God-Mode` | Status: `🟢 Operational`"
            ),
            color=COLOR_GOLD
        )
        view = HelpView(self.bot)
        await ctx.send(embed=embed, view=view)

    # ---------------- MASTER ROLE TOGGLE ----------------
    @commands.command(name="role")
    @commands.guild_only()
    @require_level(3)
    async def role_toggle(self, ctx: commands.Context, member: discord.Member, *, role: discord.Role):
        """Intelligent Role Management (Assign/Remove)"""
        if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send(embed=luxury_embed("❌ Error", "Hierarchy mismatch. Role is too high.", COLOR_DANGER))
        
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(embed=luxury_embed("🔻 Role Removed", f"Successfully removed {role.mention} from {member.mention}.", COLOR_SECONDARY))
        else:
            await member.add_roles(role)
            await ctx.send(embed=luxury_embed("🔺 Role Added", f"Successfully assigned {role.mention} to {member.mention}.", COLOR_GOLD))

    # ---------------- USER INTEL (WHOIS) ----------------
    @commands.command(name="whois", aliases=["ui", "userinfo"])
    @commands.guild_only()
    async def whois(self, ctx: commands.Context, member: discord.Member = None):
        """Deep analytics and risk assessment of a member"""
        member = member or ctx.author
        warns = getattr(state, "WARN_DATA", {}).get(member.id, 0)
        risk = "🟢 Safe" if warns < 3 else "🟡 Risky" if warns < 6 else "🔴 Dangerous"

        desc = (
            f"👤 **User:** {member.mention}\n"
            f"🆔 **ID:** `{member.id}`\n\n"
            f"🧠 **System Risk:** {risk} ({warns} infractions)\n"
            f"📅 **Created:** <t:{int(member.created_at.timestamp())}:D>\n"
            f"📅 **Joined:** <t:{int(member.joined_at.timestamp())}:R>\n\n"
            f"🎭 **Top Role:** {member.top_role.mention}"
        )
        embed = luxury_embed(f"🕵️ Intelligence: {member.name}", desc, COLOR_GOLD)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # ---------------- STATUS / DIAGNOSTICS ----------------
    @commands.command(name="status", aliases=["health"])
    @commands.guild_only()
    @require_level(1)
    async def status(self, ctx: commands.Context):
        """High-Fidelity System Diagnostics"""
        uptime = datetime.utcnow() - self.start_time
        h, r = divmod(int(uptime.total_seconds()), 3600)
        m, s = divmod(r, 60)

        # Hardware monitoring protection
        if PSUTIL_AVAILABLE:
            cpu = f"{psutil.cpu_percent()}%"
            ram = f"{round(self.process.memory_info().rss / 1024 / 1024, 2)} MB"
        else:
            cpu = ram = "N/A"

        embed = luxury_embed(
            title="📊 Ultimate System Health",
            description=(
                f"⏱ **Uptime:** `{h}h {m}m {s}s`\n"
                f"🛰 **Gateway:** `{round(self.bot.latency * 1000)}ms`\n\n"
                f"🧠 **RAM:** `{ram}` | ⚡ **CPU:** `{cpu}`\n\n"
                f"🛡 **AutoMod:** {'`🟢 ON`' if state.SYSTEM_FLAGS['automod_enabled'] else '`🔴 OFF`'}\n"
                f"🚨 **Panic:** {'`🔴 ACTIVE`' if state.SYSTEM_FLAGS['panic_mode'] else '`🟢 CLEAR`'}"
            ),
            color=COLOR_SECONDARY
        )
        await ctx.send(embed=embed)

    # ---------------- AVATAR ----------------
    @commands.command(name="avatar", aliases=["av"])
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """Fetch HD profile media"""
        member = member or ctx.author
        url = member.display_avatar.url
        embed = luxury_embed(f"🖼️ {member.name}'s Avatar", f"[Direct HD Link]({url})", COLOR_GOLD)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    # ---------------- PURGE ----------------
    @commands.command(name="purge", aliases=["clear"])
    @commands.guild_only()
    @require_level(3)
    async def purge(self, ctx: commands.Context, amount: int):
        """Sanitize channel messages"""
        if amount > 100: amount = 100
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f"🧹 Removed **{len(deleted)}** messages.")
        await asyncio.sleep(4)
        await msg.delete()

    # ---------------- PING ----------------
    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Test API/Gateway cycles"""
        start = time.perf_counter()
        message = await ctx.send("🛰️ Measuring...")
        end = time.perf_counter()
        lat = round((end - start) * 1000)
        await message.edit(content=None, embed=luxury_embed("🛰️ Latency", f"**REST:** `{lat}ms`\n**WS:** `{round(self.bot.latency*1000)}ms`", COLOR_GOLD))

    # ---------------- PANIC PROTOCOLS ----------------
    @commands.command()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(embed=luxury_embed("🚨 PANIC ACTIVE", "Server lockdown initiated.", COLOR_DANGER))

    @commands.command()
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = False
        await ctx.send(embed=luxury_embed("✅ PANIC LIFTED", "Standard operations resumed.", COLOR_GOLD))

# =====================================================
# SAFE SETUP (PREVENTS REGISTRATION ERRORS)
# =====================================================
async def setup(bot: commands.Bot):
    # This list removes existing commands from other files before loading this cog
    # to prevent the "CommandRegistrationError"
    conflicting_cmds = ['help', 'role', 'whois', 'status', 'avatar', 'purge', 'ping']
    for cmd in conflicting_cmds:
        if bot.get_command(cmd):
            bot.remove_command(cmd)
            
    await bot.add_cog(System(bot))
