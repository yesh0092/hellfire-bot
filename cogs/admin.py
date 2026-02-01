import discord
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =================================================
    # STAFF ROLE SYSTEM SETUP
    # =================================================

    @commands.command(name="setupstaff")
    @commands.guild_only()
    @require_level(4)  # Staff+++
    async def setup_staff(self, ctx: commands.Context):
        guild = ctx.guild
        state.MAIN_GUILD_ID = guild.id

        bot_member = guild.get_member(self.bot.user.id)
        if not bot_member or not bot_member.guild_permissions.manage_roles:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Missing Permissions",
                    description="I need **Manage Roles** permission to set up staff roles.",
                    color=COLOR_DANGER
                )
            )

        role_map = {
            1: "Staff",
            2: "Staff+",
            3: "Staff++",
            4: "Staff+++",
        }

        created_roles = []

        for level, name in role_map.items():
            role = discord.utils.get(guild.roles, name=name)

            if not role:
                role = await guild.create_role(
                    name=name,
                    reason="HellFire Hangout • Staff System Setup"
                )
                created_roles.append(name)

            state.STAFF_ROLE_TIERS[level] = role.id

        await ctx.send(
            embed=luxury_embed(
                title="⚙️ Staff System Ready",
                description=(
                    "The **staff hierarchy** has been successfully configured.\n\n"
                    "**Authority Levels:**\n"
                    "• **Staff** → Warnings & tickets\n"
                    "• **Staff+** → Timeouts\n"
                    "• **Staff++** → Kicks\n"
                    "• **Staff+++** → Bans & configuration\n\n"
                    f"{'🆕 Created Roles: ' + ', '.join(created_roles) if created_roles else '✅ All roles already existed.'}"
                ),
                color=COLOR_GOLD
            )
        )

    # =================================================
    # WELCOME CHANNEL
    # =================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def welcome(self, ctx: commands.Context):
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
    @commands.guild_only()
    @require_level(4)
    async def unwelcome(self, ctx: commands.Context):
        if not state.WELCOME_CHANNEL_ID:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ No Welcome Channel",
                    description="No welcome channel is currently configured.",
                    color=COLOR_SECONDARY
                )
            )

        state.WELCOME_CHANNEL_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Welcome Disabled",
                description="Welcome messages have been disabled.",
                color=COLOR_DANGER
            )
        )

    # =================================================
    # SUPPORT LOG CHANNEL
    # =================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def supportlog(self, ctx: commands.Context):
        state.SUPPORT_LOG_CHANNEL_ID = ctx.channel.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="📊 Support Logs Enabled",
                description="This channel will now receive **support logs**.",
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def unsupportlog(self, ctx: commands.Context):
        if not state.SUPPORT_LOG_CHANNEL_ID:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ Already Disabled",
                    description="Support logging is already disabled.",
                    color=COLOR_SECONDARY
                )
            )

        state.SUPPORT_LOG_CHANNEL_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Support Logs Disabled",
                description="Support logs will no longer be recorded.",
                color=COLOR_DANGER
            )
        )

    # =================================================
    # AUTOROLE
    # =================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def autorole(self, ctx: commands.Context, role: discord.Role):
        state.AUTO_ROLE_ID = role.id
        state.MAIN_GUILD_ID = ctx.guild.id

        await ctx.send(
            embed=luxury_embed(
                title="🏅 Autorole Enabled",
                description=f"New members will receive **{role.mention}** automatically.",
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def unautorole(self, ctx: commands.Context):
        if not state.AUTO_ROLE_ID:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ Autorole Disabled",
                    description="No autorole is currently configured.",
                    color=COLOR_SECONDARY
                )
            )

        state.AUTO_ROLE_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Autorole Disabled",
                description="Automatic role assignment has been turned off.",
                color=COLOR_DANGER
            )
        )

    # =================================================
    # CONFIG OVERVIEW
    # =================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def config(self, ctx: commands.Context):
        guild = ctx.guild

        welcome = guild.get_channel(state.WELCOME_CHANNEL_ID) if state.WELCOME_CHANNEL_ID else None
        supportlog = guild.get_channel(state.SUPPORT_LOG_CHANNEL_ID) if state.SUPPORT_LOG_CHANNEL_ID else None
        autorole = guild.get_role(state.AUTO_ROLE_ID) if state.AUTO_ROLE_ID else None

        await ctx.send(
            embed=luxury_embed(
                title="⚙️ Configuration Overview",
                description=(
                    f"👋 **Welcome Channel:** {welcome.mention if welcome else 'Disabled'}\n"
                    f"📊 **Support Logs:** {supportlog.mention if supportlog else 'Disabled'}\n"
                    f"🏅 **Autorole:** {autorole.mention if autorole else 'Disabled'}"
                ),
                color=COLOR_GOLD
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
