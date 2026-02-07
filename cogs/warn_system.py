import discord
from discord.ext import commands
from utils import state

class WarnSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    # Safety: ensure no collision
    if bot.get_command("warn"):
        bot.remove_command("warn")
    await bot.add_cog(WarnSystem(bot))
