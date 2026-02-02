"""
=================================================
HellFire Hangout — Global Runtime State
=================================================

⚠️ IMPORTANT:
• In-memory only (resets on restart)
• Safe for Railway / free hosting
• NO logic, NO side effects
• NO async, NO functions
• Single source of runtime truth
• Can be swapped with DB later

DO NOT put code here.
=================================================
"""

from typing import Dict, List, Set, Optional
from datetime import datetime


# =================================================
# 🧾 MODERATION — WARN SYSTEM
# =================================================

# user_id -> total warn count
WARN_DATA: Dict[int, int] = {}

# user_id -> list of warn entries
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

# user_id -> channel_id (one open ticket per user)
OPEN_TICKETS: Dict[int, int] = {}

# user_ids banned from creating tickets
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


# =================================================
# 🧠 STAFF — INTELLIGENCE & SAFETY
# =================================================

# staff_id -> activity statistics
STAFF_STATS: Dict[int, dict] = {}
"""
STAFF_STATS[staff_id] = {
    "actions": int,
    "today": int,
    "last_action": datetime
}
"""

# user_id -> private staff notes
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
# 🛡️ SECURITY — ANTI-SPAM / AUTOMOD
# =================================================

# user_id -> list of message timestamps (basic spam tracking)
MESSAGE_HISTORY: Dict[int, List[datetime]] = {}

# user_id -> last automod action timestamp
AUTOMOD_LAST_ACTION: Dict[int, datetime] = {}

# user_id -> automod strike count (for future escalation)
AUTOMOD_STRIKES: Dict[int, int] = {}


# =================================================
# 🏆 ACTIVITY — WEEKLY MVP SYSTEM
# =================================================

# guild_id -> current MVP user_id
CURRENT_TEXT_MVP: Dict[int, Optional[int]] = {}

# guild_id -> last MVP rotation time
LAST_MVP_ROTATION: Dict[int, datetime] = {}


# =================================================
# 📊 ACTIVITY — MESSAGE TRACKING (RUNTIME MIRROR)
# =================================================

# user_id -> messages counted this runtime (debug / future use)
RUNTIME_MESSAGE_COUNT: Dict[int, int] = {}


# =================================================
# 🌌 ONBOARDING — JOIN FLOW
# =================================================

# user_id -> onboarding message_id
ONBOARDING_MESSAGES: Dict[int, int] = {}


# =================================================
# ⚙️ GUILD CONFIGURATION (RUNTIME)
# =================================================

# Main guild ID (set during setup)
MAIN_GUILD_ID: Optional[int] = None

# Channel IDs
WELCOME_CHANNEL_ID: Optional[int] = None
SUPPORT_LOG_CHANNEL_ID: Optional[int] = None
BOT_LOG_CHANNEL_ID: Optional[int] = None

# Role IDs
AUTO_ROLE_ID: Optional[int] = None


# =================================================
# 👮 STAFF ROLE SYSTEM
# =================================================

# Role tiers (populated by admin setup)
STAFF_ROLE_TIERS: Dict[int, Optional[int]] = {
    1: None,  # Staff
    2: None,  # Staff+
    3: None,  # Staff++
    4: None,  # Staff+++
}


# =================================================
# 🚨 SYSTEM FLAGS
# =================================================

SYSTEM_FLAGS: Dict[str, bool] = {
    "panic_mode": False,

    # Feature toggles (informational & future control)
    "automod_enabled": True,
    "mvp_system": True,
    "profile_stats": True,
    "message_tracking": True,
}


# =================================================
# 🔊 VOICE SYSTEM
# =================================================

# Voice channel the bot should stay connected to
VOICE_CHANNEL_ID: Optional[int] = None

# Whether bot should auto-rejoin voice channel
VOICE_STAY_ENABLED: bool = False


# =================================================
# 💬 DM SUPPORT CONTROL
# =================================================

# user_id -> last DM support interaction time
# (used to prevent DM spam / duplicate panels)
DM_SUPPORT_COOLDOWN: Dict[int, datetime] = {}
