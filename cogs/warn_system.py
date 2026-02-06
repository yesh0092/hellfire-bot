import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


# =====================================================
# WARN SYSTEM — READ ONLY (GOD MODE)
# =====================================================
# • No punishments here
# • No conflicts with moderation.py
# • Pure intelligence & visibility layer
# =====================================================


class WarnSystem(commands.Cog):
    """
    GOD-MODE WARNING INTELLIGENCE SYSTEM

    • Read-only (safe)
    • Shows history, trends, risk level
    • Anime-style presentation
    • Works with moderation.py escalation
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # =================================================
        # HARDEN SHARED STATE (CRITICAL)
        # =================================================
        if not hasattr(state, "WARN_DATA"):
            state.WARN_DATA = {}

        if not hasattr(state, "WARN_LOGS"):
            state.WARN_LOGS = {}

        if not hasattr(state, "STAFF_ROLE_TIERS"):
            state.STAFF_ROLE_TIERS = {}

    # =====================================================
    # INTERNAL STAFF CHECK
    # =====================================================

    def is_staff(self, member: discord.Member) -> bool:
        for role_id in state.STAFF_ROLE_TIERS.values():
            if role_id and any(r.id == role_id for r in member.roles):
                return True
        return False

    # =====================================================
    # WARN STATS (SUMMARY)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    async def warnstats(self, ctx: commands.Context, member: discord.Member):
        if not self.is_staff(ctx.author):
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Access Denied",
                    description="Only staff may view warning intelligence.",
                    color=COLOR_DANGER
                )
            )

        warns = state.WARN_DATA.get(member.id, 0)
        logs = state.WARN_LOGS.get(member.id, [])

        if not logs:
            return await ctx.send(
                embed=luxury_embed(
                    title="📊 Warning Status",
                    description=f"{member.mention} has **no warnings** on record.",
                    color=COLOR_SECONDARY
                )
            )

        # ---------------- RISK LEVEL ----------------
        if warns >= 5:
            risk = "🔴 CRITICAL"
        elif warns >= 3:
            risk = "🟠 HIGH"
        elif warns >= 1:
            risk = "🟡 LOW"
        else:
            risk = "🟢 CLEAN"

        # ---------------- LAST WARNING ----------------
        last = logs[-1]
        last_time = last["time"].strftime("%Y-%m-%d %H:%M UTC")

        embed = luxury_embed(
            title="📊 Warning Intelligence Report",
            description=(
                f"👤 **User:** {member.mention}\n"
                f"⚠️ **Total Warnings:** {warns}\n"
                f"🧠 **Risk Level:** {risk}\n\n"
                f"🕒 **Last Warning:** {last_time}\n"
                f"👮 **Issued By:** <@{last['by']}>\n"
                f"📄 **Reason:** {last['reason']}"
            ),
            color=COLOR_GOLD
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    # =====================================================
    # FULL WARNING HISTORY (DETAILED)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    async def warnhistory(self, ctx: commands.Context, member: discord.Member):
        if not self.is_staff(ctx.author):
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Access Denied",
                    description="Only staff may view warning history.",
                    color=COLOR_DANGER
                )
            )

        logs = state.WARN_LOGS.get(member.id, [])

        if not logs:
            return await ctx.send(
                embed=luxury_embed(
                    title="📜 Warning History",
                    description="No warnings recorded for this user.",
                    color=COLOR_SECONDARY
                )
            )

        lines = []
        for i, entry in enumerate(logs[-10:], start=1):
            lines.append(
                f"**{i}.** {entry['reason']}\n"
                f"• By: <@{entry['by']}>\n"
                f"• Date: {entry['time'].strftime('%Y-%m-%d')}"
            )

        embed = luxury_embed(
            title=f"📜 Warning History — {member}",
            description="\n\n".join(lines),
            color=COLOR_GOLD
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    # =====================================================
    # SERVER WARNING LEADERBOARD (INTEL)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    async def warnboard(self, ctx: commands.Context):
        if not self.is_staff(ctx.author):
            return

        if not state.WARN_DATA:
            return await ctx.send(
                embed=luxury_embed(
                    title="📊 Warning Leaderboard",
                    description="No warnings recorded yet.",
                    color=COLOR_SECONDARY
                )
            )

        # Sort by warning count
        ranked = sorted(
            state.WARN_DATA.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        lines = []
        for user_id, count in ranked:
            user = ctx.guild.get_member(user_id)
            if not user:
                continue
            lines.append(f"• {user.mention} — **{count} warnings**")

        await ctx.send(
            embed=luxury_embed(
                title="🚨 Server Warning Leaderboard",
                description="\n".join(lines),
                color=COLOR_GOLD
            )
        )

    # =====================================================
    # SELF CHECK (USER SAFE)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    async def mywarns(self, ctx: commands.Context):
        warns = state.WARN_DATA.get(ctx.author.id, 0)

        logs = state.WARN_LOGS.get(ctx.author.id, [])
        last = logs[-1]["time"].strftime("%Y-%m-%d") if logs else "N/A"

        await ctx.send(
            embed=luxury_embed(
                title="📊 Your Warning Status",
                description=(
                    f"⚠️ **Total Warnings:** {warns}\n"
                    f"🕒 **Last Warning:** {last}\n\n"
                    "If you believe a warning was incorrect, "
                    "please contact staff respectfully."
                ),
                color=COLOR_SECONDARY
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(WarnSystem(bot))
