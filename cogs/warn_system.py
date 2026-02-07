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
        state.WARN_DATA = getattr(state, "WARN_DATA", {})
        state.WARN_LOGS = getattr(state, "WARN_LOGS", {})
        state.STAFF_ROLE_TIERS = getattr(state, "STAFF_ROLE_TIERS", {})
        
        self.prune_stale_data.start()

    def cog_unload(self):
        self.prune_stale_data.cancel()

    # =====================================================
    # INTERNAL UTILS
    # =====================================================

    def is_staff(self, member: discord.Member) -> bool:
        if member.guild_permissions.administrator:
            return True
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

    @commands.command(aliases=["ws", "intel"])
    @commands.guild_only()
    async def warnstats(self, ctx: commands.Context, member: discord.Member):
        """Advanced Warning Intelligence Report"""
        if not self.is_staff(ctx.author):
            return await ctx.send(embed=luxury_embed("❌ Denied", "Staff only.", COLOR_DANGER))

        warns = state.WARN_DATA.get(member.id, 0)
        logs = state.WARN_LOGS.get(member.id, [])

        if not logs:
            return await ctx.send(embed=luxury_embed("📊 Intel", f"{member.mention} is clean.", COLOR_SECONDARY))

        # --- RISK ANALYSIS ---
        risk_level = "🟢 CLEAN"
        if warns >= 8: risk_level = "💀 TERMINAL (7D TIMEOUT REACHED)"
        elif warns >= 6: risk_level = "🔴 CRITICAL (24H AT RISK)"
        elif warns >= 4: risk_level = "🟠 HIGH (6H AT RISK)"
        elif warns >= 1: risk_level = "🟡 ELEVATED"

        # Frequency Calculation (Warnings per week)
        first_warn = datetime.fromtimestamp(logs[0]["time"])
        days_since = (datetime.utcnow() - first_warn).days or 1
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

    @commands.command(aliases=["wh", "logs"])
    @commands.guild_only()
    async def warnhistory(self, ctx: commands.Context, member: discord.Member):
        """Full audit trail of user violations"""
        if not self.is_staff(ctx.author): return
        
        logs = state.WARN_LOGS.get(member.id, [])
        if not logs:
            return await ctx.send(embed=luxury_embed("📜 Audit", "No records found.", COLOR_SECONDARY))

        # Show last 15 instead of 10
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

    @commands.command(aliases=["wb", "topwarns"])
    @commands.guild_only()
    async def warnboard(self, ctx: commands.Context):
        """Top offenders and staff metrics"""
        if not self.is_staff(ctx.author): return

        if not state.WARN_DATA:
            return await ctx.send("📊 No warning data found.")

        # User Leaderboard
        ranked_users = sorted(state.WARN_DATA.items(), key=lambda x: x[1], reverse=True)[:5]
        user_list = []
        for uid, count in ranked_users:
            user_list.append(f"`{count}x` <@{uid}>")

        # Staff Metrics (Who is issuing the most?)
        staff_counts = {}
        for user_logs in state.WARN_LOGS.values():
            for entry in user_logs:
                staff_id = entry['by']
                staff_counts[staff_id] = staff_counts.get(staff_id, 0) + 1
        
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

    @commands.command()
    @commands.guild_only()
    async def mywarns(self, ctx: commands.Context):
        """Private check for users"""
        warns = state.WARN_DATA.get(ctx.author.id, 0)
        
        status = "Good Standing"
        if warns >= 6: status = "Near Permanent Ban"
        elif warns >= 3: status = "Strict Monitoring"

        embed = luxury_embed(
            title="🛡️ Your Security Status",
            description=(
                f"⚠️ **Total Violations:** {warns}\n"
                f"🛡️ **Account Health:** {status}\n\n"
                "*Please follow the server rules to avoid further automated escalations.*"
            ),
            color=COLOR_SECONDARY if warns < 3 else COLOR_DANGER
        )
        await ctx.send(embed=embed)

    # =====================================================
    # BACKGROUND MAINTENANCE
    # =====================================================

    @tasks.loop(hours=24)
    async def prune_stale_data(self):
        """Deletes warning data for users no longer in the server (Efficiency)"""
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(state.MAIN_GUILD_ID)
        if not guild: return

        active_uids = [m.id for m in guild.members]
        
        # Prune state.WARN_DATA
        for uid in list(state.WARN_DATA.keys()):
            if uid not in active_uids:
                state.WARN_DATA.pop(uid, None)
                state.WARN_LOGS.pop(uid, None)

async def setup(bot: commands.Bot):
    await bot.add_cog(WarnSystem(bot))
