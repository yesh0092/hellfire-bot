import discord
from discord.ext import commands
from datetime import datetime

from utils.database import db
from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state

class Profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def get_user_badges(self, member: discord.Member) -> str:
        """Generates visual badges based on member status."""
        badges = []
        if member.id == member.guild.owner_id:
            badges.append("👑 Owner")
        elif member.guild_permissions.administrator:
            badges.append("🛡️ Admin")
        elif any(r.id in state.STAFF_ROLE_TIERS.values() for r in member.roles):
            badges.append("👮 Staff")
        
        if member.premium_since:
            badges.append("💎 Booster")
        
        return " | ".join(badges) if badges else "👤 Member"

    @commands.command(name="profile", aliases=["userinfo", "whois", "ui"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author

        # ---------------- DATABASE FETCH (Enhanced) ----------------
        try:
            # We fetch message stats and warning counts in one go
            data = db.fetchone(
                """
                SELECT messages_week, messages_total, 
                (SELECT COUNT(*) FROM warnings WHERE user_id = ? AND guild_id = ?) as warns
                FROM user_stats 
                WHERE user_id = ? AND guild_id = ?
                """,
                (member.id, ctx.guild.id, member.id, ctx.guild.id)
            )
        except Exception:
            data = None

        msg_week = data["messages_week"] if data else 0
        msg_total = data["messages_total"] if data else 0
        warn_count = data["warns"] if data else 0

        # ---------------- CALCULATE LEVEL & PROGRESS ----------------
        # Level = Square root of total messages / 5 (Custom God-Level Scaling)
        level = int((msg_total ** 0.5) / 2) if msg_total > 0 else 0
        rank_name = "Unranked"
        if msg_week >= 1000: rank_name = "🔱 Overlord"
        elif msg_week >= 500: rank_name = "🔥 Demon King"
        elif msg_week >= 250: rank_name = "⚔️ Elite Warrior"
        elif msg_week >= 100: rank_name = "🌟 Rising Star"

        # ---------------- METADATA & PERMS ----------------
        joined_ts = int(member.joined_at.timestamp()) if member.joined_at else 0
        created_ts = int(member.created_at.timestamp())
        
        # Filter key permissions for display
        key_perms = []
        if member.guild_permissions.administrator: key_perms.append("Admin")
        if member.guild_permissions.manage_guild: key_perms.append("Manage Server")
        if member.guild_permissions.ban_members: key_perms.append("Ban Members")
        if member.guild_permissions.manage_messages: key_perms.append("Manage Msgs")
        
        perms_display = ", ".join(key_perms) if key_perms else "None (General)"

        # ---------------- ROLES PROCESSING ----------------
        roles = [r.mention for r in member.roles if r != ctx.guild.default_role]
        roles.reverse() # Show highest role first
        role_display = " ".join(roles[:8]) if roles else "No Roles"
        if len(roles) > 8: role_display += f" (+{len(roles)-8})"

        # ---------------- EMBED CONSTRUCTION ----------------
        embed = luxury_embed(
            title=f"{member.display_name}'s Identity Archive",
            description=(
                f"**Identity:** {self.get_user_badges(member)}\n"
                f"**Global Rank:** `{rank_name}`\n"
                f"**Status:** {str(member.status).title()} {'📱' if member.is_on_mobile() else '💻'}"
            ),
            color=COLOR_GOLD
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        if member.guild_avatar: # Use server-specific avatar if available
            embed.set_author(name=f"Level {level}", icon_url=member.guild_avatar.url)

        # Activity Field
        embed.add_field(
            name="📊 Activity Stats",
            value=(
                f"💬 **Total Msgs:** `{msg_total:,}`\n"
                f"📈 **Weekly Msgs:** `{msg_week:,}`\n"
                f"⚠️ **Strikes/Warns:** `{warn_count}`"
            ),
            inline=True
        )

        # Hierarchy Field
        embed.add_field(
            name="🛡️ Server Authority",
            value=(
                f"🔝 **Top Role:** {member.top_role.mention}\n"
                f"🔑 **Key Perms:** `{perms_display}`\n"
                f"🎙️ **Voice:** {'Active' if member.voice else 'Disconnected'}"
            ),
            inline=True
        )

        # Timeline Field (Using Discord Timestamps for dynamic viewing)
        embed.add_field(
            name="📅 Timeline",
            value=(
                f"📥 **Joined:** <t:{joined_ts}:R> (<t:{joined_ts}:d>)\n"
                f"🎂 **Created:** <t:{created_ts}:R> (<t:{created_ts}:d>)"
            ),
            inline=False
        )

        # Roles Field
        embed.add_field(name="🏷️ Role Inventory", value=role_display, inline=False)

        # Interaction Footer
        embed.set_footer(text=f"ID: {member.id} • Command handled by {ctx.author.name}")
        
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Profile(bot))
