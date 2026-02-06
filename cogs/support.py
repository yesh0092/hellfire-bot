import discord
import asyncio
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from utils.embeds import luxury_embed
from utils.config import (
    SUPPORT_CATEGORY_NAME,
    COLOR_GOLD,
    COLOR_SECONDARY,
    COLOR_DANGER
)
from utils import state


# =====================================================
# CONFIG
# =====================================================

DM_PANEL_EXPIRY = timedelta(minutes=5)
TICKET_INACTIVITY_LIMIT = timedelta(hours=24)
STAFF_ROLE_NAMES = ("Staff", "Staff+", "Staff++", "Staff+++")


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
                    description="Only the ticket owner or staff can close this ticket.",
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
                title="🔒 Ticket Closing",
                description="This ticket will be closed shortly.",
                color=COLOR_SECONDARY
            ),
            ephemeral=True
        )

        owner_id = state.TICKET_META.get(interaction.channel.id, {}).get("owner")

        state.TICKET_META.pop(interaction.channel.id, None)
        if owner_id:
            state.OPEN_TICKETS.pop(owner_id, None)

        await asyncio.sleep(3)
        try:
            await interaction.channel.delete()
        except (discord.Forbidden, discord.NotFound):
            pass


# =====================================================
# DM SUPPORT PANEL VIEW (WITH CANCEL)
# =====================================================

class SupportView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=300)
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ This panel is not for you.",
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        state.DM_SUPPORT_SESSIONS.pop(self.user.id, None)

    # ---------- CREATE TICKET ----------
    @discord.ui.button(label="Create Ticket", emoji="🎟️", style=discord.ButtonStyle.primary)
    async def create_ticket(self, interaction: discord.Interaction, _):
        state.DM_SUPPORT_SESSIONS.pop(self.user.id, None)

        if self.user.id in state.OPEN_TICKETS:
            return await interaction.response.send_message(
                embed=luxury_embed(
                    title="⏳ Ticket Already Open",
                    description="You already have an active support ticket.",
                    color=COLOR_SECONDARY
                ),
                ephemeral=True
            )

        guild = interaction.client.get_guild(state.MAIN_GUILD_ID)
        if not guild:
            return await interaction.response.send_message(
                embed=luxury_embed(
                    title="⚠️ System Error",
                    description="Support system is not linked to a server.",
                    color=COLOR_DANGER
                ),
                ephemeral=True
            )

        category = discord.utils.get(guild.categories, name=SUPPORT_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(SUPPORT_CATEGORY_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            self.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        for role in guild.roles:
            if role.name in STAFF_ROLE_NAMES:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True
                )

        channel = await guild.create_text_channel(
            name=f"ticket-{self.user.name}",
            category=category,
            overwrites=overwrites
        )

        state.OPEN_TICKETS[self.user.id] = channel.id

        panel = await channel.send(
            embed=luxury_embed(
                title="🌙 Support Ticket Opened",
                description=(
                    f"👤 **User:** {self.user.mention}\n"
                    "🟡 **Status:** Waiting for staff\n\n"
                    "Please describe your issue clearly."
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
                description="Your support ticket has been created.",
                color=COLOR_GOLD
            ),
            ephemeral=True
        )

    # ---------- CANCEL ----------
    @discord.ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, _):
        state.DM_SUPPORT_SESSIONS.pop(self.user.id, None)

        await interaction.response.edit_message(
            embed=luxury_embed(
                title="❌ Support Cancelled",
                description="Your support request has been cancelled.",
                color=COLOR_SECONDARY
            ),
            view=None
        )


# =====================================================
# SUPPORT COG
# =====================================================

class Support(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        state.OPEN_TICKETS = getattr(state, "OPEN_TICKETS", {})
        state.TICKET_META = getattr(state, "TICKET_META", {})
        state.DM_SUPPORT_SESSIONS = getattr(state, "DM_SUPPORT_SESSIONS", {})

    async def cog_load(self):
        self.ticket_watcher.start()

    def cog_unload(self):
        self.ticket_watcher.cancel()

    # ---------------- DM ENTRY POINT ----------------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not isinstance(message.channel, discord.DMChannel):
            return

        user_id = message.author.id
        now = datetime.utcnow()

        last = state.DM_SUPPORT_SESSIONS.get(user_id)
        if last and now - last < DM_PANEL_EXPIRY:
            return

        msg = await message.channel.send(
            embed=luxury_embed(
                title="🛎️ HellFire Hangout Support",
                description=(
                    "Choose how you want to proceed.\n\n"
                    "⏳ Panel expires in **5 minutes**."
                ),
                color=COLOR_GOLD
            ),
            view=SupportView(message.author)
        )

        state.DM_SUPPORT_SESSIONS[user_id] = now

    # ---------------- AUTO CLOSE ----------------

    @tasks.loop(minutes=10)
    async def ticket_watcher(self):
        now = datetime.utcnow()

        for channel_id, meta in list(state.TICKET_META.items()):
            if now - meta["last_activity"] > TICKET_INACTIVITY_LIMIT:
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
