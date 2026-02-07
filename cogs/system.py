import discord
from discord.ext import commands, tasks
from discord import ui
import asyncio
import time
import platform
import psutil
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state

BOT_PREFIX = "&"

# =====================================================
# THE INTERACTIVE HELP COMPONENTS (GOD-MODE)
# =====================================================

class HelpDropdown(ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Admin & Setup", emoji="⚙️", description="Core environment & panic protocols", value="admin"),
            discord.SelectOption(label="Ultimate Moderation", emoji="🛡️", description="Risk Analysis & Warn Logic", value="mod"),
            discord.SelectOption(label="Ultimate Support", emoji="🛎️", description="Transcripts & Ticket Management", value="support"),
            discord.SelectOption(label="Intelligence & Stats", emoji="📊", description="User Analytics & Leaderboards", value="stats"),
            discord.SelectOption(label="Utility & Roles", emoji="🛠️", description="Master roles & Media tools", value="util"),
            discord.SelectOption(label="Voice System", emoji="🎙️", description="24/7 Voice & Health", value="voice"),
        ]
        super().__init__(placeholder="🌌 Select a Department to view commands...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        
        # Comprehensive Feature Documentation Mapping
        pages = {
            "admin": {
                "title": "⚙️ Admin & Setup Commands",
                "desc": (
                    f"**{BOT_PREFIX}setup**\nSynchronize server environment and database.\n\n"
                    f"**{BOT_PREFIX}panic** / **{BOT_PREFIX}unpanic**\nEngage server-wide lockdown protocols.\n\n"
                    f"**{BOT_PREFIX}automod <on|off>**\nToggle the silent intelligence security layer.\n\n"
                    f"**{BOT_PREFIX}supportlog**\nConfigure destination for ticket transcripts."
                )
            },
            "mod": {
                "title": "🛡️ Ultimate Moderation & Intelligence",
                "desc": (
                    f"**{BOT_PREFIX}warn @user <reason>**\nAssign infraction with auto-escalation (8-warn cap).\n\n"
                    f"**{BOT_PREFIX}warnstats @user**\nView Risk Level, Velocity, and Progress Bars.\n\n"
                    f"**{BOT_PREFIX}warnhistory @user**\nAudit the 15-incident deep history.\n\n"
                    f"**{BOT_PREFIX}purge <count>**\nHigh-performance message sanitization."
                )
            },
            "support": {
                "title": "🛎️ Ultimate Support System",
                "desc": (
                    "**User-End:** DM the bot to initiate priority tickets.\n\n"
                    "**Staff Controls:**\n"
                    "• **Claim:** Take ownership of a ticket.\n"
                    "• **Close:** Auto-generates a .txt transcript to logs.\n\n"
                    "**Ghost-Detection:** Inactive tickets auto-archive after 24h."
                )
            },
            "stats": {
                "title": "📊 Intelligence & Analytics",
                "desc": (
                    f"**{BOT_PREFIX}profile [@user]**\nDeep activity and reputation analysis.\n\n"
                    f"**{BOT_PREFIX}warnboard**\nLeaderboard of offenders and Staff Enforcer stats.\n\n"
                    f"**{BOT_PREFIX}staff**\nTrack moderator activity and efficiency levels."
                )
            },
            "util": {
                "title": "🛠️ Utility & Master Roles",
                "desc": (
                    f"**{BOT_PREFIX}role @user <Role>**\nSmart toggle role assignment with hierarchy checks.\n\n"
                    f"**{BOT_PREFIX}whois @user**\nDeep profile intel including Risk Assessment.\n\n"
                    f"**{BOT_PREFIX}avatar [@user]**\nExtract high-definition profile pictures.\n\n"
                    f"**{BOT_PREFIX}ping**\nTest Gateway and REST API latency."
                )
            },
            "voice": {
                "title": "🎙️ Voice System (24/7)",
                "desc": (
                    f"**{BOT_PREFIX}setvc <channel>**\nLock bot into 24/7 voice connectivity.\n\n"
                    f"**{BOT_PREFIX}unsetvc**\nRelease the voice lock.\n\n"
                    f"**{BOT_PREFIX}vcstatus**\nDiagnostic health of the voice stream."
                )
            }
        }

        page = pages[selection]
        embed = luxury_embed(
            title=page["title"],
            description=page["desc"] + "\n\n━━━━━━━━━━━━━━━━━━━━━━\n_Ultimate Platinum Edition • Intelligent Automation_",
            color=COLOR_GOLD
        )
        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.add_item(HelpDropdown(bot))

# =====================================================
# THE SYSTEM COG (ENHANCED & UNTRIMMED)
# =====================================================

class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        self.process = psutil.Process()
        
        # Hardened State Initialization
        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {}
        
        state.SYSTEM_FLAGS.setdefault("panic_mode", False)
        state.SYSTEM_FLAGS.setdefault("automod_enabled", True)
        state.SYSTEM_FLAGS.setdefault("intelligence_active", True)
        
        self.maintenance_loop.start()

    def cog_unload(self):
        self.maintenance_loop.cancel()

    @tasks.loop(minutes=30)
    async def maintenance_loop(self):
        """Internal background thread for cache pruning and health checks"""
        # Logic for cleaning temporary state data
        pass

    # --------------------------------------------------
    # COMMAND: HELP (MANUAL)
    # --------------------------------------------------

    @commands.command(name="help", aliases=["manual", "guide"])
    @commands.guild_only()
    @require_level(1)
    async def help_command(self, ctx: commands.Context):
        """The Central Interactive Manual"""
        embed = luxury_embed(
            title="🌌 HellFire Hangout — PLATINUM MANUAL",
            description=(
                "**System Version:** `v4.5.2` | **Intelligence:** `God-Mode`\n"
                "Welcome to the central command hub. Use the menu below to explore.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "📡 **SYSTEM STATUS**\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **AutoMod:** {'`🟢 ACTIVE`' if state.SYSTEM_FLAGS['automod_enabled'] else '`🔴 DISABLED`'}\n"
                f"• **Panic Lock:** {'`🔴 ENGAGED`' if state.SYSTEM_FLAGS['panic_mode'] else '`🟢 CLEAR`'}\n"
                f"• **Risk Analysis:** `🟢 ONLINE`"
            ),
            color=COLOR_GOLD
        )
        view = HelpView(self.bot)
        await ctx.send(embed=embed, view=view)

    # --------------------------------------------------
    # COMMAND: MASTER ROLE TOGGLE
    # --------------------------------------------------

    @commands.command(name="role")
    @commands.guild_only()
    @require_level(3)
    async def role(self, ctx: commands.Context, member: discord.Member, *, role: discord.Role):
        """Intelligent role toggle with hierarchy enforcement"""
        if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send(embed=luxury_embed("❌ Authority Error", "You cannot manage a role higher than or equal to your own.", COLOR_DANGER))
        
        if role.managed:
            return await ctx.send(embed=luxury_embed("❌ System Error", "This role is managed by an integration and cannot be assigned manually.", COLOR_DANGER))

        if role in member.roles:
            await member.remove_roles(role, reason=f"Managed by {ctx.author}")
            await ctx.send(embed=luxury_embed("🔻 Role Removed", f"Removed {role.mention} from {member.mention}.", COLOR_SECONDARY))
        else:
            await member.add_roles(role, reason=f"Managed by {ctx.author}")
            await ctx.send(embed=luxury_embed("🔺 Role Added", f"Assigned {role.mention} to {member.mention}.", COLOR_GOLD))

    # --------------------------------------------------
    # COMMAND: USER INTELLIGENCE (WHOIS)
    # --------------------------------------------------

    @commands.command(name="whois", aliases=["ui", "userinfo"])
    @commands.guild_only()
    @require_level(1)
    async def whois(self, ctx: commands.Context, member: discord.Member = None):
        """Deep Analytics & Risk Assessment of a member"""
        member = member or ctx.author
        
        # Pull data from the Warn Intelligence system
        warn_data = getattr(state, "WARN_DATA", {}).get(member.id, 0)
        
        # Dynamic Risk Gauge
        if warn_data == 0: risk_status = "🟢 Safe (Clean Record)"
        elif warn_data < 4: risk_status = "🟡 Risky (Behavior Alert)"
        else: risk_status = "🔴 Dangerous (Terminal/Watchlist)"

        roles = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]
        
        desc = (
            f"👤 **Account:** {member.mention}\n"
            f"🆔 **ID:** `{member.id}`\n\n"
            f"🧠 **System Risk:** {risk_status}\n"
            f"🛡️ **Warn Count:** `{warn_data}`\n\n"
            f"📅 **Created:** <t:{int(member.created_at.timestamp())}:D>\n"
            f"📅 **Joined:** <t:{int(member.joined_at.timestamp())}:R>\n\n"
            f"🎭 **Top Role:** {member.top_role.mention}\n"
            f"🌈 **Roles:** {', '.join(roles[:5])}{'...' if len(roles) > 5 else ''}"
        )
        
        embed = luxury_embed(f"🕵️ Intelligence: {member.name}", desc, COLOR_GOLD)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # --------------------------------------------------
    # COMMAND: SERVER DATA ANALYTICS
    # --------------------------------------------------

    @commands.command(name="serverinfo", aliases=["si"])
    @commands.guild_only()
    @require_level(1)
    async def serverinfo(self, ctx: commands.Context):
        """Comprehensive server-wide data metrics"""
        g = ctx.guild
        humans = len([m for m in g.members if not m.bot])
        bots = g.member_count - humans
        
        desc = (
            f"👑 **Owner:** {g.owner.mention}\n"
            f"📅 **Created:** <t:{int(g.created_at.timestamp())}:D>\n\n"
            f"👥 **Humans:** `{humans}` | 🤖 **Bots:** `{bots}`\n"
            f"💎 **Level:** `{g.premium_tier}` ({g.premium_subscription_count} Boosts)\n"
            f"💬 **Channels:** `{len(g.channels)}` | 🎭 **Roles:** `{len(g.roles)}`"
        )
        
        embed = luxury_embed(f" castles {g.name} Metrics", desc, COLOR_GOLD)
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        if g.banner: embed.set_image(url=g.banner.url)
        await ctx.send(embed=embed)

    # --------------------------------------------------
    # COMMAND: HD MEDIA EXTRACTION
    # --------------------------------------------------

    @commands.command(name="avatar", aliases=["av", "pfp"])
    @require_level(1)
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """Fetch high-definition user profile pictures"""
        member = member or ctx.author
        url = member.display_avatar.with_static_format("png").url
        
        embed = luxury_embed(f"🖼️ {member.name}'s Avatar", f"[Direct HD Download Link]({url})", COLOR_GOLD)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    # --------------------------------------------------
    # COMMAND: SANITIZATION (PURGE)
    # --------------------------------------------------

    @commands.command(name="purge", aliases=["clear"])
    @commands.guild_only()
    @require_level(3)
    async def purge(self, ctx: commands.Context, amount: int):
        """Sanitize channel messages with auto-cleanup"""
        if amount > 100: amount = 100
        
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        
        msg = await ctx.send(f"🧹 **Sanitization Complete:** `{len(deleted)}` messages removed from history.")
        await asyncio.sleep(4)
        await msg.delete()

    # --------------------------------------------------
    # COMMAND: DIAGNOSTICS & STATUS
    # --------------------------------------------------

    @commands.command(name="status", aliases=["stats", "health"])
    @require_level(1)
    async def status(self, ctx: commands.Context):
        """High-Fidelity System Diagnostics"""
        uptime = datetime.utcnow() - self.start_time
        h, r = divmod(int(uptime.total_seconds()), 3600)
        m, s = divmod(r, 60)
        
        # Hardware Metrics
        cpu_usage = psutil.cpu_percent()
        ram_usage = self.process.memory_info().rss / 1024 / 1024 # MB

        embed = luxury_embed(
            title="📊 Universal Intelligence Diagnostics",
            description=(
                f"⏱ **Uptime:** `{h}h {m}m {s}s`\n"
                f"🛰 **Gateway Latency:** `{round(self.bot.latency * 1000)}ms`\n\n"
                f"🧠 **RAM Consumption:** `{ram_usage:.2f} MB`\n"
                f"⚡ **CPU Load:** `{cpu_usage}%`\n\n"
                f"🛡 **AutoMod:** `{'🟢 ONLINE' if state.SYSTEM_FLAGS['automod_enabled'] else '🔴 OFFLINE'}`\n"
                f"🚨 **Panic Protocol:** `{'🔴 ACTIVE' if state.SYSTEM_FLAGS['panic_mode'] else '🟢 STANDBY'}`"
            ),
            color=COLOR_SECONDARY
        )
        await ctx.send(embed=embed)

    # --------------------------------------------------
    # COMMAND: LATENCY TEST
    # --------------------------------------------------

    @commands.command(name="ping")
    @require_level(1)
    async def ping(self, ctx: commands.Context):
        """Test API and Gateway latency cycles"""
        start = time.perf_counter()
        message = await ctx.send(embed=luxury_embed("🛰️ Testing Latency...", "Measuring Gateway and REST cycles.", COLOR_SECONDARY))
        end = time.perf_counter()
        
        rest_lat = round((end - start) * 1000)
        ws_lat = round(self.bot.latency * 1000)
        
        await message.edit(embed=luxury_embed("🛰️ Connectivity Intel", f"**REST API Cycle:** `{rest_lat}ms`\n**Gateway Heartbeat:** `{ws_lat}ms`", COLOR_GOLD))

    # --------------------------------------------------
    # COMMAND: PANIC PROTOCOLS
    # --------------------------------------------------

    @commands.command(name="panic")
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        """Activate server-wide emergency lockdown"""
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(embed=luxury_embed("🚨 PROTOCOL: PANIC ENGAGED", "The system is now in lockdown mode. Permissions are restricted.", COLOR_DANGER))

    @commands.command(name="unpanic")
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        """Release emergency lockdown"""
        state.SYSTEM_FLAGS["panic_mode"] = False
        await ctx.send(embed=luxury_embed("✅ PROTOCOL: CLEAR", "Panic mode deactivated. Resuming standard operational flow.", COLOR_GOLD))

async def setup(bot: commands.Bot):
    # Ensure default help is removed to prevent naming conflicts
    bot.remove_command('help')
    await bot.add_cog(System(bot))
