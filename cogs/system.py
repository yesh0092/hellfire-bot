import discord
from discord.ext import commands
from datetime import datetime

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_SECONDARY, COLOR_DANGER
from utils.permissions import require_level
from utils import state

BOT_PREFIX = "&"  # 🔥 SINGLE SOURCE OF TRUTH


class System(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

        # 🔒 Never reassign, only mutate
        if not hasattr(state, "SYSTEM_FLAGS"):
            state.SYSTEM_FLAGS = {}

        state.SYSTEM_FLAGS.setdefault("panic_mode", False)

        # 🔥 Feature flags
        state.SYSTEM_FLAGS.setdefault("mvp_system", True)
        state.SYSTEM_FLAGS.setdefault("profile_stats", True)
        state.SYSTEM_FLAGS.setdefault("message_tracking", True)
        state.SYSTEM_FLAGS.setdefault("automod_enabled", True)

    # =====================================================
    # HELP (STAFF ONLY)
    # =====================================================

    @commands.command(name="help")
    @commands.guild_only()
    @require_level(1)
    async def system_help(self, ctx: commands.Context):
        await ctx.send(
            embed=luxury_embed(
                title="🌙 HellFire Hangout — Command Codex",
                description=(
                    f"**🔑 Active Prefix:** `{BOT_PREFIX}`\n\n"

                    "**🛎️ SUPPORT (USERS)**\n"
                    "`support` → Open support via DM\n\n"

                    "**📊 USER STATS (USERS)**\n"
                    f"`{BOT_PREFIX}profile [@user]`\n"
                    "• Weekly message tracking\n"
                    "• Compete for **Text MVP** role\n\n"

                    "**⚠️ MODERATION (STAFF)**\n"
                    f"`{BOT_PREFIX}warn @user <reason>`\n"
                    f"`{BOT_PREFIX}timeout @user <minutes> <reason>`\n"
                    f"`{BOT_PREFIX}kick @user <reason>`\n"
                    f"`{BOT_PREFIX}ban @user <reason>`\n\n"

                    "**🛡️ AUTOMOD (STAFF+++)**\n"
                    f"`{BOT_PREFIX}automod on`\n"
                    f"`{BOT_PREFIX}automod off`\n"
                    f"`{BOT_PREFIX}automod status`\n\n"

                    "**🧩 ROLE MANAGEMENT (STAFF++)**\n"
                    f"`{BOT_PREFIX}role @user @role`\n\n"

                    "**📊 SYSTEM**\n"
                    f"`{BOT_PREFIX}status`\n"
                    f"`{BOT_PREFIX}panic` / `{BOT_PREFIX}unpanic`\n\n"

                    "_Luxury-grade, silent moderation system._"
                ),
                color=COLOR_GOLD
            )
        )

    # =====================================================
    # STATUS
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(1)
    async def status(self, ctx: commands.Context):
        uptime = datetime.utcnow() - self.start_time
        h, r = divmod(int(uptime.total_seconds()), 3600)
        m, s = divmod(r, 60)

        await ctx.send(
            embed=luxury_embed(
                title="📊 System Status",
                description=(
                    "🟢 **Bot Status:** Online\n"
                    f"⏱ **Uptime:** {h}h {m}m {s}s\n\n"

                    f"🏆 **Weekly MVP:** {'ON' if state.SYSTEM_FLAGS.get('mvp_system') else 'OFF'}\n"
                    f"📊 **Message Tracking:** {'ON' if state.SYSTEM_FLAGS.get('message_tracking') else 'OFF'}\n"
                    f"🛡️ **AutoMod:** {'ON' if state.SYSTEM_FLAGS.get('automod_enabled') else 'OFF'}\n"
                    f"🚨 **Panic Mode:** {'ON' if state.SYSTEM_FLAGS.get('panic_mode') else 'OFF'}\n\n"

                    f"🧠 **Loaded Cogs:** {len(self.bot.cogs)}\n"
                    f"📁 **Bot Logs:** {'Enabled' if state.BOT_LOG_CHANNEL_ID else 'Disabled'}"
                ),
                color=COLOR_SECONDARY
            )
        )

    # =====================================================
    # AUTOMOD TOGGLE (STAFF+++)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def automod(self, ctx: commands.Context, mode: str = None):
        if not mode:
            return await ctx.send(
                embed=luxury_embed(
                    title="⚙️ AutoMod Control",
                    description=(
                        f"`{BOT_PREFIX}automod on`\n"
                        f"`{BOT_PREFIX}automod off`\n"
                        f"`{BOT_PREFIX}automod status`"
                    ),
                    color=COLOR_SECONDARY
                )
            )

        mode = mode.lower()

        if mode == "on":
            state.SYSTEM_FLAGS["automod_enabled"] = True
            await ctx.send(
                embed=luxury_embed(
                    title="🛡️ AutoMod Enabled",
                    description="Automatic moderation is now **ACTIVE**.",
                    color=COLOR_GOLD
                )
            )
            await self._log(ctx, "🛡️ AutoMod enabled")

        elif mode == "off":
            state.SYSTEM_FLAGS["automod_enabled"] = False
            await ctx.send(
                embed=luxury_embed(
                    title="⛔ AutoMod Disabled",
                    description="Automatic moderation is now **DISABLED**.",
                    color=COLOR_DANGER
                )
            )
            await self._log(ctx, "⛔ AutoMod disabled")

        elif mode == "status":
            enabled = state.SYSTEM_FLAGS.get("automod_enabled", True)
            await ctx.send(
                embed=luxury_embed(
                    title="🛡️ AutoMod Status",
                    description=f"**State:** {'ON ✅' if enabled else 'OFF ❌'}",
                    color=COLOR_SECONDARY
                )
            )

        else:
            await ctx.send(
                embed=luxury_embed(
                    title="❌ Invalid Option",
                    description="Use `on`, `off`, or `status`.",
                    color=COLOR_DANGER
                )
            )

    # =====================================================
    # ROLE ASSIGNMENT (STAFF++)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(3)  # Staff++
    async def role(
        self,
        ctx: commands.Context,
        member: discord.Member,
        role: discord.Role
    ):
        if role in member.roles:
            return await ctx.send(
                embed=luxury_embed(
                    title="ℹ️ Role Already Assigned",
                    description=f"{member.mention} already has {role.mention}.",
                    color=COLOR_SECONDARY
                )
            )

        try:
            await member.add_roles(role, reason=f"Assigned by {ctx.author}")
        except discord.Forbidden:
            return await ctx.send(
                embed=luxury_embed(
                    title="❌ Permission Error",
                    description="I cannot assign that role (check role hierarchy).",
                    color=COLOR_DANGER
                )
            )

        await ctx.send(
            embed=luxury_embed(
                title="✅ Role Assigned",
                description=f"{role.mention} has been given to {member.mention}.",
                color=COLOR_GOLD
            )
        )

        await self._log(
            ctx,
            f"🏷️ Role **{role.name}** assigned to {member.mention}"
        )

    # =====================================================
    # PANIC MODE (STAFF+++)
    # =====================================================

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def panic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = True

        await ctx.send(
            embed=luxury_embed(
                title="🚨 PANIC MODE ENABLED",
                description="Aggressive protection is now active.",
                color=COLOR_DANGER
            )
        )

        await self._log(ctx, "🚨 Panic mode enabled")

    @commands.command()
    @commands.guild_only()
    @require_level(4)
    async def unpanic(self, ctx: commands.Context):
        state.SYSTEM_FLAGS["panic_mode"] = False

        await ctx.send(
            embed=luxury_embed(
                title="✅ Panic Mode Disabled",
                description="System returned to normal operation.",
                color=COLOR_GOLD
            )
        )

        await self._log(ctx, "✅ Panic mode disabled")

    # =====================================================
    # INTERNAL LOGGER
    # =====================================================

    async def _log(self, ctx: commands.Context, message: str):
        if not ctx.guild or not state.BOT_LOG_CHANNEL_ID:
            return

        channel = ctx.guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        try:
            await channel.send(
                embed=luxury_embed(
                    title="📁 System Log",
                    description=f"{message}\n\n**By:** {ctx.author.mention}",
                    color=COLOR_SECONDARY
                )
            )
        except (discord.Forbidden, discord.HTTPException):
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(System(bot))
