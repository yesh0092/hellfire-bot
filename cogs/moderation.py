import discord
from discord.ext import commands
from datetime import timedelta, datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_DANGER, COLOR_SECONDARY
from utils.permissions import require_level
from utils import state


WARN_TIMEOUT_THRESHOLD = 3     # 3 warns → timeout
TIMEOUT_DURATION_MIN = 1440    # 24 hours
WARN_KICK_THRESHOLD = 5        # 5 warns → kick


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================

    def _bot_member(self, guild: discord.Guild) -> discord.Member | None:
        return guild.get_member(self.bot.user.id)

    async def _safe_dm(self, member: discord.Member, embed: discord.Embed) -> bool:
        try:
            await member.send(embed=embed)
            return True
        except (discord.Forbidden, discord.HTTPException):
            return False

    def _is_invalid_target(self, ctx: commands.Context, member: discord.Member) -> bool:
        if member == ctx.author:
            return True
        if member.bot:
            return True
        if member == ctx.guild.owner:
            return True
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return True
        return False

    # =====================================================
    # ESCALATION ENGINE (SAFE)
    # =====================================================

    async def _handle_escalation(self, ctx, member: discord.Member, warns: int):
        staff_level = getattr(ctx.command.callback, "required_level", 1)

        if warns == WARN_TIMEOUT_THRESHOLD and staff_level >= 2:
            await self._apply_timeout(
                ctx,
                member,
                TIMEOUT_DURATION_MIN,
                "Automatic timeout due to repeated warnings."
            )

        elif warns >= WARN_KICK_THRESHOLD and staff_level >= 3:
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
                    description="You cannot moderate this user.",
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
                title="⚠️ Warning Issued",
                description=(
                    f"📄 **Reason:** {reason}\n"
                    f"⚠️ **Total Warnings:** {warns}\n\n"
                    "Continued violations may trigger automatic moderation."
                ),
                color=COLOR_SECONDARY
            )
        )

        await ctx.send(
            embed=luxury_embed(
                title="⚠️ Warning Logged",
                description=(
                    f"👤 {member.mention}\n"
                    f"⚠️ Warnings: **{warns}**\n"
                    f"📩 DM Sent: {'✅ Yes' if dm_sent else '❌ No'}"
                ),
                color=COLOR_GOLD
            )
        )

        await self._handle_escalation(ctx, member, warns)

    # =====================================================
    # UNWARN (Staff+)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(2)
    async def unwarn(self, ctx, member: discord.Member, count: int = 1):
        user_id = member.id
        current = state.WARN_DATA.get(user_id, 0)

        if current <= 0:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ No Active Warnings",
                    description="This user has no warnings.",
                    color=COLOR_SECONDARY
                )
            )

        state.WARN_DATA[user_id] = max(0, current - count)

        await ctx.send(
            embed=luxury_embed(
                title="✅ Warnings Updated",
                description=(
                    f"👤 {member.mention}\n"
                    f"⚠️ Remaining: **{state.WARN_DATA[user_id]}**"
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================================
    # TIMEOUT (Staff+)
    # =====================================================

    async def _apply_timeout(self, ctx, member, minutes, reason):
        bot_member = self._bot_member(ctx.guild)
        if not bot_member or not bot_member.guild_permissions.moderate_members:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Missing Permission",
                    description="I need **Moderate Members** permission.",
                    color=COLOR_DANGER
                )
            )

        await self._safe_dm(
            member,
            luxury_embed(
                title="⏳ Timeout Applied",
                description=f"⏱ **Duration:** {minutes} minutes\n📄 **Reason:** {reason}",
                color=COLOR_SECONDARY
            )
        )

        await member.timeout(timedelta(minutes=minutes), reason=reason)

        await ctx.send(
            embed=luxury_embed(
                title="⏳ Timeout Executed",
                description=f"👤 {member.mention}\n⏱ {minutes} minutes",
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
        bot_member = self._bot_member(ctx.guild)
        if not bot_member or not bot_member.guild_permissions.kick_members:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Missing Permission",
                    description="I need **Kick Members** permission.",
                    color=COLOR_DANGER
                )
            )

        await self._safe_dm(
            member,
            luxury_embed(
                title="🚫 Removed from Server",
                description=f"📄 **Reason:** {reason}",
                color=COLOR_DANGER
            )
        )

        await member.kick(reason=reason)

        await ctx.send(
            embed=luxury_embed(
                title="👢 Member Kicked",
                description=f"👤 {member.mention}",
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
        bot_member = self._bot_member(ctx.guild)
        if not bot_member or not bot_member.guild_permissions.ban_members:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Missing Permission",
                    description="I need **Ban Members** permission.",
                    color=COLOR_DANGER
                )
            )

        await self._safe_dm(
