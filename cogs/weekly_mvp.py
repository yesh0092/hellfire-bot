import discord
from discord.ext import commands, tasks
from datetime import datetime

from utils.database import db
from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY
from utils import state


# =====================================================
# WEEKLY TEXT MVP SYSTEM (ULTIMATE)
# =====================================================
# • Fully automatic
# • Weekly reset
# • Role rotation
# • Tie-safe
# • Multi-guild safe
# • Anime prestige system
# =====================================================


class WeeklyTextMVP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.weekly_mvp_task.start()

    # =================================================
    # CORE WEEKLY TASK
    # =================================================

    @tasks.loop(hours=168)  # 7 days
    async def weekly_mvp_task(self):
        for guild in self.bot.guilds:
            try:
                await self.process_guild(guild)
            except Exception as e:
                print(f"[WeeklyMVP] Error in {guild.id}: {e}")

    async def process_guild(self, guild: discord.Guild):
        # ---------------- SAFETY ----------------
        if not state.SYSTEM_FLAGS.get("mvp_system", True):
            return

        if not state.MAIN_GUILD_ID or guild.id != state.MAIN_GUILD_ID:
            return

        # ---------------- ROLE ----------------
        mvp_role = discord.utils.get(guild.roles, name="Text MVP")
        if not mvp_role:
            try:
                mvp_role = await guild.create_role(
                    name="Text MVP",
                    reason="Weekly Text MVP System"
                )
            except discord.Forbidden:
                return

        # ---------------- QUERY ----------------
        rows = db.fetchall("""
            SELECT user_id, messages_week
            FROM user_stats
            WHERE guild_id = ?
            ORDER BY messages_week DESC
            LIMIT 5
        """, (guild.id,))

        if not rows or rows[0]["messages_week"] <= 0:
            return

        top_score = rows[0]["messages_week"]

        # Tie handling
        winners = [
            r["user_id"]
            for r in rows
            if r["messages_week"] == top_score
        ]

        winner_id = winners[0]  # deterministic winner
        winner = guild.get_member(winner_id)
        if not winner:
            return

        # ---------------- REMOVE OLD MVP ----------------
        for member in mvp_role.members:
            if member.id != winner.id:
                try:
                    await member.remove_roles(mvp_role, reason="Weekly MVP rotation")
                except discord.Forbidden:
                    pass

        # ---------------- ASSIGN MVP ----------------
        if mvp_role not in winner.roles:
            try:
                await winner.add_roles(mvp_role, reason="Weekly Text MVP")
            except discord.Forbidden:
                pass

        # ---------------- ANNOUNCE ----------------
        await self.announce_mvp(guild, winner, top_score)

        # ---------------- RESET WEEK ----------------
        db.execute(
            "UPDATE user_stats SET messages_week = 0 WHERE guild_id = ?",
            (guild.id,)
        )

    # =================================================
    # ANNOUNCEMENT
    # =================================================

    async def announce_mvp(self, guild: discord.Guild, winner: discord.Member, count: int):
        channel = None

        if state.WELCOME_CHANNEL_ID:
            channel = guild.get_channel(state.WELCOME_CHANNEL_ID)

        if not channel:
            channel = guild.system_channel

        if not channel:
            return

        embed = luxury_embed(
            title="🏆 WEEKLY TEXT MVP",
            description=(
                f"🔥 **{winner.mention}** has claimed the throne!\n\n"
                f"💬 **Messages This Week:** {count}\n\n"
                "This title is awarded to the most active chatter.\n"
                "The crown resets every week — fight for it."
            ),
            color=COLOR_GOLD
        )

        embed.set_thumbnail(url=winner.display_avatar.url)
        embed.set_footer(text="HellFire Hangout • Weekly Ascension")

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass

        # ---------------- BOT LOG ----------------
        if state.BOT_LOG_CHANNEL_ID:
            log_channel = guild.get_channel(state.BOT_LOG_CHANNEL_ID)
            if log_channel:
                try:
                    await log_channel.send(
                        embed=luxury_embed(
                            title="🏆 Weekly MVP Assigned",
                            description=(
                                f"👑 **Winner:** {winner.mention}\n"
                                f"💬 **Messages:** {count}"
                            ),
                            color=COLOR_SECONDARY
                        )
                    )
                except discord.Forbidden:
                    pass

    # =================================================
    # LOOP SAFETY
    # =================================================

    @weekly_mvp_task.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(WeeklyTextMVP(bot))
