import discord
from discord.ext import commands, tasks
from datetime import datetime
import pytz
import asyncio
from utils import state

class ClockStatus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Set your timezone (e.g., 'Asia/Kolkata', 'America/New_York', or 'UTC')
        self.timezone = pytz.timezone('UTC') 
        self.clock_loop.start()

    def cog_unload(self):
        self.clock_loop.cancel()

    @tasks.loop(seconds=30) # Checks every 30s to ensure accuracy
    async def clock_loop(self):
        if not self.bot.is_ready():
            return

        # Check for state-based toggle
        if not getattr(state, "SYSTEM_FLAGS", {}).get("clock_enabled", True):
            return

        now = datetime.now(self.timezone)
        time_str = now.strftime("%I:%M %p")
        
        # Minimalist Anime Status
        status_text = f"⛩️ {time_str} | HellFire"

        try:
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, 
                    name=status_text
                )
            )
            # WATCHDOG: This confirms it's working in your console
            # print(f"DEBUG: Clock updated to {time_str}")
        except Exception as e:
            print(f"❌ Clock Error: {e}")

    @clock_loop.before_loop
    async def before_clock(self):
        """Wait for the bot to be fully connected before starting status updates"""
        await self.bot.wait_until_ready()
        # Trigger an update IMMEDIATELY on boot
        print("🕒 Clock System: Internal loop synchronized.")

    @commands.command(name="clockfix")
    @commands.has_permissions(administrator=True)
    async def clock_fix(self, ctx):
        """Force-restarts the clock if it freezes"""
        self.clock_loop.restart()
        await ctx.send("🕒 **Clock status force-restarted.**")

async def setup(bot: commands.Bot):
    await bot.add_cog(ClockStatus(bot))
