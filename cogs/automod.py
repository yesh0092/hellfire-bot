import time
import re
import discord
from discord.ext import commands
from utils import state


# =====================================================
# 🔧 CONFIGURATION — SAFE & BALANCED
# =====================================================

SPAM_WINDOW = 6                 # seconds
SPAM_LIMIT_NORMAL = 6
SPAM_LIMIT_PANIC = 4

CAPS_RATIO_LIMIT = 0.7
CAPS_MIN_LEN = 8

DUPLICATE_LIMIT = 3
MENTION_LIMIT = 5
EMOJI_LIMIT = 8

# Timeout escalation (NO slowmode, USER ONLY)
TIMEOUT_TIERS = [
    300,        # 5 min
    1800,       # 30 min
    86400,      # 24h
]

POST_ACTION_COOLDOWN = 30       # prevents timeout loops
STRIKE_DECAY_TIME = 1800        # 30 min forgiveness


class SilentAutoMod(commands.Cog):
    """
    Ultimate Silent AutoMod
    • User-level enforcement ONLY
    • No slowmode
    • No channel edits
    • No loops
    • Anime-grade clean moderation
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # user_id -> [(timestamp, content)]
        self.message_cache: dict[int, list[tuple[float, str]]] = {}

        # user_id -> strikes
        self.strikes: dict[int, int] = {}

        # user_id -> last punishment time
        self.last_action: dict[int, float] = {}

    # =====================================================
    # 📩 MESSAGE LISTENER
    # =====================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore DMs & bots
        if not message.guild or message.author.bot:
            return

        # Global automod switch
        if not state.SYSTEM_FLAGS.get("automod_enabled", True):
            return

        member = message.author

        # Staff / admin immunity
        if member.guild_permissions.manage_messages:
            return

        # Ignore already timed-out users (prevents loops)
        if member.is_timed_out():
            return

        uid = member.id
        now = time.time()

        # Cooldown after punishment
        if uid in self.last_action and now - self.last_action[uid] < POST_ACTION_COOLDOWN:
            return

        # Strike decay (forgiveness)
        if uid in self.strikes:
            last = self.last_action.get(uid, now)
            if now - last > STRIKE_DECAY_TIME:
                self.strikes[uid] = max(0, self.strikes[uid] - 1)

        # Track messages
        self.message_cache.setdefault(uid, [])
        self.message_cache[uid].append((now, message.content))

        # Keep recent only
        self.message_cache[uid] = [
            (t, c) for t, c in self.message_cache[uid]
            if now - t < SPAM_WINDOW
        ]

        # =====================================================
        # 🚨 RULE CHECKS
        # =====================================================

        # 1️⃣ Message spam
        limit = SPAM_LIMIT_PANIC if state.SYSTEM_FLAGS.get("panic_mode") else SPAM_LIMIT_NORMAL
        if len(self.message_cache[uid]) >= limit:
            return await self._violate(member, message, "Message spam")

        # 2️⃣ Duplicate messages
        contents = [c for _, c in self.message_cache[uid]]
        if contents.count(message.content) >= DUPLICATE_LIMIT:
            return await self._violate(member, message, "Repeated messages")

        # 3️⃣ Caps abuse
        if len(message.content) >= CAPS_MIN_LEN:
            caps_ratio = sum(1 for c in message.content if c.isupper()) / len(message.content)
            if caps_ratio >= CAPS_RATIO_LIMIT:
                return await self._violate(member, message, "Excessive capital letters")

        # 4️⃣ Mass mentions
        if len(message.mentions) >= MENTION_LIMIT:
            return await self._violate(member, message, "Mass mentions")

        # 5️⃣ Emoji spam
        emojis = re.findall(r"<a?:\w+:\d+>|[\U0001F300-\U0001FAFF]", message.content)
        if len(emojis) >= EMOJI_LIMIT:
            return await self._violate(member, message, "Emoji spam")

    # =====================================================
    # ⚖️ VIOLATION HANDLER
    # =====================================================

    async def _violate(self, member: discord.Member, message: discord.Message, reason: str):
        uid = member.id
        now = time.time()

        self.strikes[uid] = self.strikes.get(uid, 0) + 1
        strikes = self.strikes[uid]
        self.last_action[uid] = now

        # Silent delete
        try:
            await message.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Escalation logic
        if strikes == 1:
            await self._warn(member, reason)
        else:
            tier = min(strikes - 2, len(TIMEOUT_TIERS) - 1)
            await self._timeout(member, TIMEOUT_TIERS[tier], reason)

        await self._log(member, reason, strikes)

        # Reset cache to avoid chain-trigger
        self.message_cache.pop(uid, None)

    # =====================================================
    # 🔔 ACTIONS
    # =====================================================

    async def _warn(self, member: discord.Member, reason: str):
        try:
            await member.send(
                "⚠️ **AutoMod Warning**\n\n"
                f"**Reason:** {reason}\n\n"
                "Please slow down. Continued violations will result in timeouts."
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def _timeout(self, member: discord.Member, seconds: int, reason: str):
        try:
            until = discord.utils.utcnow() + discord.timedelta(seconds=seconds)
            await member.edit(
                timed_out_until=until,
                reason=f"AutoMod: {reason}"
            )
        except (discord.Forbidden, discord.HTTPException):
            return

        try:
            await member.send(
                "⛔ **AutoMod Timeout**\n\n"
                f"⏱ **Duration:** {seconds // 60} minutes\n"
                f"📄 **Reason:** {reason}\n\n"
                "This is a user-level timeout. No channel slowmode was used."
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

    # =====================================================
    # 📁 BOT LOGGING
    # =====================================================

    async def _log(self, member: discord.Member, reason: str, strikes: int):
        if not state.BOT_LOG_CHANNEL_ID:
            return

        channel = member.guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="🛡️ Silent AutoMod Action",
            description=(
                f"**User:** {member.mention}\n"
                f"**Reason:** {reason}\n"
                f"**Strikes:** {strikes}"
            ),
            color=0x7c2d12
        )

        try:
            await channel.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(SilentAutoMod(bot))
