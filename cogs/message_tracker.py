from discord.ext import commands
from utils.database import db

class MessageTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        db.execute("""
        INSERT INTO user_stats (user_id, guild_id, messages_week, messages_total)
        VALUES (?, ?, 1, 1)
        ON CONFLICT(user_id, guild_id)
        DO UPDATE SET
            messages_week = messages_week + 1,
            messages_total = messages_total + 1
        """, (message.author.id, message.guild.id))

async def setup(bot):
    await bot.add_cog(MessageTracker(bot))
