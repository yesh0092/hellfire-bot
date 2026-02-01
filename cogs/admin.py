import discord
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =================================================
    # AUTO SETUP (STAFF ROLE SYSTEM)
    # =================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)  # Staff+++
    async def setup(self, ctx: commands.Context):
        guild = ctx.guild
        state.MAIN_GUILD_ID = guild.id

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
                if not guild.me.guild_permissions.manage_roles:
                    return await ctx.send(
                        embed=luxury_embed(
                            title="❌ Missing Permissions",
                            description="I need **Manage Roles** permission to complete setup.",
                            color=COLOR_DANGER
                        )
                    )

                role = await guild.create_role(
                    name=name,
                    reason="HellFire Hangout • Staff System Setup"
                )
                created_roles.append(name)

            state.STAFF_ROLE_TIERS[level] = role.id

        await ctx.send(
            embed=luxury_embed(
                title="⚙️ Staff System Setup Complete",
                description=(
                    "The **staff role hierarchy** is now active.\n\n"
                    "**Authority Levels:**\n"
                    "• **Staff** → Warnings & tickets\n"
                    "• **Staff+** → Timeouts\n"
                    "• **Staff++** → Kicks\n"
                    "• **Staff+++** → Bans & full configuration\n\n"
                    f"{'🆕 **Created Roles:** ' + ', '.join(created_roles) if created_roles else '✅ All required roles already existed.'}"
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
                title="👋 Welcome Channel Configured",
                description="This channel is now set as the **official welcome channel**.",
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
                    title="ℹ️ No Welcome Channel Set",
                    description="There is currently **no welcome channel** configured.",
                    color=COLOR_SECONDARY
                )
            )

        state.WELCOME_CHANNEL_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Welcome Channel Disabled",
                description="Automatic welcome messages have been **successfully disabled**.",
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
                title="📊 Support Logging Enabled",
                description="This channel will now receive **support ticket activity logs**.",
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
                    title="ℹ️ Support Logging Already Disabled",
                    description="There is currently **no support log channel** set.",
                    color=COLOR_SECONDARY
                )
            )

        state.SUPPORT_LOG_CHANNEL_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Support Logging Disabled",
                description="Support ticket logs will **no longer be recorded**.",
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
                description=f"New members will now automatically receive **{role.mention}**.",
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
                    title="ℹ️ Autorole Already Disabled",
                    description="No automatic role is currently configured.",
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
    @commands.guild_only()
    @require_level(4)
    async def config(self, ctx: commands.Context):
        guild = ctx.guild

        welcome = guild.get_channel(state.WELCOME_CHANNEL_ID) if state.WELCOME_CHANNEL_ID else None
        supportlog = guild.get_channel(state.SUPPORT_LOG_CHANNEL_ID) if state.SUPPORT_LOG_CHANNEL_ID else None
        autorole = guild.get_role(state.AUTO_ROLE_ID) if state.AUTO_ROLE_ID else None

        await ctx.send(
            embed=luxury_embed(
                title="⚙️ HellFire Hangout • Configuration Overview",
                description=(
                    f"👋 **Welcome Channel:** {welcome.mention if welcome else 'Disabled'}\n"
                    f"📊 **Support Log Channel:** {supportlog.mention if supportlog else 'Disabled'}\n"
                    f"🏅 **Autorole:** {autorole.mention if autorole else 'Disabled'}\n\n"
                    "All settings can be **updated or reverted at any time**."
                ),
                color=COLOR_GOLD
            )
        )


async def setup(bot):
    await bot.add_cog(Admin(bot))
