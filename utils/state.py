# =================================================
# 🔥 HellFire Hangout — Global Runtime State
# =================================================

from typing import Dict, List, Set, Optional, Any
from datetime import datetime

# =================================================
# ⚙️ GUILD CONFIGURATION (RUNTIME)
# =================================================

# Primary guild ID (CRITICAL: Replace with your actual Server ID)
MAIN_GUILD_ID: int = 1262025273860292628

# Channel IDs
WELCOME_CHANNEL_ID: Optional[int] = None
SUPPORT_LOG_CHANNEL_ID: Optional[int] = None
BOT_LOG_CHANNEL_ID: Optional[int] = None

# Role IDs
AUTO_ROLE_ID: Optional[int] = None

# =================================================
# 🛎️ SUPPORT — TICKET SYSTEM
# =================================================

# user_id -> active ticket channel_id
OPEN_TICKETS: Dict[int, int] = {}

# user_ids blocked from opening tickets
TICKET_BANNED_USERS: Set[int] = set()

# channel_id -> ticket metadata
TICKET_META: Dict[int, dict] = {}

# DM support session tracking (anti-spam)
DM_SUPPORT_SESSIONS: Dict[int, dict] = {}

# Role mapping for Ticket Categorization
# Replace None with the actual Role IDs from your server
TICKET_ROLES: Dict[str, Optional[int]] = {
    "Report": None,   # ID for Report Staff
    "Support": None,  # ID for General Support
    "Help": None,     # ID for Help Staff
    "Reward": None,   # ID for Reward/Giveaway Staff
    "Others": None    # ID for Admin/Other Staff
}

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
# 🧾 MODERATION — WARN & LOCKDOWN
# =================================================
WARN_DATA: Dict[int, int] = {}
WARN_LOGS: Dict[int, List[dict]] = {}
LOCKDOWN_DATA: Set[int] = set()

# =================================================
# 🧠 STAFF — INTELLIGENCE & SAFETY
# =================================================
STAFF_STATS: Dict[int, dict] = {}
STAFF_NOTES: Dict[int, List[dict]] = {}

# =================================================
# 🛡️ AUTOMOD / SECURITY — RUNTIME MEMORY
# =================================================
MESSAGE_HISTORY: Dict[int, List[float]] = {}
GHOST_PING_HISTORY: Dict[int, dict] = {}
AUTOMOD_LAST_ACTION: Dict[int, float] = {}
AUTOMOD_STRIKES: Dict[int, int] = {}

# =================================================
# 🏆 ACTIVITY — WEEKLY MVP SYSTEM
# =================================================
CURRENT_TEXT_MVP: Dict[int, Optional[int]] = {}
LAST_MVP_ROTATION: Dict[int, datetime] = {}

# =================================================
# 📊 ACTIVITY — MESSAGE TRACKING
# =================================================
RUNTIME_MESSAGE_COUNT: Dict[int, int] = {}

# =================================================
# 🌌 ONBOARDING — JOIN FLOW
# =================================================
ONBOARDING_MESSAGES: Dict[int, int] = {}

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
VOICE_CHANNEL_ID: Optional[int] = None
VOICE_STAY_ENABLED: bool = False

# =================================================
# 💬 DM SUPPORT COOLDOWN
# =================================================
DM_SUPPORT_COOLDOWN: Dict[int, float] = {}
