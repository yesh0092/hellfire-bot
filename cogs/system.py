import discord
from discord.ext import commands, tasks
from discord import ui
import asyncio
import time
import platform
from datetime import datetime, timedelta

# Safety import for hardware monitoring
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
        pages = {
            "admin": {
                "title": "⚙️ Admin & Setup Commands",
                "desc": (
                    f"**{BOT_PREFIX}setup**\nRun full environment sync.\n\n"
                    f"**{BOT_PREFIX}panic** / **{BOT_PREFIX}unpanic**\nEngage/Release global lockdown.\n\n"
                    f"**{BOT_PREFIX}automod <on|off>**\nToggle security intelligence.\n\n"
                    f"**{BOT_PREFIX}supportlog**\nSet transcript logging channel."
                )
            },
            "mod": {
                "title": "🛡️ Ultimate Moderation Intelligence",
                "desc": (
                    f"**{BOT_PREFIX}warn @user <reason>**\nFormal warning with auto-escalation.\n\n"
                    f"**{BOT_PREFIX}warnstats @user**\nView Risk, Velocity, and Progress.\n\n"
                    f"**{BOT_PREFIX}warnhistory @user**\nDeep audit of user infractions.\n\n"
                    f"**{BOT_PREFIX}purge <count>**\nAdvanced message sanitization."
                )
            },
            "support": {
                "title": "🛎️ Ultimate Support System",
                "desc": (
                    "**User Support:** DM the bot to open tickets.\n\n"
                    "**Staff Tools:**\n"
                    "• **Claim:** Assign yourself to a ticket.\n"
                    "• **Close:** Generate and log .txt transcripts.\n\n"
                    "**Auto-Archive:** 24h inactivity trigger enabled."
                )
            },
            "stats": {
                "title": "📊 Intelligence & Analytics",
                "desc": (
                    f"**{BOT_PREFIX}profile [@user]**\nFull reputation and activity analysis.\n\n"
                    f"**{BOT_PREFIX}warnboard**\nLeaderboard of top rule-breakers.\n\n"
                    f"**{BOT_PREFIX}staff**\nTrack moderator performance metrics."
                )
            },
            "util": {
                "title": "🛠️ Utility & Master Roles",
                "desc": (
                    f"**{BOT_PREFIX}role @user <Role>**\nSmart toggle with hierarchy safety.\n\n"
                    f"**{BOT_PREFIX}whois @user**\nDeep profile intel + Risk Assessment.\n\n"
                    f"**{BOT_PREFIX}avatar [@user]**\nExtract high-definition images.\n\n"
                    f"**{BOT_PREFIX}ping**\nDetailed REST/Gateway latency test."
                )
            },
            "voice": {
                "title": "🎙️ Voice System (24/7)",
                "desc": f"**{BOT_PREFIX}setvc** - 24/7 Lock.\n**{BOT_PREFIX}unsetvc** - Release.\n**{BOT_PREFIX}vcstatus** - Diagnostics."
            }
        }

        page = pages[selection]
        embed = luxury_embed(
            title=page["title"],
            description=page["desc"] + "\n\n━━━━━━━━━━━━━━━━━━━━━━\n_Ultimate Platinum Edition • Intelligence Automation_",
            color=COLOR_GOLD
        )
        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.add_item(HelpDropdown(bot))

# =====================================================
# THE SYSTEM COG (ENHANCED PLATINUM)
# =====================================================

class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()
        
        # Hardened State
        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {}
        
        state.SYSTEM_FLAGS.setdefault("panic_mode", False)
        state.SYSTEM_FLAGS.setdefault("automod_enabled", True)
        
        self.maintenance_loop.start()

    def cog_unload(self):
        self.maintenance_loop.cancel()

    @tasks.loop(minutes=30)
    async def maintenance_loop(self):
        """Internal heartbeat for system health"""
        pass

    # ---------------- HELP ----------------
    @commands.command(name="help", aliases=["manual"])
    @commands.guild_only()
    @require_level(1)
    async def help_command(self, ctx: commands.Context):
        """The Interactive Intelligence Manual"""
        embed = luxury_embed(
            title="🌌 HellFire Hangout — PLATINUM MANUAL",
            description=(
                "**Version:** `v4.5.2` | **Core:** `Active`\n\n"
                f"• **AutoMod:** {'`🟢 ACTIVE`' if state.SYSTEM_FLAGS['automod_enabled'] else '`🔴 OFF`'}\n"
                f"• **Panic Lock:** {'`🔴 ENGAGED`' if state.SYSTEM_FLAGS['panic_mode'] else '`🟢 CLEAR`'}\n"
                f"• **Risk Analysis:** `🟢 ONLINE`"
            ),
            color=COLOR_GOLD
        )
        await ctx.send(embed=embed, view=HelpView(self.bot))

    # ---------------- ROLE TOGGLE ----------------
    @commands.command(name="role")
    @commands.guild_only()
    @require_level(3)
    async def role(self, ctx: commands.Context, member: discord.Member, *, role: discord.Role):
        """Master role management with hierarchy check"""
        if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send(embed=luxury_embed("❌ Error", "Authority mismatch. Role too high.", COLOR_DANGER))
        
        if role.managed:
            return await ctx.send(embed=luxury_embed("❌ Error", "Role is system-managed.", COLOR_DANGER))

        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(embed=luxury_embed("🔻 Removed", f"Removed {role.mention} from {member.mention}", COLOR_SECONDARY))
        else:
            await member.add_roles(role)
            await ctx.send(embed=luxury_embed("🔺 Added", f"Added {role.mention} to {member.mention}", COLOR_GOLD))

    # ---------------- WHOIS ----------------
    @commands.command(name="whois", aliases=["ui"])
    @commands.guild_only()
    async def whois(self, ctx: commands.Context, member: discord.Member = None):
        """Deep User Analytics & Risk Assessment"""
        member = member or ctx.author
        warns = getattr(state, "WARN_DATA", {}).get(member.id, 0)
        risk = "🟢 Safe" if warns < 3 else "🟡 Risky" if warns < 6 else "🔴 Dangerous"

        desc = (
            f"👤 **Account:** {member.mention}\n"
            f"🆔 **ID:** `{member.id}`\n\n"
            f"🧠 **System Risk:** {risk}\n"
            f"🛡️ **Total Warns:** `{warns}`\n\n"
            f"📅 **Created:** <t:{int(member.created_at.timestamp())}:D>\n"
            f"📅 **Joined:** <t:{int(member.joined_at.timestamp())}:R>\n\n"
            f"🎭 **Top Role:** {member.top_role.mention}"
        )
        embed = luxury_embed(f"🕵️ Intel: {member.name}", desc, COLOR_GOLD)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # ---------------- STATUS ----------------
    @commands.command(name="status", aliases=["health"])
    @require_level(1)
    async def status(self, ctx: commands.Context):
        """High-Fidelity System Diagnostics"""
        uptime = datetime.utcnow() - self.start_time
        h, r = divmod(int(uptime.total_seconds()), 3600)
        m, s = divmod(r, 60)
        
        # Safe Hardware Check
        if PSUTIL_AVAILABLE:
            cpu = f"{psutil.cpu_percent()}%"
            ram = f"{round(self.process.memory_info().rss / 1024 / 1024, 2)} MB"
        else:
            cpu = "N/A (Missing psutil)"
            ram = "N/A (Missing psutil)"

        embed = luxury_embed(
            title="📊 Diagnostics",
            description=(
                f"⏱ **Uptime:** `{h}h {m}m {s}s`\n"
                f"🛰 **Latency:** `{round(self.bot.latency * 1000)}ms`\n\n"
                f"🧠 **RAM:** `{ram}`\n"
                f"⚡ **CPU:** `{cpu}`\n\n"
                f"🛡 **AutoMod:** `{'ON' if state.SYSTEM_FLAGS['automod_enabled'] else 'OFF'}`\n"
                f"🚨 **Panic:** `{'ACTIVE' if state.SYSTEM_FLAGS['panic_mode'] else 'STANDBY'}`"
            ),
            color=COLOR_SECONDARY
        )
        await ctx.send(embed=embed)

    # ---------------- AVATAR ----------------
    @commands.command(name="avatar", aliases=["av"])
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """Fetch HD profile picture"""
        member = member or ctx.author
        url = member.display_avatar.url
        embed = luxury_embed(f"🖼️ {member.name}", f"[HD Link]({url})", COLOR_GOLD)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    # ---------------- PURGE ----------------
    @commands.command(name="purge")
    @commands.guild_only()
    @require_level(3)
    async def purge(self, ctx: commands.Context, amount: int):
        """Sanitize channel history"""
        if amount > 100: amount = 100
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        msg = await ctx.send(f"🧹 Removed **{len(deleted)}** messages.")
        await asyncio.sleep(4)
        await msg.delete()

    # ---------------- PING ----------------
    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """Latency benchmark"""
        start = time.perf_counter()
        message = await ctx.send("🛰️ Measuring...")
        end = time.perf_counter()
        await message.edit(content=None, embed=luxury_embed("🛰️ Latency", 
            f"**REST:** `{round((end-start)*1000)}ms`\n**WS:** `{round(self.bot.latency*1000)}ms`", COLOR_GOLD))

    # ---------------- PANIC ----------------
    @commands.command()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(embed=luxury_embed("🚨 PANIC", "Lockdown engaged.", COLOR_DANGER))

    @commands.command()
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = False
        await ctx.send(embed=luxury_embed("✅ CLEAR", "Lockdown lifted.", COLOR_GOLD))

async def setup(bot: commands.Bot):
    # This prevents the "default help" crash
    if bot.get_command('help'):
        bot.remove_command('help')
    await bot.add_cog(System(bot))
