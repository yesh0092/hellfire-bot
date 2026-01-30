# WARN_DATA = {}        # user_id -> warn count
# WARN_LOGS = {}        # user_id -> list of reasons


# OPEN_TICKETS = {}
# TICKET_BANNED_USERS = set()
# TICKET_META = {}
# MAIN_GUILD_ID = None


# STAFF_STATS = {}     # staff_id -> activity metrics
# STAFF_NOTES = {}     # user_id -> list of notes


# MESSAGE_HISTORY = {}   # user_id -> timestamps list


# ONBOARDING_MESSAGES = {}   # user_id -> message_id
# WELCOME_CHANNEL_ID = None
# AUTO_ROLE_ID = None







"""
=================================================
Hellfire Hangout — Global Runtime State
=================================================

⚠️ IMPORTANT:
This file stores IN-MEMORY runtime state.
- Data resets on bot restart
- Safe for Railway / free hosting
- Designed to be swapped with DB later

DO NOT store secrets here.
DO NOT perform logic here.
=================================================
"""

# =================================================
# 🧾 MODERATION — WARN SYSTEM
# =================================================

# user_id -> total warn count
WARN_DATA: dict[int, int] = {}

# user_id -> list of warn reasons (chronological)
WARN_LOGS: dict[int, list[str]] = {}

# =================================================
# 🛎️ SUPPORT — TICKET SYSTEM
# =================================================

# user_id -> channel_id (only one open ticket per user)
OPEN_TICKETS: dict[int, int] = {}

# user_ids banned from creating tickets
TICKET_BANNED_USERS: set[int] = set()

# channel_id -> ticket metadata
TICKET_META: dict[int, dict] = {}
"""
TICKET_META[channel_id] = {
    "owner": user_id,
    "created_at": datetime,
    "last_activity": datetime,
    "status": "waiting_staff" | "staff_engaged" | "waiting_user" | "escalated",
    "priority": "normal" | "high",
    "panel_id": message_id
}
"""

# =================================================
# 🧠 STAFF — INTELLIGENCE & SAFETY
# =================================================

# staff_id -> activity statistics
STAFF_STATS: dict[int, dict] = {}
"""
STAFF_STATS[staff_id] = {
    "actions": int,        # total actions
    "today": int,          # actions today
    "last_action": datetime
}
"""

# user_id -> list of private staff notes
STAFF_NOTES: dict[int, list[dict]] = {}
"""
STAFF_NOTES[user_id] = [
    {
        "by": staff_id,
        "note": str,
        "time": datetime
    }
]
"""

# =================================================
# 🛡️ SECURITY — ANTI-SPAM / RAID
# =================================================

# user_id -> list of message timestamps (for spam detection)
MESSAGE_HISTORY: dict[int, list] = {}

# =================================================
# 🌌 ONBOARDING — JOIN FLOW
# =================================================

# user_id -> onboarding message_id (for cleanup)
ONBOARDING_MESSAGES: dict[int, int] = {}

# =================================================
# ⚙️ GUILD CONFIGURATION
# =================================================

# Main guild this bot is configured for
MAIN_GUILD_ID: int | None = None

# Channel IDs
WELCOME_CHANNEL_ID: int | None = None
SUPPORT_LOG_CHANNEL_ID: int | None = None

# Role IDs
AUTO_ROLE_ID: int | None = None

# =================================================
# 🚨 SYSTEM FLAGS (FUTURE-SAFE)
# =================================================

# Reserved for future system-wide toggles
SYSTEM_FLAGS: dict[str, bool] = {
    "panic_mode": False,
}

# ================= BOT LOGGING =================

BOT_LOG_CHANNEL_ID: int | None = None


# ================= STAFF ROLE SYSTEM =================

STAFF_ROLE_TIERS = {
    1: None,  # Staff
    2: None,  # Staff+
    3: None,  # Staff++
    4: None,  # Staff+++
}

SYSTEM_FLAGS = {
    "panic_mode": False
}

MAIN_GUILD_ID = None
BOT_LOG_CHANNEL_ID = None





VOICE_CHANNEL_ID = None
VOICE_STAY_ENABLED = False



