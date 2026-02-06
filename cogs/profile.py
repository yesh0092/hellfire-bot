import discord
from discord.ext import commands
from datetime import datetime

from utils.database import db
from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY
from utils import state


class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # PROFILE COMMAND
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author

        # ---------------- DATABASE SAFE FETCH ----------------
        try:
            data = db.fetchone(
                """
                SELECT messages_week, messages_total
                FROM user_stats
                WHERE user_id = ? AND guild_id = ?
                """,
                (member.id, ctx.guild.id)
            )
        except Exception:
            data = None

        # ---------------- FALLBACK IF NO DATA ----------------
        messages_week = data["messages_week"] if data else 0
        messages_total = data["messages_total"] if data else 0

        # ---------------- USER META ----------------
        joined_at = member.joined_at.strftime("%d %b %Y") if member.joined_at else "Unknown"
        created_at = member.created_at.strftime("%d %b %Y")
        roles = [r.mention for r in member.roles if r != ctx.guild.default_role]

        role_display = ", ".join(roles[:6]) if roles else "No roles"
        if len(roles) > 6:
            role_display += f" +{len(roles) - 6} more"

        # ---------------- ACTIVITY RANK (OPTIONAL) ----------------
        rank = "Unranked"
        if messages_week >= 500:
            rank = "🔥 Demon King"
        elif messages_week >= 300:
            rank = "⚔️ Elite Warrior"
        elif messages_week >= 150:
            rank = "🌟 Rising Star"
        elif messages_week >= 50:
            rank = "📖 Active Member"

        # ---------------- PROFILE EMBED ----------------
        embed = luxury_embed(
            title=f"👤 {member.display_name}'s Profile",
            description=(
                f"**Rank:** {rank}\n"
                f"**Status:** {'🟢 Online' if member.status != discord.Status.offline else '⚫ Offline'}"
            ),
            color=COLOR_GOLD
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        # ---------------- STATS ----------------
        embed.add_field(
            name="📆 Weekly Messages",
            value=f"**{messages_week}**",
            inline=True
        )
        embed.add_field(
            name="💬 Total Messages",
            value=f"**{messages_total}**",
            inline=True
        )

        # ---------------- TIMELINE ----------------
        embed.add_field(
            name="📅 Joined Server",
            value=joined_at,
            inline=False
        )
        embed.add_field(
            name="🕰️ Discord Account Created",
            value=created_at,
            inline=False
        )

        # ---------------- ROLES ----------------
        embed.add_field(
            name="🏷️ Roles",
            value=role_display,
            inline=False
        )

        # ---------------- FOOTER ----------------
        embed.set_footer(
            text="HellFire Hangout • Anime-Grade Profile System"
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))
