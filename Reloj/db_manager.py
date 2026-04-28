import sqlite3
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "clock_data.db"


class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._initialize_db()
        logger.info("DatabaseManager initialized at %s", self.db_path)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS alarms (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    label       TEXT    NOT NULL DEFAULT '',
                    hour        INTEGER NOT NULL,
                    minute      INTEGER NOT NULL,
                    enabled     INTEGER NOT NULL DEFAULT 1,
                    created_at  TEXT    DEFAULT (datetime('now'))
                );
            """)
        logger.debug("Database tables verified/created.")

    def save_preference(self, key: str, value: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO preferences (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )
        logger.debug("Preference saved: %s = %s", key, value)

    def load_preference(self, key: str, default: str = "") -> str:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT value FROM preferences WHERE key = ?", (key,)
            ).fetchone()
        return row["value"] if row else default

    def load_all_preferences(self) -> dict[str, str]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT key, value FROM preferences").fetchall()
        return {row["key"]: row["value"] for row in rows}

    def add_alarm(self, hour: int, minute: int, label: str = "") -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO alarms (hour, minute, label) VALUES (?, ?, ?)",
                (hour, minute, label),
            )
            alarm_id = cursor.lastrowid
        logger.info("Alarm added: id=%s %02d:%02d (%s)", alarm_id, hour, minute, label)
        return alarm_id

    def delete_alarm(self, alarm_id: int) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM alarms WHERE id = ?", (alarm_id,))
        logger.info("Alarm deleted: id=%s", alarm_id)

    def toggle_alarm(self, alarm_id: int, enabled: bool) -> None:
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE alarms SET enabled = ? WHERE id = ?",
                (1 if enabled else 0, alarm_id),
            )

    def load_alarms(self) -> list[dict]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT id, label, hour, minute, enabled FROM alarms "
                "ORDER BY hour, minute"
            ).fetchall()
        return [dict(row) for row in rows]