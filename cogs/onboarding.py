import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY
from utils import state


# =====================================================
# ONBOARDING VIEW
# =====================================================

class OnboardingView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__(timeout=120)
        self.member = member

    async def finalize(self, interaction: discord.Interaction):
        msg_id = state.ONBOARDING_MESSAGES.pop(self.member.id, None)

        if msg_id:
            try:
                msg = await interaction.channel.fetch_message(msg_id)
                await msg.delete()
            except:
                pass

        await interaction.response.send_message(
            embed=luxury_embed(
                title="✨ Onboarding Complete",
                description=(
                    "Thank you for joining **Hellfire Hangout**.\n\n"
                    "You are now fully integrated into our premium ecosystem.\n"
                    "Support is always available via DM by typing `support`."
                ),
                color=COLOR_GOLD
            ),
            ephemeral=True
        )

    @discord.ui.button(label="Friends", emoji="👥", style=discord.ButtonStyle.primary)
    async def friends(self, interaction: discord.Interaction, _):
        await self.finalize(interaction)

    @discord.ui.button(label="Social Media", emoji="📱", style=discord.ButtonStyle.secondary)
    async def social(self, interaction: discord.Interaction, _):
        await self.finalize(interaction)

    @discord.ui.button(label="Other", emoji="🌐", style=discord.ButtonStyle.success)
    async def other(self, interaction: discord.Interaction, _):
        await self.finalize(interaction)


# =====================================================
# ONBOARDING COG
# =====================================================

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------------------
    # MEMBER JOIN
    # -------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # Autorole
        if state.AUTO_ROLE_ID:
            role = guild.get_role(state.AUTO_ROLE_ID)
            if role:
                try:
                    await member.add_roles(role)
                except:
                    pass

        # Welcome channel message
        if state.WELCOME_CHANNEL_ID:
            channel = guild.get_channel(state.WELCOME_CHANNEL_ID)
            if channel:
                await channel.send(
                    embed=luxury_embed(
                        title="🔥 Welcome to Hellfire Hangout",
                        description=(
                            f"{member.mention} has entered our premium domain.\n\n"
                            "A realm of elite discussion, support, and experience awaits ✨"
                        ),
                        color=COLOR_GOLD
                    )
                )

        # DM onboarding
        try:
            await member.send(
                embed=luxury_embed(
                    title="🌙 Welcome to Hellfire Hangout",
                    description=(
                        "You’ve joined an exclusive sanctuary of premium conversation.\n\n"
                        "At any time, type `support` here to reach our elite concierge.\n\n"
                        "Before you begin — may we ask one thing?"
                    ),
                    color=COLOR_SECONDARY
                )
            )

            msg = await member.send(
                embed=luxury_embed(
                    title="🌌 Discovery Inquiry",
                    description=(
                        "How did you discover **Hellfire Hangout**?\n\n"
                        "Your insight helps us refine our invitation process ✨"
                    ),
                    color=COLOR_SECONDARY
                ),
                view=OnboardingView(member)
            )

            state.ONBOARDING_MESSAGES[member.id] = msg.id

        except:
            pass

    # -------------------------------------
    # DM HANDLER (SUPPORT + ONBOARDING CLEANUP)
    # -------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # DM only
        if not isinstance(message.channel, discord.DMChannel):
            return

        # Cleanup onboarding if user replies manually
        if message.author.id in state.ONBOARDING_MESSAGES:
            try:
                msg = await message.channel.fetch_message(
                    state.ONBOARDING_MESSAGES.pop(message.author.id)
                )
                await msg.delete()
            except:
                pass

            await message.channel.send(
                embed=luxury_embed(
                    title="✨ Onboarding Complete",
                    description=(
                        "Thank you for your response.\n\n"
                        "You’re now fully settled into **Hellfire Hangout**.\n"
                        "Support is always available by typing `support` ✨"
                    ),
                    color=COLOR_GOLD
                )
            )

        # Forward support keyword to support cog
        if message.content.lower() == "support":
            support_cog = self.bot.get_cog("Support")
            if support_cog:
                await support_cog.on_message(message)


async def setup(bot):
    await bot.add_cog(Onboarding(bot))
