import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY
from utils import state


WELCOME_GIF_URL = "https://github.com/yesh0092/hellfire-bot/blob/916d3f67d1ec0c98ff7d2072165beda0b8544834/welcome%20hell.mp4"


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
                title="Onboarding Complete",
                description=(
                    "Welcome aboard.\n\n"
                    "Your access to **Hellfire Hangout** is now fully active.\n"
                    "If you ever need assistance, simply type `support` here."
                ),
                color=COLOR_GOLD
            ),
            ephemeral=True
        )

    @discord.ui.button(label="Friends", style=discord.ButtonStyle.primary)
    async def friends(self, interaction: discord.Interaction, _):
        await self.finalize(interaction)

    @discord.ui.button(label="Social Media", style=discord.ButtonStyle.secondary)
    async def social(self, interaction: discord.Interaction, _):
        await self.finalize(interaction)

    @discord.ui.button(label="Other", style=discord.ButtonStyle.success)
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

        # ---------------- WELCOME CHANNEL ----------------

        if state.WELCOME_CHANNEL_ID:
            channel = guild.get_channel(state.WELCOME_CHANNEL_ID)
            if channel:
                embed = luxury_embed(
                    title="Welcome to Hellfire Hangout",
                    description=(
                        f"{member.mention}\n\n"
                        "You’ve joined a space built for quality discussion, support, "
                        "and a premium community experience."
                    ),
                    color=COLOR_GOLD
                )

                embed.set_image(url=WELCOME_GIF_URL)
                embed.set_thumbnail(url=member.display_avatar.url)

                await channel.send(embed=embed)

        # ---------------- DM WELCOME ----------------

        try:
            embed = luxury_embed(
                title="Welcome",
                description=(
                    "We’re glad to have you here.\n\n"
                    "This server is designed for focused conversation and quality support.\n"
                    "Whenever you need help, just type `support`."
                ),
                color=COLOR_SECONDARY
            )

            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_image(url=WELCOME_GIF_URL)

            await member.send(embed=embed)

            inquiry = luxury_embed(
                title="Quick Question",
                description=(
                    "How did you discover **Hellfire Hangout**?\n\n"
                    "Your response helps us improve our reach."
                ),
                color=COLOR_SECONDARY
            )

            inquiry.set_thumbnail(url=member.display_avatar.url)

            msg = await member.send(
                embed=inquiry,
                view=OnboardingView(member)
            )

            state.ONBOARDING_MESSAGES[member.id] = msg.id

        except:
            pass

    # -------------------------------------
    # DM HANDLER (ONBOARDING CLEANUP + SUPPORT)
    # -------------------------------------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

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
                    title="Onboarding Complete",
                    description=(
                        "Thanks for the response.\n\n"
                        "You’re all set. Enjoy your time in **Hellfire Hangout**.\n"
                        "Type `support` anytime if you need assistance."
                    ),
                    color=COLOR_GOLD
                )
            )

        # Forward support keyword
        if message.content.lower() == "support":
            support_cog = self.bot.get_cog("Support")
            if support_cog:
                await support_cog.on_message(message)


async def setup(bot):
    await bot.add_cog(Onboarding(bot))

