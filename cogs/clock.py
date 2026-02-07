import discord
from discord.ext import commands, tasks
from datetime import datetime
import pytz
import asyncio

class ClockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Set your desired timezone
        self.tz = pytz.timezone('Asia/Kolkata') 
        self.update_clock.start()

    def cog_unload(self):
        self.update_clock.cancel()

    async def _do_status_update(self):
        """Internal helper to push the status update to Discord."""
        now = datetime.now(self.tz)
        time_str = now.strftime("%I:%M %p")
        
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"⛩️ {time_str} | HellFire"
            )
        )

    @tasks.loop(seconds=10) # Check every 10s to ensure we never miss a minute
    async def update_clock(self):
        """Updates the bot status, ensuring the time is always fresh."""
        try:
            await self._do_status_update()
        except Exception as e:
            print(f"❌ Clock Loop Error: {e}")

    @update_clock.before_loop
    async def before_update_clock(self):
        """Pre-syncing the clock logic."""
        await self.bot.wait_until_ready()
        
        # ENHANCEMENT: Trigger an update IMMEDIATELY on boot
        # This removes the 'one minute wait' delay.
        try:
            await self._do_status_update()
            print("🕒 Clock System: Initial sync complete.")
        except:
            pass

async def setup(bot):
    await bot.add_cog(ClockCog(bot))
