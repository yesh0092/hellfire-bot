import discord
from discord.ext import commands
from utils.embeds import luxury_embed
from utils.config import STAFF_ROLES, COLOR_DANGER, COLOR_GOLD
from utils.state import WARN_DATA, WARN_LOGS

class WarnSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_staff_level(self, member):
        for i, role in enumerate(STAFF_ROLES):
            if discord.utils.get(member.roles, name=role):
                return i + 1
        return 0

    @commands.command()
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        staff_level = self.get_staff_level(ctx.author)

        if staff_level < 1:
            await ctx.send("❌ You are not authorized to issue warnings.")
            return

        user_id = member.id
        WARN_DATA[user_id] = WARN_DATA.get(user_id, 0) + 1
        WARN_LOGS.setdefault(user_id, []).append(reason)

        warns = WARN_DATA[user_id]

        try:
            await member.send(
                embed=luxury_embed(
                    title="⚠️ Official Warning Issued",
                    description=f"**Reason:** {reason}\n\nPlease follow server rules.",
                    color=COLOR_DANGER
                )
            )
        except:
            pass

        await ctx.send(
            embed=luxury_embed(
                title="⚠️ Warning Recorded",
                description=f"{member.mention} now has **{warns} warning(s)**.",
                color=COLOR_GOLD
            )
        )

        # AUTO ESCALATION
        if warns == 3 and staff_level >= 2:
            await member.timeout(discord.utils.utcnow().replace(hour=0) + discord.timedelta(hours=24))
            await ctx.send(f"⏳ {member.mention} timed out for **24 hours**.")

        elif warns == 4 and staff_level >= 3:
            await member.kick(reason="Exceeded warning limit")
            await ctx.send(f"🚫 {member} kicked due to repeated warnings.")

        elif warns >= 5 and staff_level >= 4:
            await member.ban(reason="Exceeded warning limit")
            await ctx.send(f"⛔ {member} banned due to repeated warnings.")

async def setup(bot):
    await bot.add_cog(WarnSystem(bot))
