import json
from typing import Dict

from nebula_writer.supabase_db import SupabaseDB as CodexDatabase


class VersioningService:
    """
    Handles snapshots and rollbacks for Chapters and Codex states.
    """

    def __init__(self, db: CodexDatabase = None):
        self.db = db or CodexDatabase()

    def create_snapshot(self, db=None, snapshot_type: str = "manual") -> int:
        """Creates a lightweight snapshot of the current Codex entities."""
        db = db or self.db
        entities = db.get_entities()
        relationships = db.get_relationships()

        snapshot_data = {"entities": entities, "relationships": relationships}

        result = db._query(
            "INSERT INTO codex_snapshots (snapshot_type, data) VALUES (%s, %s) RETURNING id",
            (snapshot_type, json.dumps(snapshot_data)),
        )
        return int(result[0]['id']) if result else 0

    def rollback_to_snapshot(self, snapshot_id: str):
        pass

    def get_narrative_diff(self, snapshot_id_a: str, snapshot_id_b: str) -> Dict:
        result_a = self.db._query("SELECT data FROM codex_snapshots WHERE id = %s", (snapshot_id_a,))
        result_b = self.db._query("SELECT data FROM codex_snapshots WHERE id = %s", (snapshot_id_b,))
        data_a = json.loads(result_a[0]['data']) if result_a else {"entities": [], "relationships": []}
        data_b = json.loads(result_b[0]['data']) if result_b else {"entities": [], "relationships": []}

        diff = {"entity_changes": [], "relationship_changes": [], "narrative_drift_detected": False}

        entities_a = {e["id"]: e for e in data_a["entities"]}
        entities_b = {e["id"]: e for e in data_b["entities"]}

        for eid, e_b in entities_b.items():
            if eid not in entities_a:
                diff["entity_changes"].append(f"Added character: {e_b['name']}")
            elif e_b["description"] != entities_a[eid]["description"]:
                diff["entity_changes"].append(f"Modified character: {e_b['name']} (Potential drift in motivation)")
                diff["narrative_drift_detected"] = True

        return diff

    def get_diff(self, snapshot_id_a: str, snapshot_id_b: str) -> Dict:
        return {"added": [], "removed": [], "modified": []}
