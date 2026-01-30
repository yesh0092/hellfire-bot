import discord
from discord.ext import commands, tasks

from utils.embeds import luxury_embed
from utils.permissions import require_level
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


class VoiceSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_guard.start()

    def cog_unload(self):
        self.voice_guard.cancel()

    # =====================================================
    # AUTO REJOIN TASK
    # =====================================================

    @tasks.loop(seconds=20)
    async def voice_guard(self):
        if not state.VOICE_STAY_ENABLED:
            return

        if not state.VOICE_CHANNEL_ID:
            return

        guild = self.bot.get_guild(state.MAIN_GUILD_ID)
        if not guild:
            return

        channel = guild.get_channel(state.VOICE_CHANNEL_ID)
        if not channel or not isinstance(channel, discord.VoiceChannel):
            return

        vc = guild.voice_client

        # If not connected → reconnect
        if not vc or not vc.is_connected():
            try:
                await channel.connect(self_deaf=True)
            except discord.HTTPException:
                pass

    # =====================================================
    # SET VOICE CHANNEL
    # =====================================================

    @commands.command()
    @require_level(4)  # Staff+++
    async def setvc(self, ctx, channel: discord.VoiceChannel):
        state.VOICE_CHANNEL_ID = channel.id
        state.VOICE_STAY_ENABLED = True
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="🔊 Voice Presence Enabled",
                description=(
                    f"Bot will now stay connected to:\n"
                    f"🎧 **{channel.name}**\n\n"
                    "• Auto-rejoin enabled\n"
                    "• Silent presence\n"
                    "• No recording"
                ),
                color=COLOR_GOLD
            )
        )

        try:
            await channel.connect(self_deaf=True)
        except discord.HTTPException:
            pass

    # =====================================================
    # DISABLE VOICE SYSTEM
    # =====================================================

    @commands.command()
    @require_level(4)
    async def unsetvc(self, ctx):
        state.VOICE_STAY_ENABLED = False

        vc = ctx.guild.voice_client
        if vc:
            await vc.disconnect(force=True)

        await ctx.send(
            embed=luxury_embed(
                title="❌ Voice Presence Disabled",
                description="Bot will no longer stay in any voice channel.",
                color=COLOR_DANGER
            )
        )

    # =====================================================
    # STATUS
    # =====================================================

    @commands.command()
    @require_level(1)
    async def vcstatus(self, ctx):
        if not state.VOICE_CHANNEL_ID or not state.VOICE_STAY_ENABLED:
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
                    f"🎧 Channel: **{channel.name if channel else 'Unknown'}**\n"
                    f"🔁 Auto Rejoin: Enabled\n"
                    f"🔒 Silent Mode: Active"
                ),
                color=COLOR_GOLD
            )
        )


async def setup(bot):
    await bot.add_cog(VoiceSystem(bot))
