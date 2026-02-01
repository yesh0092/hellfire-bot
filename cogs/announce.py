import discord
import asyncio
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER


class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # ANNOUNCE COMMAND
    # =====================================

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx: commands.Context, *, message: str):
        """
        Sends a premium announcement DM to all non-bot members.
        """
        guild = ctx.guild

        announcement_embed = luxury_embed(
            title="📜 Imperial Proclamation",
            description=message,
            color=COLOR_GOLD
        )

        announcement_embed.set_footer(
            text="HellFire Hangout • Official Announcement"
        )

        if self.bot.user and self.bot.user.avatar:
            announcement_embed.set_thumbnail(url=self.bot.user.avatar.url)

        sent = 0
        failed = 0

        status_msg = await ctx.send(
            embed=luxury_embed(
                title="📡 Announcement Broadcast Initiated",
                description=(
                    "The announcement is now being **securely delivered** to all members.\n\n"
                    "⏳ This process may take a few moments depending on server size."
                ),
                color=COLOR_SECONDARY
            )
        )

        for member in guild.members:
            if member.bot:
                continue

            try:
                await member.send(embed=announcement_embed)
                sent += 1
                await asyncio.sleep(1)  # DM rate-limit safety
            except discord.Forbidden:
                failed += 1
            except Exception:
                failed += 1

        await status_msg.edit(
            embed=luxury_embed(
                title="📊 Announcement Broadcast Complete",
                description=(
                    "**Delivery Summary**\n\n"
                    f"✅ **Successfully Delivered:** {sent}\n"
                    f"❌ **Failed Deliveries:** {failed}\n\n"
                    "Failures usually occur when a member has **DMs disabled**."
                ),
                color=COLOR_GOLD
            )
        )

        # Auto-clean status message
        await asyncio.sleep(10)
        try:
            await status_msg.delete()
        except discord.Forbidden:
            pass


async def setup(bot):
    await bot.add_cog(Announce(bot))
