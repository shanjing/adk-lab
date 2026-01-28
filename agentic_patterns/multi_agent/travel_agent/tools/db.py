import sqlite3
from tools.logging_utils import logger


# -----------------------------
# 1. PERSISTENT MEMORY SERVICE (SQLite)
# -----------------------------
class SqlitePolicyService:
    """
    Manages Long-Term Memory (User Travel History).
    Acts as the 'Persistent Memory' node in the architecture diagram.
    """
    def __init__(self, db_path="adk_agent_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    city TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, city)
                )
            """)
            conn.commit()

    def has_visited(self, user_id: str, city: str) -> bool:
        city_norm = city.strip().lower()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM trips WHERE user_id = ? AND LOWER(city) = ?", 
                (user_id, city_norm)
            )
            return cursor.fetchone() is not None

    def record_visit(self, user_id: str, city: str):
        city_norm = city.strip().lower()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO trips (user_id, city) VALUES (?, ?)", 
                    (user_id, city_norm)
                )
                conn.commit()
            logger.info(f"MEMORY: Persisted trip to '{city}' for {user_id}")
        except sqlite3.IntegrityError:
            logger.warning(f"MEMORY: Duplicate trip write blocked for '{city}'")