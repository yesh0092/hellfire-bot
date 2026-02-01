import discord
from discord.ext import commands
from utils.database import db

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        data = db.fetchone("""
        SELECT messages_week, messages_total
        FROM user_stats
        WHERE user_id = ? AND guild_id = ?
        """, (member.id, ctx.guild.id))

        if not data:
            return await ctx.send("No stats found yet.")

        embed = discord.Embed(
            title=f"{member.display_name}'s Profile",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="📆 Messages This Week",
            value=data["messages_week"],
            inline=True
        )
        embed.add_field(
            name="💬 Total Messages",
            value=data["messages_total"],
            inline=True
        )
        embed.add_field(
            name="📅 Joined Server",
            value=member.joined_at.strftime("%d %b %Y"),
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Profile(bot))
