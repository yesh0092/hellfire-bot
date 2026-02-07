import discord
from discord.ext import commands, tasks
from utils import state

class WeeklyTextMVP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(hours=168)
    async def weekly_mvp_task(self):
        # We leave this empty for now just to see if the cog LOADS
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.weekly_mvp_task.is_running():
            self.weekly_mvp_task.start()

async def setup(bot):
    await bot.add_cog(WeeklyTextMVP(bot))
