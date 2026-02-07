import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state

# =====================================================
# WARN SYSTEM — READ ONLY (GOD MODE)
# =====================================================

class WarnSystem(commands.Cog):
    """
    GOD-MODE WARNING INTELLIGENCE SYSTEM
    
    • Advanced Analytics & Risk Assessment
    • Non-Invasive (Read-Only)
    • Staff Enforcer Tracking
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Harden Shared State
        if not hasattr(state, "WARN_DATA"): state.WARN_DATA = {}
        if not hasattr(state, "WARN_LOGS"): state.WARN_LOGS = {}
        if not hasattr(state, "STAFF_ROLE_TIERS"): state.STAFF_ROLE_TIERS = {}
        
        # Start background maintenance
        self.prune_stale_data.start()

    def cog_unload(self):
        self.prune_stale_data.cancel()

    # =====================================================
    # INTERNAL UTILS
    # =====================================================

    def is_staff(self, member: discord.Member) -> bool:
        if member.guild_permissions.administrator:
            return True
        # Check against the intelligence tiers in state
        for role_id in state.STAFF_ROLE_TIERS.values():
            if role_id and any(r.id == role_id for r in member.roles):
                return True
        return False

    def get_progress_bar(self, count: int, max_val: int = 8) -> str:
        """Generates a visual bar for warning progression"""
        filled = min(count, max_val)
        empty = max_val - filled
        return f"{'🟥' * filled}{'⬜' * empty}"

    # =====================================================
    # INTELLIGENCE COMMANDS
    # =====================================================

    @commands.command(name="warnstats", aliases=["ws", "intel"])
    @commands.guild_only()
    async def warnstats(self, ctx: commands.Context, member: discord.Member):
        """Advanced Warning Intelligence Report"""
        if not self.is_staff(ctx.author):
            return await ctx.send(embed=luxury_embed("❌ Denied", "Staff Only: Intelligence clearance required.", COLOR_DANGER))

        warns = state.WARN_DATA.get(member.id, 0)
        logs = state.WARN_LOGS.get(member.id, [])

        if not logs:
            return await ctx.send(embed=luxury_embed("📊 Intel", f"{member.mention} has a clean record in the archives.", COLOR_SECONDARY))

        # --- RISK ANALYSIS ---
        risk_level = "🟢 CLEAN"
        if warns >= 8: risk_level = "💀 TERMINAL (7D TIMEOUT REACHED)"
        elif warns >= 6: risk_level = "🔴 CRITICAL (24H AT RISK)"
        elif warns >= 4: risk_level = "🟠 HIGH (6H AT RISK)"
        elif warns >= 1: risk_level = "🟡 ELEVATED"

        # Frequency Calculation (Warnings per week)
        first_warn_time = logs[0]["time"]
        first_warn_dt = datetime.fromtimestamp(first_warn_time)
        days_since = (datetime.utcnow() - first_warn_dt).days or 1
        frequency = round((warns / days_since) * 7, 2)

        last = logs[-1]
        progress = self.get_progress_bar(warns)

        embed = luxury_embed(
            title="🧠 Intelligence Report",
            description=(
                f"👤 **Target:** {member.mention}\n"
                f"📊 **Risk Status:** {risk_level}\n"
                f"📈 **Velocity:** `{frequency}` warns/week\n\n"
                f"**Punishment Progress:**\n`{progress}` ({warns}/8)\n\n"
                f"🕒 **Recent Activity:** <t:{int(last['time'])}:R>\n"
                f"👮 **Assigned Mod:** <@{last['by']}>\n"
                f"📄 **Last Reason:** {last['reason']}"
            ),
            color=COLOR_GOLD if warns < 6 else COLOR_DANGER
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="warnhistory", aliases=["wh", "logs"])
    @commands.guild_only()
    async def warnhistory(self, ctx: commands.Context, member: discord.Member):
        """Full audit trail of user violations"""
        if not self.is_staff(ctx.author):
             return await ctx.send(embed=luxury_embed("❌ Denied", "Clearance Required.", COLOR_DANGER))
        
        logs = state.WARN_LOGS.get(member.id, [])
        if not logs:
            return await ctx.send(embed=luxury_embed("📜 Audit", "No incident records found for this user.", COLOR_SECONDARY))

        # Show last 15 incidents
        history = []
        for i, entry in enumerate(reversed(logs[-15:]), start=1):
            history.append(
                f"**#{len(logs)-i+1}** | <t:{int(entry['time'])}:d>\n"
                f"└ `Reason:` {entry['reason']}\n"
                f"└ `Staff:` <@{entry['by']}>"
            )

        embed = luxury_embed(
            title=f"📜 Incident History: {member.name}",
            description="\n".join(history),
            color=COLOR_GOLD
        )
        await ctx.send(embed=embed)

    @commands.command(name="warnboard", aliases=["wb", "topwarns"])
    @commands.guild_only()
    async def warnboard(self, ctx: commands.Context):
        """Top offenders and staff metrics"""
        if not self.is_staff(ctx.author): return

        if not state.WARN_DATA:
            return await ctx.send(embed=luxury_embed("📊 Intel", "The archives are currently empty.", COLOR_SECONDARY))

        # User Leaderboard
        ranked_users = sorted(state.WARN_DATA.items(), key=lambda x: x[1], reverse=True)[:5]
        user_list = [f"`{count}x` <@{uid}>" for uid, count in ranked_users]

        # Staff Metrics
        staff_counts = {}
        for user_logs in state.WARN_LOGS.values():
            for entry in user_logs:
                sid = entry['by']
                staff_counts[sid] = staff_counts.get(sid, 0) + 1
        
        ranked_staff = sorted(staff_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        staff_list = [f"`{count}x` <@{sid}>" for sid, count in ranked_staff]

        embed = luxury_embed(
            title="🚨 Security Intelligence Dashboard",
            description=(
                "**🔥 Top Offenders**\n" + ("\n".join(user_list) or "None") + 
                "\n\n**👮 Most Active Enforcers**\n" + ("\n".join(staff_list) or "None")
            ),
            color=COLOR_GOLD
        )
        await ctx.send(embed=embed)

    @commands.command(name="mywarns")
    @commands.guild_only()
    async def mywarns(self, ctx: commands.Context):
        """Private check for users"""
        warns = state.WARN_DATA.get(ctx.author.id, 0)
        
        status = "🟢 Good Standing"
        if warns >= 6: status = "🔴 Near Permanent Ban"
        elif warns >= 3: status = "🟡 Strict Monitoring"

        embed = luxury_embed(
            title="🛡️ Your Security Status",
            description=(
                f"⚠️ **Total Violations:** {warns}\n"
                f"🛡️ **Account Health:** {status}\n\n"
                "*Maintain protocol to avoid automated escalations.*"
            ),
            color=COLOR_SECONDARY if warns < 3 else COLOR_DANGER
        )
        await ctx.send(embed=embed)

    # =====================================================
    # BACKGROUND MAINTENANCE
    # =====================================================

    @tasks.loop(hours=24)
    async def prune_stale_data(self):
        """Cleans up data for users who left to keep state lightweight"""
        await self.bot.wait_until_ready()
        
        # FIXED: Use a loop across all guilds the bot is in if MAIN_GUILD_ID is missing
        all_member_ids = set()
        for guild in self.bot.guilds:
            for member in guild.members:
                all_member_ids.add(member.id)
        
        # Prune dead records
        removed_count = 0
        for uid in list(state.WARN_DATA.keys()):
            if uid not in all_member_ids:
                state.WARN_DATA.pop(uid, None)
                state.WARN_LOGS.pop(uid, None)
                removed_count += 1
        
        if removed_count > 0:
            print(f"[Intelligence] Pruned {removed_count} stale records from archives.")

# =====================================================
# SETUP
# =====================================================

async def setup(bot: commands.Bot):
    # Prevent Registration Collisions
    conflicting = ['warnstats', 'warnhistory', 'warnboard', 'mywarns']
    for cmd in conflicting:
        if bot.get_command(cmd):
            bot.remove_command(cmd)

    await bot.add_cog(WarnSystem(bot))
