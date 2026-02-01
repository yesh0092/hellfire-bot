import discord
from discord.ext import commands

from utils.config import STAFF_ROLES
from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_DANGER


class Core(commands.Cog):
    def __init__(self, bot):
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
        success = await self.ensure_staff_roles(ctx.guild)

        if success:
            await ctx.send(
                embed=luxury_embed(
                    title="✅ Staff Hierarchy Initialized",
                    description=(
                        "The **staff role hierarchy** has been successfully verified and initialized.\n\n"
                        "Missing roles were created where necessary."
                    ),
                    color=COLOR_GOLD
                )
            )

    # =====================================
    # INTERNAL ROLE ENSURER
    # =====================================

    async def ensure_staff_roles(self, guild: discord.Guild) -> bool:
        if not guild.me.guild_permissions.manage_roles:
            return False

        existing_roles = {role.name for role in guild.roles}
        created = []

        for role_name in STAFF_ROLES:
            if role_name not in existing_roles:
                try:
                    await guild.create_role(
                        name=role_name,
                        reason="HellFire Hangout • Staff hierarchy initialization"
                    )
                    created.append(role_name)
                except discord.Forbidden:
                    return False
                except discord.HTTPException:
                    return False

        return True


async def setup(bot):
    await bot.add_cog(Core(bot))
