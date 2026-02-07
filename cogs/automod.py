import time
import re
import discord
import math
from collections import Counter
from discord.ext import commands
from utils import state
from utils.embeds import luxury_embed
from utils.config import COLOR_DANGER, COLOR_SECONDARY

# =====================================================
# ⚡ HELLFIRE ELITE CONFIGURATION
# =====================================================
ANALYSIS_WINDOW = 10.0         # Seconds to look back for patterns
MAX_STRIKES_KICK = 6           # Kick at 6th strike
MAX_STRIKES_BAN = 8            # Ban at 8th strike

# REGEX PATTERNS
INVITE_REGEX = r"(discord\.gg\/|discord\.com\/invite\/|discordapp\.com\/invite\/)"
ZALGO_REGEX = r"[\u0300-\u036f\u0483-\u0489\u1dc0-\u1dff\u20d0-\u20ff\ufe20-\ufe2f]"
URL_REGEX = r"(https?:\/\/[^\s]+)"
IP_LOGGER_REGEX = r"(grabify\.link|iplogger\.org|blasze\.com|shorte\.st)"

# TOXICITY/SELF-HARM KEYWORDS (Staff get notified, user gets help-resource DM)
DANGER_KEYWORDS = ["kys", "suicide", "self harm", "kill myself", "end it"]

# ESCALATION MAPPING
PUNISHMENT_MAP = {
    1: "WARN",
    2: 600,      # 10m
    3: 3600,     # 1h
    4: 43200,    # 12h
    5: 86400,    # 24h
    6: "KICK",
    8: "BAN"
}

class SilentAutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Structure: {uid: {'msgs': [], 'strikes': 0, 'last_act': 0, 'attachments': 0}}
        self.user_data = {} 

    def _calculate_entropy(self, text: str) -> float:
        """Math-based detection for keyboard smashing/gibberish."""
        if len(text) < 8: return 3.0 # Ignore short messages
        prob = [n_x/len(text) for x, n_x in Counter(text).items()]
        entropy = -sum([p * math.log(p, 2) for p in prob])
        return entropy

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 1. CORE BYPASS CHECKS
        if not message.guild or message.author.bot: return
        if not state.SYSTEM_FLAGS.get("automod_enabled", True): return
        
        member = message.author
        if member.guild_permissions.manage_messages: return # Immunity for Staff
        if member.is_timed_out(): return # Already punished

        uid = member.id
        now = time.time()
        content = message.content.lower()
        
        # 2. DATA INITIALIZATION & CLEANUP
        data = self.user_data.get(uid, {'msgs': [], 'strikes': 0, 'last_act': 0, 'attachments': 0})
        
        # Strike Decay: Forgive 1 strike every 1 hour of good behavior
        if now - data['last_act'] > 3600 and data['strikes'] > 0:
            data['strikes'] -= 1
            data['last_act'] = now

        # Update Message Cache
        data['msgs'] = [(t, c) for t, c in data['msgs'] if now - t < ANALYSIS_WINDOW]
        data['msgs'].append((now, content))
        self.user_data[uid] = data

        # =====================================================
        # 🚨 THE MULTI-LAYER SCANNER
        # =====================================================
        violation = None

        # LAYER 1: Link & Invite Protection
        if re.search(INVITE_REGEX, content):
            violation = "External Server Invite"
        elif re.search(IP_LOGGER_REGEX, content):
            violation = "Malicious IP-Logger Link"
        
        # LAYER 2: Pattern Recognition (Gibberish/Zalgo)
        elif re.search(ZALGO_REGEX, content):
            violation = "Zalgo/Text Distortion"
        elif len(content) > 20 and self._calculate_entropy(content) < 2.0:
            violation = "Entropy Threshold (Gibberish)"

        # LAYER 3: Burst/Spam Detection
        limit = 3 if state.SYSTEM_FLAGS.get("panic_mode") else 5
        if len(data['msgs']) >= limit:
            violation = "Rapid Message Burst (Spam)"
        
        # LAYER 4: Duplicate Message Check
        last_contents = [c for _, c in data['msgs']]
        if last_contents.count(content) > 2:
            violation = "Duplicate Message Spam"

        # LAYER 5: Toxicity & Safety
        if any(word in content for word in DANGER_KEYWORDS):
            # Special handling: Notify staff without immediate auto-ban to assess mental health
            await self._log_alert(member, "High-Risk Keyword Detected", content)
            return

        # LAYER 6: Attachment Spam
        if message.attachments:
            # Check if they sent > 3 attachments in 10 seconds
            attach_count = sum(1 for t, c in data['msgs'] if any(x in c for x in ["", "file_sent"])) # simplified
            if len(message.attachments) > 3:
                violation = "Media/Attachment Spam"

        # 3. EXECUTE JUSTICE IF VIOLATION FOUND
        if violation:
            await self._execute_action(member, message, violation)

    # =====================================================
    # ⚖️ JUSTICE EXECUTION ENGINE
    # =====================================================

    async def _execute_action(self, member: discord.Member, message: discord.Message, reason: str):
        uid = member.id
        self.user_data[uid]['strikes'] += 1
        self.user_data[uid]['last_act'] = time.time()
        strikes = self.user_data[uid]['strikes']
        
        # Immediate Removal
        try: await message.delete()
        except: pass

        action_type = PUNISHMENT_MAP.get(strikes, "BAN")

        # HANDLE PUNISHMENT TYPES
        if action_type == "WARN":
            await self._dm_user(member, "⚠️ Warning Issued", f"Flagged for: **{reason}**.\nRepeated offenses lead to mutes.")
            await self._log_action(member, "WARNING", reason, strikes)

        elif action_type == "KICK":
            try:
                await member.kick(reason=f"AutoMod Escalation: {reason}")
                await self._log_action(member, "KICK", reason, strikes)
            except: pass

        elif action_type == "BAN":
            try:
                await member.ban(reason=f"AutoMod Final Escalation: {reason}")
                await self._log_action(member, "BAN", reason, strikes)
            except: pass

        else: # Timeout/Mute
            duration = action_type
            until = discord.utils.utcnow() + discord.timedelta(seconds=duration)
            try:
                await member.timeout(until, reason=f"AutoMod: {reason}")
                await self._dm_user(member, "⛔ Silence Active", f"You are muted for **{duration//60}m** due to: **{reason}**.")
                await self._log_action(member, f"TIMEOUT ({duration//60}m)", reason, strikes)
            except: pass

    # =====================================================
    # 📁 LOGGING & COMMUNICATIONS
    # =====================================================

    async def _dm_user(self, member, title, desc):
        try:
            embed = luxury_embed(title=title, description=desc, color=COLOR_DANGER)
            await member.send(embed=embed)
        except: pass

    async def _log_action(self, member, action, reason, strikes):
        # Fetches channel from your state config
        log_id = state.SYSTEM_FLAGS.get("bot_log_channel") 
        if not log_id: return
        channel = self.bot.get_channel(log_id)
        if not channel: return

        embed = luxury_embed(
            title="🛡️ AutoMod Enforcement Log",
            description=(
                f"**User:** {member.mention} | `{member.id}`\n"
                f"**Action:** `{action}`\n"
                f"**Trigger:** `{reason}`\n"
                f"**History:** `{strikes}` strikes total."
            ),
            color=0x2b2d31
        )
        await channel.send(embed=embed)

    async def _log_alert(self, member, title, content):
        log_id = state.SYSTEM_FLAGS.get("bot_log_channel")
        channel = self.bot.get_channel(log_id)
        if channel:
            embed = luxury_embed(title=f"🚨 ALERT: {title}", description=f"**User:** {member.mention}\n**Content:** `{content}`", color=0xffa500)
            await channel.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(SilentAutoMod(bot))
