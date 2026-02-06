import discord
from discord.ext import commands
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils import state
from utils.config import COLOR_SECONDARY, COLOR_DANGER, COLOR_GOLD


class BotLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Prevent log spam (same user + same command)
        self._recent_logs: dict[tuple[int, str], datetime] = {}

    # =================================================
    # INTERNAL HELPERS
    # =================================================

    def _get_log_channel(self, guild: discord.Guild):
        if not state.BOT_LOG_CHANNEL_ID:
            return None
        return guild.get_channel(state.BOT_LOG_CHANNEL_ID)

    def _should_log(self, user_id: int, key: str, window: int = 3) -> bool:
        """
        Prevents duplicate spam logs for same action
        """
        now = datetime.utcnow()
        last = self._recent_logs.get((user_id, key))

        if last and (now - last).total_seconds() < window:
            return False

        self._recent_logs[(user_id, key)] = now
        return True

    async def _safe_send(self, channel: discord.TextChannel, embed: discord.Embed):
        try:
            await channel.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

    # =================================================
    # BOT READY
    # =================================================

    @commands.Cog.listener()
    async def on_ready(self):
        print("📜 [BotLog] System online")

    # =================================================
    # COMMAND SUCCESS LOG
    # =================================================

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        if not ctx.guild or not ctx.command:
            return

        channel = self._get_log_channel(ctx.guild)
        if not channel:
            return

        key = ctx.command.qualified_name

        if not self._should_log(ctx.author.id, key):
            return

        embed = luxury_embed(
            title="📘 Command Executed",
            description=(
                f"👤 **User:** {ctx.author.mention}\n"
                f"🧾 **Command:** `{ctx.command.qualified_name}`\n"
                f"📍 **Channel:** {ctx.channel.mention}\n"
                f"🕒 **Time:** <t:{int(datetime.utcnow().timestamp())}:R>"
            ),
            color=COLOR_SECONDARY
        )

        await self._safe_send(channel, embed)

    # =================================================
    # COMMAND ERROR LOG (SMART)
    # =================================================

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if not ctx.guild:
            return

        # Ignore handled / normal errors
        if isinstance(
            error,
            (
                commands.CommandNotFound,
                commands.CommandOnCooldown,
                commands.MissingRequiredArgument,
                commands.BadArgument,
                commands.CheckFailure,
            )
        ):
            return

        channel = self._get_log_channel(ctx.guild)
        if not channel:
            return

        command_name = ctx.command.qualified_name if ctx.command else "Unknown"

        if not self._should_log(ctx.author.id, f"error:{command_name}"):
            return

        embed = luxury_embed(
            title="⚠️ Command Failure",
            description=(
                f"👤 **User:** {ctx.author.mention}\n"
                f"🧾 **Command:** `{command_name}`\n"
                f"📍 **Channel:** {ctx.channel.mention}\n"
                f"❌ **Error Type:** `{type(error).__name__}`\n"
                f"📝 **Details:** `{str(error)[:500]}`"
            ),
            color=COLOR_DANGER
        )

        await self._safe_send(channel, embed)

    # =================================================
    # GUILD JOIN / LEAVE LOG
    # =================================================

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        print(f"✅ Joined guild: {guild.name} ({guild.id})")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        print(f"❌ Removed from guild: {guild.name} ({guild.id})")

    # =================================================
    # MEMBER JOIN / LEAVE LOG (OPTIONAL BUT USEFUL)
    # =================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self._get_log_channel(member.guild)
        if not channel:
            return

        embed = luxury_embed(
            title="➕ Member Joined",
            description=(
                f"👤 **User:** {member.mention}\n"
                f"🆔 `{member.id}`\n"
                f"📅 **Account Created:** <t:{int(member.created_at.timestamp())}:R>"
            ),
            color=COLOR_GOLD
        )

        await self._safe_send(channel, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = self._get_log_channel(member.guild)
        if not channel:
            return

        embed = luxury_embed(
            title="➖ Member Left",
            description=(
                f"👤 **User:** {member}\n"
                f"🆔 `{member.id}`"
            ),
            color=COLOR_DANGER
        )

        await self._safe_send(channel, embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(BotLog(bot))
