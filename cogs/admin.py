import discord
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY
from utils import state


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # SET WELCOME CHANNEL
    # =====================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        """
        Sets the current channel as the welcome channel.
        """
        state.WELCOME_CHANNEL_ID = ctx.channel.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="✅ Welcome Channel Set",
                description=(
                    "This channel has been designated as the **official welcome channel**.\n\n"
                    "New members will now be greeted here with a luxury introduction ✨"
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================
    # SET SUPPORT LOG CHANNEL
    # =====================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def supportlog(self, ctx):
        """
        Sets the current channel as the support log channel.
        """
        state.SUPPORT_LOG_CHANNEL_ID = ctx.channel.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="📊 Support Log Initialized",
                description=(
                    "This channel will now receive **support ticket logs**.\n\n"
                    "All ticket activity will be quietly archived here."
                ),
                color=COLOR_SECONDARY
            )
        )

    # =====================================
    # SET AUTOROLE
    # =====================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def autorole(self, ctx, role: discord.Role):
        """
        Sets the autorole for new members.
        """
        state.AUTO_ROLE_ID = role.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="🏅 Autorole Enabled",
                description=(
                    f"New members will now automatically receive the role:\n\n"
                    f"**{role.name}**"
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================
    # SYSTEM OVERVIEW (ADMIN)
    # =====================================

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        """
        Shows current system configuration.
        """
        guild = ctx.guild

        welcome = guild.get_channel(state.WELCOME_CHANNEL_ID) if state.WELCOME_CHANNEL_ID else None
        supportlog = guild.get_channel(state.SUPPORT_LOG_CHANNEL_ID) if state.SUPPORT_LOG_CHANNEL_ID else None
        autorole = guild.get_role(state.AUTO_ROLE_ID) if state.AUTO_ROLE_ID else None

        await ctx.send(
            embed=luxury_embed(
                title="⚙️ System Configuration",
                description=(
                    f"**Guild:** {guild.name}\n\n"
                    f"👋 **Welcome Channel:** {welcome.mention if welcome else 'Not Set'}\n"
                    f"📊 **Support Log:** {supportlog.mention if supportlog else 'Not Set'}\n"
                    f"🏅 **Autorole:** {autorole.name if autorole else 'Not Set'}\n\n"
                    "All systems are currently operational."
                ),
                color=COLOR_GOLD
            )
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
