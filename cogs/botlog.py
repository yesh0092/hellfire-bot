import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils import state
from utils.config import COLOR_SECONDARY, COLOR_DANGER


class BotLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =================================================
    # INTERNAL HELPER
    # =================================================

    def get_log_channel(self, guild: discord.Guild):
        if not state.BOT_LOG_CHANNEL_ID:
            return None
        return guild.get_channel(state.BOT_LOG_CHANNEL_ID)

    # =================================================
    # BOT READY LOG
    # =================================================

    @commands.Cog.listener()
    async def on_ready(self):
        print("📜 BotLog system active")

    # =================================================
    # COMMAND USAGE LOG
    # =================================================

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        if not ctx.guild:
            return

        channel = self.get_log_channel(ctx.guild)
        if not channel:
            return

        await channel.send(
            embed=luxury_embed(
                title="📘 Command Executed",
                description=(
                    f"👤 **User:** {ctx.author} (`{ctx.author.id}`)\n"
                    f"🧾 **Command:** `{ctx.command.qualified_name}`\n"
                    f"📍 **Channel:** {ctx.channel.mention}"
                ),
                color=COLOR_SECONDARY
            )
        )

    # =================================================
    # COMMAND ERROR LOG
    # =================================================

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if not ctx.guild:
            return

        channel = self.get_log_channel(ctx.guild)
        if not channel:
            return

        await channel.send(
            embed=luxury_embed(
                title="⚠️ Command Error",
                description=(
                    f"👤 **User:** {ctx.author}\n"
                    f"🧾 **Command:** `{ctx.command}`\n"
                    f"❌ **Error:** `{type(error).__name__}`"
                ),
                color=COLOR_DANGER
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(BotLog(bot))
