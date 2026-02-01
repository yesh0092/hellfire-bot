import discord
from discord.ext import commands, tasks

from utils.embeds import luxury_embed
from utils.permissions import require_level
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


class VoiceSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Safe defaults (never overwrite)
        state.VOICE_STAY_ENABLED = getattr(state, "VOICE_STAY_ENABLED", False)
        state.VOICE_CHANNEL_ID = getattr(state, "VOICE_CHANNEL_ID", None)

    # =====================================================
    # STARTUP
    # =====================================================

    async def cog_load(self):
        self.voice_guard.start()

    def cog_unload(self):
        self.voice_guard.cancel()

    # =====================================================
    # CORE VOICE CONNECTOR (BULLETPROOF)
    # =====================================================

    async def ensure_voice_connection(self):
        if not state.VOICE_STAY_ENABLED:
            return

        if not state.VOICE_CHANNEL_ID or not state.MAIN_GUILD_ID:
            return

        guild = self.bot.get_guild(state.MAIN_GUILD_ID)
        if not guild:
            return

        bot_member = guild.get_member(self.bot.user.id)
        if not bot_member:
            return

        channel = guild.get_channel(state.VOICE_CHANNEL_ID)
        if not isinstance(channel, discord.VoiceChannel):
            return

        if not channel.permissions_for(bot_member).connect:
            return

        vc = guild.voice_client

        try:
            # Not connected at all
            if not vc or not vc.is_connected():
                await channel.connect(self_deaf=True)
                return

            # Connected to wrong channel
            if vc.channel.id != channel.id:
                await vc.disconnect(force=True)
                await channel.connect(self_deaf=True)
                return

        except (discord.Forbidden, discord.HTTPException):
            pass

    # =====================================================
    # AUTO REJOIN LOOP (24/7)
    # =====================================================

    @tasks.loop(seconds=20)
    async def voice_guard(self):
        await self.ensure_voice_connection()

    @voice_guard.before_loop
    async def before_voice_guard(self):
        await self.bot.wait_until_ready()

    # =====================================================
    # SET VOICE CHANNEL
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def setvc(self, ctx: commands.Context, channel: discord.VoiceChannel):
        bot_member = ctx.guild.get_member(self.bot.user.id)

        if not bot_member or not channel.permissions_for(bot_member).connect:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Missing Permissions",
                    description="I cannot connect to that voice channel.",
                    color=COLOR_DANGER
                )
            )

        state.VOICE_CHANNEL_ID = channel.id
        state.VOICE_STAY_ENABLED = True
        state.MAIN_GUILD_ID = ctx.guild.id

        await self.ensure_voice_connection()

        await ctx.send(
            embed=luxury_embed(
                title="🔊 Voice Presence Enabled",
                description=(
                    f"🎧 **Channel:** {channel.name}\n\n"
                    "• 24/7 Presence\n"
                    "• Auto-rejoin on disconnect\n"
                    "• Silent (self-deaf)\n"
                    "• No recording"
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================================
    # DISABLE VOICE SYSTEM
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def unsetvc(self, ctx: commands.Context):
        state.VOICE_STAY_ENABLED = False

        vc = ctx.guild.voice_client
        if vc:
            try:
                await vc.disconnect(force=True)
            except (discord.Forbidden, discord.HTTPException):
                pass

        await ctx.send(
            embed=luxury_embed(
                title="❌ Voice Presence Disabled",
                description="The bot will no longer stay in voice channels.",
                color=COLOR_DANGER
            )
        )

    # =====================================================
    # STATUS
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(1)
    async def vcstatus(self, ctx: commands.Context):
        if not state.VOICE_STAY_ENABLED or not state.VOICE_CHANNEL_ID:
            return await ctx.send(
                embed=luxury_embed(
                    title="🔇 Voice System",
                    description="Voice presence is currently **disabled**.",
                    color=COLOR_SECONDARY
                )
            )

        channel = ctx.guild.get_channel(state.VOICE_CHANNEL_ID)

        await ctx.send(
            embed=luxury_embed(
                title="🔊 Voice System Active",
                description=(
                    f"🎧 **Channel:** {channel.name if channel else 'Unknown'}\n"
                    "🔁 Auto-rejoin: Enabled\n"
                    "🕒 Presence: 24/7\n"
                    "🔒 Silent mode: Active"
                ),
                color=COLOR_GOLD
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceSystem(bot))
