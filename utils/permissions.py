from functools import wraps
import discord
from discord.ext import commands
from utils import state
from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER


# =====================================================
# 🔐 CORE STAFF LEVEL RESOLVER
# =====================================================

def get_staff_level(member: discord.Member) -> int:
    """
    Returns the highest staff level of a member.
    Owner / Administrator = MAX (4)
    """

    # Owner always max
    if member == member.guild.owner:
        return 4

    # Admin permission bypass
    if member.guild_permissions.administrator:
        return 4

    highest = 0

    # STAFF_ROLE_TIERS example:
    # {1: role_id, 2: role_id, 3: role_id, 4: role_id}
    for level, role_id in state.STAFF_ROLE_TIERS.items():
        if not role_id:
            continue

        if any(role.id == role_id for role in member.roles):
            highest = max(highest, level)

    return highest


# =====================================================
# 🧠 REQUIRE LEVEL DECORATOR (FIXED & ENFORCED)
# =====================================================

def require_level(level: int):
    """
    Enforces staff hierarchy for commands.

    Usage:
    @require_level(2)
    async def timeout(...)
    """

    if not isinstance(level, int) or level < 1:
        raise ValueError("require_level() expects a positive integer")

    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):

            # Must be used in guild
            if not ctx.guild:
                return

            # Resolve staff level safely
            staff_level = get_staff_level(ctx.author)

            if staff_level < level:
                try:
                    await ctx.send(
                        embed=luxury_embed(
                            title="❌ Permission Denied",
                            description=(
                                f"You do not have sufficient staff privileges.\n\n"
                                f"🔒 **Required Level:** {level}\n"
                                f"🧠 **Your Level:** {staff_level}"
                            ),
                            color=COLOR_DANGER
                        ),
                        delete_after=6
                    )
                except (discord.Forbidden, discord.HTTPException):
                    pass

                return

            return await func(self, ctx, *args, **kwargs)

        # Metadata (used by help / audits)
        wrapper.required_level = level
        return wrapper

    return decorator


# =====================================================
# 🛡️ OPTIONAL GLOBAL CHECK (SAFE)
# =====================================================

def staff_only():
    """
    Lightweight decorator for ANY staff role.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: commands.Context, *args, **kwargs):
            if get_staff_level(ctx.author) < 1:
                await ctx.send(
                    embed=luxury_embed(
                        title="❌ Staff Only",
                        description="This command is restricted to staff members.",
                        color=COLOR_DANGER
                    ),
                    delete_after=5
                )
                return

            return await func(self, ctx, *args, **kwargs)

        return wrapper

    return decorator
