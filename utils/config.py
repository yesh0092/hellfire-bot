# =====================================================
# 🔱 HELLFIRE HANGOUT — GLOBAL CONFIGURATION
# Single source of truth for the entire bot
# =====================================================


# =====================================================
# 🔐 STAFF ROLES (HIERARCHY — ORDER MATTERS)
# =====================================================

STAFF_ROLES = [
    "Staff",
    "Staff+",
    "Staff++",
    "Staff+++"
]

# Numeric mapping (used by permissions, checks, UI)
STAFF_ROLE_LEVELS = {
    "Staff": 1,
    "Staff+": 2,
    "Staff++": 3,
    "Staff+++": 4
}

# Reverse lookup (level → name)
STAFF_LEVEL_NAMES = {
    1: "Staff",
    2: "Staff+",
    3: "Staff++",
    4: "Staff+++"
}


# =====================================================
# 🎟️ SUPPORT SYSTEM
# =====================================================

SUPPORT_CATEGORY_NAME = "SUPPORT"

SUPPORT_TICKET_PREFIX = "ticket-"
SUPPORT_INACTIVITY_HOURS = 24
SUPPORT_DM_PANEL_EXPIRY_MIN = 5


# =====================================================
# 🎨 EMBED COLORS — HELLFIRE / ANIME THEME
# =====================================================

COLOR_PRIMARY = 0x020617      # Abyss Midnight (background panels)
COLOR_SECONDARY = 0x1F2937    # Shadow Slate (info, neutral)
COLOR_GOLD = 0xD4AF37         # Imperial Gold (success, premium)
COLOR_DANGER = 0x7C2D12       # Blood Crimson (warnings, bans)
COLOR_SUCCESS = 0x15803D     # Emerald Flame (positive actions)
COLOR_WARNING = 0x92400E     # Amber Warning (alerts)


# =====================================================
# 🛡️ MODERATION DEFAULTS
# =====================================================

DEFAULT_TIMEOUT_MINUTES = 1440     # 24h escalation timeout
SPAM_TIMEOUT_MINUTES = 5
RAID_TIMEOUT_MINUTES = 10

WARN_TIMEOUT_THRESHOLD = 3
WARN_KICK_THRESHOLD = 5


# =====================================================
# 🤖 AUTOMOD LIMITS (GLOBAL FALLBACKS)
# =====================================================

SPAM_WINDOW_SECONDS = 6
SPAM_LIMIT_NORMAL = 6
SPAM_LIMIT_PANIC = 4

CAPS_RATIO_LIMIT = 0.7
CAPS_MIN_LENGTH = 8

MENTION_LIMIT = 5
EMOJI_LIMIT = 8

AUTOMOD_COOLDOWN_SECONDS = 30


# =====================================================
# 🧠 SYSTEM FLAGS (DEFAULT STATES)
# =====================================================

DEFAULT_SYSTEM_FLAGS = {
    "automod_enabled": True,
    "panic_mode": False,
    "mvp_system": True,
    "message_tracking": True,
    "voice_system": True,
}


# =====================================================
# 🎧 VOICE SYSTEM DEFAULTS
# =====================================================

VOICE_RECONNECT_INTERVAL = 20       # seconds
VOICE_RECONNECT_COOLDOWN = 10        # anti-loop
VOICE_SELF_MUTE = True
VOICE_SELF_DEAF = True


# =====================================================
# 🏆 MVP / ECONOMY (FUTURE READY)
# =====================================================

WEEKLY_MVP_RESET_HOURS = 168         # 7 days

CURRENCY_NAME = "Inferno"
CURRENCY_SYMBOL = "🔥"
CURRENCY_DAILY_REWARD = 100
CURRENCY_MESSAGE_REWARD = 1


# =====================================================
# 📊 LOGGING & AUDIT
# =====================================================

ENABLE_COMMAND_LOGS = True
ENABLE_ERROR_LOGS = True
ENABLE_AUDIT_DMS = True


# =====================================================
# 🧪 DEV / DEBUG
# =====================================================

DEBUG_MODE = False
