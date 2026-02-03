import discord
from discord.ext import commands
from datetime import timedelta, datetime
import time

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_DANGER, COLOR_SECONDARY
from utils.permissions import require_level
from utils import state


# =====================================================
# CONFIGURATION
# =====================================================

WARN_TIMEOUT_THRESHOLD = 3     # 3 warns → timeout
WARN_KICK_THRESHOLD = 5        # 5 warns → kick

TIMEOUT_DURATION_MIN = 1440    # 24 hours
SPAM_TIMEOUT_MIN = 5           # 5 minutes (spam)
SPAM_WINDOW_SEC = 6
SPAM_LIMIT_NORMAL = 6
SPAM_LIMIT_PANIC = 4


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.spam_cache = {}

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================

    def _bot_member(self, guild: discord.Guild):
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

    async def _log(self, ctx, title: str, description: str, color=COLOR_SECONDARY):
        if not state.BOT_LOG_CHANNEL_ID:
            return

        channel = ctx.guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        try:
            await channel.send(
                embed=luxury_embed(
                    title=title,
                    description=description,
                    color=color
                )
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

    # =====================================================
    # AUTOMATIC SPAM PROTECTION
    # =====================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if not state.SYSTEM_FLAGS.get("automod_enabled", True):
            return

        member = message.author

        # Ignore staff
        if member.guild_permissions.manage_messages:
            return

        uid = member.id
        now = time.time()

        self.spam_cache.setdefault(uid, [])
        self.spam_cache[uid].append(now)

        # Keep only recent timestamps
        self.spam_cache[uid] = [
            t for t in self.spam_cache[uid]
            if now - t < SPAM_WINDOW_SEC
        ]

        limit = SPAM_LIMIT_PANIC if state.SYSTEM_FLAGS.get("panic_mode") else SPAM_LIMIT_NORMAL

        if len(self.spam_cache[uid]) >= limit:
            try:
                await message.delete()
            except:
                pass

            await self._apply_timeout(
                ctx=None,
                member=member,
                minutes=SPAM_TIMEOUT_MIN,
                reason="Automatic timeout due to message spam",
                silent=True
            )

            self.spam_cache.pop(uid, None)

    # =====================================================
    # ESCALATION ENGINE
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
    # WARN
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

        uid = member.id
        state.WARN_DATA[uid] = state.WARN_DATA.get(uid, 0) + 1
        warns = state.WARN_DATA[uid]

        state.WARN_LOGS.setdefault(uid, []).append({
            "reason": reason,
            "by": ctx.author.id,
            "time": datetime.utcnow()
        })

        dm_sent = await self._safe_dm(
            member,
            luxury_embed(
                title="⚠️ Warning Issued",
                description=(
                    f"📄 **Reason:** {reason}\n"
                    f"⚠️ **Total Warnings:** {warns}\n\n"
                    "Further violations may trigger automatic punishment."
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

        await self._log(
            ctx,
            "⚠️ Warning Issued",
            f"{member.mention}\nReason: {reason}\nTotal warnings: {warns}"
        )

        await self._handle_escalation(ctx, member, warns)

    # =====================================================
    # UNWARN
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(2)
    async def unwarn(self, ctx, member: discord.Member, count: int = 1):
        uid = member.id
        current = state.WARN_DATA.get(uid, 0)

        if current <= 0:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ No Active Warnings",
                    description="This user has no warnings.",
                    color=COLOR_SECONDARY
                )
            )

        state.WARN_DATA[uid] = max(0, current - count)

        await ctx.send(
            embed=luxury_embed(
                title="✅ Warnings Updated",
                description=(
                    f"👤 {member.mention}\n"
                    f"⚠️ Remaining: **{state.WARN_DATA[uid]}**"
                ),
                color=COLOR_GOLD
            )
        )

        await self._log(
            ctx,
            "⚠️ Warnings Reduced",
            f"{member.mention}\nRemaining warnings: {state.WARN_DATA[uid]}"
        )

    # =====================================================
    # TIMEOUT
    # =====================================================

    async def _apply_timeout(self, ctx, member, minutes, reason, silent=False):
        bot_member = self._bot_member(member.guild)
        if not bot_member or not bot_member.guild_permissions.moderate_members:
            return

        await self._safe_dm(
            member,
            luxury_embed(
                title="⏳ Timeout Applied",
                description=f"⏱ **Duration:** {minutes} minutes\n📄 **Reason:** {reason}",
                color=COLOR_SECONDARY
            )
        )

        await member.timeout(
            timedelta(minutes=minutes),
            reason=reason
        )

        if not silent and ctx:
            await ctx.send(
                embed=luxury_embed(
                    title="⏳ Timeout Executed",
                    description=f"👤 {member.mention}\n⏱ {minutes} minutes",
                    color=COLOR_GOLD
                )
            )

        if ctx:
            await self._log(
                ctx,
                "⏳ Timeout Applied",
                f"{member.mention}\nDuration: {minutes} min\nReason: {reason}"
            )

    @commands.command()
    @commands.guild_only()
    @require_level(2)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
        await self._apply_timeout(ctx, member, minutes, reason)

    # =====================================================
    # KICK
    # =====================================================

    async def _apply_kick(self, ctx, member, reason):
        bot_member = self._bot_member(ctx.guild)
        if not bot_member or not bot_member.guild_permissions.kick_members:
            return

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

        await self._log(
            ctx,
            "👢 Member Kicked",
            f"{member.mention}\nReason: {reason}"
        )

    @commands.command()
    @commands.guild_only()
    @require_level(3)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await self._apply_kick(ctx, member, reason)

    # =====================================================
    # BAN
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        bot_member = self._bot_member(ctx.guild)
        if not bot_member or not bot_member.guild_permissions.ban_members:
            return

        await self._safe_dm(
            member,
            luxury_embed(
                title="⚖️ Permanently Banned",
                description=f"📄 **Reason:** {reason}",
                color=COLOR_DANGER
            )
        )

        await member.ban(reason=reason)

        await ctx.send(
            embed=luxury_embed(
                title="⛔ Member Banned",
                description=f"👤 {member.mention}",
                color=COLOR_GOLD
            )
        )

        await self._log(
            ctx,
            "⛔ Member Banned",
            f"{member.mention}\nReason: {reason}"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
