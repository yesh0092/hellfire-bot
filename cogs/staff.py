import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


STAFF_ROLE_PREFIX = "Staff"
ABUSE_ALERT_COOLDOWN = timedelta(hours=1)


class Staff(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._abuse_alert_cache: dict[int, datetime] = {}

    async def cog_load(self):
        self.activity_monitor.start()

    def cog_unload(self):
        self.activity_monitor.cancel()

    # =====================================
    # INTERNAL HELPERS
    # =====================================

    def is_staff(self, member: discord.Member) -> bool:
        return any(
            role.name in ("Staff", "Staff+", "Staff++", "Staff+++")
            for role in member.roles
        )

    def record_action(self, staff_id: int):
        stats = state.STAFF_STATS.setdefault(
            staff_id,
            {"actions": 0, "today": 0, "last_action": None}
        )
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
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Access Denied",
                    description="Only staff members may use this command.",
                    color=COLOR_DANGER
                )
            )

        notes = state.STAFF_NOTES.setdefault(user.id, [])
        notes.append({
            "by": ctx.author.id,
            "note": note,
            "time": datetime.utcnow()
        })

        self.record_action(ctx.author.id)

        await ctx.send(
            embed=luxury_embed(
                title="📝 Staff Note Added",
                description=f"A private note has been recorded for **{user}**.",
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @commands.guild_only()
    async def notes(self, ctx: commands.Context, user: discord.Member):
        if not self.is_staff(ctx.author):
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Access Denied",
                    description="Only staff members may view staff notes.",
                    color=COLOR_DANGER
                )
            )

        notes = state.STAFF_NOTES.get(user.id, [])
        if not notes:
            return await ctx.send(
                embed=luxury_embed(
                    title="📝 Staff Notes",
                    description="No internal notes recorded for this user.",
                    color=COLOR_SECONDARY
                )
            )

        desc = "\n".join(
            f"• <@{n['by']}> — {n['note']} (`{n['time'].strftime('%Y-%m-%d')}`)"
            for n in notes[-5:]
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

        if not staff_members:
            return await ctx.send(
                embed=luxury_embed(
                    title="👥 Staff Activity Snapshot",
                    description="No staff activity recorded yet.",
                    color=COLOR_SECONDARY
                )
            )

        lines = []
        for member in staff_members:
            stats = state.STAFF_STATS.get(member.id, {})
            lines.append(
                f"• {member.mention} — {stats.get('today', 0)} actions today"
            )

        await ctx.send(
            embed=luxury_embed(
                title="👥 Staff Activity Snapshot",
                description="\n".join(lines),
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
            user = self.bot.get_user(staff_id)
            if not user:
                continue

            today = stats.get("today", 0)
            last_action = stats.get("last_action")

            # Burnout warning
            if today >= 20:
                try:
                    await user.send(
                        embed=luxury_embed(
                            title="🧠 Staff Wellness Reminder",
                            description=(
                                "You’ve been highly active today.\n\n"
                                "Please consider taking a short break to avoid burnout."
                            ),
                            color=COLOR_SECONDARY
                        )
                    )
                except (discord.Forbidden, discord.HTTPException):
                    pass

            # Abuse detection with cooldown
            if (
                last_action
                and now - last_action < timedelta(minutes=2)
                and today >= 10
            ):
                last_alert = self._abuse_alert_cache.get(staff_id)
                if last_alert and now - last_alert < ABUSE_ALERT_COOLDOWN:
                    continue

                self._abuse_alert_cache[staff_id] = now

                guild = self.bot.get_guild(state.MAIN_GUILD_ID)
                if guild and guild.owner:
                    try:
                        await guild.owner.send(
                            embed=luxury_embed(
                                title="⚠️ Staff Action Alert",
                                description=(
                                    f"<@{staff_id}> has performed many moderation "
                                    "actions in a short time.\n\n"
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Staff(bot))
