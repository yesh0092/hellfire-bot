import discord
from discord.ext import commands
import asyncio
import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils import state

# =====================================================
# CONFIGURATION & ASSETS
# =====================================================

WELCOME_GIF_URL = (
    "https://raw.githubusercontent.com/yesh0092/hellfire-bot/main/welcome%20hell.mp4"
)
ANIME_DIVIDER = "╰─────── •『 🔥 』• ───────╯"
ANIME_BULLET = "🏮"

# =====================================================
# MODALS (THE CHARACTER CREATOR)
# =====================================================

class NicknameModal(discord.ui.Modal, title="Character Registration"):
    name_input = discord.ui.TextInput(
        label="What is your name/alias?",
        placeholder="Enter your hero name...",
        min_length=2,
        max_length=32
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.user.edit(nick=self.name_input.value)
            await interaction.response.send_message(
                f"✨ Your identity has been updated to **{self.name_input.value}**!", 
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have power over your name (Permissions), but I've recorded it!", 
                ephemeral=True
            )

# =====================================================
# ONBOARDING VIEW (THE MULTI-STAGE JOURNEY)
# =====================================================

class OnboardingView(discord.ui.View):
    def __init__(self, bot: commands.Bot, member: discord.Member):
        super().__init__(timeout=300)  # Extended timeout for the long journey
        self.bot = bot
        self.member = member
        self.stage = 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(
                "🏮 **Halt!** This destiny is not yours to claim.",
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        msg_id = state.ONBOARDING_MESSAGES.pop(self.member.id, None)
        if not msg_id:
            return

        try:
            channel = self.member.dm_channel
            if not channel:
                return
            msg = await channel.fetch_message(msg_id)
            await msg.delete()
        except:
            pass

    async def finalize(self, interaction: discord.Interaction, discovery_source: str):
        """Final stage of the anime onboarding"""
        msg_id = state.ONBOARDING_MESSAGES.pop(self.member.id, None)

        try:
            if msg_id:
                await interaction.message.delete()
        except:
            pass

        # Ultimate Final Embed
        final_embed = luxury_embed(
            title="✨ A Legend Has Arrived",
            description=(
                f"**Welcome to the Inner Circle, {self.member.name}!**\n"
                f"{ANIME_DIVIDER}\n"
                f"{ANIME_BULLET} **Access Level:** `LEGENDARY`\n"
                f"{ANIME_BULLET} **Path Chosen:** `{discovery_source}`\n"
                f"{ANIME_BULLET} **Status:** `Active`\n\n"
                "Go forth and leave your mark on **HellFire Hangout**. "
                "The community awaits your presence."
            ),
            color=COLOR_GOLD
        )
        final_embed.set_image(url=WELCOME_GIF_URL)
        final_embed.set_footer(text="Type 'support' anytime to open the gates of help.")

        await interaction.response.send_message(embed=final_embed, ephemeral=True)
        self.stop()

    # --- STAGE 1 BUTTONS: DISCOVERY ---

    @discord.ui.button(label="Friends", style=discord.ButtonStyle.primary, emoji="🤝", row=0)
    async def friends(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.finalize(interaction, "Fellow Travelers")

    @discord.ui.button(label="Social Media", style=discord.ButtonStyle.secondary, emoji="🌐", row=0)
    async def social(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.finalize(interaction, "Ancient Prophecy")

    @discord.ui.button(label="Other", style=discord.ButtonStyle.success, emoji="🔮", row=0)
    async def other(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.finalize(interaction, "Fate & Chaos")

    # --- STAGE 2 TOOLS: CHARACTER CUSTOMIZATION ---

    @discord.ui.button(label="Set Nickname", style=discord.ButtonStyle.gray, emoji="✍️", row=1)
    async def set_nick(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NicknameModal())

    @discord.ui.button(label="Age: 18+", style=discord.ButtonStyle.danger, emoji="🔞", row=1)
    async def age_verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        button.label = "Verified"
        await interaction.response.edit_message(view=self)
        await interaction.followup.send("Identity verified. Access to restricted areas granted.", ephemeral=True)


# =====================================================
# ONBOARDING COG (ULTIMATE EDITION)
# =====================================================

class Onboarding(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # State Initialization
        if not hasattr(state, "ONBOARDING_MESSAGES"):
            state.ONBOARDING_MESSAGES = {}
        
        if not hasattr(state, "TOTAL_JOINS"):
            state.TOTAL_JOINS = 0

    # =====================================================
    # UTILITY: ANIME STYLING
    # =====================================================

    def get_join_card_description(self, member: discord.Member, count: int):
        return (
            f"### {ANIME_BULLET} A New Soul Has Awakened\n"
            f"{ANIME_DIVIDER}\n"
            f"**Hero:** {member.mention}\n"
            f"**Soul Rank:** `#{count}`\n"
            f"**Joined:** <t:{int(datetime.datetime.now().timestamp())}:R>\n\n"
            f"> *“In the heart of the HellFire, only the strongest bonds are forged. "
            f"Prepare for a journey beyond the ordinary.”*\n"
            f"{ANIME_DIVIDER}"
        )

    # =====================================================
    # MEMBER JOIN EVENT
    # =====================================================

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return

        guild = member.guild
        state.TOTAL_JOINS += 1
        
        # ---------- AUTO ROLE ----------
        if hasattr(state, "AUTO_ROLE_ID") and state.AUTO_ROLE_ID:
            role = guild.get_role(state.AUTO_ROLE_ID)
            if role:
                try:
                    await member.add_roles(role, reason="Anime Onboarding: Initiation")
                except discord.Forbidden:
                    print(f"Failed to add role to {member.name}: Missing Permissions")

        # ---------- SERVER WELCOME (MAIN CHANNEL) ----------
        if hasattr(state, "WELCOME_CHANNEL_ID") and state.WELCOME_CHANNEL_ID:
            channel = guild.get_channel(state.WELCOME_CHANNEL_ID)
            if channel:
                embed = luxury_embed(
                    title="🔥 HELLFIRE ARRIVAL 🔥",
                    description=self.get_join_card_description(member, state.TOTAL_JOINS),
                    color=COLOR_GOLD
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_image(url=WELCOME_GIF_URL)
                embed.set_footer(text=f"Server Population: {guild.member_count} Warriors")

                try:
                    await channel.send(f"Welcome to the realm, {member.mention}!", embed=embed)
                except:
                    pass

        # ---------- DM ONBOARDING (PHASED INTRODUCTION) ----------
        try:
            if member.id in state.ONBOARDING_MESSAGES:
                return

            # Phase 1: The Visual Intro
            intro_embed = luxury_embed(
                title="🏮 THE PROLOGUE",
                description=(
                    f"Greetings, **{member.name}**.\n\n"
                    "You have crossed the threshold into **HellFire Hangout**.\n"
                    "Before the gates fully open, we must document your origin.\n\n"
                    "**Server Laws:**\n"
                    f"{ANIME_BULLET} Absolute Respect\n"
                    f"{ANIME_BULLET} High-Tier Quality\n"
                    f"{ANIME_BULLET} Elite Discussion"
                ),
                color=COLOR_SECONDARY
            )
            intro_embed.set_image(url=WELCOME_GIF_URL)
            await member.send(embed=intro_embed)

            # Phase 2: The Character Sheet (View)
            inquiry = luxury_embed(
                title="📜 CHARACTER REGISTRATION",
                description=(
                    "Help us refine your destiny. \n\n"
                    "**1.** Set your nickname if you wish.\n"
                    "**2.** Verify your age for restricted scrolls.\n"
                    "**3.** Tell us how you found this domain.\n\n"
                    f"*You have 5 minutes before this scroll burns away.*"
                ),
                color=COLOR_SECONDARY
            )
            inquiry.set_thumbnail(url=guild.icon.url if guild.icon else None)

            view = OnboardingView(self.bot, member)
            msg = await member.send(embed=inquiry, view=view)

            state.ONBOARDING_MESSAGES[member.id] = msg.id

        except (discord.Forbidden, discord.HTTPException):
            if hasattr(state, "BOT_LOG_CHANNEL_ID") and state.BOT_LOG_CHANNEL_ID:
                log_chan = guild.get_channel(state.BOT_LOG_CHANNEL_ID)
                if log_chan:
                    await log_chan.send(f"⚠️ Could not send onboarding DM to {member.mention} (DMs Closed).")

    # =====================================================
    # DM HANDLER (ULTIMATE COMMAND SYNC)
    # =====================================================

    async def handle_dm(self, message: discord.Message):
        user_id = message.author.id

        # Auto-Close Onboarding on any DM response
        if user_id in state.ONBOARDING_MESSAGES:
            try:
                msg_id = state.ONBOARDING_MESSAGES.pop(user_id)
                msg = await message.channel.fetch_message(msg_id)
                await msg.delete()
            except:
                pass

            success_embed = luxury_embed(
                title="✅ JOURNEY UPDATED",
                description=(
                    "Your message has been received by the archives.\n"
                    "You are now a full member of the community.\n\n"
                    "**Go forth, Hero!**"
                ),
                color=COLOR_GOLD
            )
            await message.channel.send(embed=success_embed)

        # Keyword Detection: Support
        if message.content.lower().strip() == "support":
            support_cog = self.bot.get_cog("Support")
            if support_cog and hasattr(support_cog, "handle_dm"):
                await support_cog.handle_dm(message)
        
        # Keyword Detection: Help/Commands
        elif message.content.lower().strip() == "help":
            help_embed = luxury_embed(
                title="🏮 HELLFIRE COMMANDS",
                description="Type `support` to contact staff.\nType `!onboard` in the server to restart your journey.",
                color=COLOR_SECONDARY
            )
            await message.channel.send(embed=help_embed)

    # =====================================================
    # ADMIN COMMANDS
    # =====================================================

    @commands.command(name="joinstats")
    @commands.has_permissions(administrator=True)
    async def joinstats(self, ctx):
        """Shows onboarding statistics"""
        count = getattr(state, "TOTAL_JOINS", 0)
        active = len(state.ONBOARDING_MESSAGES)
        
        embed = luxury_embed(
            title="📊 Recruitment Statistics",
            description=(
                f"**Total Souls Recruited:** `{count}`\n"
                f"**Active Onboardings:** `{active}`"
            ),
            color=COLOR_GOLD
        )
        await ctx.send(embed=embed)

    @commands.command(name="forceonboard")
    @commands.has_permissions(moderate_members=True) # FIXED: Changed from manage_members
    async def forceonboard(self, ctx, member: discord.Member):
        """Manual trigger for onboarding"""
        await self.on_member_join(member)
        await ctx.send(f"✅ Initiation sequence restarted for {member.mention}.")

# =====================================================
# SETUP
# =====================================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Onboarding(bot))
