import discord
import re
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER, COLOR_SECONDARY
from utils import state


INVITE_REGEX = re.compile(r"(discord\.gg/|discord\.com/invite/)", re.IGNORECASE)

SCAM_KEYWORDS = [
    "free nitro",
    "steam skin",
    "crypto drop",
    "airdrop",
    "claim now",
    "limited offer",
    "free btc"
]

SPAM_TIMEOUT_MIN = 5  # minutes
SPAM_BURST_LIMIT = 6
SPAM_WINDOW_SEC = 10

RAID_JOIN_LIMIT = 5
RAID_WINDOW_SEC = 60
RAID_TIMEOUT_MIN = 10


class Security(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.join_tracker: list[datetime] = []
        self.spam_tracker: dict[int, list[datetime]] = {}

    async def cog_load(self):
        self.raid_watcher.start()

    def cog_unload(self):
        self.raid_watcher.cancel()

    # =====================================
    # MESSAGE PROTECTION
    # =====================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        if not state.SYSTEM_FLAGS.get("automod_enabled", True):
            return

        member = message.author

        # Ignore staff
        if member.guild_permissions.manage_messages:
            return

        content = message.content.lower()

        # ---------- INVITE FILTER ----------
        if INVITE_REGEX.search(content):
            await self._safe_delete(message)
            await self.soft_warn(
                member,
                "Posting Discord invite links is not permitted."
            )
            return

        # ---------- SCAM DETECTION ----------
        if any(keyword in content for keyword in SCAM_KEYWORDS):
            await self._safe_delete(message)
            await self.soft_warn(
                member,
                "Potential scam content detected. Please avoid misleading messages."
            )
            return

        # ---------- SPAM BURST DETECTION ----------
        now = datetime.utcnow()
        history = self.spam_tracker.setdefault(member.id, [])
        history.append(now)

        self.spam_tracker[member.id] = [
            t for t in history if now - t < timedelta(seconds=SPAM_WINDOW_SEC)
        ]

        if len(self.spam_tracker[member.id]) >= SPAM_BURST_LIMIT:
            await self._apply_timeout(
                member,
                SPAM_TIMEOUT_MIN,
                "Message spam detected"
            )
            self.spam_tracker.pop(member.id, None)

    # =====================================
    # SAFE UTILITIES
    # =====================================

    async def _safe_delete(self, message: discord.Message):
        try:
            await message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

    # =====================================
    # SOFT ACTIONS
    # =====================================

    async def soft_warn(self, member: discord.Member, reason: str):
        try:
            await member.send(
                embed=luxury_embed(
                    title="⚠️ Security Notice",
                    description=(
                        f"{reason}\n\n"
                        "This is an automated safety reminder.\n"
                        "No further action will be taken if behavior is corrected."
                    ),
                    color=COLOR_SECONDARY
                )
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def _apply_timeout(self, member: discord.Member, minutes: int, reason: str):
        if member.is_timed_out():
            return

        try:
            await member.timeout(
                timedelta(minutes=minutes),
                reason=f"Security: {reason}"
            )
        except (discord.Forbidden, discord.HTTPException):
            return

        try:
            await member.send(
                embed=luxury_embed(
                    title="⛔ Temporary Restriction",
                    description=(
                        f"⏱ **Duration:** {minutes} minutes\n"
                        f"📄 **Reason:** {reason}\n\n"
                        "This is not slowmode. Please wait until the timeout ends."
                    ),
                    color=COLOR_DANGER
                )
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

        await self._log_action(member, reason, minutes)

    # =====================================
    # RAID DETECTION (JOIN BURST)
    # =====================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        now = datetime.utcnow()
        self.join_tracker.append(now)

        self.join_tracker = [
            t for t in self.join_tracker if now - t < timedelta(seconds=RAID_WINDOW_SEC)
        ]

        if len(self.join_tracker) >= RAID_JOIN_LIMIT:
            await self.handle_possible_raid(member.guild)

    async def handle_possible_raid(self, guild: discord.Guild):
        if state.SYSTEM_FLAGS.get("panic_mode"):
            return

        for member in guild.members:
            if member.bot or member.guild_permissions.manage_messages:
                continue

            try:
                await member.timeout(
                    timedelta(minutes=RAID_TIMEOUT_MIN),
                    reason="Preventive action during suspected raid"
                )
            except:
                continue

        try:
            if guild.owner:
                await guild.owner.send(
                    embed=luxury_embed(
                        title="🚨 Possible Raid Detected",
                        description=(
                            "Multiple users joined in a short time.\n\n"
                            "Preventive **member timeouts** have been applied.\n"
                            "No channel slowmode was used."
                        ),
                        color=COLOR_DANGER
                    )
                )
        except:
            pass

    # =====================================
    # LOGGING
    # =====================================

    async def _log_action(self, member: discord.Member, reason: str, minutes: int):
        if not state.BOT_LOG_CHANNEL_ID:
            return

        channel = member.guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        try:
            await channel.send(
                embed=luxury_embed(
                    title="🛡️ Security Action",
                    description=(
                        f"**User:** {member.mention}\n"
                        f"**Action:** Timeout ({minutes} min)\n"
                        f"**Reason:** {reason}"
                    ),
                    color=COLOR_DANGER
                )
            )
        except:
            pass

    # =====================================
    # PERIODIC CLEANUP
    # =====================================

    @tasks.loop(minutes=5)
    async def raid_watcher(self):
        self.join_tracker.clear()
        self.spam_tracker.clear()

    @raid_watcher.before_loop
    async def before_raid_watcher(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Security(bot))
