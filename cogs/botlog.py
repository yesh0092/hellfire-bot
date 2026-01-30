import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_SECONDARY, COLOR_DANGER, COLOR_GOLD
from utils import state


class BotLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # INTERNAL LOGGER
    # =====================================================

    async def log(self, title: str, description: str, color=COLOR_SECONDARY):
        if not state.BOT_LOG_CHANNEL_ID:
            return

        guild = self.bot.get_guild(state.MAIN_GUILD_ID)
        if not guild:
            return

        channel = guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        await channel.send(
            embed=luxury_embed(
                title=title,
                description=description,
                color=color
            )
        )

    # =====================================================
    # EVENTS
    # =====================================================

    @commands.Cog.listener()
    async def on_ready(self):
        await self.log(
            "🤖 Bot Online",
            f"**{self.bot.user}** is now online and operational.",
            COLOR_GOLD
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await self.log(
            "❌ Command Error",
            f"**Command:** {ctx.command}\n"
            f"**User:** {ctx.author} ({ctx.author.id})\n"
            f"**Error:** `{error}`",
            COLOR_DANGER
        )

    # =====================================================
    # ADMIN COMMAND
    # =====================================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setbotlog(self, ctx):
        state.BOT_LOG_CHANNEL_ID = ctx.channel.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="📜 Bot Log Channel Set",
                description="This channel will now receive **bot system logs**.",
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unsetbotlog(self, ctx):
        state.BOT_LOG_CHANNEL_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Bot Logging Disabled",
                description="Bot system logs are now disabled.",
                color=COLOR_DANGER
            )
        )


async def setup(bot):
    await bot.add_cog(BotLog(bot))
