import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_SECONDARY, COLOR_DANGER, COLOR_GOLD
from utils.permissions import require_level
from utils import state


class BotLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================================
    # INTERNAL LOGGER (SAFE)
    # =====================================================

    async def log(self, title: str, description: str, color=COLOR_SECONDARY):
        if not state.BOT_LOG_CHANNEL_ID or not state.MAIN_GUILD_ID:
            return

        guild = self.bot.get_guild(state.MAIN_GUILD_ID)
        if not guild:
            return

        channel = guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        try:
            await channel.send(
                embed=luxury_embed(
                    title=title,
                    description=description,
                    color=color
                )
            )
        except discord.HTTPException:
            pass

    # =====================================================
    # EVENTS
    # =====================================================

    @commands.Cog.listener()
    async def on_ready(self):
        await self.log(
            "🤖 Bot Online",
            (
                f"**{self.bot.user}** is now online.\n\n"
                f"🧠 Loaded Cogs: `{len(self.bot.cogs)}`\n"
                f"⏱ Time: `{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}`"
            ),
            COLOR_GOLD
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore missing permissions silently
        if isinstance(error, commands.CheckFailure):
            return

        await self.log(
            "❌ Command Error",
            (
                f"**Command:** `{ctx.command}`\n"
                f"**User:** {ctx.author} (`{ctx.author.id}`)\n"
                f"**Channel:** {ctx.channel.mention}\n"
                f"**Error:** `{error}`"
            ),
            COLOR_DANGER
        )

    # =====================================================
    # ADMIN COMMANDS (STAFF+++)
    # =====================================================

    @commands.command()
    @require_level(4)  # Staff+++
    async def setbotlog(self, ctx):
        state.BOT_LOG_CHANNEL_ID = ctx.channel.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="📜 Bot Log Channel Set",
                description=(
                    "This channel will now receive:\n"
                    "• System logs\n"
                    "• Command errors\n"
                    "• Security alerts\n"
                    "• Bot lifecycle events"
                ),
                color=COLOR_GOLD
            )
        )

        await self.log(
            "📜 Bot Logging Enabled",
            f"Logging channel set by {ctx.author.mention}",
            COLOR_GOLD
        )

    @commands.command()
    @require_level(4)  # Staff+++
    async def unsetbotlog(self, ctx):
        if not state.BOT_LOG_CHANNEL_ID:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ Already Disabled",
                    description="Bot logging is already disabled.",
                    color=COLOR_SECONDARY
                )
            )

        state.BOT_LOG_CHANNEL_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Bot Logging Disabled",
                description="System & security logs will no longer be sent.",
                color=COLOR_DANGER
            )
        )


async def setup(bot):
    await bot.add_cog(BotLog(bot))
