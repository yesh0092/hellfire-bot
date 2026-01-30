import discord
import asyncio
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY


class Announce(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # ANNOUNCE COMMAND
    # =====================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx, *, message: str):
        """
        Sends a luxury announcement DM to all non-bot members.
        """
        guild = ctx.guild

        embed = luxury_embed(
            title="📜 Imperial Proclamation",
            description=message,
            color=COLOR_GOLD
        )

        embed.set_footer(
            text="From the Halls of Hellfire Hangout | Elite Broadcast"
        )

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        sent = 0
        failed = 0

        status_msg = await ctx.send(
            embed=luxury_embed(
                title="📡 Broadcasting Announcement",
                description="Messages are being delivered across the realm…",
                color=COLOR_SECONDARY
            )
        )

        for member in guild.members:
            if member.bot:
                continue

            try:
                await member.send(embed=embed)
                sent += 1
                await asyncio.sleep(1)  # Rate safety
            except:
                failed += 1

        await status_msg.edit(
            embed=luxury_embed(
                title="📊 Broadcast Complete",
                description=(
                    f"**Announcement Dispatch Summary**\n\n"
                    f"✅ **Delivered:** {sent}\n"
                    f"❌ **Failed:** {failed}\n\n"
                    "Delivery failures are typically caused by closed DMs."
                ),
                color=COLOR_GOLD
            )
        )

        # Optional confirmation delete after delay
        await asyncio.sleep(10)
        try:
            await status_msg.delete()
        except:
            pass


async def setup(bot):
    await bot.add_cog(Announce(bot))


