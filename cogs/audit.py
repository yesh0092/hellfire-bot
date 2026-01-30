import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER, COLOR_SECONDARY, COLOR_GOLD


class Audit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # MANUAL BAN DETECTION
    # =====================================

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """
        Detect bans issued via Discord UI and notify the user.
        """
        await asyncio.sleep(1)  # wait for audit log sync

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.ban,
            limit=3
        ):
            if entry.target.id == user.id:
                await self.notify_user(
                    user=user,
                    title="⚖️ Imperial Banishment",
                    description=(
                        "You have been permanently banned from **Hellfire Hangout**.\n\n"
                        f"**Moderator:** {entry.user}\n"
                        f"**Reason:** {entry.reason or 'Policy violation.'}"
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
        Detects manual kicks (not voluntary leaves).
        """
        await asyncio.sleep(1)

        guild = member.guild
        cutoff = datetime.utcnow() - timedelta(seconds=10)

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.kick,
            limit=3
        ):
            if (
                entry.target.id == member.id
                and entry.created_at.replace(tzinfo=None) >= cutoff
            ):
                await self.notify_user(
                    user=member,
                    title="🚫 Departure Notice",
                    description=(
                        "Your presence at **Hellfire Hangout** has been concluded.\n\n"
                        f"**Action:** Manual Kick\n"
                        f"**Moderator:** {entry.user}\n"
                        f"**Reason:** {entry.reason or 'Management decision.'}"
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

        await asyncio.sleep(1)

        guild = after.guild
        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.member_update,
            limit=5
        ):
            if entry.target.id == after.id:
                await self.notify_user(
                    user=after,
                    title="⏳ Silence Bestowed",
                    description=(
                        "Your privileges at **Hellfire Hangout** have been temporarily suspended.\n\n"
                        f"**Moderator:** {entry.user}\n"
                        f"**Until:** {after.timed_out_until.strftime('%Y-%m-%d %H:%M UTC')}\n"
                        f"**Reason:** {entry.reason or 'Reflection period required.'}"
                    ),
                    color=COLOR_SECONDARY
                )
                break

    # =====================================
    # NOTIFICATION HELPER
    # =====================================

    async def notify_user(self, user: discord.abc.User, title: str, description: str, color: int):
        """
        Safely DM a user with audit information.
        """
        try:
            await user.send(
                embed=luxury_embed(
                    title=title,
                    description=description,
                    color=color
                )
            )
        except:
            # User DMs closed or blocked — silently ignore
            pass


async def setup(bot):
    await bot.add_cog(Audit(bot))
