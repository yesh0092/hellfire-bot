import time
from discord.ext import commands

class SilentAutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        uid = message.author.id
        now = time.time()

        self.cache.setdefault(uid, [])
        self.cache[uid].append(now)

        self.cache[uid] = [
            t for t in self.cache[uid] if now - t < 6
        ]

        if len(self.cache[uid]) >= 6:
            try:
                await message.delete()
                await message.author.send(
                    "⚠️ Please avoid spamming in the server."
                )
            except:
                pass

async def setup(bot):
    await bot.add_cog(SilentAutoMod(bot))
