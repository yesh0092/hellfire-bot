import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_DANGER, COLOR_SECONDARY
from utils import state


class Core(commands.Cog):
    """
    Core system guardian.
    • Ensures staff hierarchy integrity
    • Auto-heals missing runtime state
    • Handles first-time guild bootstrap safety
    • Zero overlap with Admin / System cogs
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # =================================================
        # 🔒 HARDEN GLOBAL STATE (CRITICAL)
        # =================================================

        if not hasattr(state, "STAFF_ROLE_TIERS"):
            state.STAFF_ROLE_TIERS = {
                1: None,
                2: None,
                3: None,
                4: None,
            }

        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {
                "panic_mode": False,
                "automod_enabled": True,
            }

        if not hasattr(state, "MAIN_GUILD_ID"):
            state.MAIN_GUILD_ID = None

    # =================================================
    # 🤖 BOT READY
    # =================================================

    @commands.Cog.listener()
    async def on_ready(self):
        print("🧠 Core system online")
        print(f"🛡️ Staff tiers loaded: {state.STAFF_ROLE_TIERS}")

    # =================================================
    # 🏰 AUTO-VERIFY ON GUILD JOIN
    # =================================================

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """
        Auto-verifies staff hierarchy when bot joins a guild.
        Does NOT create channels or logs (Admin.setup handles that).
        """
        await self.ensure_staff_roles(guild, silent=True)
        state.MAIN_GUILD_ID = guild.id

    # =================================================
    # 🧩 MANUAL STAFF VERIFY COMMAND
    # =================================================

    @commands.command(name="setupstaff")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setupstaff(self, ctx: commands.Context):
        """
        Repairs / verifies staff roles only.
        Safe to run anytime.
        """

        ok, created = await self.ensure_staff_roles(ctx.guild)

        if not ok:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Staff Setup Failed",
                    description="I need **Manage Roles** permission to repair staff roles.",
                    color=COLOR_DANGER
                )
            )

        await ctx.send(
            embed=luxury_embed(
                title="🛡️ Staff Hierarchy Verified",
                description=(
                    "**HellFire Hangout staff system is stable.**\n\n"
                    + (
                        f"🆕 **Created Roles:** {', '.join(created)}"
                        if created else
                        "✅ All required staff roles already existed."
                    )
                ),
                color=COLOR_GOLD
            )
        )

    # =================================================
    # 🔧 INTERNAL STAFF ROLE ENSURER (ULTIMATE)
    # =================================================

    async def ensure_staff_roles(self, guild: discord.Guild, silent: bool = False):
        """
        Creates missing staff roles and syncs IDs into runtime state.
        NEVER deletes roles.
        NEVER overwrites permissions.
        """

        bot_member = guild.get_member(self.bot.user.id)
        if not bot_member or not bot_member.guild_permissions.manage_roles:
            return False, []

        role_map = {
            1: "Staff",
            2: "Staff+",
            3: "Staff++",
            4: "Staff+++",
        }

        existing_roles = {role.name: role for role in guild.roles}
        created_roles = []

        for level, role_name in role_map.items():
            role = existing_roles.get(role_name)

            if not role:
                try:
                    role = await guild.create_role(
                        name=role_name,
                        reason="HellFire Hangout • Staff hierarchy initialization"
                    )
                    created_roles.append(role_name)
                except (discord.Forbidden, discord.HTTPException):
                    return False, created_roles

            # 🔒 ALWAYS sync IDs
            state.STAFF_ROLE_TIERS[level] = role.id

        if not silent:
            print(f"🛡️ Staff roles synced for {guild.name}")

        return True, created_roles

    # =================================================
    # 🧠 SELF-HEAL CHECK (OPTIONAL FUTURE USE)
    # =================================================

    def audit_state(self):
        """
        Internal diagnostic helper.
        """
        return {
            "guild_id": state.MAIN_GUILD_ID,
            "staff_roles": state.STAFF_ROLE_TIERS,
            "flags": state.SYSTEM_FLAGS,
            "timestamp": datetime.utcnow().isoformat()
        }


async def setup(bot: commands.Bot):
    await bot.add_cog(Core(bot))
