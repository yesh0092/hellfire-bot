import discord
from discord.ext import commands
from datetime import timedelta, datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_DANGER, COLOR_SECONDARY
from utils.permissions import require_level
from utils import state


# ===================== CONFIG =====================

WARN_TIMEOUT_THRESHOLD = 3     # 3 warns → timeout
TIMEOUT_DURATION_MIN = 1440    # 24 hours
WARN_KICK_THRESHOLD = 5        # 5 warns → kick


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # INTERNAL: SAFE DM
    # =====================================================

    async def _safe_dm(self, member: discord.Member, embed: discord.Embed) -> bool:
        try:
            await member.send(embed=embed)
            return True
        except (discord.Forbidden, discord.HTTPException):
            return False

    # =====================================================
    # INTERNAL: ESCALATION ENGINE
    # =====================================================

    async def _handle_escalation(self, ctx, member: discord.Member, warns: int):
        # 3 WARNS → TIMEOUT (Staff+ equivalent)
        if warns == WARN_TIMEOUT_THRESHOLD:
            await self._apply_timeout(
                ctx,
                member,
                TIMEOUT_DURATION_MIN,
                "Automatic timeout due to repeated warnings."
            )

        # 5 WARNS → KICK (Staff++ equivalent)
        elif warns >= WARN_KICK_THRESHOLD:
            await self._apply_kick(
                ctx,
                member,
                "Automatic kick due to excessive warnings."
            )

    # =====================================================
    # WARN (Staff)
    # =====================================================

    @commands.command()
    @require_level(1)  # Staff
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        user_id = member.id

        state.WARN_DATA[user_id] = state.WARN_DATA.get(user_id, 0) + 1
        state.WARN_LOGS.setdefault(user_id, []).append({
            "reason": reason,
            "by": ctx.author.id,
            "time": datetime.utcnow()
        })

        warns = state.WARN_DATA[user_id]

        dm_sent = await self._safe_dm(
            member,
            luxury_embed(
                title="⚠️ Official Warning Issued",
                description=(
                    f"You have received a warning in **{ctx.guild.name}**.\n\n"
                    f"**Reason:** {reason}\n"
                    f"**Total Warnings:** {warns}\n\n"
                    "Continued violations may result in automatic punishment."
                ),
                color=COLOR_SECONDARY
            )
        )

        await ctx.send(
            embed=luxury_embed(
                title="⚠️ Warning Logged",
                description=(
                    f"**User:** {member.mention}\n"
                    f"**Reason:** {reason}\n"
                    f"**Warn Count:** {warns}\n"
                    f"**DM Sent:** {'✅ Yes' if dm_sent else '❌ Failed'}"
                ),
                color=COLOR_GOLD
            )
        )

        # Escalation check
        await self._handle_escalation(ctx, member, warns)

    # =====================================================
    # REMOVE WARN (Staff+)
    # =====================================================

    @commands.command()
    @require_level(2)  # Staff+
    async def unwarn(self, ctx, member: discord.Member, count: int = 1):
        user_id = member.id

        if user_id not in state.WARN_DATA or state.WARN_DATA[user_id] <= 0:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ No Warnings Found",
                    description="This user has no active warnings.",
                    color=COLOR_SECONDARY
                )
            )

        state.WARN_DATA[user_id] = max(0, state.WARN_DATA[user_id] - count)

        await ctx.send(
            embed=luxury_embed(
                title="✅ Warnings Reduced",
                description=(
                    f"**User:** {member.mention}\n"
                    f"**Remaining Warnings:** {state.WARN_DATA[user_id]}"
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================================
    # TIMEOUT (Staff+)
    # =====================================================

    async def _apply_timeout(self, ctx, member, minutes, reason):
        dm_sent = await self._safe_dm(
            member,
            luxury_embed(
                title="⏳ Timeout Applied",
                description=(
                    f"You have been timed out in **{ctx.guild.name}**.\n\n"
                    f"**Duration:** {minutes} minutes\n"
                    f"**Reason:** {reason}"
                ),
                color=COLOR_SECONDARY
            )
        )

        await member.timeout(
            timedelta(minutes=minutes),
            reason=reason
        )

        await ctx.send(
            embed=luxury_embed(
                title="⏳ Timeout Executed",
                description=(
                    f"**User:** {member.mention}\n"
                    f"**Duration:** {minutes} minutes\n"
                    f"**DM Sent:** {'✅ Yes' if dm_sent else '❌ Failed'}"
                ),
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @require_level(2)  # Staff+
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
        await self._apply_timeout(ctx, member, minutes, reason)

    # =====================================================
    # KICK (Staff++)
    # =====================================================

    async def _apply_kick(self, ctx, member, reason):
        dm_sent = await self._safe_dm(
            member,
            luxury_embed(
                title="🚫 Removed from Server",
                description=(
                    f"You have been kicked from **{ctx.guild.name}**.\n\n"
                    f"**Reason:** {reason}"
                ),
                color=COLOR_DANGER
            )
        )

        await member.kick(reason=reason)

        await ctx.send(
            embed=luxury_embed(
                title="👢 Member Kicked",
                description=(
                    f"**User:** {member.mention}\n"
                    f"**Reason:** {reason}\n"
                    f"**DM Sent:** {'✅ Yes' if dm_sent else '❌ Failed'}"
                ),
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @require_level(3)  # Staff++
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await self._apply_kick(ctx, member, reason)

    # =====================================================
    # BAN (Staff+++)
    # =====================================================

    @commands.command()
    @require_level(4)  # Staff+++
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        dm_sent = await self._safe_dm(
            member,
            luxury_embed(
                title="⚖️ Permanently Banned",
                description=(
                    f"You have been banned from **{ctx.guild.name}**.\n\n"
                    f"**Reason:** {reason}"
                ),
                color=COLOR_DANGER
            )
        )

        await member.ban(reason=reason)

        await ctx.send(
            embed=luxury_embed(
                title="⛔ Member Banned",
                description=(
                    f"**User:** {member.mention}\n"
                    f"**Reason:** {reason}\n"
                    f"**DM Sent:** {'✅ Yes' if dm_sent else '❌ Failed'}"
                ),
                color=COLOR_GOLD
            )
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
