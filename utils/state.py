# =================================================
# 🔥 HellFire Hangout — Global Runtime State
# =================================================

# ⚠️ CRITICAL RULES:
# • In-memory only (resets on restart)
# • Safe for Railway / Replit / free hosting
# • NO logic | NO async | NO functions
# • ONLY variables & documentation
# =================================================

from typing import Dict, List, Set, Optional, Any
from datetime import datetime


# =================================================
# 🧾 MODERATION — WARN & LOCKDOWN
# =================================================

# user_id -> total warning count
WARN_DATA: Dict[int, int] = {}

# user_id -> list of warning records
WARN_LOGS: Dict[int, List[dict]] = {}
"""
WARN_LOGS[user_id] = [
    {
        "reason": str,
        "by": staff_id,
        "time": float (timestamp)
    }
]
"""

# set of channel_ids currently under lockdown
LOCKDOWN_DATA: Set[int] = set()


# =================================================
# 🛎️ SUPPORT — TICKET SYSTEM
# =================================================

# user_id -> active ticket channel_id
OPEN_TICKETS: Dict[int, int] = {}

# user_ids blocked from opening tickets
TICKET_BANNED_USERS: Set[int] = set()

# channel_id -> ticket metadata
TICKET_META: Dict[int, dict] = {}
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

# DM support session tracking (anti-spam)
DM_SUPPORT_SESSIONS: Dict[int, dict] = {}


# =================================================
# 🧠 STAFF — INTELLIGENCE & SAFETY
# =================================================

# staff_id -> moderation activity stats
STAFF_STATS: Dict[int, dict] = {}

# user_id -> private internal staff notes
STAFF_NOTES: Dict[int, List[dict]] = {}


# =================================================
# 🛡️ AUTOMOD / SECURITY — RUNTIME MEMORY
# =================================================

# user_id -> list of recent message timestamps (float) for spam detection
MESSAGE_HISTORY: Dict[int, List[float]] = {}

# channel_id -> { "author_id": int, "content": str, "timestamp": datetime }
GHOST_PING_HISTORY: Dict[int, dict] = {}

# user_id -> last automod action timestamp
AUTOMOD_LAST_ACTION: Dict[int, float] = {}

# user_id -> automod strike count
AUTOMOD_STRIKES: Dict[int, int] = {}


# =================================================
# 🏆 ACTIVITY — WEEKLY MVP SYSTEM
# =================================================

# guild_id -> current MVP user_id
CURRENT_TEXT_MVP: Dict[int, Optional[int]] = {}

# guild_id -> last MVP rotation timestamp
LAST_MVP_ROTATION: Dict[int, datetime] = {}


# =================================================
# 📊 ACTIVITY — MESSAGE TRACKING
# =================================================

# user_id -> message count since last restart
RUNTIME_MESSAGE_COUNT: Dict[int, int] = {}


# =================================================
# 🌌 ONBOARDING — JOIN FLOW
# =================================================

# user_id -> onboarding message_id
ONBOARDING_MESSAGES: Dict[int, int] = {}


# =================================================
# ⚙️ GUILD CONFIGURATION (RUNTIME)
# =================================================

# Primary guild ID
MAIN_GUILD_ID: Optional[int] = None

# Channel IDs
WELCOME_CHANNEL_ID: Optional[int] = None
SUPPORT_LOG_CHANNEL_ID: Optional[int] = None
BOT_LOG_CHANNEL_ID: Optional[int] = None

# Role IDs
AUTO_ROLE_ID: Optional[int] = None


# =================================================
# 👮 STAFF ROLE SYSTEM (HIERARCHY)
# =================================================

# Staff tier mapping (Tier Level -> Role ID)
STAFF_ROLE_TIERS: Dict[int, Optional[int]] = {
    1: None,  # Staff
    2: None,  # Staff+
    3: None,  # Staff++
    4: None,  # Staff+++
}


# =================================================
# 🚨 SYSTEM FLAGS (GLOBAL TOGGLES)
# =================================================

SYSTEM_FLAGS: Dict[str, bool] = {
    "panic_mode": False,
    "automod_enabled": True,
    "mvp_system": True,
    "profile_stats": True,
    "message_tracking": True,
    "maintenance_mode": False
}


# =================================================
# 🔊 VOICE SYSTEM
# =================================================

# Voice channel ID to stay connected
VOICE_CHANNEL_ID: Optional[int] = None

# Whether voice stay system is enabled
VOICE_STAY_ENABLED: bool = False


# =================================================
# 💬 DM SUPPORT COOLDOWN
# =================================================

# user_id -> last DM support interaction timestamp
DM_SUPPORT_COOLDOWN: Dict[int, float] = {}
