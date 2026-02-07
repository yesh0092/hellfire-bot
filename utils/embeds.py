import discord
from datetime import datetime
from typing import Optional
from utils.config import COLOR_PRIMARY, COLOR_SECONDARY, COLOR_GOLD, COLOR_DANGER

BRAND_NAME = "HellFire Hangout"
BRAND_TAGLINE = "Elite Automation • Silent Power • Anime Authority"
DEFAULT_FOOTER = f"🔥 {BRAND_NAME} | {BRAND_TAGLINE}"
DEFAULT_ICON = None 

def luxury_embed(
    title: Optional[str] = None,
    description: Optional[str] = None,
    color: int = COLOR_PRIMARY, # Moved before the '*' to fix the Warn crash
    *,
    footer: Optional[str] = DEFAULT_FOOTER,
    footer_icon: Optional[str] = DEFAULT_ICON,
    timestamp: bool = True,
    thumbnail: Optional[str] = None,
    image: Optional[str] = None,
    author: Optional[str] = None,
    author_icon: Optional[str] = None
) -> discord.Embed:
    if not title and not description:
        description = "\u200b"

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow() if timestamp else None
    )

    if author:
        embed.set_author(name=author, icon_url=author_icon or DEFAULT_ICON)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if footer:
        embed.set_footer(text=footer, icon_url=footer_icon)

    return embed

# Variant helpers stay the same as they use keywords internally
def staff_embed(title: str, description: str, *, color: int = COLOR_GOLD) -> discord.Embed:
    return luxury_embed(title=title, description=description, color=color, footer="👮 Staff System • HellFire Hangout")

def danger_embed(title: str, description: str) -> discord.Embed:
    return luxury_embed(title=title, description=description, color=COLOR_DANGER, footer="⛔ Security • HellFire Hangout")
