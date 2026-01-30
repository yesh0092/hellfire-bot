import discord
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =================================================
    # WELCOME CHANNEL
    # =================================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        state.WELCOME_CHANNEL_ID = ctx.channel.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="👋 Welcome Channel Set",
                description="This channel is now the **official welcome channel**.",
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unwelcome(self, ctx):
        if not state.WELCOME_CHANNEL_ID:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ Nothing to Remove",
                    description="No welcome channel is currently set.",
                    color=COLOR_SECONDARY
                )
            )

        state.WELCOME_CHANNEL_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Welcome Channel Removed",
                description="Welcome messages have been **disabled**.",
                color=COLOR_DANGER
            )
        )

    # =================================================
    # SUPPORT LOG CHANNEL
    # =================================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def supportlog(self, ctx):
        state.SUPPORT_LOG_CHANNEL_ID = ctx.channel.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="📊 Support Log Enabled",
                description="This channel will now receive support logs.",
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unsupportlog(self, ctx):
        if not state.SUPPORT_LOG_CHANNEL_ID:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ Nothing to Remove",
                    description="Support logging is already disabled.",
                    color=COLOR_SECONDARY
                )
            )

        state.SUPPORT_LOG_CHANNEL_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Support Logging Disabled",
                description="Support ticket logs will no longer be recorded.",
                color=COLOR_DANGER
            )
        )

    # =================================================
    # AUTOROLE
    # =================================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, role: discord.Role):
        state.AUTO_ROLE_ID = role.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="🏅 Autorole Enabled",
                description=f"New members will receive **{role.name}**.",
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unautorole(self, ctx):
        if not state.AUTO_ROLE_ID:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ Nothing to Remove",
                    description="Autorole is already disabled.",
                    color=COLOR_SECONDARY
                )
            )

        state.AUTO_ROLE_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Autorole Disabled",
                description="New members will no longer receive an automatic role.",
                color=COLOR_DANGER
            )
        )

    # =================================================
    # CONFIG OVERVIEW
    # =================================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        guild = ctx.guild

        welcome = guild.get_channel(state.WELCOME_CHANNEL_ID) if state.WELCOME_CHANNEL_ID else None
        supportlog = guild.get_channel(state.SUPPORT_LOG_CHANNEL_ID) if state.SUPPORT_LOG_CHANNEL_ID else None
        autorole = guild.get_role(state.AUTO_ROLE_ID) if state.AUTO_ROLE_ID else None

        await ctx.send(
            embed=luxury_embed(
                title="⚙️ Current Configuration",
                description=(
                    f"👋 **Welcome Channel:** {welcome.mention if welcome else 'Disabled'}\n"
                    f"📊 **Support Log:** {supportlog.mention if supportlog else 'Disabled'}\n"
                    f"🏅 **Autorole:** {autorole.name if autorole else 'Disabled'}\n\n"
                    "All settings are reversible at any time."
                ),
                color=COLOR_GOLD
            )
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
