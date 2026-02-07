import discord
from discord.ext import commands, tasks
from datetime import datetime
import asyncio
import pytz  # Ensure you have 'pytz' installed: pip install pytz

from utils import state
from utils.config import COLOR_GOLD

class ClockStatus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Set your timezone here
        self.timezone = pytz.timezone('UTC') 
        self.clock_loop.start()

    def cog_unload(self):
        self.clock_loop.cancel()

    @tasks.loop(seconds=60)
    async def clock_loop(self):
        """Updates the bot status to a minimalist anime-style clock."""
        if not self.bot.is_ready():
            return

        # Check if a global toggle in state exists
        if not getattr(state, "SYSTEM_FLAGS", {}).get("clock_enabled", True):
            return

        # Format: 🕒 04:20 PM | HellFire
        now = datetime.now(self.timezone)
        time_str = now.strftime("%I:%M %p")
        
        # Anime Minimalist Aesthetic variations (Choose one):
        # 1. ⛩️ 12:00 PM 
        # 2. 「 12:00 PM 」
        # 3. 🌙 12:00 PM | VIBING
        status_text = f"⛩️ {time_str} | HellFire Hangout"

        try:
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, 
                    name=status_text
                )
            )
        except Exception as e:
            print(f"Clock Status Error: {e}")

    @clock_loop.before_loop
    async def before_clock(self):
        """Syncs the clock to start exactly at the start of the next minute."""
        await self.bot.wait_until_ready()
        # Sleep until the next 00 seconds to keep it perfectly accurate
        now = datetime.now()
        seconds_until_next_minute = 60 - now.second
        await asyncio.sleep(seconds_until_next_minute)

    @commands.command(name="clocktoggle")
    @commands.has_permissions(administrator=True)
    async def toggle_clock(self, ctx):
        """Toggles the clock status on/off"""
        if "clock_enabled" not in state.SYSTEM_FLAGS:
            state.SYSTEM_FLAGS["clock_enabled"] = True
            
        current = state.SYSTEM_FLAGS["clock_enabled"]
        state.SYSTEM_FLAGS["clock_enabled"] = not current
        
        status = "ENABLED" if not current else "DISABLED"
        await ctx.send(f"🕒 **Clock Status is now {status}.**")

async def setup(bot: commands.Bot):
    await bot.add_cog(ClockStatus(bot))
