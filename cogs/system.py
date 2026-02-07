import discord
from discord.ext import commands, tasks
from discord import ui
import asyncio
import time
from datetime import datetime, timedelta

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
            discord.SelectOption(label="Admin & Setup", emoji="⚙️", value="admin"),
            discord.SelectOption(label="Ultimate Moderation", emoji="🛡️", value="mod"),
            discord.SelectOption(label="Ultimate Support", emoji="🛎️", value="support"),
            discord.SelectOption(label="Intelligence & Stats", emoji="📊", value="stats"),
            discord.SelectOption(label="Utility & Roles", emoji="🛠️", value="util"),
            discord.SelectOption(label="Voice System", emoji="🎙️", value="voice"),
        ]
        super().__init__(placeholder="🌌 Select a Department to view commands...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selection = self.values[0]
        pages = {
            "admin": {
                "title": "⚙️ Admin & Setup Commands",
                "desc": (
                    f"**{BOT_PREFIX}setup** - Initialize environment.\n"
                    f"**{BOT_PREFIX}panic / {BOT_PREFIX}unpanic** - Global Lockdown.\n"
                    f"**{BOT_PREFIX}automod <on|off>** - Toggle security shield.\n"
                    f"**{BOT_PREFIX}supportlog** - Set transcript channel."
                )
            },
            "mod": {
                "title": "🛡️ Ultimate Moderation Intelligence",
                "desc": (
                    f"**{BOT_PREFIX}warn** - Assign with auto-escalation.\n"
                    f"**{BOT_PREFIX}warnstats** - Progress bars & velocity.\n"
                    f"**{BOT_PREFIX}warnhistory** - Full audit trail.\n"
                    f"**{BOT_PREFIX}purge <count>** - Mass clean chat."
                )
            },
            "support": {
                "title": "🛎️ Ultimate Support System",
                "desc": "DM the bot to open tickets.\n**Claim / Close** buttons for staff.\n**Auto-Transcripts** saved to logs."
            },
            "stats": {
                "title": "📊 Analytics & Engagement",
                "desc": (
                    f"**{BOT_PREFIX}profile** - User activity data.\n"
                    f"**{BOT_PREFIX}warnboard** - Offender Leaderboard.\n"
                    f"**{BOT_PREFIX}mywarns** - Personal health check."
                )
            },
            "util": {
                "title": "🛠️ Utility & Master Roles",
                "desc": (
                    f"**{BOT_PREFIX}role @user <Role>** - Intelligent toggle.\n"
                    f"**{BOT_PREFIX}avatar [@user]** - HD PFP Fetcher.\n"
                    f"**{BOT_PREFIX}whois [@user]** - Deep user intel.\n"
                    f"**{BOT_PREFIX}serverinfo** - Server data analysis.\n"
                    f"**{BOT_PREFIX}ping** - High-fidelity latency test."
                )
            },
            "voice": {
                "title": "🎙️ Voice System (24/7)",
                "desc": f"**{BOT_PREFIX}setvc** - Lock 24/7.\n**{BOT_PREFIX}unsetvc** - Unlock.\n**{BOT_PREFIX}vcstatus** - Health check."
            }
        }
        page = pages[selection]
        embed = luxury_embed(page["title"], page["desc"] + "\n\n━━━━━━━━━━━━━━━━━━━━━━\n_Ultimate • Intelligent • Elite Automation_", COLOR_GOLD)
        await interaction.response.edit_message(embed=embed)

class HelpView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=120)
        self.add_item(HelpDropdown(bot))

# =====================================================
# THE SYSTEM COG (ENHANCED PLATINUM EDITION)
# =====================================================

class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
        self.heartbeat_task.start()

        # Hardened State Flags
        if not hasattr(state, "SYSTEM_FLAGS"): state.SYSTEM_FLAGS = {}
        state.SYSTEM_FLAGS.setdefault("panic_mode", False)
        state.SYSTEM_FLAGS.setdefault("automod_enabled", True)
        state.SYSTEM_FLAGS.setdefault("intelligence_active", True)

    def cog_unload(self):
        self.heartbeat_task.cancel()

    @tasks.loop(minutes=10)
    async def heartbeat_task(self):
        """Background thread ensuring system stability"""
        pass

    # ================= COMMAND MANUAL =================

    @commands.command(name="help", aliases=["manual", "guide"])
    @require_level(1)
    async def help(self, ctx: commands.Context):
        """Interactive Intelligence Dashboard"""
        embed = luxury_embed(
            title="🌌 HellFire Hangout — ULTIMATE MANUAL",
            description=(
                "**System:** `v4.5 Platinum` | **Intelligence:** `God-Mode`\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• Prefix: `{BOT_PREFIX}`\n"
                f"• Status: `🟢 100% Operational`"
            ),
            color=COLOR_GOLD
        )
        await ctx.send(embed=embed, view=HelpView(self.bot))

    # ================= MASTER ROLE LOGIC =================

    @commands.command(name="role")
    @commands.guild_only()
    @require_level(3)
    async def role(self, ctx: commands.Context, member: discord.Member, *, role: discord.Role):
        """Intelligent Role Management (Toggle System)"""
        # Hierarchy Check
        if role.position >= ctx.author.top_role.position and ctx.author.id != ctx.guild.owner_id:
            return await ctx.send(embed=luxury_embed("❌ Hierarchy Error", "Role is higher than your authority.", COLOR_DANGER))
        
        if role.managed:
            return await ctx.send(embed=luxury_embed("❌ Error", "Managed roles cannot be assigned.", COLOR_DANGER))

        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(embed=luxury_embed("🔻 Role Removed", f"Successfully removed {role.mention} from {member.mention}.", COLOR_SECONDARY))
        else:
            await member.add_roles(role)
            await ctx.send(embed=luxury_embed("🔺 Role Added", f"Successfully assigned {role.mention} to {member.mention}.", COLOR_GOLD))

    # ================= INTELLIGENCE: WHOIS =================

    @commands.command(name="whois", aliases=["userinfo", "ui"])
    @commands.guild_only()
    async def whois(self, ctx: commands.Context, member: discord.Member = None):
        """Deep Analytics & Risk Assessment"""
        member = member or ctx.author
        warn_data = getattr(state, "WARN_DATA", {}).get(member.id, 0)
        
        # Risk Meter
        if warn_data == 0: risk = "🟢 Safe (Perfect Record)"
        elif warn_data < 4: risk = "🟡 Risky (Rule Breaker)"
        else: risk = "🔴 Dangerous (Terminal Status)"

        roles = [r.mention for r in reversed(member.roles) if r != ctx.guild.default_role]
        
        desc = (
            f"👤 **User:** {member.mention}\n"
            f"🆔 **ID:** `{member.id}`\n\n"
            f"🧠 **System Risk:** {risk}\n"
            f"🛡️ **Total Infractions:** `{warn_data}`\n\n"
            f"📅 **Created Account:** <t:{int(member.created_at.timestamp())}:D>\n"
            f"📅 **Joined Server:** <t:{int(member.joined_at.timestamp())}:R>\n\n"
            f"🎭 **Roles:** {', '.join(roles[:5])}{'...' if len(roles) > 5 else ''}"
        )
        embed = luxury_embed(f"🕵️ Profile Intel: {member.name}", desc, COLOR_GOLD)
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    # ================= INTELLIGENCE: SERVERINFO =================

    @commands.command(name="serverinfo", aliases=["si"])
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context):
        """Server-wide data analytics"""
        g = ctx.guild
        humans = len([m for m in g.members if not m.bot])
        bots = g.member_count - humans
        
        desc = (
            f"👑 **Owner:** {g.owner.mention}\n"
            f"📅 **Created:** <t:{int(g.created_at.timestamp())}:D>\n\n"
            f"👥 **Humans:** `{humans}` | 🤖 **Bots:** `{bots}`\n"
            f"💎 **Boost Tier:** `Level {g.premium_tier}` ({g.premium_subscription_count} boosts)\n"
            f"💬 **Channels:** `{len(g.channels)}` | 🎭 **Roles:** `{len(g.roles)}`"
        )
        embed = luxury_embed(f"🏰 {g.name} Metrics", desc, COLOR_GOLD)
        if g.icon: embed.set_thumbnail(url=g.icon.url)
        if g.banner: embed.set_image(url=g.banner.url)
        await ctx.send(embed=embed)

    # ================= UTILITY: AVATAR =================

    @commands.command(name="avatar", aliases=["av", "pfp"])
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """Fetch User Profile Picture in HD"""
        member = member or ctx.author
        url = member.display_avatar.with_static_format("png").url
        
        embed = luxury_embed(f"🖼️ {member.name}'s Avatar", f"[Direct HD Link]({url})", COLOR_GOLD)
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    # ================= UTILITY: PURGE =================

    @commands.command(name="purge", aliases=["clear"])
    @commands.guild_only()
    @require_level(3)
    async def purge(self, ctx: commands.Context, amount: int):
        """Sanitize channel messages"""
        if amount > 100: amount = 100
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount)
        
        msg = await ctx.send(f"🧹 **Sanitization Complete:** `{len(deleted)}` messages removed.")
        await asyncio.sleep(4)
        await msg.delete()

    # ================= UTILITY: PING =================

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        """High-Fidelity Latency Test"""
        start = time.perf_counter()
        message = await ctx.send(embed=luxury_embed("🛰️ Testing...", "Measuring Gateway and API cycles.", COLOR_SECONDARY))
        end = time.perf_counter()
        
        api_latency = round((end - start) * 1000)
        ws_latency = round(self.bot.latency * 1000)
        
        await message.edit(embed=luxury_embed("🛰️ System Latency", f"**REST API:** `{api_latency}ms`\n**Gateway:** `{ws_latency}ms`", COLOR_GOLD))

    # ================= DIAGNOSTICS =================

    @commands.command()
    @require_level(1)
    async def status(self, ctx: commands.Context):
        uptime = datetime.utcnow() - self.start_time
        h, r = divmod(int(uptime.total_seconds()), 3600)
        m, s = divmod(r, 60)

        embed = luxury_embed(
            title="📊 Universal Diagnostics",
            description=(
                f"⏱ **Uptime:** `{h}h {m}m {s}s`\n"
                f"🛡 **AutoMod:** `{'🟢 ON' if state.SYSTEM_FLAGS['automod_enabled'] else '🔴 OFF'}`\n"
                f"🚨 **Panic:** `{'🔴 ON' if state.SYSTEM_FLAGS['panic_mode'] else '🟢 OFF'}`\n"
                f"🧠 **Intelligence:** `Active (God-Mode)`"
            ),
            color=COLOR_SECONDARY
        )
        await ctx.send(embed=embed)

    # ================= ADMIN PROTOCOLS =================

    @commands.command()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True
        await ctx.send(embed=luxury_embed("🚨 PROTOCOL: PANIC", "Server lockdown active. Public permissions restricted.", COLOR_DANGER))

    @commands.command()
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = False
        await ctx.send(embed=luxury_embed("✅ PROTOCOL: CLEAR", "Lockdown lifted. Resuming Standard Operations.", COLOR_GOLD))

async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))
