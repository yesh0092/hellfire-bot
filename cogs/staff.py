import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


class Staff(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.activity_monitor.start()

    def cog_unload(self):
        self.activity_monitor.cancel()

    # =====================================
    # INTERNAL HELPERS
    # =====================================

    def is_staff(self, member: discord.Member) -> bool:
        return any(role.name.startswith("Staff") for role in member.roles)

    def record_action(self, staff_id: int):
        stats = state.STAFF_STATS.setdefault(staff_id, {
            "actions": 0,
            "last_action": None,
            "today": 0
        })
        stats["actions"] += 1
        stats["today"] += 1
        stats["last_action"] = datetime.utcnow()

    # =====================================
    # STAFF NOTES (PRIVATE)
    # =====================================

    @commands.command()
    @commands.guild_only()
    async def note(self, ctx: commands.Context, user: discord.Member, *, note: str):
        if not self.is_staff(ctx.author):
            return

        notes = state.STAFF_NOTES.setdefault(user.id, [])
        notes.append({
            "by": ctx.author.id,
            "note": note,
            "time": datetime.utcnow()
        })

        await ctx.send(
            embed=luxury_embed(
                title="📝 Staff Note Added",
                description=f"A private staff note has been recorded for **{user}**.",
                color=COLOR_GOLD
            )
        )

        self.record_action(ctx.author.id)

    @commands.command()
    @commands.guild_only()
    async def notes(self, ctx: commands.Context, user: discord.Member):
        if not self.is_staff(ctx.author):
            return

        notes = state.STAFF_NOTES.get(user.id, [])
        if not notes:
            await ctx.send(
                embed=luxury_embed(
                    title="📝 Staff Notes",
                    description="No internal notes are recorded for this user.",
                    color=COLOR_SECONDARY
                )
            )
            return

        desc = ""
        for n in notes[-5:]:
            desc += (
                f"• <@{n['by']}> — {n['note']} "
                f"(`{n['time'].strftime('%Y-%m-%d')}`)\n"
            )

        await ctx.send(
            embed=luxury_embed(
                title=f"🧠 Staff Notes — {user}",
                description=desc,
                color=COLOR_GOLD
            )
        )

    # =====================================
    # STAFF SNAPSHOT
    # =====================================

    @commands.command()
    @commands.guild_only()
    async def staff(self, ctx: commands.Context):
        staff_members = [m for m in ctx.guild.members if self.is_staff(m)]

        lines = []
        for m in staff_members:
            stats = state.STAFF_STATS.get(m.id, {})
            today = stats.get("today", 0)
            lines.append(f"• {m.mention} — {today} actions today")

        await ctx.send(
            embed=luxury_embed(
                title="👥 Staff Activity Snapshot",
                description="\n".join(lines) if lines else "No staff activity recorded yet.",
                color=COLOR_GOLD
            )
        )

    # =====================================
    # BURNOUT & ABUSE MONITOR
    # =====================================

    @tasks.loop(minutes=30)
    async def activity_monitor(self):
        now = datetime.utcnow()

        for staff_id, stats in state.STAFF_STATS.items():
            last = stats.get("last_action")
            today = stats.get("today", 0)

            user = self.bot.get_user(staff_id)

            # Burnout detection
            if today >= 20 and user:
                try:
                    await user.send(
                        embed=luxury_embed(
                            title="🧠 Staff Wellness Reminder",
                            description=(
                                "You’ve been very active today.\n\n"
                                "Consider taking a short break to avoid burnout."
                            ),
                            color=COLOR_SECONDARY
                        )
                    )
                except (discord.Forbidden, discord.HTTPException):
                    pass

            # Abuse detection (rapid actions)
            if last and now - last < timedelta(minutes=2) and today >= 10:
                for guild in self.bot.guilds:
                    owner = guild.owner
                    if owner:
                        try:
                            await owner.send(
                                embed=luxury_embed(
                                    title="⚠️ Staff Action Alert",
                                    description=(
                                        f"<@{staff_id}> has performed many moderation actions rapidly.\n\n"
                                        "This is a **safety signal**, not an accusation."
                                    ),
                                    color=COLOR_DANGER
                                )
                            )
                        except (discord.Forbidden, discord.HTTPException):
                            pass

        # Daily reset
        for stats in state.STAFF_STATS.values():
            if stats.get("last_action") and stats["last_action"].date() != now.date():
                stats["today"] = 0

    @activity_monitor.before_loop
    async def before_monitor(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Staff(bot))
