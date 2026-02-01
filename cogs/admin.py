import discord
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =================================================
    # BOOTSTRAP SETUP (CRITICAL FIX)
    # =================================================

    @commands.command(name="setup")
    @commands.guild_only()
    async def setup(self, ctx: commands.Context):
        """
        Bootstrap command:
        • Allowed for Server Owner OR Administrator
        • Creates staff roles
        • Initializes STAFF_ROLE_TIERS
        """

        # ---------- PERMISSION GATE ----------
        if not (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
        ):
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Permission Denied",
                    description=(
                        "Only the **Server Owner** or an **Administrator** "
                        "can run the initial setup."
                    ),
                    color=COLOR_DANGER
                )
            )

        guild = ctx.guild
        state.MAIN_GUILD_ID = guild.id

        bot_member = guild.get_member(self.bot.user.id)
        if not bot_member or not bot_member.guild_permissions.manage_roles:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Missing Permissions",
                    description="I need **Manage Roles** permission to complete setup.",
                    color=COLOR_DANGER
                )
            )

        # ---------- STAFF ROLE MAP ----------
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
                    reason="HellFire Hangout • Initial Staff Setup"
                )
                created_roles.append(name)

            state.STAFF_ROLE_TIERS[level] = role.id

        await ctx.send(
            embed=luxury_embed(
                title="⚙️ Initial Setup Complete",
                description=(
                    "The **HellFire Hangout staff system** is now live.\n\n"
                    "**Staff Hierarchy:**\n"
                    "• **Staff** → Warnings & tickets\n"
                    "• **Staff+** → Timeouts\n"
                    "• **Staff++** → Kicks\n"
                    "• **Staff+++** → Bans & configuration\n\n"
                    f"{'🆕 Created Roles: ' + ', '.join(created_roles) if created_roles else '✅ All roles already existed.'}\n\n"
                    "👉 You may now assign roles and use all admin commands."
                ),
                color=COLOR_GOLD
            )
        )

    # =================================================
    # WELCOME CHANNEL
    # =================================================

    @commands.command()
    @commands.guild_only()
    async def welcome(self, ctx: commands.Context):
        if not self._is_staff_level(ctx, 4):
            return

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
    async def unwelcome(self, ctx: commands.Context):
        if not self._is_staff_level(ctx, 4):
            return

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
    async def supportlog(self, ctx: commands.Context):
        if not self._is_staff_level(ctx, 4):
            return

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
    async def unsupportlog(self, ctx: commands.Context):
        if not self._is_staff_level(ctx, 4):
            return

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
    async def autorole(self, ctx: commands.Context, role: discord.Role):
        if not self._is_staff_level(ctx, 4):
            return

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
    async def unautorole(self, ctx: commands.Context):
        if not self._is_staff_level(ctx, 4):
            return

        state.AUTO_ROLE_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Autorole Disabled",
                description="Automatic role assignment has been turned off.",
                color=COLOR_DANGER
            )
        )

    # =================================================
    # INTERNAL STAFF CHECK (SAFE)
    # =================================================

    def _is_staff_level(self, ctx: commands.Context, required: int) -> bool:
        if ctx.author == ctx.guild.owner:
            return True
        if ctx.author.guild_permissions.administrator:
            return True

        highest = 0
        for level, role_id in state.STAFF_ROLE_TIERS.items():
            if role_id and any(r.id == role_id for r in ctx.author.roles):
                highest = max(highest, level)

        if highest < required:
            ctx.bot.loop.create_task(
                ctx.send(
                    embed=luxury_embed(
                        title="❌ Permission Denied",
                        description="Your staff level is too low for this action.",
                        color=COLOR_DANGER
                    ),
                    delete_after=5
                )
            )
            return False

        return True


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
