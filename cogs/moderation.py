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
    # INTERNAL: TARGET SAFETY
    # =====================================================

    def _is_invalid_target(self, ctx, member: discord.Member) -> bool:
        if member == ctx.author:
            return True
        if member.bot:
            return True
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return True
        return False

    # =====================================================
    # INTERNAL: ESCALATION ENGINE
    # =====================================================

    async def _handle_escalation(self, ctx, member: discord.Member, warns: int):
        if warns == WARN_TIMEOUT_THRESHOLD:
            await self._apply_timeout(
                ctx,
                member,
                TIMEOUT_DURATION_MIN,
                "Automatic timeout due to repeated warnings."
            )

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
    @commands.guild_only()
    @require_level(1)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if self._is_invalid_target(ctx, member):
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Invalid Target",
                    description="You cannot issue moderation actions on this user.",
                    color=COLOR_DANGER
                )
            )

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
                    f"📄 **Reason:** {reason}\n"
                    f"⚠️ **Total Warnings:** {warns}\n\n"
                    "Repeated violations may result in automatic moderation."
                ),
                color=COLOR_SECONDARY
            )
        )

        await ctx.send(
            embed=luxury_embed(
                title="⚠️ Warning Logged",
                description=(
                    f"👤 **User:** {member.mention}\n"
                    f"📄 **Reason:** {reason}\n"
                    f"⚠️ **Total Warnings:** {warns}\n"
                    f"📩 **DM Sent:** {'✅ Yes' if dm_sent else '❌ No'}"
                ),
                color=COLOR_GOLD
            )
        )

        await self._handle_escalation(ctx, member, warns)

    # =====================================================
    # REMOVE WARN (Staff+)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(2)
    async def unwarn(self, ctx, member: discord.Member, count: int = 1):
        user_id = member.id

        if state.WARN_DATA.get(user_id, 0) <= 0:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ No Active Warnings",
                    description="This user currently has no warnings.",
                    color=COLOR_SECONDARY
                )
            )

        state.WARN_DATA[user_id] = max(0, state.WARN_DATA[user_id] - count)

        await ctx.send(
            embed=luxury_embed(
                title="✅ Warnings Updated",
                description=(
                    f"👤 **User:** {member.mention}\n"
                    f"⚠️ **Remaining Warnings:** {state.WARN_DATA[user_id]}"
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================================
    # TIMEOUT (Staff+)
    # =====================================================

    async def _apply_timeout(self, ctx, member, minutes, reason):
        if not ctx.guild.me.guild_permissions.moderate_members:
            return

        dm_sent = await self._safe_dm(
            member,
            luxury_embed(
                title="⏳ Timeout Applied",
                description=(
                    f"You have been temporarily restricted in **{ctx.guild.name}**.\n\n"
                    f"⏱ **Duration:** {minutes} minutes\n"
                    f"📄 **Reason:** {reason}"
                ),
                color=COLOR_SECONDARY
            )
        )

        try:
            await member.timeout(timedelta(minutes=minutes), reason=reason)
        except discord.Forbidden:
            return

        await ctx.send(
            embed=luxury_embed(
                title="⏳ Timeout Executed",
                description=(
                    f"👤 **User:** {member.mention}\n"
                    f"⏱ **Duration:** {minutes} minutes\n"
                    f"📩 **DM Sent:** {'✅ Yes' if dm_sent else '❌ No'}"
                ),
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @commands.guild_only()
    @require_level(2)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
        await self._apply_timeout(ctx, member, minutes, reason)

    # =====================================================
    # KICK (Staff++)
    # =====================================================

    async def _apply_kick(self, ctx, member, reason):
        if not ctx.guild.me.guild_permissions.kick_members:
            return

        dm_sent = await self._safe_dm(
            member,
            luxury_embed(
                title="🚫 Removed from Server",
                description=(
                    f"You have been removed from **{ctx.guild.name}**.\n\n"
                    f"📄 **Reason:** {reason}"
                ),
                color=COLOR_DANGER
            )
        )

        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            return

        await ctx.send(
            embed=luxury_embed(
                title="👢 Member Kicked",
                description=(
                    f"👤 **User:** {member.mention}\n"
                    f"📄 **Reason:** {reason}\n"
                    f"📩 **DM Sent:** {'✅ Yes' if dm_sent else '❌ No'}"
                ),
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @commands.guild_only()
    @require_level(3)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await self._apply_kick(ctx, member, reason)

    # =====================================================
    # BAN (Staff+++)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if not ctx.guild.me.guild_permissions.ban_members:
            return

        dm_sent = await self._safe_dm(
            member,
            luxury_embed(
                title="⚖️ Permanently Banned",
                description=(
                    f"You have been permanently banned from **{ctx.guild.name}**.\n\n"
                    f"📄 **Reason:** {reason}"
                ),
                color=COLOR_DANGER
            )
        )

        try:
            await member.ban(reason=reason)
        except discord.Forbidden:
            return

        await ctx.send(
            embed=luxury_embed(
                title="⛔ Member Banned",
                description=(
                    f"👤 **User:** {member.mention}\n"
                    f"📄 **Reason:** {reason}\n"
                    f"📩 **DM Sent:** {'✅ Yes' if dm_sent else '❌ No'}"
                ),
                color=COLOR_GOLD
            )
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
