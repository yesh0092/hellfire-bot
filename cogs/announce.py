import discord
import asyncio
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state


# =====================================================
# RUNTIME STATE (SAFE, IN-MEMORY)
# =====================================================

state.ANNOUNCE_TEMPLATES = getattr(state, "ANNOUNCE_TEMPLATES", {})
state.ANNOUNCE_OPTOUT = getattr(state, "ANNOUNCE_OPTOUT", set())
state.ANNOUNCE_HISTORY = getattr(state, "ANNOUNCE_HISTORY", [])


class Announce(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================================
    # MAIN COMMAND GROUP
    # =====================================================

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @require_level(4)
    async def announce(self, ctx):
        await ctx.send(
            embed=luxury_embed(
                title="📢 Announcement System",
                description=(
                    "`&announce dm <message>`\n"
                    "`&announce channel #channel <message>`\n"
                    "`&announce preview <message>`\n"
                    "`&announce schedule <minutes> <message>`\n"
                    "`&announce template add/use`\n"
                    "`&announce optout / optin`"
                ),
                color=COLOR_SECONDARY
            )
        )

    # =====================================================
    # DM ANNOUNCEMENT
    # =====================================================

    @announce.command(name="dm")
    async def announce_dm(self, ctx, *, message: str):
        if state.SYSTEM_FLAGS.get("panic_mode"):
            return await ctx.send(embed=luxury_embed(
                title="🚨 Panic Mode Active",
                description="Announcements are disabled.",
                color=COLOR_DANGER
            ))

        embed = self._build_embed(message)
        sent, failed = 0, 0

        status = await ctx.send(embed=luxury_embed(
            title="📡 Broadcasting (DM)",
            description="Sending announcements...",
            color=COLOR_SECONDARY
        ))

        for member in ctx.guild.members:
            if member.bot or member.id in state.ANNOUNCE_OPTOUT:
                continue
            try:
                await member.send(embed=embed)
                sent += 1
                await asyncio.sleep(0.9)
            except:
                failed += 1
                await asyncio.sleep(0.3)

        await self._finalize(ctx, status, sent, failed, "DM")

    # =====================================================
    # CHANNEL ANNOUNCEMENT
    # =====================================================

    @announce.command(name="channel")
    async def announce_channel(self, ctx, channel: discord.TextChannel, *, message: str):
        embed = self._build_embed(message)
        await channel.send(embed=embed)
        await ctx.send(embed=luxury_embed(
            title="📣 Announcement Posted",
            description=f"Sent to {channel.mention}",
            color=COLOR_GOLD
        ))

    # =====================================================
    # PREVIEW
    # =====================================================

    @announce.command(name="preview")
    async def announce_preview(self, ctx, *, message: str):
        await ctx.send(embed=self._build_embed(message))

    # =====================================================
    # SCHEDULED ANNOUNCEMENT
    # =====================================================

    @announce.command(name="schedule")
    async def announce_schedule(self, ctx, minutes: int, *, message: str):
        await ctx.send(embed=luxury_embed(
            title="⏰ Announcement Scheduled",
            description=f"Will send in **{minutes} minutes**.",
            color=COLOR_GOLD
        ))

        async def delayed_send():
            await asyncio.sleep(minutes * 60)
            await self.announce_dm(ctx, message=message)

        self.bot.loop.create_task(delayed_send())

    # =====================================================
    # TEMPLATE SYSTEM
    # =====================================================

    @announce.group()
    async def template(self, ctx):
        pass

    @template.command(name="add")
    async def template_add(self, ctx, name: str, *, message: str):
        state.ANNOUNCE_TEMPLATES[name.lower()] = message
        await ctx.send(embed=luxury_embed(
            title="📌 Template Saved",
            description=f"Template `{name}` added.",
            color=COLOR_GOLD
        ))

    @template.command(name="use")
    async def template_use(self, ctx, name: str):
        msg = state.ANNOUNCE_TEMPLATES.get(name.lower())
        if not msg:
            return await ctx.send(embed=luxury_embed(
                title="❌ Template Not Found",
                description="No such template.",
                color=COLOR_DANGER
            ))
        await ctx.send(embed=self._build_embed(msg))

    # =====================================================
    # OPTOUT SYSTEM (USERS)
    # =====================================================

    @announce.command()
    async def optout(self, ctx):
        state.ANNOUNCE_OPTOUT.add(ctx.author.id)
        await ctx.send("🔕 You will no longer receive announcements.")

    @announce.command()
    async def optin(self, ctx):
        state.ANNOUNCE_OPTOUT.discard(ctx.author.id)
        await ctx.send("🔔 You will now receive announcements.")

    # =====================================================
    # INTERNAL UTILITIES
    # =====================================================

    def _build_embed(self, message: str):
        embed = luxury_embed(
            title="📜 Imperial Proclamation",
            description=message,
            color=COLOR_GOLD
        )
        embed.set_footer(text="HellFire Hangout • Official Announcement")
        if self.bot.user and self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        return embed

    async def _finalize(self, ctx, status, sent, failed, mode):
        await status.edit(embed=luxury_embed(
            title="📊 Announcement Complete",
            description=f"Mode: {mode}\n✅ Sent: {sent}\n❌ Failed: {failed}",
            color=COLOR_GOLD
        ))

        state.ANNOUNCE_HISTORY.append({
            "by": ctx.author.id,
            "sent": sent,
            "failed": failed,
            "time": datetime.utcnow()
        })

        if len(state.ANNOUNCE_HISTORY) > 10:
            state.ANNOUNCE_HISTORY.pop(0)


async def setup(bot: commands.Bot):
    await bot.add_cog(Announce(bot))
