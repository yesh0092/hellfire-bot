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

# =====================================================
# TICKET UTILS
# =====================================================

async def generate_transcript(channel: discord.TextChannel):
    """Generates a text-based transcript of the ticket"""
    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        content = msg.content if msg.content else "[No Text Content/Attachment]"
        messages.append(f"[{timestamp}] {msg.author.name}: {content}")
    
    return "\n".join(messages)

# =====================================================
# ENHANCED TICKET CONTROL VIEW
# =====================================================

class TicketControlView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.claimed_by = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Check if staff or owner
        is_staff = any(role.name in STAFF_ROLE_NAMES for role in interaction.user.roles)
        if interaction.user.id != self.owner_id and not is_staff:
            await interaction.response.send_message("❌ This control panel is restricted to ticket staff/owners.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Claim Ticket", emoji="🙋‍♂️", style=discord.ButtonStyle.success)
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.claimed_by:
            return await interaction.response.send_message(f"⚠️ Already claimed by <@{self.claimed_by}>", ephemeral=True)
        
        self.claimed_by = interaction.user.id
        button.disabled = True
        button.label = f"Claimed by {interaction.user.name}"
        
        embed = luxury_embed(
            title="🎫 Ticket Claimed",
            description=f"Staff member {interaction.user.mention} is now assisting you.",
            color=COLOR_GOLD
        )
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(embed=embed)

    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, _):
        await interaction.response.send_message("🔒 **Generating transcript and closing...**", ephemeral=True)
        
        # Transcript Logic
        transcript_text = await generate_transcript(interaction.channel)
        file = discord.File(io.BytesIO(transcript_text.encode()), filename=f"transcript-{interaction.channel.name}.txt")

        # Log to Log Channel
        if state.BOT_LOG_CHANNEL_ID:
            log_channel = interaction.guild.get_channel(state.BOT_LOG_CHANNEL_ID)
            if log_channel:
                log_embed = luxury_embed(
                    title="📂 Ticket Archived",
                    description=f"**Ticket:** {interaction.channel.name}\n**Owner:** <@{self.owner_id}>\n**Closed by:** {interaction.user.mention}",
                    color=COLOR_SECONDARY
                )
                await log_channel.send(embed=log_embed, file=file)

        # Cleanup State
        state.TICKET_META.pop(interaction.channel.id, None)
        state.OPEN_TICKETS.pop(self.owner_id, None)

        await asyncio.sleep(3)
        await interaction.channel.delete()

# =====================================================
# PRIORITY SELECTION (MODAL)
# =====================================================

class PrioritySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Low Priority", emoji="🟢", description="General questions"),
            discord.SelectOption(label="Medium Priority", emoji="🟡", description="Report or Tech issues"),
            discord.SelectOption(label="High Priority", emoji="🔴", description="Urgent/Payment issues"),
        ]
        super().__init__(placeholder="Select the urgency of your ticket...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await self.view.create_ticket_logic(interaction, self.values[0])

# =====================================================
# ULTIMATE SUPPORT VIEW
# =====================================================

class SupportView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=300)
        self.user = user
        self.add_item(PrioritySelect())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            return False
        return True

    async def create_ticket_logic(self, interaction: discord.Interaction, priority: str):
        state.DM_SUPPORT_SESSIONS.pop(self.user.id, None)

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
            name=f"🎫-{self.user.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket for {self.user.name} | Priority: {priority}"
        )

        state.OPEN_TICKETS[self.user.id] = channel.id
        
        panel_embed = luxury_embed(
            title=f"🛎️ Ticket: {priority}",
            description=(
                f"Welcome {self.user.mention},\n\n"
                "A staff member will be with you shortly. While you wait:\n"
                "🔹 Describe your issue in detail.\n"
                "🔹 Upload relevant screenshots.\n"
                "🔹 Be patient, our team is in a different time zone."
            ),
            color=COLOR_GOLD if "High" not in priority else COLOR_DANGER
        )
        
        view = TicketControlView(self.user.id)
        msg = await channel.send(f"{self.user.mention} | <@&{state.STAFF_PING_ROLE_ID if hasattr(state, 'STAFF_PING_ROLE_ID') else ''}>", embed=panel_embed, view=view)

        state.TICKET_META[channel.id] = {
            "owner": self.user.id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "panel_id": msg.id
        }

        await interaction.response.edit_message(content="✅ **Ticket Created!** Check your server.", embed=None, view=None)

    @discord.ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.secondary, row=2)
    async def cancel(self, interaction: discord.Interaction, _):
        state.DM_SUPPORT_SESSIONS.pop(self.user.id, None)
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
        if message.author.bot:
            return

        # 1. Update activity if message is in a ticket channel
        if message.guild and message.channel.id in state.TICKET_META:
            state.TICKET_META[message.channel.id]["last_activity"] = datetime.utcnow()

        # 2. DM Entry Point
        if isinstance(message.channel, discord.DMChannel):
            user_id = message.author.id
            now = datetime.utcnow()
            
            # Check for "support" keyword or active session
            if message.content.lower().strip() == "support" or user_id not in state.DM_SUPPORT_SESSIONS:
                last = state.DM_SUPPORT_SESSIONS.get(user_id)
                if last and now - last < DM_PANEL_EXPIRY:
                    return

                await message.channel.send(
                    embed=luxury_embed(
                        title="🛎️ HellFire Support System",
                        description="Welcome. Please select your priority level to open a ticket.",
                        color=COLOR_GOLD
                    ),
                    view=SupportView(message.author)
                )
                state.DM_SUPPORT_SESSIONS[user_id] = now

    @tasks.loop(minutes=5)
    async def ticket_watcher(self):
        """Checks for inactive tickets and warns/closes them"""
        now = datetime.utcnow()
        for channel_id, meta in list(state.TICKET_META.items()):
            diff = now - meta["last_activity"]
            
            if diff > TICKET_INACTIVITY_LIMIT:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    try:
                        await channel.send("⚠️ **Ticket closed due to 24h inactivity.**")
                        # Generate transcript before auto-deletion
                        txt = await generate_transcript(channel)
                        if state.BOT_LOG_CHANNEL_ID:
                            log = self.bot.get_channel(state.BOT_LOG_CHANNEL_ID)
                            if log:
                                await log.send(f"📁 **Auto-Archive:** {channel.name}", file=discord.File(io.BytesIO(txt.encode()), f"{channel.name}.txt"))
                        await asyncio.sleep(5)
                        await channel.delete()
                    except: pass
                
                state.TICKET_META.pop(channel_id, None)
                state.OPEN_TICKETS.pop(meta["owner"], None)

    @ticket_watcher.before_loop
    async def before_watcher(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(Support(bot))
