import discord
from discord.ext import commands
from datetime import timedelta, datetime
import time
import asyncio
import re

from utils.embeds import luxury_embed
from utils.config import COLOR_GOLD, COLOR_DANGER, COLOR_SECONDARY
from utils.permissions import require_level
from utils import state

# =====================================================
# CONFIGURATION (GOD LEVEL SENSITIVITY)
# =====================================================

WARN_TIMEOUT_THRESHOLD = 3
WARN_KICK_THRESHOLD = 9 # Increased to accommodate the 8-warn milestone

TIMEOUT_DURATION_MIN = 1440        # 24h escalation
SPAM_TIMEOUT_MIN = 5               # spam timeout
SPAM_WINDOW_SEC = 6
SPAM_LIMIT_NORMAL = 6
SPAM_LIMIT_PANIC = 4

SPAM_COOLDOWN = 30                 # prevents punishment loops

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.spam_cache: dict[int, list[float]] = {}
        self.last_spam_action: dict[int, float] = {}
        
        # Ghost-ping tracking
        self.last_pings: dict[int, dict] = {} # channel_id -> data

        # =================================================
        # HARDEN RUNTIME STATE (CRITICAL)
        # =================================================
        state.WARN_DATA = getattr(state, "WARN_DATA", {})
        state.WARN_LOGS = getattr(state, "WARN_LOGS", {})
        state.LOCKDOWN_DATA = getattr(state, "LOCKDOWN_DATA", set())

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================

    def _bot_member(self, guild: discord.Guild):
        return guild.get_member(self.bot.user.id)

    def _invalid_target(self, ctx, member: discord.Member) -> bool:
        if member == ctx.author:
            return True
        if member.bot:
            return True
        if member == ctx.guild.owner:
            return True
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return True
        return False

    async def _safe_dm(self, member: discord.Member, embed: discord.Embed):
        try:
            await member.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def _log(self, ctx_or_guild, title: str, description: str, color=COLOR_SECONDARY):
        guild = ctx_or_guild.guild if isinstance(ctx_or_guild, commands.Context) else ctx_or_guild
        
        if not state.BOT_LOG_CHANNEL_ID:
            return

        channel = guild.get_channel(state.BOT_LOG_CHANNEL_ID)
        if not channel:
            return

        try:
            await channel.send(
                embed=luxury_embed(
                    title=title,
                    description=description,
                    color=color
                )
            )
        except:
            pass

    # =====================================================
    # FUTURISTIC LISTENERS (GHOST PING & PANIC)
    # =====================================================

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Detects Ghost Pings instantly"""
        if message.author.bot or not message.guild:
            return
        
        if message.mentions or message.role_mentions or message.mention_everyone:
            # Only trigger if the message was deleted within 60 seconds of being sent
            if (discord.utils.utcnow() - message.created_at).total_seconds() < 60:
                embed = luxury_embed(
                    title="👻 Ghost Ping Detected",
                    description=(
                        f"**Author:** {message.author.mention} ({message.author.id})\n"
                        f"**Channel:** {message.channel.mention}\n"
                        f"**Content:** {message.content or '[No Text Content]'}"
                    ),
                    color=COLOR_DANGER
                )
                await message.channel.send(embed=embed, delete_after=15)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Enhanced Auto-Spam Protection"""
        if message.author.bot or not message.guild:
            return

        if not state.SYSTEM_FLAGS.get("automod_enabled", True):
            return

        member = message.author

        # Ignore staff
        if member.guild_permissions.manage_messages:
            return

        # Ignore timed out users
        if member.is_timed_out():
            return

        uid = member.id
        now = time.time()

        # Cooldown after action
        if uid in self.last_spam_action and now - self.last_spam_action[uid] < SPAM_COOLDOWN:
            return

        self.spam_cache.setdefault(uid, []).append(now)
        self.spam_cache[uid] = [
            t for t in self.spam_cache[uid] if now - t < SPAM_WINDOW_SEC
        ]

        limit = (
            SPAM_LIMIT_PANIC
            if state.SYSTEM_FLAGS.get("panic_mode")
            else SPAM_LIMIT_NORMAL
        )

        if len(self.spam_cache[uid]) >= limit:
            try:
                await message.delete()
                # Purge a few more just in case
                await message.channel.purge(limit=5, check=lambda m: m.author == member)
            except:
                pass

            self.last_spam_action[uid] = now

            # FIX: Used keyword arguments to prevent positional error
            await self._apply_timeout(
                ctx=None,
                member=member,
                minutes=SPAM_TIMEOUT_MIN,
                reason="[Automated] High Velocity Spam",
                silent=True,
                guild=message.guild
            )

            self.spam_cache.pop(uid, None)

    # =====================================================
    # WARN SYSTEM (ESCALATING)
    # =====================================================

    @commands.command(name="warn")
    @commands.guild_only()
    @require_level(1)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Formally warns a user and escalates if necessary"""
        if self._invalid_target(ctx, member):
            return await ctx.send(embed=luxury_embed("❌ Error", "Target is immune.", COLOR_DANGER))

        uid = member.id
        state.WARN_DATA[uid] = state.WARN_DATA.get(uid, 0) + 1
        warns = state.WARN_DATA[uid]

        state.WARN_LOGS.setdefault(uid, []).append({
            "reason": reason,
            "by": ctx.author.id,
            "time": datetime.utcnow().timestamp()
        })

        await self._safe_dm(
            member,
            luxury_embed(
                title="⚠️ Warning Issued",
                description=f"📄 **Reason:** {reason}\n⚠️ **Total Warnings:** {warns}",
                color=COLOR_SECONDARY
            )
        )

        await ctx.send(embed=luxury_embed("⚠️ Warning Logged", f"{member.mention} has **{warns}** warnings.", COLOR_GOLD))

        await self._log(ctx, "⚠️ Warning Issued", f"User: {member.mention}\nMod: {ctx.author.mention}\nReason: {reason}\nTotal: {warns}")

        await self._handle_escalation(ctx, member, warns)

    async def _handle_escalation(self, ctx, member, warns: int):
        """Applies automated punishments based on warn count"""
        if warns == 3:
            await self._apply_timeout(ctx, member, 240, "Auto-Escalation (3 Warnings: 4h Timeout)")
        elif warns == 4:
            await self._apply_timeout(ctx, member, 360, "Auto-Escalation (4 Warnings: 6h Timeout)")
        elif warns == 6:
            await self._apply_timeout(ctx, member, 1440, "Auto-Escalation (6 Warnings: 24h Timeout)")
        elif warns == 8:
            await self._apply_timeout(ctx, member, 10080, "Auto-Escalation (8 Warnings: 7d Timeout)")
        elif warns >= WARN_KICK_THRESHOLD:
            await self._apply_kick(ctx, member, f"Auto-Escalation ({warns} Warnings)")

    @commands.command(name="warns", aliases=["warnings"])
    @require_level(1)
    async def warnings(self, ctx, member: discord.Member):
        """Views warning history for a user"""
        uid = member.id
        count = state.WARN_DATA.get(uid, 0)
        logs = state.WARN_LOGS.get(uid, [])

        if not logs:
            return await ctx.send(embed=luxury_embed("✅ Clean History", f"{member.mention} has no warnings.", COLOR_GOLD))

        desc = ""
        for i, log in enumerate(logs[-10:], 1): # Show last 10
            mod = ctx.guild.get_member(log['by'])
            mod_name = mod.name if mod else "Unknown Mod"
            date = datetime.fromtimestamp(log['time']).strftime('%Y-%m-%d')
            desc += f"**{i}.** `{date}` - {log['reason']} (By: {mod_name})\n"

        embed = luxury_embed(title=f"⚠️ Warning History: {member.name}", description=f"Total Warnings: **{count}**\n\n{desc}", color=COLOR_GOLD)
        await ctx.send(embed=embed)

    @commands.command(name="clearwarns")
    @require_level(3)
    async def clearwarns(self, ctx, member: discord.Member):
        """Resets all warnings for a user"""
        state.WARN_DATA[member.id] = 0
        state.WARN_LOGS[member.id] = []
        await ctx.send(embed=luxury_embed("✅ Warnings Cleared", f"Reset history for {member.mention}", COLOR_GOLD))

    # =====================================================
    # TIMEOUT / UNTIMEOUT
    # =====================================================

    @commands.command(name="timeout", aliases=["mute"])
    @commands.guild_only()
    @require_level(2)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason="No reason provided"):
        """Silences a user for a specific duration"""
        if self._invalid_target(ctx, member):
            return await ctx.send(embed=luxury_embed("❌ Error", "Cannot timeout staff.", COLOR_DANGER))
        await self._apply_timeout(ctx, member, minutes, reason)

    @commands.command(name="untimeout", aliases=["unmute"])
    @require_level(2)
    async def untimeout(self, ctx, member: discord.Member):
        """Removes a timeout from a user"""
        await member.timeout(None)
        await ctx.send(embed=luxury_embed("⏳ Timeout Removed", f"{member.mention} can now speak.", COLOR_GOLD))

    async def _apply_timeout(self, ctx, member, minutes: int, reason: str, silent=False, guild=None):
        target_guild = ctx.guild if ctx else guild
        bot = self._bot_member(target_guild)
        
        if not bot.guild_permissions.moderate_members:
            return

        await self._safe_dm(
            member,
            luxury_embed(
                title="⏳ Timeout Applied",
                description=f"⏱ **Duration:** {minutes}m\n📄 **Reason:** {reason}",
                color=COLOR_SECONDARY
            )
        )

        await member.timeout(timedelta(minutes=minutes), reason=reason)

        if ctx and not silent:
            await ctx.send(embed=luxury_embed("⏳ Timeout Executed", f"{member.mention} silenced for **{minutes}m**.", COLOR_GOLD))

        await self._log(target_guild, "⏳ Timeout", f"User: {member.mention}\nDuration: {minutes}m\nReason: {reason}")

    # =====================================================
    # KICK / BAN / SOFTBAN
    # =====================================================

    @commands.command(name="kick")
    @commands.guild_only()
    @require_level(3)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ejects a user from the server"""
        if self._invalid_target(ctx, member):
            return await ctx.send(embed=luxury_embed("❌ Error", "Target immune.", COLOR_DANGER))
        await self._apply_kick(ctx, member, reason)

    async def _apply_kick(self, ctx, member, reason: str):
        bot = self._bot_member(ctx.guild)
        if not bot.guild_permissions.kick_members: return

        await self._safe_dm(member, luxury_embed("🚫 Kicked", f"📄 **Reason:** {reason}", COLOR_DANGER))
        await member.kick(reason=reason)

        if ctx:
            await ctx.send(embed=luxury_embed("👢 Kicked", f"{member.mention} removed.", COLOR_GOLD))
            await self._log(ctx, "👢 Kick", f"User: {member}\nReason: {reason}")

    @commands.command(name="ban")
    @commands.guild_only()
    @require_level(4)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Permanently bans a user"""
        if self._invalid_target(ctx, member): return
        
        await self._safe_dm(member, luxury_embed("⛔ Banned", f"📄 **Reason:** {reason}", COLOR_DANGER))
        await member.ban(reason=reason)
        await ctx.send(embed=luxury_embed("⛔ Banned", f"{member.mention} blacklisted.", COLOR_GOLD))
        await self._log(ctx, "⛔ Ban", f"User: {member}\nReason: {reason}")

    @commands.command(name="softban")
    @require_level(3)
    async def softban(self, ctx, member: discord.Member, *, reason="Softban (Kick + Message Clear)"):
        """Bans and immediately unbans to clear recent messages"""
        if self._invalid_target(ctx, member): return
        await member.ban(reason=reason, delete_message_days=7)
        await ctx.guild.unban(member)
        await ctx.send(embed=luxury_embed("🧼 Softbanned", f"Cleared messages for {member.mention}.", COLOR_GOLD))

    @commands.command(name="unban")
    @require_level(4)
    async def unban(self, ctx, user_id: int):
        """Unbans a user by their ID"""
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(embed=luxury_embed("🔓 Unbanned", f"Restored access for {user.name}", COLOR_GOLD))
        except:
            await ctx.send("❌ User not found or not banned.")

    # =====================================================
    # UTILITY & LOCKDOWN (REVERSIBLE)
    # =====================================================

    @commands.command(name="purge", aliases=["clear"])
    @require_level(1)
    async def purge(self, ctx, amount: int):
        """Bulk delete messages"""
        if amount > 100: amount = 100
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(embed=luxury_embed("🧹 Purge", f"Deleted {len(deleted)-1} messages.", COLOR_GOLD), delete_after=5)

    @commands.command(name="slowmode")
    @require_level(2)
    async def slowmode(self, ctx, seconds: int):
        """Set channel slowmode"""
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(embed=luxury_embed("⏲️ Slowmode", f"Set to {seconds}s.", COLOR_GOLD))

    @commands.command(name="lock")
    @require_level(3)
    async def lock(self, ctx):
        """Lock the current channel"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(embed=luxury_embed("🔒 Locked", "Channel is now restricted.", COLOR_DANGER))

    @commands.command(name="unlock")
    @require_level(3)
    async def unlock(self, ctx):
        """Unlock the current channel"""
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send(embed=luxury_embed("🔓 Unlocked", "Channel is open.", COLOR_GOLD))

    @commands.command(name="lockdown")
    @require_level(4)
    async def lockdown(self, ctx):
        """Lockdown the ENTIRE server (Safety Trigger)"""
        msg = await ctx.send("⚠️ **INITIATING SERVER-WIDE LOCKDOWN... PLEASE CONFIRM.**")
        count = 0
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=False)
                count += 1
            except: continue
        await ctx.send(embed=luxury_embed("🚨 LOCKDOWN COMPLETE", f"Secured {count} channels.", COLOR_DANGER))

    @commands.command(name="unlockdown")
    @require_level(4)
    async def unlockdown(self, ctx):
        """Reverses a server-wide lockdown"""
        msg = await ctx.send("🔓 **RESTORING SERVER ACCESS...**")
        count = 0
        for channel in ctx.guild.text_channels:
            try:
                await channel.set_permissions(ctx.guild.default_role, send_messages=None)
                count += 1
            except: continue
        await ctx.send(embed=luxury_embed("🔓 UNLOCKDOWN COMPLETE", f"Restored {count} channels.", COLOR_GOLD))

    # =====================================================
    # VOICE MODERATION (REVERSIBLE)
    # =====================================================

    @commands.command(name="vmuteall")
    @require_level(3)
    async def vmuteall(self, ctx):
        """Mutes every user in your current voice channel"""
        if not ctx.author.voice:
            return await ctx.send("❌ You must be in a VC.")
        
        count = 0
        for member in ctx.author.voice.channel.members:
            if member.top_role < ctx.author.top_role:
                await member.edit(mute=True)
                count += 1
        await ctx.send(embed=luxury_embed("🎙️ Voice Mute", f"Muted {count} users.", COLOR_DANGER))

    @commands.command(name="vunmuteall")
    @require_level(3)
    async def vunmuteall(self, ctx):
        """Unmutes every user in your current voice channel"""
        if not ctx.author.voice:
            return await ctx.send("❌ You must be in a VC.")
        
        count = 0
        for member in ctx.author.voice.channel.members:
            await member.edit(mute=False)
            count += 1
        await ctx.send(embed=luxury_embed("🎙️ Voice Unmute", f"Unmuted {count} users.", COLOR_GOLD))

    @commands.command(name="vdeafenall")
    @require_level(3)
    async def vdeafenall(self, ctx):
        """Deafens everyone in the current voice channel"""
        if not ctx.author.voice: return
        for member in ctx.author.voice.channel.members:
            if member.top_role < ctx.author.top_role:
                await member.edit(deafen=True)
        await ctx.send(embed=luxury_embed("🔇 Voice Deafen", "Deafened everyone in VC.", COLOR_DANGER))

    @commands.command(name="vundeafenall")
    @require_level(3)
    async def vundeafenall(self, ctx):
        """Undeafens everyone in the current voice channel"""
        if not ctx.author.voice: return
        for member in ctx.author.voice.channel.members:
            await member.edit(deafen=False)
        await ctx.send(embed=luxury_embed("🔊 Voice Undeafen", "Restored hearing for everyone in VC.", COLOR_GOLD))

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
