import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER, COLOR_SECONDARY


class Audit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # MANUAL BAN DETECTION
    # =====================================

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """
        Detect bans issued manually via Discord UI and notify the user.
        """
        if not guild.me.guild_permissions.view_audit_log:
            return

        await asyncio.sleep(1)  # Allow audit logs to sync

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.ban,
            limit=5
        ):
            if entry.target.id != user.id:
                continue

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

    # =====================================
    # MANUAL KICK DETECTION
    # =====================================

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """
        Detects manual kicks (not voluntary departures).
        """
        guild = member.guild

        if not guild.me.guild_permissions.view_audit_log:
            return

        await asyncio.sleep(1)

        cutoff = datetime.utcnow() - timedelta(seconds=10)

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.kick,
            limit=5
        ):
            if (
                entry.target.id == member.id
                and entry.created_at.replace(tzinfo=None) >= cutoff
            ):
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

    # =====================================
    # MANUAL TIMEOUT DETECTION
    # =====================================

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """
        Detects manual timeouts applied via Discord UI.
        """
        if before.timed_out_until == after.timed_out_until:
            return

        if after.timed_out_until is None:
            return

        guild = after.guild

        if not guild.me.guild_permissions.view_audit_log:
            return

        await asyncio.sleep(1)

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.member_update,
            limit=5
        ):
            if entry.target.id != after.id:
                continue

            until = after.timed_out_until.strftime("%Y-%m-%d %H:%M UTC")

            await self.notify_user(
                user=after,
                title="⏳ Temporary Restriction Applied",
                description=(
                    "Your communication privileges in **HellFire Hangout** have been **temporarily restricted**.\n\n"
                    f"👤 **Moderator:** {entry.user}\n"
                    f"⏰ **Until:** {until}\n"
                    f"📄 **Reason:** {entry.reason or 'Cooldown period required.'}"
                ),
                color=COLOR_SECONDARY
            )
            break

    # =====================================
    # NOTIFICATION HELPER
    # =====================================

    async def notify_user(
        self,
        user: discord.abc.User,
        title: str,
        description: str,
        color: int
    ):
        """
        Safely DM a user with audit-related information.
        """
        try:
            await user.send(
                embed=luxury_embed(
                    title=title,
                    description=description,
                    color=color
                )
            )
        except (discord.Forbidden, discord.HTTPException):
            # DMs closed or user blocked the bot — ignore silently
            pass


async def setup(bot):
    await bot.add_cog(Audit(bot))
