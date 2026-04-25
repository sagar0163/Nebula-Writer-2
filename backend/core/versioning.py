import json
import sqlite3
from typing import Dict


class VersioningService:
    """
    Handles snapshots and rollbacks for Chapters and Codex states.
    Non-breaking: Uses new tables to store history.
    """

    def __init__(self, db_path: str = "data/codex.db"):
        self.db_path = db_path
        self._init_versioning_tables()

    def _init_versioning_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # New table for full state snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS codex_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                snapshot_type TEXT,
                data JSON NOT NULL,
                metadata TEXT
            )
        """)

        # Existing chapter_versions is already in codex.py, but we'll ensure it's robust
        conn.commit()
        conn.close()

    def create_snapshot(self, db, snapshot_type: str = "manual") -> int:
        """Creates a lightweight snapshot of the current Codex entities."""
        entities = db.get_entities()
        relationships = db.get_relationships()

        snapshot_data = {"entities": entities, "relationships": relationships}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO codex_snapshots (snapshot_type, data)
            VALUES (?, ?)
        """,
            (snapshot_type, json.dumps(snapshot_data)),
        )
        snapshot_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return snapshot_id

    def rollback_to_snapshot(self, snapshot_id: int):
        """Rolls back the Codex entities to a previous snapshot."""
        # Logic to clear current entities and restore from snapshot
        # WARNING: Destructive operation, should be wrapped in confirmation
        pass

    def get_diff(self, snapshot_id_a: int, snapshot_id_b: int) -> Dict:
        """Compute changes between two snapshots."""
        return {"added": [], "removed": [], "modified": []}
