import discord
from discord.ext import commands, tasks
from datetime import datetime
import pytz
import asyncio

class ClockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tz = pytz.timezone('Asia/Kolkata') 
        self.update_clock.start()

    def cog_unload(self):
        self.update_clock.cancel()

    async def _do_status_update(self):
        """Internal helper to push the status update to Discord."""
        now = datetime.now(self.tz)
        time_str = now.strftime("%I:%M %p")
        
        try:
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"⛩️ {time_str} | HellFire"
                )
            )
        except discord.HTTPException as e:
            # If we hit a ratelimit, this will catch it without crashing the loop
            print(f"⚠️ Discord Ratelimit: {e}")

    @tasks.loop(minutes=1) # Update exactly once a minute
    async def update_clock(self):
        """Updates the bot status every minute."""
        await self._do_status_update()

    @update_clock.before_loop
    async def before_update_clock(self):
        """Precise Sync Logic: Wait until the start of the next minute."""
        await self.bot.wait_until_ready()
        
        # Immediate update on startup
        await self._do_status_update()
        
        # Calculate seconds remaining until the next minute starts (:00 seconds)
        now = datetime.now(self.tz)
        seconds_until_next_minute = 60 - now.second
        
        print(f"🕒 Clock Sync: Waiting {seconds_until_next_minute}s to align with system clock...")
        await asyncio.sleep(seconds_until_next_minute)
        print("🕒 Clock System: Fully Synced.")

async def setup(bot):
    await bot.add_cog(ClockCog(bot))
