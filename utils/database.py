import sqlite3
import threading

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(
            "hellfire.db",
            check_same_thread=False
        )
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        self._setup()

    def _setup(self):
        with self.lock:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER,
                guild_id INTEGER,
                messages_week INTEGER DEFAULT 0,
                messages_total INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id)
            )
            """)
            self.conn.commit()

    def execute(self, query, params=()):
        with self.lock:
            cur = self.conn.execute(query, params)
            self.conn.commit()
            return cur

    def fetchone(self, query, params=()):
        return self.execute(query, params).fetchone()

    def fetchall(self, query, params=()):
        return self.execute(query, params).fetchall()

db = Database()
