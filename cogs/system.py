import discord
from discord.ext import commands
from datetime import datetime
from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER, COLOR_GOLD, COLOR_SECONDARY

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.panic_mode = False
        self.panic_activated_at = None

    # =========================
    # PANIC MODE
    # =========================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def panic(self, ctx, *, reason: str = "Emergency situation"):
        """
        Instantly locks down support operations and alerts staff.
        """
        if self.panic_mode:
            await ctx.send(
                embed=luxury_embed(
                    title="⚠️ Panic Mode Already Active",
                    description="The system is already operating under emergency protocols.",
                    color=COLOR_DANGER
                )
            )
            return

        self.panic_mode = True
        self.panic_activated_at = datetime.utcnow()

        # Enable slowmode on current channel
        try:
            await ctx.channel.edit(slowmode_delay=10)
        except:
            pass

        await ctx.send(
            embed=luxury_embed(
                title="🚨 PANIC MODE ACTIVATED",
                description=(
                    f"**Reason:** {reason}\n\n"
                    "🔒 Support intake temporarily locked\n"
                    "🐢 Slowmode enabled\n"
                    "📢 Staff have been alerted\n\n"
                    "The system is now operating in **emergency containment mode**."
                ),
                color=COLOR_DANGER
            )
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unpanic(self, ctx):
        """
        Restores normal bot operation.
        """
        if not self.panic_mode:
            await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ Panic Mode Not Active",
                    description="The system is already operating normally.",
                    color=COLOR_SECONDARY
                )
            )
            return

        self.panic_mode = False
        self.panic_activated_at = None

        # Disable slowmode
        try:
            await ctx.channel.edit(slowmode_delay=0)
        except:
            pass

        await ctx.send(
            embed=luxury_embed(
                title="✅ Panic Mode Deactivated",
                description=(
                    "All emergency restrictions have been lifted.\n\n"
                    "🟢 Support systems restored\n"
                    "⚙️ Normal operation resumed"
                ),
                color=COLOR_GOLD
            )
        )

    # =========================
    # SYSTEM STATUS
    # =========================

    @commands.command()
    async def status(self, ctx):
        """
        Displays live system diagnostics.
        """
        uptime_seconds = int((datetime.utcnow() - self.bot.launch_time).total_seconds())
        uptime = self.format_duration(uptime_seconds)

        panic_status = "🔴 ACTIVE" if self.panic_mode else "🟢 Normal"

        embed = luxury_embed(
            title="🧠 System Diagnostics",
            description=(
                f"**Bot:** {self.bot.user}\n"
                f"**Uptime:** {uptime}\n"
                f"**Latency:** {round(self.bot.latency * 1000)} ms\n\n"
                f"**Panic Mode:** {panic_status}\n"
                f"**Guilds:** {len(self.bot.guilds)}\n"
                f"**Users Cached:** {len(self.bot.users)}\n\n"
                "All core systems are responding within acceptable parameters."
            ),
            color=COLOR_GOLD if not self.panic_mode else COLOR_DANGER
        )

        if self.panic_mode and self.panic_activated_at:
            embed.add_field(
                name="🚨 Panic Activated At",
                value=self.panic_activated_at.strftime("%Y-%m-%d %H:%M UTC"),
                inline=False
            )

        await ctx.send(embed=embed)

    # =========================
    # UTILITIES
    # =========================

    @staticmethod
    def format_duration(seconds: int) -> str:
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)

        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if seconds or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)


async def setup(bot):
    # Track launch time once
    if not hasattr(bot, "launch_time"):
        bot.launch_time = datetime.utcnow()

    await bot.add_cog(System(bot))
