"""
Paisano Conversion Repository - stores product conversion factors in SQLite
"""
import sqlite3
from pathlib import Path
from typing import Dict


class PaisanoConversionRepository:
    """SQLite-backed repository for El Paisano product conversion factors"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_table()

    def _ensure_table(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS paisano_conversions (
                    name TEXT PRIMARY KEY,
                    factor REAL NOT NULL
                )
                """
            )
            conn.commit()

    def get_all(self) -> Dict[str, float]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT name, factor FROM paisano_conversions")
            return {row[0]: row[1] for row in cur.fetchall()}

    def upsert(self, name: str, factor: float):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO paisano_conversions (name, factor)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET factor=excluded.factor
                """,
                (name, factor),
            )
            conn.commit()

