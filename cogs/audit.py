import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER, COLOR_SECONDARY


class Audit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =================================================
    # INTERNAL PERMISSION CHECK
    # =================================================

    def can_view_audit_logs(self, guild: discord.Guild) -> bool:
        bot_member = guild.get_member(self.bot.user.id)
        return bool(bot_member and bot_member.guild_permissions.view_audit_log)

    # =================================================
    # MANUAL BAN DETECTION
    # =================================================

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if not self.can_view_audit_logs(guild):
            return

        await asyncio.sleep(1)

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.ban,
            limit=5
        ):
            if entry.target.id != user.id:
                continue

            # Ignore bot-issued bans
            if entry.user and entry.user.id == self.bot.user.id:
                return

            await self.notify_user(
                user=user,
                title="⚖️ Imperial Banishment",
                description=(
                    "You have been **permanently banned** from **HellFire Hangout**.\n\n"
                    f"👤 **Moderator:** {entry.user}\n"
                    f"📄 **Reason:** {entry.reason or 'Violation of community policies.'}"
                ),
                color=COLOR_DANGER
            )
            break

    # =================================================
    # MANUAL KICK DETECTION
    # =================================================

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild

        if not self.can_view_audit_logs(guild):
            return

        await asyncio.sleep(1)
        cutoff = datetime.utcnow() - timedelta(seconds=10)

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.kick,
            limit=5
        ):
            if entry.target.id != member.id:
                continue

            if entry.created_at.replace(tzinfo=None) < cutoff:
                continue

            # Ignore bot-issued kicks
            if entry.user and entry.user.id == self.bot.user.id:
                return

            await self.notify_user(
                user=member,
                title="🚫 Removal Notice",
                description=(
                    "You have been **removed** from **HellFire Hangout**.\n\n"
                    f"⚙️ **Action:** Manual Kick\n"
                    f"👤 **Moderator:** {entry.user}\n"
                    f"📄 **Reason:** {entry.reason or 'Administrative decision.'}"
                ),
                color=COLOR_DANGER
            )
            break

    # =================================================
    # MANUAL TIMEOUT DETECTION
    # =================================================

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.timed_out_until == after.timed_out_until:
            return

        if after.timed_out_until is None:
            return

        guild = after.guild

        if not self.can_view_audit_logs(guild):
            return

        await asyncio.sleep(1)

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.member_update,
            limit=5
        ):
            if entry.target.id != after.id:
                continue

            # Ignore bot-issued timeouts
            if entry.user and entry.user.id == self.bot.user.id:
                return

            until = after.timed_out_until.strftime("%Y-%m-%d %H:%M UTC")

            await self.notify_user(
                user=after,
                title="⏳ Temporary Restriction Applied",
                description=(
                    "Your communication privileges in **HellFire Hangout** have been "
                    "**temporarily restricted**.\n\n"
                    f"👤 **Moderator:** {entry.user}\n"
                    f"⏰ **Until:** {until}\n"
                    f"📄 **Reason:** {entry.reason or 'Cooldown period required.'}"
                ),
                color=COLOR_SECONDARY
            )
            break

    # =================================================
    # SAFE DM HELPER
    # =================================================

    async def notify_user(
        self,
        user: discord.abc.User,
        title: str,
        description: str,
        color: int
    ):
        try:
            await user.send(
                embed=luxury_embed(
                    title=title,
                    description=description,
                    color=color
                )
            )
        except (discord.Forbidden, discord.HTTPException):
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Audit(bot))
