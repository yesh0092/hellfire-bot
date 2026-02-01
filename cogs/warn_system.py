import discord
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import STAFF_ROLES, COLOR_GOLD, COLOR_SECONDARY
from utils import state


class WarnSystem(commands.Cog):
    """
    READ-ONLY warning system.
    Actual moderation actions are handled in moderation.py
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Ensure shared state exists
        state.WARN_DATA = getattr(state, "WARN_DATA", {})
        state.WARN_LOGS = getattr(state, "WARN_LOGS", {})

    # =====================================================
    # STAFF LEVEL CHECK (VIEW ONLY)
    # =====================================================

    def is_staff(self, member: discord.Member) -> bool:
        return any(role.name in STAFF_ROLES for role in member.roles)

    # =====================================================
    # WARNING STATS (SAFE)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    async def warnstats(self, ctx: commands.Context, member: discord.Member):
        if not self.is_staff(ctx.author):
            return

        warns = state.WARN_DATA.get(member.id, 0)
        logs = state.WARN_LOGS.get(member.id, [])

        if not logs:
            return await ctx.send(
                embed=luxury_embed(
                    title="📊 Warning Status",
                    description=f"{member.mention} has **no warnings**.",
                    color=COLOR_SECONDARY
                )
            )

        recent = logs[-5:]
        details = ""

        for i, entry in enumerate(recent, start=1):
            details += (
                f"**{i}.** {entry['reason']}\n"
                f"• By: <@{entry['by']}>\n"
                f"• Date: {entry['time'].strftime('%Y-%m-%d')}\n\n"
            )

        await ctx.send(
            embed=luxury_embed(
                title="📊 Warning History",
                description=(
                    f"👤 **User:** {member.mention}\n"
                    f"⚠️ **Total Warnings:** {warns}\n\n"
                    f"{details}"
                ),
                color=COLOR_GOLD
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(WarnSystem(bot))
