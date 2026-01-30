import discord
import re
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER, COLOR_SECONDARY, COLOR_GOLD
from utils import state


INVITE_REGEX = re.compile(r"(discord\.gg/|discord\.com/invite/)", re.IGNORECASE)

SCAM_KEYWORDS = [
    "free nitro",
    "steam skin",
    "crypto drop",
    "airdrop",
    "claim now",
    "limited offer",
    "free btc"
]


class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_tracker = []
        self.raid_watcher.start()

    def cog_unload(self):
        self.raid_watcher.cancel()

    # =====================================
    # MESSAGE PROTECTION
    # =====================================

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.author.bot:
            return

        content = message.content.lower()

        # ---------- INVITE FILTER ----------
        if INVITE_REGEX.search(content):
            if not message.author.guild_permissions.manage_messages:
                await message.delete()
                await self.soft_warn(
                    message.author,
                    "Posting Discord invite links is not permitted."
                )
                return

        # ---------- SCAM DETECTION ----------
        if any(keyword in content for keyword in SCAM_KEYWORDS):
            if not message.author.guild_permissions.manage_messages:
                await message.delete()
                await self.soft_warn(
                    message.author,
                    "Potential scam message detected. Please avoid misleading content."
                )
                return

        # ---------- SPAM BURST DETECTION ----------
        now = datetime.utcnow()
        history = state.MESSAGE_HISTORY.setdefault(message.author.id, [])
        history.append(now)

        # Keep last 10 seconds only
        state.MESSAGE_HISTORY[message.author.id] = [
            t for t in history if now - t < timedelta(seconds=10)
        ]

        if len(state.MESSAGE_HISTORY[message.author.id]) >= 6:
            await self.apply_slow_action(message.author, message.channel)

    # =====================================
    # SOFT ACTIONS (CALM, LUXURY)
    # =====================================

    async def soft_warn(self, member: discord.Member, reason: str):
        try:
            await member.send(
                embed=luxury_embed(
                    title="⚠️ Security Notice",
                    description=(
                        f"{reason}\n\n"
                        "This is an automated safety reminder. "
                        "No action is required if behavior is adjusted."
                    ),
                    color=COLOR_SECONDARY
                )
            )
        except:
            pass

    async def apply_slow_action(self, member: discord.Member, channel: discord.TextChannel):
        try:
            await channel.edit(slowmode_delay=5)
            await channel.send(
                embed=luxury_embed(
                    title="🐢 Slowmode Enabled",
                    description=(
                        "High message frequency detected.\n\n"
                        "Slowmode has been temporarily enabled to maintain calm discussion."
                    ),
                    color=COLOR_SECONDARY
                )
            )
        except:
            pass

    # =====================================
    # RAID DETECTION (JOIN BURST)
    # =====================================

    @commands.Cog.listener()
    async def on_member_join(self, member):
        now = datetime.utcnow()
        self.join_tracker.append(now)

        # Keep last 60 seconds
        self.join_tracker = [
            t for t in self.join_tracker if now - t < timedelta(seconds=60)
        ]

        if len(self.join_tracker) >= 5:
            await self.handle_possible_raid(member.guild)

    async def handle_possible_raid(self, guild: discord.Guild):
        try:
            system_cog = self.bot.get_cog("System")
            panic_active = system_cog.panic_mode if system_cog else False

            if panic_active:
                return

            # Enable slowmode across text channels
            for channel in guild.text_channels:
                try:
                    await channel.edit(slowmode_delay=10)
                except:
                    pass

            # Alert owner silently
            if guild.owner:
                await guild.owner.send(
                    embed=luxury_embed(
                        title="🚨 Possible Raid Detected",
                        description=(
                            "Multiple users joined within a short time window.\n\n"
                            "Preventive slowmode has been enabled automatically."
                        ),
                        color=COLOR_DANGER
                    )
                )

        except:
            pass

    # =====================================
    # PERIODIC CLEANUP
    # =====================================

    @tasks.loop(minutes=5)
    async def raid_watcher(self):
        """
        Clears stale join data periodically.
        """
        self.join_tracker.clear()

    @raid_watcher.before_loop
    async def before_raid_watcher(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Security(bot))
