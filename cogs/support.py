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
                    title="❌ Access Denied",
                    description="Only the ticket owner or authorized staff may close this ticket.",
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
                description="This support session has been gracefully concluded.",
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
        super().__init__(timeout=120)
        self.bot = bot
        self.user = user

    # ---------------- OPEN TICKET ----------------

    @discord.ui.button(label="Open Support Ticket", emoji="🎟️", style=discord.ButtonStyle.primary)
    async def open_ticket(self, interaction: discord.Interaction, _):
        guild = self.bot.get_guild(state.MAIN_GUILD_ID)

        if not guild:
            await interaction.response.send_message(
                embed=luxury_embed(
                    title="⚙️ System Not Ready",
                    description="Support system is not configured yet.",
                    color=COLOR_SECONDARY
                ),
                ephemeral=True
            )
            return

        if self.user.id in state.TICKET_BANNED_USERS:
            await interaction.response.send_message(
                embed=luxury_embed(
                    title="🚫 Access Restricted",
                    description="You are restricted from opening support tickets.",
                    color=COLOR_DANGER
                ),
                ephemeral=True
            )
            return

        if self.user.id in state.OPEN_TICKETS:
            await interaction.response.send_message(
                embed=luxury_embed(
                    title="⏳ Ticket Already Exists",
                    description="You already have an active ticket.",
                    color=COLOR_SECONDARY
                ),
                ephemeral=True
            )
            return

        category = discord.utils.get(guild.categories, name=SUPPORT_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(SUPPORT_CATEGORY_NAME)

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
                title="🌙 Premium Support Ticket",
                description=(
                    f"**Client:** {self.user.mention}\n"
                    f"**Status:** 🟡 Waiting for Staff\n"
                    f"**Priority:** 🟢 Normal\n\n"
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
                description="Your support ticket is ready.",
                color=COLOR_GOLD
            ),
            ephemeral=True
        )

    # ---------------- PERSONAL ASSISTANCE (FIXED) ----------------

    @discord.ui.button(label="Personal Assistance", emoji="👑", style=discord.ButtonStyle.secondary)
    async def vip(self, interaction: discord.Interaction, _):

        # 1️⃣ ACK IMMEDIATELY
        await interaction.response.send_message(
            embed=luxury_embed(
                title="🛎️ Concierge Notified",
                description="A senior staff member will contact you shortly.",
                color=COLOR_GOLD
            ),
            ephemeral=True
        )

        # 2️⃣ FETCH GUILD MANUALLY (DM SAFE)
        guild = self.bot.get_guild(state.MAIN_GUILD_ID)
        if not guild:
            return

        logged = False

        # 3️⃣ SUPPORT LOG
        if state.SUPPORT_LOG_CHANNEL_ID:
            ch = guild.get_channel(state.SUPPORT_LOG_CHANNEL_ID)
            if ch:
                await ch.send(
                    embed=luxury_embed(
                        title="👑 VIP Personal Assistance",
                        description=(
                            f"**User:** {self.user.mention}\n"
                            f"**User ID:** `{self.user.id}`\n"
                            "**Priority:** HIGH"
                        ),
                        color=COLOR_GOLD
                    )
                )
                logged = True

        # 4️⃣ BOT LOG FALLBACK
        if not logged and state.BOT_LOG_CHANNEL_ID:
            ch = guild.get_channel(state.BOT_LOG_CHANNEL_ID)
            if ch:
                await ch.send(
                    embed=luxury_embed(
                        title="👑 VIP Request (Fallback)",
                        description=f"{self.user.mention} requested personal assistance.",
                        color=COLOR_GOLD
                    )
                )


# =====================================================
# SUPPORT COG
# =====================================================

class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_watcher.start()

    def cog_unload(self):
        self.ticket_watcher.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel):
            if message.content.lower() == "support":
                await message.channel.send(
                    embed=luxury_embed(
                        title="🛎️ Elite Concierge Portal",
                        description="Choose how you'd like to proceed.",
                        color=COLOR_PRIMARY
                    ),
                    view=SupportView(self.bot, message.author)
                )
                return

        if message.guild and message.channel.id in state.TICKET_META:
            meta = state.TICKET_META[message.channel.id]
            meta["last_activity"] = datetime.utcnow()
            meta["status"] = (
                "waiting_staff"
                if message.author.id == meta["owner"]
                else "staff_engaged"
            )
            await self.update_ticket_panel(message.channel)

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
                title="🌙 Premium Support Ticket",
                description=(
                    f"**Status:** {meta['status'].replace('_',' ').title()}\n"
                    f"**Priority:** {'🔴 Critical' if meta['priority']=='high' else '🟢 Normal'}"
                ),
                color=COLOR_GOLD
            )
        )

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
