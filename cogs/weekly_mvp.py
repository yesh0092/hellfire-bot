from discord.ext import commands, tasks
from utils.database import db

TEXT_MVP_ROLE_ID = 123456789012345678  # 🔴 PUT YOUR ROLE ID HERE

class WeeklyTextMVP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekly_task.start()

    @tasks.loop(hours=168)  # once per week
    async def weekly_task(self):
        for guild in self.bot.guilds:
            role = guild.get_role(TEXT_MVP_ROLE_ID)
            if not role:
                continue

            top_user = db.fetchone("""
            SELECT user_id, messages_week
            FROM user_stats
            WHERE guild_id = ?
            ORDER BY messages_week DESC
            LIMIT 1
            """, (guild.id,))

            if not top_user or top_user["messages_week"] == 0:
                continue

            new_mvp = guild.get_member(top_user["user_id"])
            if not new_mvp:
                continue

            # remove role from everyone else
            for member in role.members:
                if member != new_mvp:
                    await member.remove_roles(role)

            # give role to new MVP
            if role not in new_mvp.roles:
                await new_mvp.add_roles(role)

            # reset weekly counts
            db.execute(
                "UPDATE user_stats SET messages_week = 0 WHERE guild_id = ?",
                (guild.id,)
            )

    @weekly_task.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WeeklyTextMVP(bot))
