import discord
import asyncio
import io
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
STAFF_ROLE_NAMES = ("Staff", "Staff+", "Staff++", "Staff+++", "Admin")

# Role Mapping - Ensure these IDs exist in your utils/state or config
ROLE_MAP = {
    "Report": getattr(state, "REPORT_ROLE_ID", None),
    "Support": getattr(state, "SUPPORT_ROLE_ID", None),
    "Help": getattr(state, "HELP_ROLE_ID", None),
    "Reward": getattr(state, "REWARD_ROLE_ID", None),
    "Others": getattr(state, "OTHERS_ROLE_ID", None)
}

# =====================================================
# TICKET UTILS
# =====================================================

async def generate_transcript(channel: discord.TextChannel):
    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        content = msg.content if msg.content else "[No Text Content/Attachment]"
        messages.append(f"[{timestamp}] {msg.author.name}: {content}")
    return "\n".join(messages)

# =====================================================
# CATEGORY SELECTION VIEW (Inside Ticket)
# =====================================================

class TicketCategoryView(discord.ui.View):
    def __init__(self, owner: discord.Member):
        super().__init__(timeout=None)
        self.owner = owner

    async def _handle_selection(self, interaction: discord.Interaction, category_name: str):
        if interaction.user.id != self.owner.id:
            return await interaction.response.send_message("❌ Only the ticket owner can select the category.", ephemeral=True)

        # Rename channel
        new_name = f"{category_name.lower()}-{self.owner.name}"
        await interaction.channel.edit(name=new_name)

        # Determine Ping
        role_id = ROLE_MAP.get(category_name)
        ping_text = f"<@&{role_id}>" if role_id else "@here"

        # Disable all buttons in the view
        for child in self.children:
            child.disabled = True
        
        await interaction.response.edit_message(view=self)
        
        # Announcement
        confirm_embed = luxury_embed(
            title=f"📌 Category: {category_name}",
            description=f"Ticket has been routed to **{category_name}** staff. {ping_text} will assist you shortly.",
            color=COLOR_GOLD
        )
        await interaction.channel.send(content=ping_text, embed=confirm_embed)

    @discord.ui.button(label="Report", style=discord.ButtonStyle.danger, emoji="🚫")
    async def report(self, interaction: discord.Interaction, _):
        await self._handle_selection(interaction, "Report")

    @discord.ui.button(label="Support", style=discord.ButtonStyle.primary, emoji="🛠️")
    async def support(self, interaction: discord.Interaction, _):
        await self._handle_selection(interaction, "Support")

    @discord.ui.button(label="Help", style=discord.ButtonStyle.success, emoji="❓")
    async def help(self, interaction: discord.Interaction, _):
        await self._handle_selection(interaction, "Help")

    @discord.ui.button(label="Reward", style=discord.ButtonStyle.secondary, emoji="🎁")
    async def reward(self, interaction: discord.Interaction, _):
        await self._handle_selection(interaction, "Reward")

    @discord.ui.button(label="Others", style=discord.ButtonStyle.secondary, emoji="📁")
    async def others(self, interaction: discord.Interaction, _):
        await self._handle_selection(interaction, "Others")

# =====================================================
# TICKET CONTROL VIEW
# =====================================================

class TicketControlView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.claimed_by = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        is_staff = any(role.name in STAFF_ROLE_NAMES for role in interaction.user.roles)
        if interaction.user.id != self.owner_id and not is_staff:
            await interaction.response.send_message("❌ Restricted to staff/owners.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Claim Ticket", emoji="🙋‍♂️", style=discord.ButtonStyle.success)
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.claimed_by:
            return await interaction.response.send_message(f"⚠️ Claimed by <@{self.claimed_by}>", ephemeral=True)
        
        self.claimed_by = interaction.user.id
        button.disabled = True
        button.label = f"Claimed by {interaction.user.name}"
        
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(embed=luxury_embed(
            title="🎫 Ticket Claimed",
            description=f"Staff member {interaction.user.mention} is now assisting you.",
            color=COLOR_GOLD
        ))

    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, _):
        await interaction.response.send_message("🔒 **Archiving and closing...**", ephemeral=True)
        transcript_text = await generate_transcript(interaction.channel)
        file = discord.File(io.BytesIO(transcript_text.encode()), filename=f"transcript-{interaction.channel.name}.txt")

        if state.BOT_LOG_CHANNEL_ID:
            log_channel = interaction.guild.get_channel(state.BOT_LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=luxury_embed(
                    title="📂 Ticket Archived",
                    description=f"**Ticket:** {interaction.channel.name}\n**Owner:** <@{self.owner_id}>\n**Closed by:** {interaction.user.mention}",
                    color=COLOR_SECONDARY
                ), file=file)

        state.TICKET_META.pop(interaction.channel.id, None)
        state.OPEN_TICKETS.pop(self.owner_id, None)
        await asyncio.sleep(3)
        await interaction.channel.delete()

# =====================================================
# DM CONFIRMATION VIEW
# =====================================================

class DMConfirmView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=300)
        self.user = user

    @discord.ui.button(label="Yes, Open Ticket", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, _):
        if self.user.id in state.OPEN_TICKETS:
            return await interaction.response.send_message("❌ You already have an open ticket.", ephemeral=True)

        guild = interaction.client.get_guild(state.MAIN_GUILD_ID)
        category = discord.utils.get(guild.categories, name=SUPPORT_CATEGORY_NAME) or await guild.create_category(SUPPORT_CATEGORY_NAME)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            self.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        for role in guild.roles:
            if role.name in STAFF_ROLE_NAMES:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{self.user.name}",
            category=category,
            overwrites=overwrites
        )

        state.OPEN_TICKETS[self.user.id] = channel.id
        
        # Send Control Panel
        control_view = TicketControlView(self.user.id)
        panel_msg = await channel.send(
            embed=luxury_embed(
                title="🎫 Support Ticket",
                description="Use the buttons below to manage the ticket.",
                color=COLOR_GOLD
            ),
            view=control_view
        )

        # Send Question to user in the channel
        question_embed = luxury_embed(
            title="🛎️ How can we help you?",
            description="Please select a category below so we can ping the right staff members.",
            color=COLOR_GOLD
        )
        await channel.send(content=self.user.mention, embed=question_embed, view=TicketCategoryView(self.user))

        state.TICKET_META[channel.id] = {
            "owner": self.user.id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "panel_id": panel_msg.id
        }
        await interaction.response.edit_message(content=f"✅ **Ticket Created!** Go to: {channel.mention}", embed=None, view=None)

    @discord.ui.button(label="No, Cancel", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, _):
        await interaction.response.edit_message(content="❌ Support request cancelled.", embed=None, view=None)

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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return

        if message.guild and message.channel.id in state.TICKET_META:
            state.TICKET_META[message.channel.id]["last_activity"] = datetime.utcnow()

        if isinstance(message.channel, discord.DMChannel):
            user_id = message.author.id
            now = datetime.utcnow()
            
            # Simplified DM Entry
            last = state.DM_SUPPORT_SESSIONS.get(user_id)
            if last and now - last < DM_PANEL_EXPIRY:
                return

            await message.channel.send(
                embed=luxury_embed(
                    title="🛎️ HellFire Support",
                    description="Would you like to open a support ticket in the server?",
                    color=COLOR_GOLD
                ),
                view=DMConfirmView(message.author)
            )
            state.DM_SUPPORT_SESSIONS[user_id] = now

    @tasks.loop(minutes=5)
    async def ticket_watcher(self):
        now = datetime.utcnow()
        for channel_id, meta in list(state.TICKET_META.items()):
            diff = now - meta["last_activity"]
            if diff > TICKET_INACTIVITY_LIMIT:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    try:
                        txt = await generate_transcript(channel)
                        if state.BOT_LOG_CHANNEL_ID:
                            log = self.bot.get_channel(state.BOT_LOG_CHANNEL_ID)
                            if log:
                                await log.send(f"📁 **Auto-Archive:** {channel.name}", file=discord.File(io.BytesIO(txt.encode()), f"{channel.name}.txt"))
                        await channel.delete()
                    except: pass
                state.TICKET_META.pop(channel_id, None)
                state.OPEN_TICKETS.pop(meta["owner"], None)

    @ticket_watcher.before_loop
    async def before_watcher(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(Support(bot))
