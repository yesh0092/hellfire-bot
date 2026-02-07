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

class WeeklyTextMVP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Start the task loop safely
        self.weekly_mvp_task.start()

    def cog_unload(self):
        self.weekly_mvp_task.cancel()

    # =================================================
    # CORE WEEKLY TASK
    # =================================================

    @tasks.loop(hours=168)  # 7 days
    async def weekly_mvp_task(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            try:
                await self.process_guild(guild)
            except Exception as e:
                print(f"[WeeklyMVP] Error in {guild.id}: {e}")

    async def process_guild(self, guild: discord.Guild):
        # ---------------- SAFETY & ATTRIBUTE CHECKS ----------------
        flags = getattr(state, "SYSTEM_FLAGS", {})
        if not flags.get("mvp_system", True):
            return

        main_id = getattr(state, "MAIN_GUILD_ID", None)
        if not main_id or guild.id != main_id:
            return

        # ---------------- ROLE MANAGEMENT ----------------
        mvp_role = discord.utils.get(guild.roles, name="Text MVP")
        if not mvp_role:
            try:
                mvp_role = await guild.create_role(
                    name="Text MVP",
                    reason="Weekly Text MVP System Initialization",
                    color=discord.Color.gold(),
                    hoist=True
                )
            except discord.Forbidden:
                return

        # ---------------- QUERY DATABASE ----------------
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

        # Tie handling (gets all users with the same top score)
        winners = [
            r["user_id"]
            for r in rows
            if r["messages_week"] == top_score
        ]

        winner_id = winners[0]  
        winner = guild.get_member(winner_id)
        
        # If the winner left the server, try the next person in the tie or list
        if not winner:
            for r in rows[1:]:
                winner = guild.get_member(r["user_id"])
                if winner: 
                    top_score = r["messages_week"]
                    break
        
        if not winner: return

        # ---------------- ROLE ROTATION ----------------
        # Remove role from old MVPs
        for member in mvp_role.members:
            if member.id != winner.id:
                try:
                    await member.remove_roles(mvp_role, reason="Weekly MVP rotation")
                except: pass

        # Assign to new winner
        if mvp_role not in winner.roles:
            try:
                await winner.add_roles(mvp_role, reason="Weekly Text MVP Achievement")
            except: pass

        # ---------------- ANNOUNCE & RESET ----------------
        await self.announce_mvp(guild, winner, top_score)

        db.execute(
            "UPDATE user_stats SET messages_week = 0 WHERE guild_id = ?",
            (guild.id,)
        )

    # =================================================
    # ANNOUNCEMENT LOGIC
    # =================================================

    async def announce_mvp(self, guild: discord.Guild, winner: discord.Member, count: int):
        channel = None
        welcome_id = getattr(state, "WELCOME_CHANNEL_ID", None)
        
        if welcome_id:
            channel = guild.get_channel(welcome_id)

        if not channel:
            channel = guild.system_channel or guild.text_channels[0]

        embed = luxury_embed(
            title="🏆 WEEKLY TEXT MVP",
            description=(
                f"🔥 **{winner.mention}** has claimed the throne!\n\n"
                f"💬 **Messages This Week:** `{count}`\n\n"
                "This title is awarded to our most active chattered.\n"
                "The crown resets every week — protect your legacy."
            ),
            color=COLOR_GOLD
        )
        embed.set_thumbnail(url=winner.display_avatar.url)
        embed.set_footer(text="HellFire Hangout • Weekly Ascension")

        try:
            await channel.send(content=f"👑 Attention {guild.default_role}!", embed=embed)
        except: pass

    # =================================================
    # TEST COMMAND (STAFF ONLY)
    # =================================================

    @commands.command(name="forcemvp")
    @commands.has_permissions(administrator=True)
    async def forcemvp(self, ctx):
        """Manually triggers the Weekly MVP rotation"""
        await ctx.send("⏳ Processing weekly statistics and rotating MVP...")
        await self.process_guild(ctx.guild)
        await ctx.send("✅ MVP Rotation Complete.")

    @weekly_mvp_task.before_loop
    async def before_task(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(WeeklyTextMVP(bot))
