import time
from discord.ext import commands, tasks
from utils.database import db
from utils import state


class MessageTracker(commands.Cog):
    """
    Ultimate Message Tracking System
    • Weekly + lifetime stats
    • MVP-ready
    • Command-safe
    • Auto-reset weekly
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.weekly_reset.start()

    # =====================================================
    # 📩 MESSAGE TRACKING
    # =====================================================

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore DMs, bots
        if not message.guild or message.author.bot:
            return

        # Feature flag check
        if not state.SYSTEM_FLAGS.get("message_tracking", True):
            return

        # Ignore commands (prevents spam via prefixes)
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return

        user_id = message.author.id
        guild_id = message.guild.id
        now = int(time.time())

        # Insert or update atomically
        db.execute(
            """
            INSERT INTO user_stats (user_id, guild_id, messages_week, messages_total, last_message_ts)
            VALUES (?, ?, 1, 1, ?)
            ON CONFLICT(user_id, guild_id)
            DO UPDATE SET
                messages_week = messages_week + 1,
                messages_total = messages_total + 1,
                last_message_ts = ?
            """,
            (user_id, guild_id, now, now)
        )

    # =====================================================
    # 🏆 WEEKLY RESET (MVP SYSTEM READY)
    # =====================================================

    @tasks.loop(hours=24)
    async def weekly_reset(self):
        """
        Resets weekly stats every Monday 00:00 UTC
        """
        now = time.gmtime()

        # Only reset on Monday
        if now.tm_wday != 0:
            return

        # Reset only once per week
        db.execute("""
            UPDATE user_stats
            SET messages_week = 0
        """)

    @weekly_reset.before_loop
    async def before_weekly_reset(self):
        await self.bot.wait_until_ready()

    # =====================================================
    # 🔍 PUBLIC API (FOR MVP / PROFILE)
    # =====================================================

    @staticmethod
    def get_user_stats(user_id: int, guild_id: int):
        return db.fetchone(
            """
            SELECT messages_week, messages_total
            FROM user_stats
            WHERE user_id = ? AND guild_id = ?
            """,
            (user_id, guild_id)
        )

    @staticmethod
    def get_top_users(guild_id: int, limit: int = 10):
        return db.fetchall(
            """
            SELECT user_id, messages_week
            FROM user_stats
            WHERE guild_id = ?
            ORDER BY messages_week DESC
            LIMIT ?
            """,
            (guild_id, limit)
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageTracker(bot))
