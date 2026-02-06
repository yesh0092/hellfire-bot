import discord
from datetime import datetime
from typing import Optional

from utils.config import (
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_GOLD,
    COLOR_DANGER
)

# =====================================================
# 🔱 GLOBAL BRANDING (SINGLE SOURCE)
# =====================================================

BRAND_NAME = "HellFire Hangout"
BRAND_TAGLINE = "Elite Automation • Silent Power • Anime Authority"

DEFAULT_FOOTER = f"🔥 {BRAND_NAME} | {BRAND_TAGLINE}"
DEFAULT_ICON = None  # You can later put a CDN / GitHub raw image URL


# =====================================================
# 🧠 CORE LUXURY EMBED FACTORY
# =====================================================

def luxury_embed(
    title: Optional[str] = None,
    description: Optional[str] = None,
    *,
    color: int = COLOR_PRIMARY,
    footer: Optional[str] = DEFAULT_FOOTER,
    footer_icon: Optional[str] = DEFAULT_ICON,
    timestamp: bool = True,
    thumbnail: Optional[str] = None,
    image: Optional[str] = None,
    author: Optional[str] = None,
    author_icon: Optional[str] = None
) -> discord.Embed:
    """
    🔥 Universal embed factory used across the entire bot.

    ✅ Backward compatible
    ✅ Anime-theme ready
    ✅ Safe (Discord limits)
    ✅ Centralized branding
    """

    # Discord requires at least one visible field
    if not title and not description:
        description = "\u200b"

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow() if timestamp else None
    )

    # ---------- AUTHOR ----------
    if author:
        embed.set_author(
            name=author,
            icon_url=author_icon or DEFAULT_ICON
        )

    # ---------- THUMBNAIL ----------
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    # ---------- IMAGE ----------
    if image:
        embed.set_image(url=image)

    # ---------- FOOTER ----------
    if footer:
        embed.set_footer(
            text=footer,
            icon_url=footer_icon
        )

    return embed


# =====================================================
# 🎭 SPECIALIZED EMBED VARIANTS (NON-BREAKING)
# =====================================================

def staff_embed(
    title: str,
    description: str,
    *,
    color: int = COLOR_GOLD
) -> discord.Embed:
    """
    👮 Staff-only actions, warnings, moderation logs
    """
    return luxury_embed(
        title=title,
        description=description,
        color=color,
        footer="👮 Staff System • HellFire Hangout"
    )


def system_embed(
    title: str,
    description: str,
    *,
    color: int = COLOR_SECONDARY
) -> discord.Embed:
    """
    ⚙️ System / automation / background logs
    """
    return luxury_embed(
        title=title,
        description=description,
        color=color,
        footer="⚙️ System Core • HellFire Hangout"
    )


def danger_embed(
    title: str,
    description: str
) -> discord.Embed:
    """
    ⛔ Errors, bans, critical actions
    """
    return luxury_embed(
        title=title,
        description=description,
        color=COLOR_DANGER,
        footer="⛔ Security & Enforcement • HellFire Hangout"
    )


def profile_embed(
    user: discord.Member,
    title: str,
    description: str
) -> discord.Embed:
    """
    🧬 Profile / stats / economy embeds
    """
    return luxury_embed(
        title=title,
        description=description,
        color=COLOR_GOLD,
        thumbnail=user.display_avatar.url,
        footer=f"🧬 Profile System • {BRAND_NAME}"
    )


# =====================================================
# 🛡️ QUICK FIELD HELPER (OPTIONAL)
# =====================================================

def add_field_safe(
    embed: discord.Embed,
    *,
    name: str,
    value: str,
    inline: bool = False
):
    """
    Safely adds a field without breaking Discord limits.
    """
    if len(embed.fields) >= 25:
        return

    embed.add_field(
        name=name[:256],
        value=value[:1024],
        inline=inline
    )
