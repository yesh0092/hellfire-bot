import discord
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # 🔒 Ensure staff role tiers always exist
        if not hasattr(state, "STAFF_ROLE_TIERS"):
            state.STAFF_ROLE_TIERS = {
                1: None,
                2: None,
                3: None,
                4: None,
            }

    # =================================================
    # BOOTSTRAP SETUP (FIXED & STABLE)
    # =================================================

    @commands.command(name="setup")
    @commands.guild_only()
    async def setup(self, ctx: commands.Context):
        """
        Bootstrap command:
        • Server Owner / Admin only
        • Creates staff roles
        • Initializes STAFF_ROLE_TIERS
        • Creates bot-log channel
        """

        if not (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
        ):
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Permission Denied",
                    description="Only the **Server Owner** or an **Administrator** can run setup.",
                    color=COLOR_DANGER
                )
            )

        guild = ctx.guild
        state.MAIN_GUILD_ID = guild.id

        bot_member = guild.get_member(self.bot.user.id)
        if not bot_member:
            return

        if not bot_member.guild_permissions.manage_roles:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Missing Permissions",
                    description="I need **Manage Roles** permission.",
                    color=COLOR_DANGER
                )
            )

        # ---------- STAFF ROLES ----------
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
                    reason="HellFire Hangout • Staff Setup"
                )
                created_roles.append(name)

            state.STAFF_ROLE_TIERS[level] = role.id

        # ---------- BOT LOG CHANNEL ----------
        if not bot_member.guild_permissions.manage_channels:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Missing Permissions",
                    description="I need **Manage Channels** permission to create bot logs.",
                    color=COLOR_DANGER
                )
            )

        log_channel = discord.utils.get(guild.text_channels, name="bot-logs")

        if not log_channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                bot_member: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    embed_links=True
                )
            }

            log_channel = await guild.create_text_channel(
                name="bot-logs",
                overwrites=overwrites,
                reason="HellFire Hangout • Bot Logs"
            )

        state.BOT_LOG_CHANNEL_ID = log_channel.id

        # ---------- CONFIRM ----------
        await ctx.send(
            embed=luxury_embed(
                title="⚙️ Setup Complete",
                description=(
                    "**Staff system initialized successfully.**\n\n"
                    f"{'🆕 Created Roles: ' + ', '.join(created_roles) if created_roles else '✅ All roles already existed.'}\n\n"
                    f"📁 **Bot Logs:** {log_channel.mention}\n\n"
                    "You may now use all admin commands."
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
                description="This channel is now the welcome channel.",
                color=COLOR_GOLD
            )
        )

    @commands.command()
    @commands.guild_only()
    async def unwelcome(self, ctx: commands.Context):
        if not self._is_staff_level(ctx, 4):
            return

        state.WELCOME_CHANNEL_ID = None

        await ctx.send(
            embed=luxury_embed(
                title="❌ Welcome Disabled",
                description="Welcome messages are now disabled.",
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
        await ctx.send(
            embed=luxury_embed(
                title="📊 Support Logs Enabled",
                description="Support logs will be sent here.",
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
                description="Support logging disabled.",
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
        await ctx.send(
            embed=luxury_embed(
                title="🏅 Autorole Enabled",
                description=f"New members will get {role.mention}.",
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
                description="Autorole has been disabled.",
                color=COLOR_DANGER
            )
        )

    # =================================================
    # STAFF CHECK (FIXED)
    # =================================================

    def _is_staff_level(self, ctx: commands.Context, required: int) -> bool:
        if ctx.author == ctx.guild.owner or ctx.author.guild_permissions.administrator:
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
                        description="Your staff level is too low.",
                        color=COLOR_DANGER
                    ),
                    delete_after=5
                )
            )
            return False

        return True


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))