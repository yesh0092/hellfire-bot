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
# CLOSE TICKET VIEW
# =====================================================

class CloseTicketView(discord.ui.View):
    def __init__(self, bot, owner_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.owner_id = owner_id

    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (
            interaction.user.id != self.owner_id
            and not interaction.user.guild_permissions.administrator
        ):
            await interaction.response.send_message(
                embed=luxury_embed(
                    title="❌ Permission Denied",
                    description="Only the ticket owner or staff may close this ticket.",
                    color=COLOR_DANGER
                ),
                ephemeral=True
            )
            return

        button.disabled = True
        await interaction.message.edit(view=self)

        await interaction.response.send_message(
            embed=luxury_embed(
                title="🔒 Ticket Closed",
                description="This ticket has been closed successfully.",
                color=COLOR_SECONDARY
            )
        )

        state.OPEN_TICKETS.pop(self.owner_id, None)
        state.TICKET_META.pop(interaction.channel.id, None)

        await asyncio.sleep(3)
        await interaction.channel.delete()


# =====================================================
# SUPPORT VIEW (DM PANEL)
# =====================================================

class SupportView(discord.ui.View):
    def __init__(self, bot, user: discord.User):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user

    def clear_dm_session(self):
        state.DM_SUPPORT_ACTIVE.discard(self.user.id)

    # ---------------- CREATE TICKET ----------------

    @discord.ui.button(label="Create Ticket", emoji="🎟️", style=discord.ButtonStyle.primary)
    async def open_ticket(self, interaction: discord.Interaction, _):
        self.clear_dm_session()

        guild = self.bot.get_guild(state.MAIN_GUILD_ID)
        if not guild:
            await interaction.response.send_message(
                embed=luxury_embed(
                    title="⚙️ System Unavailable",
                    description="Support is not available right now.",
                    color=COLOR_SECONDARY
                ),
                ephemeral=True
            )
            return

        if self.user.id in state.TICKET_BANNED_USERS:
            await interaction.response.send_message(
                embed=luxury_embed(
                    title="🚫 Access Restricted",
                    description="You are not permitted to open tickets.",
                    color=COLOR_DANGER
                ),
                ephemeral=True
            )
            return

        if self.user.id in state.OPEN_TICKETS:
            await interaction.response.send_message(
                embed=luxury_embed(
                    title="⏳ Ticket Already Open",
                    description="You already have an active ticket.",
                    color=COLOR_SECONDARY
                ),
                ephemeral=True
            )
            return

        category = discord.utils.get(
            guild.categories, name=SUPPORT_CATEGORY_NAME
        ) or await guild.create_category(SUPPORT_CATEGORY_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            self.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

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
                    "**Status:** 🟡 Awaiting Staff\n"
                    "**Priority:** 🟢 Normal\n\n"
                    "Please describe your issue below."
                ),
                color=COLOR_GOLD
            ),
            view=CloseTicketView(self.bot, self.user.id)
        )

        state.TICKET_META[channel.id] = {
            "owner": self.user.id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "status": "waiting_staff",
            "priority": "normal",
            "panel_id": panel.id
        }

        await interaction.response.send_message(
            embed=luxury_embed(
                title="✅ Ticket Created",
                description="Your support ticket is now open.",
                color=COLOR_GOLD
            ),
            ephemeral=True
        )

    # ---------------- PERSONAL ASSISTANCE ----------------

    @discord.ui.button(label="Personal Assistance", emoji="👑", style=discord.ButtonStyle.secondary)
    async def vip(self, interaction: discord.Interaction, _):
        self.clear_dm_session()

        await interaction.response.send_message(
            embed=luxury_embed(
                title="🛎️ Request Submitted",
                description="A senior staff member will contact you shortly.",
                color=COLOR_GOLD
            ),
            ephemeral=True
        )

        guild = self.bot.get_guild(state.MAIN_GUILD_ID)
        if not guild:
            return

        log_channel = guild.get_channel(
            state.SUPPORT_LOG_CHANNEL_ID or state.BOT_LOG_CHANNEL_ID
        )
        if log_channel:
            await log_channel.send(
                embed=luxury_embed(
                    title="👑 VIP Assistance Request",
                    description=(
                        f"**User:** {self.user.mention}\n"
                        f"**ID:** `{self.user.id}`\n"
                        "**Priority:** 🔴 High"
                    ),
                    color=COLOR_GOLD
                )
            )

    # ---------------- CANCEL ----------------

    @discord.ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _):
        self.clear_dm_session()

        # EDIT SAME MESSAGE → remove embed, buttons, footer
        await interaction.message.edit(
            content="Ticket creation cancelled.",
            embed=None,
            view=None
        )

        # Required interaction acknowledgement
        await interaction.response.defer()


# =====================================================
# SUPPORT COG
# =====================================================

class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_watcher.start()

        if not hasattr(state, "DM_SUPPORT_ACTIVE"):
            state.DM_SUPPORT_ACTIVE = set()

    def cog_unload(self):
        self.ticket_watcher.cancel()

    # ---------------- DM HANDLER ----------------

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # DM SUPPORT FLOW
        if isinstance(message.channel, discord.DMChannel):
            user_id = message.author.id

            # Panel already shown → stay silent
            if user_id in state.DM_SUPPORT_ACTIVE:
                return

            state.DM_SUPPORT_ACTIVE.add(user_id)

            await message.channel.send(
                embed=luxury_embed(
                    title="🛎️ Support Portal",
                    description=(
                        "**Hellfire Hangout Support** ✨\n\n"
                        "Choose how you'd like to proceed."
                    ),
                    color=COLOR_PRIMARY
                ),
                view=SupportView(self.bot, message.author)
            )
            return

        # Ticket activity tracking
        if message.guild and message.channel.id in state.TICKET_META:
            meta = state.TICKET_META[message.channel.id]
            meta["last_activity"] = datetime.utcnow()
            meta["status"] = (
                "waiting_staff"
                if message.author.id == meta["owner"]
                else "staff_engaged"
            )
            await self.update_ticket_panel(message.channel)

    # ---------------- PANEL UPDATE ----------------

    async def update_ticket_panel(self, channel):
        meta = state.TICKET_META.get(channel.id)
        if not meta:
            return

        try:
            panel = await channel.fetch_message(meta["panel_id"])
        except:
            return

        await panel.edit(
            embed=luxury_embed(
                title="🌙 Support Ticket",
                description=(
                    f"**Status:** {meta['status'].replace('_', ' ').title()}\n"
                    f"**Priority:** {'🔴 High' if meta['priority']=='high' else '🟢 Normal'}"
                ),
                color=COLOR_GOLD
            )
        )

    # ---------------- AUTO CLOSE ----------------

    @tasks.loop(minutes=10)
    async def ticket_watcher(self):
        now = datetime.utcnow()

        for channel_id, meta in list(state.TICKET_META.items()):
            if now - meta["last_activity"] > timedelta(hours=24):
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send(
                        embed=luxury_embed(
                            title="⏳ Ticket Closed",
                            description="Closed due to inactivity.",
                            color=COLOR_SECONDARY
                        )
                    )
                    await asyncio.sleep(2)
                    await channel.delete()

                state.TICKET_META.pop(channel_id, None)
                state.OPEN_TICKETS.pop(meta["owner"], None)

    @ticket_watcher.before_loop
    async def before_watcher(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Support(bot))
