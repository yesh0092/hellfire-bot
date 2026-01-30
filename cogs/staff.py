import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
    async def note(self, ctx, user: discord.Member, *, note: str):
        """
        Add a private staff note about a user.
        """
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
                description=f"Note recorded privately for **{user}**.",
                color=COLOR_GOLD
            )
        )

        self.record_action(ctx.author.id)

    @commands.command()
    async def notes(self, ctx, user: discord.Member):
        """
        View staff notes for a user.
        """
        if not self.is_staff(ctx.author):
            return

        notes = state.STAFF_NOTES.get(user.id, [])
        if not notes:
            await ctx.send(
                embed=luxury_embed(
                    title="📝 Staff Notes",
                    description="No internal notes found for this user.",
                    color=COLOR_SECONDARY
                )
            )
            return

        desc = ""
        for n in notes[-5:]:
            desc += f"• <@{n['by']}> — {n['note']} ({n['time'].strftime('%Y-%m-%d')})\n"

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
    async def staff(self, ctx):
        """
        Shows staff activity snapshot.
        """
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
    # BURNOUT & ABUSE MONITOR (OG FEATURE)
    # =====================================

    @tasks.loop(minutes=30)
    async def activity_monitor(self):
        """
        Detect staff burnout or abuse silently.
        """
        now = datetime.utcnow()

        for staff_id, stats in state.STAFF_STATS.items():
            last = stats.get("last_action")
            today = stats.get("today", 0)

            # Burnout detection
            if today >= 20:
                user = self.bot.get_user(staff_id)
                if user:
                    try:
                        await user.send(
                            embed=luxury_embed(
                                title="🧠 Staff Wellness Notice",
                                description=(
                                    "You’ve been very active today.\n\n"
                                    "Consider taking a short break to avoid burnout ✨"
                                ),
                                color=COLOR_SECONDARY
                            )
                        )
                    except:
                        pass

            # Abuse detection (too many actions too fast)
            if last and now - last < timedelta(minutes=2) and today >= 10:
                guild = self.bot.guilds[0]
                owner = guild.owner
                if owner:
                    try:
                        await owner.send(
                            embed=luxury_embed(
                                title="⚠️ Staff Action Alert",
                                description=(
                                    f"<@{staff_id}> has performed many moderation actions rapidly.\n\n"
                                    "This is **not an accusation**, just a safety signal."
                                ),
                                color=COLOR_DANGER
                            )
                        )
                    except:
                        pass

        # Reset daily counters every loop after midnight UTC
        for stats in state.STAFF_STATS.values():
            if stats.get("last_action") and stats["last_action"].date() != now.date():
                stats["today"] = 0

    @activity_monitor.before_loop
    async def before_monitor(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Staff(bot))
