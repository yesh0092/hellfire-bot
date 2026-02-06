import discord
import re
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import time

from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER, COLOR_SECONDARY
from utils import state


# =====================================================
# REGEX & KEYWORDS
# =====================================================

INVITE_REGEX = re.compile(r"(discord\.gg/|discord\.com/invite/)", re.IGNORECASE)

SCAM_KEYWORDS = [
    "free nitro",
    "steam skin",
    "crypto drop",
    "airdrop",
    "claim now",
    "limited offer",
    "free btc",
    "free crypto",
    "gift nitro",
]

LINK_REGEX = re.compile(r"https?://", re.IGNORECASE)

# =====================================================
# SECURITY CONFIG
# =====================================================

SPAM_WINDOW_SEC = 10
SPAM_BURST_LIMIT = 6
SPAM_TIMEOUT_MIN = 5

RAID_JOIN_LIMIT = 5
RAID_WINDOW_SEC = 60
RAID_TIMEOUT_MIN = 10

POST_ACTION_COOLDOWN = 30  # seconds


class Security(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.join_tracker: list[datetime] = []
        self.spam_tracker: dict[int, list[float]] = {}
        self.last_action: dict[int, float] = {}

    # =====================================================
    # MESSAGE PROTECTION
    # =====================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return

        if not state.SYSTEM_FLAGS.get("automod_enabled", True):
            return

        member = message.author

        if member.guild_permissions.manage_messages:
            return

        if member.is_timed_out():
            return

        uid = member.id
        now = time.time()

        if uid in self.last_action and now - self.last_action[uid] < POST_ACTION_COOLDOWN:
            return

        content = message.content.lower()

        # ---------------- INVITE LINKS ----------------
        if INVITE_REGEX.search(content):
            await self._safe_delete(message)
            await self._soft_warn(member, "Posting Discord invite links is not allowed.")
            return

        # ---------------- SCAM KEYWORDS ----------------
        if any(word in content for word in SCAM_KEYWORDS):
            await self._safe_delete(message)
            await self._soft_warn(member, "Potential scam message detected.")
            return

        # ---------------- LINK FLOOD ----------------
        if len(LINK_REGEX.findall(content)) >= 3:
            await self._apply_timeout(member, SPAM_TIMEOUT_MIN, "Link spam detected")
            self.last_action[uid] = now
            return

        # ---------------- SPAM BURST ----------------
        timestamps = self.spam_tracker.setdefault(uid, [])
        timestamps.append(now)

        self.spam_tracker[uid] = [
            t for t in timestamps if now - t < SPAM_WINDOW_SEC
        ]

        if len(self.spam_tracker[uid]) >= SPAM_BURST_LIMIT:
            await self._apply_timeout(member, SPAM_TIMEOUT_MIN, "Message spam detected")
            self.spam_tracker.pop(uid, None)
            self.last_action[uid] = now

    # =====================================================
    # MEMBER JOIN — RAID PROTECTION
    # =====================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        now = datetime.utcnow()
        self.join_tracker.append(now)

        self.join_tracker = [
            t for t in self.join_tracker if now - t < timedelta(seconds=RAID_WINDOW_SEC)
        ]

        if len(self.join_tracker) >= RAID_JOIN_LIMIT:
            await self._handle_raid(member.guild)

    async def _handle_raid(self, guild: discord.Guild):
        if state.SYSTEM_FLAGS.get("panic_mode"):
            return

        for member in guild.members:
            if member.bot or member.guild_permissions.manage_messages:
                continue

            if member.is_timed_out():
                continue

            try:
                await member.timeout(
                    timedelta(minutes=RAID_TIMEOUT_MIN),
                    reason="Preventive security action (suspected raid)"
                )
            except:
                continue

        await self._notify_owner(guild)

    # =====================================================
    # ACTIONS
    # =====================================================

    async def _safe_delete(self, message: discord.Message):
        try:
            await message.delete()
        except:
            pass

    async def _soft_warn(self, member: discord.Member, reason: str):
        try:
            await member.send(
                embed=luxury_embed(
                    title="⚠️ Security Warning",
                    description=(
                        f"{reason}\n\n"
                        "This is an automated warning.\n"
                        "Repeated violations may result in timeouts."
                    ),
                    color=COLOR_SECONDARY
                )
            )
        except:
            pass

    async def _apply_timeout(self, member: discord.Member, minutes: int, reason: str):
        if member.is_timed_out():
            return

        try:
            await member.timeout(
                timedelta(minutes=minutes),
                reason=f"Security: {reason}"
            )
        except:
            return

        try:
            await member.send(
                embed=luxury_embed(
                    title="⛔ Security Timeout",
                    description=(
                        f"⏱ **Duration:** {minutes} minutes\n"
                        f"📄 **Reason:** {reason}\n\n"
                        "This is NOT slowmode."
                    ),
                    color=COLOR_DANGER
                )
            )
        except:
            pass

        await self._log_action(member, reason, minutes)

    # =====================================================
    # LOGGING
    # =====================================================

    async def _log_action(self, member: discord.Member, reason: str, minutes: int):
        if not state.BOT_LOG_CHANNEL_ID:
            return

        channel = member.guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        try:
            await channel.send(
                embed=luxury_embed(
                    title="🛡️ Security Enforcement",
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

    async def _notify_owner(self, guild: discord.Guild):
        try:
            if guild.owner:
                await guild.owner.send(
                    embed=luxury_embed(
                        title="🚨 Raid Protection Triggered",
                        description=(
                            "Multiple users joined rapidly.\n\n"
                            "Preventive **user timeouts** applied.\n"
                            "No channels were modified."
                        ),
                        color=COLOR_DANGER
                    )
                )
        except:
            pass

    # =====================================================
    # CLEANUP LOOP
    # =====================================================

    @tasks.loop(minutes=5)
    async def cleanup(self):
        self.join_tracker.clear()
        self.spam_tracker.clear()
        self.last_action.clear()

    @cleanup.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()

    async def cog_load(self):
        self.cleanup.start()

    def cog_unload(self):
        self.cleanup.cancel()


async def setup(bot: commands.Bot):
    await bot.add_cog(Security(bot))
