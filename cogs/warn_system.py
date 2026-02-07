import discord
from discord.ext import commands

class WarnSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    # This prevents the "Already Registered" error by 
    # checking if Moderation.py already loaded 'warn'
    if bot.get_command("warn"):
        bot.remove_command("warn")
    await bot.add_cog(WarnSystem(bot))
