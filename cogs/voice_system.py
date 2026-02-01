import discord
from discord.ext import commands, tasks

from utils.embeds import luxury_embed
from utils.permissions import require_level
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


class VoiceSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------------- AUTO REJOIN LOOP ----------------

    @tasks.loop(seconds=15)
    async def voice_guard(self):
        if not state.VOICE_STAY_ENABLED:
            return

        if not state.MAIN_GUILD_ID or not state.VOICE_CHANNEL_ID:
            return

        guild = self.bot.get_guild(state.MAIN_GUILD_ID)
        if not guild:
            return

        channel = guild.get_channel(state.VOICE_CHANNEL_ID)
        if not isinstance(channel, discord.VoiceChannel):
            return

        vc = guild.voice_client

        try:
            if not vc or not vc.is_connected():
                await channel.connect(self_mute=True, self_deaf=True)
        except Exception as e:
            print("VOICE ERROR:", e)

    @voice_guard.before_loop
    async def before_guard(self):
        await self.bot.wait_until_ready()

    async def cog_load(self):
        self.voice_guard.start()

    def cog_unload(self):
        self.voice_guard.cancel()

    # ---------------- SET VC ----------------

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def setvc(self, ctx: commands.Context, channel_id: int):
        channel = ctx.guild.get_channel(channel_id)

        if not isinstance(channel, discord.VoiceChannel):
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Invalid Voice Channel",
                    description="Provide a **voice channel ID** only.",
                    color=COLOR_DANGER
                )
            )

        perms = channel.permissions_for(ctx.guild.me)
        if not perms.connect or not perms.speak:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Missing Permissions",
                    description="I need **Connect + Speak** permissions.",
                    color=COLOR_DANGER
                )
            )

        state.MAIN_GUILD_ID = ctx.guild.id
        state.VOICE_CHANNEL_ID = channel.id
        state.VOICE_STAY_ENABLED = True

        await channel.connect(self_mute=True, self_deaf=True)

        await ctx.send(
            embed=luxury_embed(
                title="🔊 Voice Connected",
                description=(
                    f"🎧 **Channel:** {channel.name}\n"
                    "🎤 Mic: OFF\n"
                    "🔇 Deafened: ON\n"
                    "🕒 24/7 Mode: ENABLED"
                ),
                color=COLOR_GOLD
            )
        )

    # ---------------- STATUS ----------------

    @commands.command()
    @commands.guild_only()
    async def vcstatus(self, ctx):
        vc = ctx.guild.voice_client

        await ctx.send(
            embed=luxury_embed(
                title="🔊 Voice Status",
                description=(
                    f"Connected: {'Yes' if vc else 'No'}\n"
                    f"Channel: {vc.channel.name if vc else '—'}"
                ),
                color=COLOR_SECONDARY
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceSystem(bot))
