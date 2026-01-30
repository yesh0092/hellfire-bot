from discord.ext import commands
from utils.config import STAFF_ROLES

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.ensure_staff_roles(guild)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setupstaff(self, ctx):
        await self.ensure_staff_roles(ctx.guild)
        await ctx.send("✅ Staff hierarchy initialized.")

    async def ensure_staff_roles(self, guild):
        existing = [r.name for r in guild.roles]
        for role_name in STAFF_ROLES:
            if role_name not in existing:
                await guild.create_role(
                    name=role_name,
                    reason="Hellfire staff hierarchy setup"
                )

async def setup(bot):
    await bot.add_cog(Core(bot))
