import discord
import asyncio
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state


class Announce(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================
    # ANNOUNCE COMMAND (STAFF+++)
    # =====================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)  # Staff+++
    async def announce(self, ctx: commands.Context, *, message: str):
        """
        Sends a premium announcement DM to all non-bot members.
        """

        # Panic mode safety
        if state.SYSTEM_FLAGS.get("panic_mode"):
            return await ctx.send(
                embed=luxury_embed(
                    title="🚨 Panic Mode Active",
                    description="Announcements are disabled while panic mode is enabled.",
                    color=COLOR_DANGER
                )
            )

        guild = ctx.guild

        embed = luxury_embed(
            title="📜 Imperial Proclamation",
            description=message,
            color=COLOR_GOLD
        )
        embed.set_footer(text="HellFire Hangout • Official Announcement")

        if self.bot.user and self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        status = await ctx.send(
            embed=luxury_embed(
                title="📡 Broadcasting Announcement",
                description=(
                    "The announcement is being delivered securely.\n\n"
                    "⏳ Please do not interrupt this process."
                ),
                color=COLOR_SECONDARY
            )
        )

        sent = 0
        failed = 0

        # Process members in chunks to avoid blocking
        members = [m for m in guild.members if not m.bot]

        for member in members:
            try:
                await member.send(embed=embed)
                sent += 1
                await asyncio.sleep(0.8)  # safer than 1s
            except (discord.Forbidden, discord.HTTPException):
                failed += 1

        await status.edit(
            embed=luxury_embed(
                title="📊 Broadcast Complete",
                description=(
                    f"✅ **Delivered:** {sent}\n"
                    f"❌ **Failed:** {failed}\n\n"
                    "Failures usually occur due to closed DMs."
                ),
                color=COLOR_GOLD
            )
        )

        # Auto-clean
        await asyncio.sleep(10)
        try:
            await status.delete()
        except discord.Forbidden:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Announce(bot))
