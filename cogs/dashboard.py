import discord
from discord.ext import commands
from discord import ui
from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER

# =====================================================
# THE INTERACTIVE DASHBOARD VIEW
# =====================================================

class MainDashboard(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot

    @ui.select(
        placeholder="💎 Select a Department...",
        options=[
            discord.SelectOption(label="Moderation", emoji="🛡️", description="Lockdown, Purge, and Mutes"),
            discord.SelectOption(label="Role Management", emoji="🎭", description="Assign or Remove user roles"),
            discord.SelectOption(label="Bot Intelligence", emoji="🧠", description="Usage stats and latency"),
        ]
    )
    async def select_category(self, interaction: discord.Interaction, select: ui.Select):
        # SECURITY CHECK: Ensure only staff can use the dash
        if not interaction.user.guild_permissions.moderate_members:
            return await interaction.response.send_message("❌ You are not authorized.", ephemeral=True)

        choice = select.values[0]

        if choice == "Moderation":
            await self.show_moderation(interaction)
        elif choice == "Role Management":
            await self.show_roles(interaction)
        elif choice == "Bot Intelligence":
            await self.show_stats(interaction)

    async def show_moderation(self, interaction: discord.Interaction):
        embed = luxury_embed(
            title="🛡️ Moderation Command Center",
            description="Use the buttons below to control the channel state."
        )
        # Create a new view for the sub-menu
        view = ui.View()
        view.add_item(ui.Button(label="Lock Channel", style=discord.ButtonStyle.danger, custom_id="lock_btn"))
        view.add_item(ui.Button(label="Unlock Channel", style=discord.ButtonStyle.success, custom_id="unlock_btn"))
        
        await interaction.response.edit_message(embed=embed, view=view)

    async def show_roles(self, interaction: discord.Interaction):
        # This triggers a Modal for manual role input as you requested
        modal = RoleManagementModal()
        await interaction.response.send_modal(modal)

    async def show_stats(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = luxury_embed(
            title="🧠 Bot Intelligence",
            description=f"**Latency:** `{latency}ms`\n**Servers:** `{len(self.bot.guilds)}`"
        )
        await interaction.response.edit_message(embed=embed, view=self)

# =====================================================
# ROLE MANAGEMENT MODAL (The &role @user @role logic)
# =====================================================

class RoleManagementModal(ui.Modal, title="Assign/Remove Role"):
    user_id = ui.TextInput(label="User ID", placeholder="Paste the User ID here...", required=True)
    role_id = ui.TextInput(label="Role ID", placeholder="Paste the Role ID here...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = guild.get_member(int(self.user_id.value))
        role = guild.get_role(int(self.role_id.value))

        if not member or not role:
            return await interaction.response.send_message("❌ Invalid User or Role ID.", ephemeral=True)

        # HIERARCHY CHECK
        if role >= interaction.guild.me.top_role:
            return await interaction.response.send_message("❌ I cannot manage this role (Hierarchy).", ephemeral=True)

        if role in member.roles:
            await member.remove_roles(role)
            msg = f"✅ Removed **{role.name}** from **{member.display_name}**"
        else:
            await member.add_roles(role)
            msg = f"✅ Added **{role.name}** to **{member.display_name}**"

        await interaction.response.send_message(msg, ephemeral=True)

# =====================================================
# THE COG CLASS
# =====================================================

class DashboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dashboard", aliases=["dash"])
    async def open_dashboard(self, ctx):
        """Opens the Ultimate High-Grade Dashboard"""
        embed = luxury_embed(
            title="🔥 HellFire Command Center",
            description="Welcome to the God-Level Management Interface.\nSelect a category from the dropdown below to begin."
        )
        view = MainDashboard(self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(DashboardCog(bot))
