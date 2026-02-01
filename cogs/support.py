import discord
import asyncio
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import (
    SUPPORT_CATEGORY_NAME,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_GOLD,
    COLOR_DANGER
)
from utils import state


# =====================================================
# CONFIG
# =====================================================

DM_PANEL_EXPIRY = timedelta(minutes=5)


# =====================================================
# CLOSE TICKET VIEW
# =====================================================

class CloseTicketView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if (
            interaction.user.id != self.owner_id
            and not interaction.user.guild_permissions.manage_channels
        ):
            await interaction.response.send_message(
                embed=luxury_embed(
                    title="❌ Permission Denied",
                    description="Only the ticket owner or staff may close this ticket.",
                    color=COLOR_DANGER
                ),
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(
            embed=luxury_embed(
                title="🔒 Ticket Closed",
                description="This ticket will close shortly.",
                color=COLOR_SECONDARY
            ),
            ephemeral=True
        )

        state.OPEN_TICKETS.pop(self.owner_id, None)
        state.TICKET_META.pop(interaction.channel.id, None)

        await asyncio.sleep(3)
        try:
            await interaction.channel.delete()
        except (discord.Forbidden, discord.NotFound):
            pass


# =====================================================
# SUPPORT VIEW (DM PANEL)
# =====================================================

class SupportView(discord.ui.View):
    def __init__(self, user: discord.User, message_id: int):
        super().__init__(timeout=180)
        self.user = user
        self.message_id = message_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ This support panel is not for you.",
                ephemeral=True
            )
            return False
        return True

    def clear_session(self):
        state.DM_SUPPORT_SESSIONS.pop(self.user.id, None)

    async def on_timeout(self):
        """
        Edit the panel when it expires instead of deleting it
        """
        self.clear_session()

        try:
            channel = self.user.dm_channel or await self.user.create_dm()
            msg = await channel.fetch_message(self.message_id)

            await msg.edit(
                embed=luxury_embed(
                    title="⏳ Support Session Expired",
                    description=(
                        "This support panel is no longer active.\n\n"
                        "Please send **any message** again to open a new support session."
                    ),
                    color=COLOR_SECONDARY
                ),
                view=None
            )
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass

    # ---------------- CREATE TICKET ----------------

    @discord.ui.button(label="Create Ticket", emoji="🎟️", style=discord.ButtonStyle.primary)
    async def open_ticket(self, interaction: discord.Interaction, _):
        self.clear_session()

        guild = interaction.client.get_guild(state.MAIN_GUILD_ID)
        if not guild:
            return await interaction.response.send_message(
                embed=luxury_embed(
                    title="⚙️ System Unavailable",
                    description="Support is currently unavailable.",
                    color=COLOR_SECONDARY
                ),
                ephemeral=True
            )

        if self.user.id in state.OPEN_TICKETS:
            return await interaction.response.send_message(
                embed=luxury_embed(
                    title="⏳ Ticket Already Open",
                    description="You already have an active support ticket.",
                    color=COLOR_SECONDARY
                ),
                ephemeral=True
            )

        category = discord.utils.get(guild.categories, name=SUPPORT_CATEGORY_NAME)
        if not category:
            try:
                category = await guild.create_category(SUPPORT_CATEGORY_NAME)
            except discord.Forbidden:
                return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            self.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        for role in guild.roles:
            if role.name.startswith("Staff"):
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                )

        channel = await guild.create_text_channel(
            f"ticket-{self.user.name}",
            category=category,
            overwrites=overwrites
        )

        state.OPEN_TICKETS[self.user.id] = channel.id

        panel = await channel.send(
            embed=luxury_embed(
                title="🌙 Support Ticket",
                description=(
                    f"**User:** {self.user.mention}\n"
                    "**Status:** 🟡 Awaiting Staff\n\n"
                    "Please describe your issue below."
                ),
                color=COLOR_GOLD
            ),
            view=CloseTicketView(self.user.id)
        )

        state.TICKET_META[channel.id] = {
            "owner": self.user.id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "panel_id": panel.id
        }

        await interaction.response.send_message(
            embed=luxury_embed(
                title="✅ Ticket Created",
                description="Your support ticket has been opened successfully.",
                color=COLOR_GOLD
            ),
            ephemeral=True
        )

    # ---------------- CANCEL ----------------

    @discord.ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, _):
        self.clear_session()
        await interaction.response.edit_message(
            content="Support request cancelled.",
            embed=None,
            view=None
        )


# =====================================================
# SUPPORT COG
# =====================================================

class Support(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        state.DM_SUPPORT_SESSIONS = getattr(state, "DM_SUPPORT_SESSIONS", {})

    async def cog_load(self):
        self.ticket_watcher.start()

    def cog_unload(self):
        self.ticket_watcher.cancel()

    # ---------------- DM HANDLER ----------------
    # ANY MESSAGE IN DM TRIGGERS SUPPORT (ONCE)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not isinstance(message.channel, discord.DMChannel):
            return

        user_id = message.author.id
        now = datetime.utcnow()

        session = state.DM_SUPPORT_SESSIONS.get(user_id)

        # Active panel still valid → do nothing
        if session and now - session["created_at"] < DM_PANEL_EXPIRY:
            return

        # Send new panel
        panel_msg = await message.channel.send(
            embed=luxury_embed(
                title="🛎️ HellFire Hangout Support",
                description=(
                    "Please choose how you’d like to proceed.\n\n"
                    "⏳ This panel will expire in **5 minutes**."
                ),
                color=COLOR_PRIMARY
            )
        )

        view = SupportView(message.author, panel_msg.id)
        await panel_msg.edit(view=view)

        state.DM_SUPPORT_SESSIONS[user_id] = {
            "message_id": panel_msg.id,
            "created_at": now
        }

    # ---------------- AUTO CLOSE TICKETS ----------------

    @tasks.loop(minutes=10)
    async def ticket_watcher(self):
        now = datetime.utcnow()

        for channel_id, meta in list(state.TICKET_META.items()):
            if now - meta["last_activity"] > timedelta(hours=24):
                channel = self.bot.get_channel(channel_id)
                if channel:
                    try:
                        await channel.send(
                            embed=luxury_embed(
                                title="⏳ Ticket Closed",
                                description="Closed due to inactivity.",
                                color=COLOR_SECONDARY
                            )
                        )
                        await asyncio.sleep(2)
                        await channel.delete()
                    except (discord.Forbidden, discord.NotFound):
                        pass

                state.TICKET_META.pop(channel_id, None)
                state.OPEN_TICKETS.pop(meta["owner"], None)

    @ticket_watcher.before_loop
    async def before_watcher(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Support(bot))
