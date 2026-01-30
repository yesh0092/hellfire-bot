import discord
from datetime import datetime
from utils.config import COLOR_PRIMARY

def luxury_embed(title=None, description=None, color=COLOR_PRIMARY):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(
        text="🔥 Hellfire Hangout | Elite Support Services | Premium Automation"
    )
    return embed
