import discord
from discord.ext import commands

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY
from utils import state


WELCOME_GIF_URL = (
    "https://raw.githubusercontent.com/yesh0092/hellfire-bot/main/welcome%20hell.mp4"
)

# =====================================================
# ONBOARDING VIEW
# =====================================================

class OnboardingView(discord.ui.View):
    def __init__(self, bot: commands.Bot, member: discord.Member):
        super().__init__(timeout=120)
        self.bot = bot
        self.member = member

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(
                "❌ This onboarding session is not for you.",
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        # Auto-clean expired onboarding panel
        msg_id = state.ONBOARDING_MESSAGES.pop(self.member.id, None)
        if not msg_id:
            return

        try:
            channel = self.member.dm_channel or await self.member.create_dm()
            msg = await channel.fetch_message(msg_id)
            await msg.delete()
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass

    async def finalize(self, interaction: discord.Interaction):
        msg_id = state.ONBOARDING_MESSAGES.pop(self.member.id, None)

        if msg_id:
            try:
                msg = await interaction.channel.fetch_message(msg_id)
                await msg.delete()
            except (discord.NotFound, discord.Forbidden):
                pass

        await interaction.response.send_message(
            embed=luxury_embed(
                title="✅ Onboarding Complete",
                description=(
                    "Welcome to **HellFire Hangout**.\n\n"
                    "Your access is now fully active.\n"
                    "If you ever need assistance, simply type **support**."
                ),
                color=COLOR_GOLD
            ),
            ephemeral=True
        )

        self.stop()

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
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -------------------------------------
    # MEMBER JOIN
    # -------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # ---------------- AUTO ROLE ----------------
        if state.AUTO_ROLE_ID:
            role = guild.get_role(state.AUTO_ROLE_ID)
            if role:
                try:
                    await member.add_roles(role, reason="Automatic onboarding role")
                except discord.Forbidden:
                    pass

        # ---------------- SERVER WELCOME ----------------
        if state.WELCOME_CHANNEL_ID:
            channel = guild.get_channel(state.WELCOME_CHANNEL_ID)
            if channel:
                embed = luxury_embed(
                    title="🔥 Welcome to HellFire Hangout",
                    description=(
                        f"{member.mention}\n\n"
                        "You’ve joined a community built around **quality discussion**, "
                        "**reliable support**, and **a premium experience**."
                    ),
                    color=COLOR_GOLD
                )

                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_image(url=WELCOME_GIF_URL)

                await channel.send(embed=embed)

        # ---------------- DM ONBOARDING ----------------
        try:
            welcome = luxury_embed(
                title="Welcome",
                description=(
                    "We’re glad to have you here.\n\n"
                    "This server values respect, clarity, and meaningful interaction.\n"
                    "Whenever you need help, simply type **support**."
                ),
                color=COLOR_SECONDARY
            )

            welcome.set_thumbnail(url=member.display_avatar.url)
            welcome.set_image(url=WELCOME_GIF_URL)

            await member.send(embed=welcome)

            inquiry = luxury_embed(
                title="Quick Question",
                description=(
                    "How did you discover **HellFire Hangout**?\n\n"
                    "Your response helps us improve our outreach."
                ),
                color=COLOR_SECONDARY
            )

            inquiry.set_thumbnail(url=member.display_avatar.url)

            msg = await member.send(
                embed=inquiry,
                view=OnboardingView(self.bot, member)
            )

            state.ONBOARDING_MESSAGES[member.id] = msg.id

        except (discord.Forbidden, discord.HTTPException):
            pass

    # -------------------------------------
    # EXTERNAL DM HANDLER (CALLED FROM MAIN)
    # -------------------------------------

    async def handle_dm(self, message: discord.Message):
        """
        Called safely from main.py for DM-only logic.
        """
        user_id = message.author.id

        # Manual onboarding completion via text
        if user_id in state.ONBOARDING_MESSAGES:
            try:
                msg = await message.channel.fetch_message(
                    state.ONBOARDING_MESSAGES.pop(user_id)
                )
                await msg.delete()
            except (discord.NotFound, discord.Forbidden):
                pass

            await message.channel.send(
                embed=luxury_embed(
                    title="✅ Onboarding Complete",
                    description=(
                        "Thank you for the response.\n\n"
                        "You’re all set — enjoy your time in **HellFire Hangout**.\n"
                        "Type **support** anytime if you need assistance."
                    ),
                    color=COLOR_GOLD
                )
            )

        # Forward support keyword
        if message.content.lower().strip() == "support":
            support_cog = self.bot.get_cog("Support")
            if support_cog and hasattr(support_cog, "handle_dm"):
                await support_cog.handle_dm(message)


# =====================================================
# SETUP
# =====================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Onboarding(bot))
