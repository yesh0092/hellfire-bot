import discord
from datetime import datetime
from utils.config import COLOR_PRIMARY

# =====================================================
# GLOBAL BRANDING
# =====================================================

DEFAULT_FOOTER = "🔥 HellFire Hangout | Elite Support Services | Premium Automation"


# =====================================================
# LUXURY EMBED FACTORY
# =====================================================

def luxury_embed(
    title: str | None = None,
    description: str | None = None,
    *,
    color: int = COLOR_PRIMARY,
    footer: str = DEFAULT_FOOTER,
    timestamp: bool = True
) -> discord.Embed:
    """
    Creates a premium-styled embed used across the entire bot.

    Backward compatible with all existing calls.
    """

    # Discord safety: at least something must exist
    if not title and not description:
        description = "\u200b"

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow() if timestamp else None
    )

    if footer:
        embed.set_footer(text=footer)

    return embed


# =====================================================
# OPTIONAL HELPERS (NON-BREAKING)
# =====================================================

def staff_embed(title: str, description: str, color: int = COLOR_PRIMARY) -> discord.Embed:
    """
    Embed variant for staff-only messages.
    """
    return luxury_embed(
        title=title,
        description=description,
        color=color,
        footer="👮 Staff System | HellFire Hangout"
    )


def system_embed(title: str, description: str, color: int = COLOR_PRIMARY) -> discord.Embed:
    """
    Embed variant for system / automation logs.
    """
    return luxury_embed(
        title=title,
        description=description,
        color=color,
        footer="⚙️ System Automation | HellFire Hangout"
    )
