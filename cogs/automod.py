import time
import re
import discord
from discord.ext import commands
from utils import state

# =====================================================
# CONFIGURATION
# =====================================================

SPAM_WINDOW = 6
SPAM_LIMIT_NORMAL = 6
SPAM_LIMIT_PANIC = 4

CAPS_RATIO_LIMIT = 0.7
CAPS_MIN_LEN = 8

DUPLICATE_LIMIT = 3
MENTION_LIMIT = 5
EMOJI_LIMIT = 8

TIMEOUT_TIERS = [
    300,    # 5 min
    1800,   # 30 min
    86400,  # 24 hours
]

POST_ACTION_COOLDOWN = 30     # seconds (prevents loop)
STRIKE_DECAY_TIME = 1800      # 30 min decay


class SilentAutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}
        self.violations = {}
        self.last_action = {}

    # =====================================================
    # MESSAGE LISTENER
    # =====================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if not state.SYSTEM_FLAGS.get("automod_enabled", True):
            return

        member = message.author

        # Ignore staff/admin
        if member.guild_permissions.manage_messages:
            return

        # 🚫 Ignore if already timed out
        if member.is_timed_out():
            return

        uid = member.id
        now = time.time()

        # ⏳ Grace period after punishment
        if uid in self.last_action and now - self.last_action[uid] < POST_ACTION_COOLDOWN:
            return

        # 🧠 Strike decay
        if uid in self.violations:
            last = self.last_action.get(uid, now)
            if now - last > STRIKE_DECAY_TIME:
                self.violations[uid] = max(0, self.violations[uid] - 1)

        self.cache.setdefault(uid, [])
        self.cache[uid].append((now, message.content))

        self.cache[uid] = [
            (t, c) for t, c in self.cache[uid] if now - t < SPAM_WINDOW
        ]

        # ==========================
        # RULE 1: MESSAGE SPAM
        # ==========================
        limit = SPAM_LIMIT_PANIC if state.SYSTEM_FLAGS.get("panic_mode") else SPAM_LIMIT_NORMAL
        if len(self.cache[uid]) >= limit:
            return await self._violate(member, message, "Message spam")

        # ==========================
        # RULE 2: DUPLICATE SPAM
        # ==========================
        contents = [c for _, c in self.cache[uid]]
        if contents.count(message.content) >= DUPLICATE_LIMIT:
            return await self._violate(member, message, "Repeated messages")

        # ==========================
        # RULE 3: CAPS ABUSE
        # ==========================
        if len(message.content) >= CAPS_MIN_LEN:
            ratio = sum(1 for c in message.content if c.isupper()) / len(message.content)
            if ratio >= CAPS_RATIO_LIMIT:
                return await self._violate(member, message, "Excessive capital letters")

        # ==========================
        # RULE 4: MASS MENTIONS
        # ==========================
        if len(message.mentions) >= MENTION_LIMIT:
            return await self._violate(member, message, "Mass mentions")

        # ==========================
        # RULE 5: EMOJI SPAM
        # ==========================
        emojis = re.findall(r"<a?:\w+:\d+>|[\U0001F300-\U0001FAFF]", message.content)
        if len(emojis) >= EMOJI_LIMIT:
            return await self._violate(member, message, "Emoji spam")

    # =====================================================
    # VIOLATION HANDLER
    # =====================================================

    async def _violate(self, member: discord.Member, message: discord.Message, reason: str):
        uid = member.id
        now = time.time()

        self.violations[uid] = self.violations.get(uid, 0) + 1
        strikes = self.violations[uid]

        self.last_action[uid] = now

        try:
            await message.delete()
        except:
            pass

        if strikes == 1:
            await self._warn(member, reason)
        else:
            tier = min(strikes - 2, len(TIMEOUT_TIERS) - 1)
            await self._timeout(member, TIMEOUT_TIERS[tier], reason)

        await self._log(member, reason, strikes)

        self.cache.pop(uid, None)

    # =====================================================
    # ACTIONS
    # =====================================================

    async def _warn(self, member: discord.Member, reason: str):
        try:
            await member.send(
                "⚠️ **AutoMod Warning**\n\n"
                f"**Reason:** {reason}\n\n"
                "Please slow down. Continued violations will result in timeouts."
            )
        except:
            pass

    async def _timeout(self, member: discord.Member, seconds: int, reason: str):
        try:
            until = discord.utils.utcnow() + discord.timedelta(seconds=seconds)
            await member.edit(
                timed_out_until=until,
                reason=f"AutoMod: {reason}"
            )
        except:
            return

        try:
            await member.send(
                "⛔ **You have been timed out**\n\n"
                f"⏱ **Duration:** {seconds // 60} minutes\n"
                f"📄 **Reason:** {reason}\n\n"
                "This is NOT slowmode. Please wait for the timeout to end."
            )
        except:
            pass

    # =====================================================
    # LOGGING
    # =====================================================

    async def _log(self, member: discord.Member, reason: str, strikes: int):
        if not state.BOT_LOG_CHANNEL_ID:
            return

        channel = member.guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="🛡️ AutoMod Action",
            description=(
                f"**User:** {member.mention}\n"
                f"**Reason:** {reason}\n"
                f"**Strikes:** {strikes}"
            ),
            color=0x7c2d12
        )

        try:
            await channel.send(embed=embed)
        except:
            pass


async def setup(bot):
    await bot.add_cog(SilentAutoMod(bot))
