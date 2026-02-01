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
        except (discord.Forbidden, discord.HTTPException):
            pass

    # =====================================================
    # EVENTS
    # =====================================================

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.user:
            return

        await self.log(
            "🤖 Bot Online",
            (
                f"**{self.bot.user}** is now online.\n\n"
                f"🧠 **Loaded Cogs:** `{len(self.bot.cogs)}`\n"
                f"⏱ **Timestamp:** `{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}`"
            ),
            COLOR_GOLD
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore permission-related failures silently
        if isinstance(error, commands.CheckFailure):
            return

        command_name = ctx.command.qualified_name if ctx.command else "Unknown"

        await self.log(
            "❌ Command Error",
            (
                f"**Command:** `{command_name}`\n"
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
    @commands.guild_only()
    @require_level(4)  # Staff+++
    async def setbotlog(self, ctx: commands.Context):
        state.BOT_LOG_CHANNEL_ID = ctx.channel.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="📜 Bot Log Channel Configured",
                description=(
                    "This channel will now receive:\n"
                    "• System lifecycle events\n"
                    "• Command execution errors\n"
                    "• Security and audit alerts\n"
                    "• Internal bot notifications"
                ),
                color=COLOR_GOLD
            )
        )

        await self.log(
            "📜 Bot Logging Enabled",
            f"Logging channel configured by {ctx.author.mention}.",
            COLOR_GOLD
        )

    @commands.command()
    @commands.guild_only()
    @require_level(4)  # Staff+++
    async def unsetbotlog(self, ctx: commands.Context):
        if not state.BOT_LOG_CHANNEL_ID:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ Bot Logging Already Disabled",
                    description="There is currently **no bot log channel** configured.",
                    color=COLOR_SECONDARY
                )
            )

        state.BOT_LOG_CHANNEL_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Bot Logging Disabled",
                description="System, error, and security logs will no longer be sent.",
                color=COLOR_DANGER
            )
        )


async def setup(bot):
    await bot.add_cog(BotLog(bot))
