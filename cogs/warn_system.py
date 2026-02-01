import discord
from discord.ext import commands
from datetime import timedelta

from utils.embeds import luxury_embed
from utils.config import STAFF_ROLES, COLOR_DANGER, COLOR_GOLD, COLOR_SECONDARY
from utils import state


class WarnSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Ensure state exists
        state.WARN_DATA = getattr(state, "WARN_DATA", {})
        state.WARN_LOGS = getattr(state, "WARN_LOGS", {})

    # =====================================================
    # STAFF LEVEL RESOLUTION (LEGACY COMPAT)
    # =====================================================

    def get_staff_level(self, member: discord.Member) -> int:
        for i, role in enumerate(STAFF_ROLES):
            if discord.utils.get(member.roles, name=role):
                return i + 1
        return 0

    # =====================================================
    # CORE WARNING ENGINE (NO COMMAND)
    # =====================================================

    async def apply_warning(
        self,
        ctx: commands.Context,
        member: discord.Member,
        reason: str,
        staff_level: int
    ):
        # Safety checks
        if member.bot or member == ctx.author:
            return

        user_id = member.id

        state.WARN_DATA[user_id] = state.WARN_DATA.get(user_id, 0) + 1
        state.WARN_LOGS.setdefault(user_id, []).append({
            "reason": reason,
            "by": ctx.author.id,
            "time": discord.utils.utcnow()
        })

        warns = state.WARN_DATA[user_id]

        # DM user
        try:
            await member.send(
                embed=luxury_embed(
                    title="⚠️ Official Warning Issued",
                    description=(
                        f"You have received a warning in **{ctx.guild.name}**.\n\n"
                        f"📄 **Reason:** {reason}\n"
                        f"⚠️ **Total Warnings:** {warns}\n\n"
                        "Continued violations may result in further action."
                    ),
                    color=COLOR_DANGER
                )
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Escalation logic (UNCHANGED, BUT FIXED)
        if warns == 3 and staff_level >= 2:
            if ctx.guild.me.guild_permissions.moderate_members:
                try:
                    await member.timeout(
                        timedelta(hours=24),
                        reason="Automatic timeout due to repeated warnings."
                    )
                except discord.Forbidden:
                    pass

        elif warns == 4 and staff_level >= 3:
            if ctx.guild.me.guild_permissions.kick_members:
                try:
                    await member.kick(
                        reason="Exceeded warning limit."
                    )
                except discord.Forbidden:
                    pass

        elif warns >= 5 and staff_level >= 4:
            if ctx.guild.me.guild_permissions.ban_members:
                try:
                    await member.ban(
                        reason="Exceeded warning limit."
                    )
                except discord.Forbidden:
                    pass

    # =====================================================
    # STAFF VIEW (READ-ONLY)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    async def warnstats(self, ctx: commands.Context, member: discord.Member):
        staff_level = self.get_staff_level(ctx.author)
        if staff_level < 1:
            return

        warns = state.WARN_DATA.get(member.id, 0)

        await ctx.send(
            embed=luxury_embed(
                title="📊 Warning Status",
                description=(
                    f"👤 **User:** {member.mention}\n"
                    f"⚠️ **Total Warnings:** {warns}"
                ),
                color=COLOR_GOLD
            )
        )


async def setup(bot):
    await bot.add_cog(WarnSystem(bot))
