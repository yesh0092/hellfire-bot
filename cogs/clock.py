import discord
from discord.ext import commands, tasks
from datetime import datetime
import pytz

class ClockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Set your desired timezone here
        self.tz = pytz.timezone('Asia/Kolkata') 
        self.update_clock.start()

    def cog_unload(self):
        self.update_clock.cancel()

    @tasks.loop(seconds=60)
    async def update_clock(self):
        """Updates the bot status every minute with the live time."""
        try:
            now = datetime.now(self.tz)
            time_str = now.strftime("%I:%M %p")
            
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"⛩️ {time_str} | HellFire"
                )
            )
        except Exception as e:
            print(f"❌ Clock Loop Error: {e}")

    @update_clock.before_loop
    async def before_update_clock(self):
        """Wait for the bot to be ready before starting the loop."""
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ClockCog(bot))
