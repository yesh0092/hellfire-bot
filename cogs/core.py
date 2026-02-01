import discord
from discord.ext import commands

from utils.config import STAFF_ROLES, COLOR_GOLD, COLOR_DANGER
from utils.embeds import luxury_embed


class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =====================================
    # AUTO SETUP ON GUILD JOIN
    # =====================================

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self.ensure_staff_roles(guild)

    # =====================================
    # MANUAL SETUP COMMAND
    # =====================================

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setupstaff(self, ctx: commands.Context):
        ok, created = await self.ensure_staff_roles(ctx.guild)

        if not ok:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Staff Setup Failed",
                    description="I need **Manage Roles** permission to create staff roles.",
                    color=COLOR_DANGER
                )
            )

        await ctx.send(
            embed=luxury_embed(
                title="✅ Staff Hierarchy Ready",
                description=(
                    "The **staff role hierarchy** is now verified.\n\n"
                    + (
                        f"🆕 **Created Roles:** {', '.join(created)}"
                        if created else
                        "✅ All required staff roles already existed."
                    )
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================
    # INTERNAL ROLE ENSURER
    # =====================================

    async def ensure_staff_roles(self, guild: discord.Guild):
        bot_member = guild.get_member(self.bot.user.id)

        if not bot_member or not bot_member.guild_permissions.manage_roles:
            return False, []

        existing_roles = {role.name for role in guild.roles}
        created_roles = []

        for role_name in STAFF_ROLES:
            if role_name not in existing_roles:
                try:
                    await guild.create_role(
                        name=role_name,
                        reason="HellFire Hangout • Staff hierarchy initialization"
                    )
                    created_roles.append(role_name)
                except (discord.Forbidden, discord.HTTPException):
                    return False, created_roles

        return True, created_roles


async def setup(bot: commands.Bot):
    await bot.add_cog(Core(bot))
