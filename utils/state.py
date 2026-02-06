"""
=================================================
🔥 HellFire Hangout — Global Runtime State
=================================================

⚠️ CRITICAL RULES:
• In-memory only (resets on restart)
• Safe for Railway / Replit / free hosting
• NO logic
• NO async
• NO functions
• NO side effects
• ONLY variables & documentation

This file is the SINGLE SOURCE OF RUNTIME TRUTH.
=================================================
"""

from typing import Dict, List, Set, Optional
from datetime import datetime


# =================================================
# 🧾 MODERATION — WARN SYSTEM
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
        "time": datetime
    }
]
"""


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
"""
DM_SUPPORT_SESSIONS[user_id] = {
    "message_id": int,
    "created_at": datetime
}
"""


# =================================================
# 🧠 STAFF — INTELLIGENCE & SAFETY
# =================================================

# staff_id -> moderation activity stats
STAFF_STATS: Dict[int, dict] = {}
"""
STAFF_STATS[staff_id] = {
    "actions": int,
    "today": int,
    "last_action": datetime
}
"""

# user_id -> private internal staff notes
STAFF_NOTES: Dict[int, List[dict]] = {}
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
# 🛡️ AUTOMOD / SECURITY — RUNTIME MEMORY
# =================================================

# user_id -> recent message timestamps
MESSAGE_HISTORY: Dict[int, List[datetime]] = {}

# user_id -> last automod action timestamp
AUTOMOD_LAST_ACTION: Dict[int, datetime] = {}

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
# 📊 ACTIVITY — MESSAGE TRACKING (RUNTIME MIRROR)
# =================================================

# user_id -> message count since last restart (debug / future use)
RUNTIME_MESSAGE_COUNT: Dict[int, int] = {}


# =================================================
# 🌌 ONBOARDING — JOIN FLOW
# =================================================

# user_id -> onboarding message_id
ONBOARDING_MESSAGES: Dict[int, int] = {}


# =================================================
# ⚙️ GUILD CONFIGURATION (RUNTIME)
# =================================================

# Primary guild ID (set during &setup)
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

# Staff tier mapping (set by admin setup)
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

    # Feature toggles
    "automod_enabled": True,
    "mvp_system": True,
    "profile_stats": True,
    "message_tracking": True,
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
DM_SUPPORT_COOLDOWN: Dict[int, datetime] = {}
