import discord
from discord.ext import commands
from datetime import timedelta, datetime
import time

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_DANGER, COLOR_SECONDARY
from utils.permissions import require_level
from utils import state


# =====================================================
# CONFIGURATION (SMART & SAFE)
# =====================================================

WARN_TIMEOUT_THRESHOLD = 3
WARN_KICK_THRESHOLD = 5

TIMEOUT_DURATION_MIN = 1440        # 24h escalation
SPAM_TIMEOUT_MIN = 5               # spam timeout
SPAM_WINDOW_SEC = 6
SPAM_LIMIT_NORMAL = 6
SPAM_LIMIT_PANIC = 4

SPAM_COOLDOWN = 30                 # prevents punishment loops


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.spam_cache: dict[int, list[float]] = {}
        self.last_spam_action: dict[int, float] = {}

        # =================================================
        # HARDEN RUNTIME STATE (CRITICAL)
        # =================================================
        state.WARN_DATA = getattr(state, "WARN_DATA", {})
        state.WARN_LOGS = getattr(state, "WARN_LOGS", {})

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================

    def _bot_member(self, guild: discord.Guild):
        return guild.get_member(self.bot.user.id)

    def _invalid_target(self, ctx, member: discord.Member) -> bool:
        if member == ctx.author:
            return True
        if member.bot:
            return True
        if member == ctx.guild.owner:
            return True
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return True
        return False

    async def _safe_dm(self, member: discord.Member, embed: discord.Embed):
        try:
            await member.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def _log(self, ctx, title: str, description: str, color=COLOR_SECONDARY):
        if not ctx or not state.BOT_LOG_CHANNEL_ID:
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
    # AUTOMATIC SPAM PROTECTION (SILENT, NO SLOWMODE)
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

        # Ignore timed out users
        if member.is_timed_out():
            return

        uid = member.id
        now = time.time()

        # Cooldown after action
        if uid in self.last_spam_action and now - self.last_spam_action[uid] < SPAM_COOLDOWN:
            return

        self.spam_cache.setdefault(uid, []).append(now)
        self.spam_cache[uid] = [
            t for t in self.spam_cache[uid] if now - t < SPAM_WINDOW_SEC
        ]

        limit = (
            SPAM_LIMIT_PANIC
            if state.SYSTEM_FLAGS.get("panic_mode")
            else SPAM_LIMIT_NORMAL
        )

        if len(self.spam_cache[uid]) >= limit:
            try:
                await message.delete()
            except:
                pass

            self.last_spam_action[uid] = now

            await self._apply_timeout(
                ctx=None,
                member=member,
                minutes=SPAM_TIMEOUT_MIN,
                reason="Automatic spam protection",
                silent=True
            )

            self.spam_cache.pop(uid, None)

    # =====================================================
    # WARN SYSTEM (ESCALATING)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(1)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        if self._invalid_target(ctx, member):
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

        await self._safe_dm(
            member,
            luxury_embed(
                title="⚠️ Warning Issued",
                description=(
                    f"📄 **Reason:** {reason}\n"
                    f"⚠️ **Total Warnings:** {warns}"
                ),
                color=COLOR_SECONDARY
            )
        )

        await ctx.send(
            embed=luxury_embed(
                title="⚠️ Warning Logged",
                description=f"{member.mention} now has **{warns}** warnings.",
                color=COLOR_GOLD
            )
        )

        await self._log(
            ctx,
            "⚠️ Warning Issued",
            f"{member.mention}\nReason: {reason}\nTotal warnings: {warns}"
        )

        await self._handle_escalation(ctx, member, warns)

    async def _handle_escalation(self, ctx, member, warns: int):
        if warns == WARN_TIMEOUT_THRESHOLD:
            await self._apply_timeout(
                ctx,
                member,
                TIMEOUT_DURATION_MIN,
                "Automatic timeout due to repeated warnings"
            )

        elif warns >= WARN_KICK_THRESHOLD:
            await self._apply_kick(
                ctx,
                member,
                "Automatic kick due to excessive warnings"
            )

    # =====================================================
    # TIMEOUT
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(2)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
        await self._apply_timeout(ctx, member, minutes, reason)

    async def _apply_timeout(self, ctx, member, minutes: int, reason: str, silent=False):
        bot = self._bot_member(member.guild)
        if not bot or not bot.guild_permissions.moderate_members:
            return

        await self._safe_dm(
            member,
            luxury_embed(
                title="⏳ Timeout Applied",
                description=(
                    f"⏱ **Duration:** {minutes} minutes\n"
                    f"📄 **Reason:** {reason}"
                ),
                color=COLOR_SECONDARY
            )
        )

        await member.timeout(timedelta(minutes=minutes), reason=reason)

        if ctx and not silent:
            await ctx.send(
                embed=luxury_embed(
                    title="⏳ Timeout Executed",
                    description=f"{member.mention} timed out for **{minutes} minutes**.",
                    color=COLOR_GOLD
                )
            )

        if ctx:
            await self._log(
                ctx,
                "⏳ Timeout Applied",
                f"{member.mention}\nDuration: {minutes} min\nReason: {reason}"
            )

    # =====================================================
    # KICK
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(3)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await self._apply_kick(ctx, member, reason)

    async def _apply_kick(self, ctx, member, reason: str):
        bot = self._bot_member(ctx.guild)
        if not bot or not bot.guild_permissions.kick_members:
            return

        await self._safe_dm(
            member,
            luxury_embed(
                title="🚫 You Were Kicked",
                description=f"📄 **Reason:** {reason}",
                color=COLOR_DANGER
            )
        )

        await member.kick(reason=reason)

        await ctx.send(
            embed=luxury_embed(
                title="👢 Member Kicked",
                description=f"{member.mention} has been kicked.",
                color=COLOR_GOLD
            )
        )

        await self._log(
            ctx,
            "👢 Member Kicked",
            f"{member.mention}\nReason: {reason}"
        )

    # =====================================================
    # BAN
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        bot = self._bot_member(ctx.guild)
        if not bot or not bot.guild_permissions.ban_members:
            return

        await self._safe_dm(
            member,
            luxury_embed(
                title="⛔ You Were Banned",
                description=f"📄 **Reason:** {reason}",
                color=COLOR_DANGER
            )
        )

        await member.ban(reason=reason)

        await ctx.send(
            embed=luxury_embed(
                title="⛔ Member Banned",
                description=f"{member.mention} has been banned.",
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
