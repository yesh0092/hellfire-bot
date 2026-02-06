import sqlite3
import threading
import time
from contextlib import contextmanager


# =====================================================
# 🔱 HELLFIRE DATABASE ENGINE
# • Thread-safe
# • Efficient
# • Auto-healing
# • Future-ready
# =====================================================

DB_PATH = "hellfire.db"


class Database:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        self.lock = threading.RLock()

        self.conn = sqlite3.connect(
            self.path,
            check_same_thread=False,
            timeout=30
        )
        self.conn.row_factory = sqlite3.Row

        self._optimize()
        self._setup()

    # =================================================
    # DATABASE OPTIMIZATION (CRITICAL)
    # =================================================

    def _optimize(self):
        with self.lock:
            self.conn.execute("PRAGMA journal_mode = WAL;")
            self.conn.execute("PRAGMA synchronous = NORMAL;")
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.conn.execute("PRAGMA temp_store = MEMORY;")
            self.conn.execute("PRAGMA cache_size = -64000;")  # ~64MB cache
            self.conn.commit()

    # =================================================
    # TABLE CREATION (SAFE & EXTENSIBLE)
    # =================================================

    def _setup(self):
        with self.lock:

            # ---------------- USER MESSAGE STATS ----------------
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                messages_week INTEGER DEFAULT 0,
                messages_total INTEGER DEFAULT 0,
                last_message_ts INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id)
            )
            """)

            # ---------------- WARN SYSTEM ----------------
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                created_at INTEGER
            )
            """)

            # ---------------- STAFF ACTION LOG ----------------
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS staff_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                target_id INTEGER,
                reason TEXT,
                created_at INTEGER
            )
            """)

            # ---------------- SUPPORT TICKETS ----------------
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS support_tickets (
                channel_id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                created_at INTEGER,
                last_activity INTEGER,
                status TEXT DEFAULT 'open'
            )
            """)

            # ---------------- SERVER ECONOMY (FUTURE) ----------------
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                balance INTEGER DEFAULT 0,
                last_daily INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id)
            )
            """)

            self.conn.commit()

    # =================================================
    # SAFE CONTEXT MANAGER
    # =================================================

    @contextmanager
    def cursor(self):
        with self.lock:
            cur = self.conn.cursor()
            try:
                yield cur
                self.conn.commit()
            except Exception:
                self.conn.rollback()
                raise
            finally:
                cur.close()

    # =================================================
    # CORE QUERY METHODS (BACKWARD COMPATIBLE)
    # =================================================

    def execute(self, query: str, params: tuple = ()):
        with self.lock:
            cur = self.conn.execute(query, params)
            self.conn.commit()
            return cur

    def executemany(self, query: str, seq):
        with self.lock:
            cur = self.conn.executemany(query, seq)
            self.conn.commit()
            return cur

    def fetchone(self, query: str, params: tuple = ()):
        with self.lock:
            return self.conn.execute(query, params).fetchone()

    def fetchall(self, query: str, params: tuple = ()):
        with self.lock:
            return self.conn.execute(query, params).fetchall()

    # =================================================
    # HIGH-LEVEL HELPERS (PERFORMANCE)
    # =================================================

    def increment_message(self, user_id: int, guild_id: int):
        now = int(time.time())
        with self.lock:
            self.conn.execute("""
            INSERT INTO user_stats (user_id, guild_id, messages_week, messages_total, last_message_ts)
            VALUES (?, ?, 1, 1, ?)
            ON CONFLICT(user_id, guild_id)
            DO UPDATE SET
                messages_week = messages_week + 1,
                messages_total = messages_total + 1,
                last_message_ts = ?
            """, (user_id, guild_id, now, now))
            self.conn.commit()

    def reset_weekly_messages(self, guild_id: int):
        with self.lock:
            self.conn.execute(
                "UPDATE user_stats SET messages_week = 0 WHERE guild_id = ?",
                (guild_id,)
            )
            self.conn.commit()

    def add_warning(self, user_id: int, guild_id: int, moderator_id: int, reason: str):
        with self.lock:
            self.conn.execute("""
            INSERT INTO warnings (user_id, guild_id, moderator_id, reason, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (user_id, guild_id, moderator_id, reason, int(time.time())))
            self.conn.commit()

    def log_staff_action(self, staff_id: int, guild_id: int, action: str, target_id: int = None, reason: str = None):
        with self.lock:
            self.conn.execute("""
            INSERT INTO staff_actions (staff_id, guild_id, action, target_id, reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (staff_id, guild_id, action, target_id, reason, int(time.time())))
            self.conn.commit()

    # =================================================
    # SHUTDOWN (SAFE)
    # =================================================

    def close(self):
        with self.lock:
            self.conn.close()


# =====================================================
# GLOBAL INSTANCE (USED EVERYWHERE)
# =====================================================

db = Database()
