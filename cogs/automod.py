import time
import discord
from discord.ext import commands
from utils import state

TIMEOUT_SECONDS = 300  # 5 minutes


class SilentAutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}

    # =====================================================
    # MESSAGE LISTENER
    # =====================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        member = message.author

        # Ignore admins & staff
        if member.guild_permissions.manage_messages:
            return

        uid = member.id
        now = time.time()

        self.cache.setdefault(uid, [])
        self.cache[uid].append(now)

        # Keep only last 6 seconds
        self.cache[uid] = [
            t for t in self.cache[uid] if now - t < 6
        ]

        # ==========================
        # RULE: MESSAGE SPAM
        # ==========================
        limit = 5 if state.SYSTEM_FLAGS.get("panic_mode") else 6

        if len(self.cache[uid]) >= limit:
            await self._punish(
                member,
                message,
                "Spamming messages rapidly"
            )

    # =====================================================
    # PUNISHMENT HANDLER
    # =====================================================

    async def _punish(self, member: discord.Member, message: discord.Message, reason: str):
        # Delete message silently
        try:
            await message.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Apply timeout
        try:
            until = discord.utils.utcnow() + discord.timedelta(seconds=TIMEOUT_SECONDS)
            await member.edit(
                timed_out_until=until,
                reason=f"AutoMod: {reason}"
            )
        except (discord.Forbidden, discord.HTTPException):
            return

        # DM user
        try:
            await member.send(
                "⛔ **You have been timed out for 5 minutes**\n\n"
                f"**Reason:** {reason}\n\n"
                "Please follow the server rules to avoid further action."
            )
        except discord.Forbidden:
            pass

        # Log to bot logs
        await self._log_action(member, reason)

        # Clear cache so it doesn’t re-trigger instantly
        self.cache.pop(member.id, None)

    # =====================================================
    # BOT LOGGING
    # =====================================================

    async def _log_action(self, member: discord.Member, reason: str):
        if not getattr(state, "BOT_LOG_CHANNEL_ID", None):
            return

        channel = member.guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        embed = discord.Embed(
            title="🛡️ AutoMod Timeout",
            description=(
                f"**User:** {member.mention}\n"
                f"**Action:** Timeout (5 minutes)\n"
                f"**Reason:** {reason}"
            ),
            color=0x7c2d12
        )

        try:
            await channel.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            pass


async def setup(bot):
    await bot.add_cog(SilentAutoMod(bot))
