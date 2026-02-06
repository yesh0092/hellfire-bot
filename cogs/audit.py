import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER, COLOR_SECONDARY, COLOR_GOLD
from utils import state


class Audit(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Prevent duplicate notifications
        self._recent_actions: dict[tuple[int, str], datetime] = {}

    # =================================================
    # INTERNAL HELPERS
    # =================================================

    def _can_view_audit(self, guild: discord.Guild) -> bool:
        me = guild.get_member(self.bot.user.id)
        return bool(me and me.guild_permissions.view_audit_log)

    def _is_duplicate(self, user_id: int, action: str, window: int = 10) -> bool:
        """
        Prevent duplicate DM spam for same action
        """
        key = (user_id, action)
        now = datetime.utcnow()

        last = self._recent_actions.get(key)
        if last and (now - last).total_seconds() < window:
            return True

        self._recent_actions[key] = now
        return False

    async def _safe_dm(self, user: discord.abc.User, embed: discord.Embed):
        try:
            await user.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def _log(self, guild: discord.Guild, title: str, description: str, color=COLOR_SECONDARY):
        if not state.BOT_LOG_CHANNEL_ID:
            return

        channel = guild.get_channel(state.BOT_LOG_CHANNEL_ID)
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

    # =================================================
    # MANUAL BAN DETECTION
    # =================================================

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if not self._can_view_audit(guild):
            return

        await asyncio.sleep(1)

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.ban,
            limit=5
        ):
            if entry.target.id != user.id:
                continue

            # Ignore bot bans
            if entry.user and entry.user.id == self.bot.user.id:
                return

            if self._is_duplicate(user.id, "ban"):
                return

            await self._safe_dm(
                user,
                luxury_embed(
                    title="⚖️ Imperial Banishment",
                    description=(
                        "You have been **permanently banned** from **HellFire Hangout**.\n\n"
                        f"👤 **Moderator:** {entry.user}\n"
                        f"📄 **Reason:** {entry.reason or 'Violation of server rules.'}"
                    ),
                    color=COLOR_DANGER
                )
            )

            await self._log(
                guild,
                "⛔ Manual Ban Detected",
                f"**User:** {user}\n**Moderator:** {entry.user}\n**Reason:** {entry.reason or 'N/A'}",
                COLOR_DANGER
            )
            break

    # =================================================
    # MANUAL KICK DETECTION
    # =================================================

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = member.guild

        if not self._can_view_audit(guild):
            return

        await asyncio.sleep(1)
        cutoff = datetime.utcnow() - timedelta(seconds=15)

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.kick,
            limit=5
        ):
            if entry.target.id != member.id:
                continue

            if entry.created_at.replace(tzinfo=None) < cutoff:
                continue

            if entry.user and entry.user.id == self.bot.user.id:
                return

            if self._is_duplicate(member.id, "kick"):
                return

            await self._safe_dm(
                member,
                luxury_embed(
                    title="🚫 Removal Notice",
                    description=(
                        "You have been **removed** from **HellFire Hangout**.\n\n"
                        f"👤 **Moderator:** {entry.user}\n"
                        f"📄 **Reason:** {entry.reason or 'Administrative decision.'}"
                    ),
                    color=COLOR_DANGER
                )
            )

            await self._log(
                guild,
                "👢 Manual Kick Detected",
                f"**User:** {member}\n**Moderator:** {entry.user}\n**Reason:** {entry.reason or 'N/A'}",
                COLOR_DANGER
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

        if not self._can_view_audit(guild):
            return

        await asyncio.sleep(1)

        async for entry in guild.audit_logs(
            action=discord.AuditLogAction.member_update,
            limit=5
        ):
            if entry.target.id != after.id:
                continue

            if entry.user and entry.user.id == self.bot.user.id:
                return

            if self._is_duplicate(after.id, "timeout"):
                return

            until = after.timed_out_until.strftime("%d %b %Y • %H:%M UTC")

            await self._safe_dm(
                after,
                luxury_embed(
                    title="⏳ Temporal Seal Applied",
                    description=(
                        "Your communication privileges have been **temporarily restricted**.\n\n"
                        f"👤 **Moderator:** {entry.user}\n"
                        f"⏰ **Until:** {until}\n"
                        f"📄 **Reason:** {entry.reason or 'Cooldown enforced.'}"
                    ),
                    color=COLOR_SECONDARY
                )
            )

            await self._log(
                guild,
                "⏳ Manual Timeout Detected",
                f"**User:** {after}\n**Moderator:** {entry.user}\n**Until:** {until}",
                COLOR_SECONDARY
            )
            break


async def setup(bot: commands.Bot):
    await bot.add_cog(Audit(bot))
