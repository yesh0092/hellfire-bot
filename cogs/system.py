import discord
from discord.ext import commands, tasks
from discord import ui
import asyncio
import time
import platform
import os
from datetime import datetime

# =====================================================
# SYSTEM DEPENDENCIES & SAFETY
# =====================================================
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
# INTERACTIVE HELP UI COMPONENTS
# =====================================================

class HelpDropdown(ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Admin & Setup", emoji="⚙️", description="Server configuration & protocols", value="admin"),
            discord.SelectOption(label="Ultimate Moderation", emoji="🛡️", description="Risk Analysis & Security", value="mod"),
            discord.SelectOption(label="Support & System", emoji="🛎️", description="Transcripts & Health", value="system"),
            discord.SelectOption(label="Stats & Intelligence", emoji="📊", description="User Profiles & Analytics", value="stats"),
            discord.SelectOption(label="Voice System", emoji="🎙️", description="24/7 Voice Connectivity", value="voice"),
        ]
        super().__init__(placeholder="🌌 Select a Department to view commands...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        
        # Comprehensive documentation mapping
        pages = {
            "admin": {
                "title": "⚙️ Admin & Setup Commands",
                "desc": (
                    f"**{BOT_PREFIX}setup** - Initialize environment.\n"
                    f"**{BOT_PREFIX}welcome / unwelcome** - Toggle join system.\n"
                    f"**{BOT_PREFIX}autorole <role>** - Set auto-assign role.\n"
                    f"**{BOT_PREFIX}supportlog** - Set transcript channel."
                ), "color": COLOR_GOLD
            },
            "mod": {
                "title": "🛡️ Intelligence Moderation",
                "desc": (
                    f"**{BOT_PREFIX}warn @user <reason>** - Assign infraction.\n"
                    f"**{BOT_PREFIX}warnstats @user** - Risk & Progress Analysis.\n"
                    f"**{BOT_PREFIX}warnhistory @user** - Deep audit trail.\n"
                    f"**{BOT_PREFIX}clearwarns @user** - Remove all Warns.\n"
                    f"**{BOT_PREFIX}purge <count>** - Mass clean channel."
                ), "color": COLOR_DANGER
            },
            "system": {
                "title": "🛎️ Support & System Health",
                "desc": (
                    f"**{BOT_PREFIX}status** - Hardware/Bot diagnostics.\n"
                    f"**{BOT_PREFIX}automod <on|off>** - Toggle security shield.\n"
                    f"**{BOT_PREFIX}panic / unpanic** - Global Lockdown.\n"
                    f"**{BOT_PREFIX}ping** - REST & Gateway latency test."
                ), "color": COLOR_SECONDARY
            },
            "stats": {
                "title": "📊 User Intelligence & Activity",
                "desc": (
                    f"**{BOT_PREFIX}profile** - Reputation & Activity stats.\n"
                    f"**{BOT_PREFIX}whois @user** - Deep profile assessment.\n"
                    f"**{BOT_PREFIX}avatar @user** - Fetch HD profile media.\n"
                    f"**{BOT_PREFIX}staff** - Moderator efficiency metrics."
                ), "color": COLOR_GOLD
            },
            "voice": {
                "title": "🎙️ Voice System Protocols",
                "desc": (
                    f"**{BOT_PREFIX}setvc <channel>** - Lock bot 24/7.\n"
                    f"**{BOT_PREFIX}unsetvc** - Release voice lock.\n"
                    f"**{BOT_PREFIX}vcstatus** - Voice stream health."
                ), "color": COLOR_SECONDARY
            }
        }

        page = pages[selection]
        embed = luxury_embed(
            title=page["title"], 
            description=page["desc"] + "\n\n━━━━━━━━━━━━━━━━━━━━━━\n_Intelligence • Elite Automation_", 
            color=page["color"]
        )
        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.add_item(HelpDropdown(bot))

# =====================================================
# THE MASTER SYSTEM COG (PLATINUM)
# =====================================================

class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()

        # Harden System State
        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {}

        state.SYSTEM_FLAGS.setdefault("panic_mode", False)
        state.SYSTEM_FLAGS.setdefault("automod_enabled", True)
        state.SYSTEM_FLAGS.setdefault("mvp_system", True)
        state.SYSTEM_FLAGS.setdefault("intelligence_layer", True)

    # ================= COMMAND MANUAL =================

    @commands.command(name="help", aliases=["commands", "guide", "manual"])
    @commands.guild_only()
    @require_level(1)
    async def help_command(self, ctx: commands.Context):
        """The Interactive Intelligence Dashboard"""
        embed = luxury_embed(
            title="🌌 HellFire Hangout — ULTIMATE MANUAL",
            description=(
                "**System Integrity:** `🟢 100%` | **Intelligence:** `God-Mode`\n"
                "Please select a department below to access specific commands.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "🛰️ **CORE DATA**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• Prefix: `{BOT_PREFIX}`\n"
                f"• AutoMod: `{'ACTIVE' if state.SYSTEM_FLAGS['automod_enabled'] else 'DISABLED'}`\n"
                f"• Panic Level: `{'CRITICAL' if state.SYSTEM_FLAGS['panic_mode'] else 'NORMAL'}`"
            ),
            color=COLOR_GOLD
        )
        view = HelpView(self.bot)
        await ctx.send(embed=embed, view=view)

    # ================= MASTER ROLE LOGIC =================

    @commands.command(name="role")
    @commands.guild_only()
    @require_level(3)
    async def role_toggle(self, ctx: commands.Context, member: discord.Member, *, role: discord.Role):
        """Intelligent role toggle with hierarchy protection"""
        # Security Hierarchy Check
        if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send(embed=luxury_embed("❌ Hierarchy Conflict", "Role is above your authority.", COLOR_DANGER))
        
        if role.managed:
            return await ctx.send(embed=luxury_embed("❌ System Restricted", "Managed roles cannot be assigned manually.", COLOR_DANGER))

        if role in member.roles:
            await member.remove_roles(role, reason=f"Managed by {ctx.author}")
            await ctx.send(embed=luxury_embed("🔻 Access Revoked", f"Removed {role.mention} from {member.mention}.", COLOR_SECONDARY))
        else:
            await member.add_roles(role, reason=f"Managed by {ctx.author}")
            await ctx.send(embed=luxury_embed("🔺 Access Granted", f"Assigned {role.mention} to {member.mention}.", COLOR_GOLD))

    # ================= USER INTELLIGENCE (WHOIS) =================

    @commands.command(name="whois", aliases=["ui", "userinfo", "intel"])
    @commands.guild_only()
    @require_level(1)
    async def whois(self, ctx: commands.Context, member: discord.Member = None):
        """Deep analytics & reputation risk assessment"""
        member = member or ctx.author
        warn_data = getattr(state, "WARN_DATA", {}).get(member.id, 0)
        
        # Risk Meter Calculation
        if warn_data == 0: risk_status = "🟢 Safe (Clean)"
        elif warn_data < 4: risk_status = "🟡 Risky (Rule Breaker)"
        else: risk_status = "🔴 Dangerous (Watchlist)"

        roles = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]
        
        desc = (
            f"👤 **Member:** {member.mention}\n"
            f"🆔 **ID:** `{member.id}`\n\n"
            f"🧠 **System Risk:** {risk_status}\n"
            f"🛡️ **Total Warns:** `{warn_data}`\n\n"
            f"📅 **Created:** <t:{int(member.created_at.timestamp())}:D>\n"
            f"📅 **Joined:** <t:{int(member.joined_at.timestamp())}:R>\n\n"
            f"🎭 **Roles:** {', '.join(roles[:5])}{'...' if len(roles) > 5 else ''}"
        )
        embed = luxury_embed(f"🕵️ Intelligence: {member.name}", desc, COLOR_GOLD)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # ================= SYSTEM DIAGNOSTICS =================

    @commands.command(name="status", aliases=["health", "sysinfo"])
    @require_level(1)
    async def status(self, ctx: commands.Context):
        """Real-time bot and hardware health analysis"""
        uptime = datetime.utcnow() - self.start_time
        h, r = divmod(int(uptime.total_seconds()), 3600)
        m, s = divmod(r, 60)

        # Hardware metrics with PSUTIL protection
        if PSUTIL_AVAILABLE:
            cpu = f"{psutil.cpu_percent()}%"
            ram = f"{round(self.process.memory_info().rss / 1024 / 1024, 2)} MB"
        else:
            cpu = ram = "N/A (Missing psutil)"

        embed = luxury_embed(
            title="📊 Universal System Health",
            description=(
                f"⏱ **Uptime:** `{h}h {m}m {s}s`\n"
                f"🛰 **Gateway:** `{round(self.bot.latency * 1000)}ms`\n\n"
                f"🧠 **RAM Consumption:** `{ram}`\n"
                f"⚡ **CPU Usage:** `{cpu}`\n\n"
                f"🛡 **AutoMod:** `{'🟢 ON' if state.SYSTEM_FLAGS['automod_enabled'] else '🔴 OFF'}`\n"
                f"🚨 **Panic Mode:** `{'🔴 ACTIVE' if state.SYSTEM_FLAGS['panic_mode'] else '🟢 CLEAR'}`"
            ),
            color=COLOR_SECONDARY
        )
        await ctx.send(embed=embed)

    # ================= UTILITIES (AVATAR, PING, PURGE) =================

    @commands.command(name="avatar", aliases=["av", "pfp"])
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """Fetch HD profile media"""
        member = member or ctx.author
        url = member.display_avatar.with_static_format("png").url
        embed = luxury_embed(f"🖼️ {member.name}", f"[Direct HD Link]({url})", COLOR_GOLD)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Test API/Gateway latency"""
        start = time.perf_counter()
        message = await ctx.send("🛰️ Measuring...")
        end = time.perf_counter()
        lat = round((end - start) * 1000)
        await message.edit(content=None, embed=luxury_embed("🛰️ Connectivity", f"**REST API:** `{lat}ms`\n**Gateway:** `{round(self.bot.latency*1000)}ms`", COLOR_GOLD))

    @commands.command(name="purge")
    @require_level(3)
    async def purge(self, ctx: commands.Context, amount: int):
        """Sanitize channel messages"""
        if amount > 100: amount = 100
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f"🧹 Removed **{len(deleted)}** messages.")
        await asyncio.sleep(4)
        await msg.delete()

    # ================= PANIC PROTOCOLS =================

    @commands.command()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(embed=luxury_embed("🚨 PANIC MODE ENGAGED", "Global Lockdown Active. Permissions Restricted.", COLOR_DANGER))

    @commands.command()
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = False
        await ctx.send(embed=luxury_embed("✅ PANIC MODE LIFTED", "Standard Operations Resumed.", COLOR_GOLD))

# =====================================================
# SAFE SETUP (CRASH PREVENTION)
# =====================================================
async def setup(bot: commands.Bot):
    # Pre-load cleanup to avoid CommandRegistrationError
    conflicting = ['help', 'role', 'whois', 'status', 'avatar', 'purge', 'ping']
    for cmd in conflicting:
        if bot.get_command(cmd):
            bot.remove_command(cmd)
            
    await bot.add_cog(System(bot))
