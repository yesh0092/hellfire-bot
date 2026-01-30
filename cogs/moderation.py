import discord
from discord.ext import commands
from datetime import timedelta, datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER, COLOR_GOLD, COLOR_SECONDARY, STAFF_ROLES
from utils import state


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # INTERNAL HELPERS
    # =====================================

    def get_staff_level(self, member: discord.Member) -> int:
        """
        Staff → 1
        Staff+ → 2
        Staff++ → 3
        Staff+++ → 4
        """
        for index, role_name in enumerate(STAFF_ROLES, start=1):
            if discord.utils.get(member.roles, name=role_name):
                return index
        return 0

    def is_staff(self, member: discord.Member) -> bool:
        return self.get_staff_level(member) > 0

    def record_staff_action(self, staff_id: int):
        stats = state.STAFF_STATS.setdefault(staff_id, {
            "actions": 0,
            "today": 0,
            "last_action": None
        })
        stats["actions"] += 1
        stats["today"] += 1
        stats["last_action"] = datetime.utcnow()

    # =====================================
    # TIMEOUT
    # =====================================

    @commands.command()
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
        staff_level = self.get_staff_level(ctx.author)

        if staff_level < 2:
            await ctx.send(
                embed=luxury_embed(
                    title="❌ Permission Denied",
                    description="You need **Staff+** or higher to timeout members.",
                    color=COLOR_DANGER
                )
            )
            return

        duration = timedelta(minutes=minutes)

        try:
            await member.send(
                embed=luxury_embed(
                    title="⏳ Temporary Timeout",
                    description=(
                        f"You have been temporarily restricted.\n\n"
                        f"**Duration:** {minutes} minutes\n"
                        f"**Reason:** {reason}"
                    ),
                    color=COLOR_SECONDARY
                )
            )
        except:
            pass

        await member.timeout(duration, reason=reason)

        await ctx.send(
            embed=luxury_embed(
                title="⏳ Timeout Applied",
                description=f"{member.mention} has been timed out for **{minutes} minutes**.",
                color=COLOR_GOLD
            )
        )

        self.record_staff_action(ctx.author.id)

    # =====================================
    # KICK
    # =====================================

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        staff_level = self.get_staff_level(ctx.author)

        if staff_level < 3:
            await ctx.send(
                embed=luxury_embed(
                    title="❌ Permission Denied",
                    description="You need **Staff++** or higher to kick members.",
                    color=COLOR_DANGER
                )
            )
            return

        try:
            await member.send(
                embed=luxury_embed(
                    title="🚫 Removal Notice",
                    description=(
                        f"You have been removed from the server.\n\n"
                        f"**Reason:** {reason}"
                    ),
                    color=COLOR_DANGER
                )
            )
        except:
            pass

        await member.kick(reason=reason)

        await ctx.send(
            embed=luxury_embed(
                title="🚫 Member Kicked",
                description=f"{member.mention} has been removed.",
                color=COLOR_GOLD
            )
        )

        self.record_staff_action(ctx.author.id)

    # =====================================
    # BAN
    # =====================================

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        staff_level = self.get_staff_level(ctx.author)

        if staff_level < 4:
            await ctx.send(
                embed=luxury_embed(
                    title="❌ Permission Denied",
                    description="You need **Staff+++** to ban members.",
                    color=COLOR_DANGER
                )
            )
            return

        try:
            await member.send(
                embed=luxury_embed(
                    title="⚖️ Permanent Ban",
                    description=(
                        f"You have been permanently banned.\n\n"
                        f"**Reason:** {reason}"
                    ),
                    color=COLOR_DANGER
                )
            )
        except:
            pass

        await member.ban(reason=reason, delete_message_days=1)

        await ctx.send(
            embed=luxury_embed(
                title="⚖️ Member Banned",
                description=f"{member.mention} has been permanently banned.",
                color=COLOR_GOLD
            )
        )

        self.record_staff_action(ctx.author.id)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
