"""
Nebula-Writer Migration Script
Migrate data between versions
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from nebula_writer.supabase_db import SupabaseDB as CodexDatabase


def backup_database(db_path: str, backup_dir: str = "backups"):
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_path / f"codex_backup_{timestamp}.db"

    shutil.copy2(db_path, backup_file)
    print(f"Backed up to: {backup_file}")
    return str(backup_file)


def export_to_json(db_path: str, output_file: str):
    db = CodexDatabase()

    data = {
        "exported": datetime.now().isoformat(),
        "entities": db.get_entities(),
        "relationships": db.get_relationships(),
        "events": db.get_events(),
        "chapters": db.get_chapters(),
    }

    for entity in data["entities"]:
        entity["attributes"] = db.get_attributes(entity["id"])

    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Exported to: {output_file}")
    return data


def import_from_json(db_path: str, input_file: str):
    with open(input_file, "r") as f:
        data = json.load(f)

    db = CodexDatabase()

    entity_id_map = {}

    for entity in data.get("entities", []):
        new_id = db.add_entity(
            name=entity["name"],
            entity_type=entity.get("entity_type", entity.get("type", "character")),
            description=entity.get("description", ""),
        )
        entity_id_map[entity["id"]] = new_id

        for attr in entity.get("attributes", []):
            db.add_attribute(new_id, attr["key"], attr["value"])

    for rel in data.get("relationships", []):
        from_id = entity_id_map.get(rel["from_entity_id"])
        to_id = entity_id_map.get(rel["to_entity_id"])
        if from_id and to_id:
            db.add_relationship(from_id, to_id, rel.get("relationship_type", "related"))

    for chapter in data.get("chapters", []):
        db.add_chapter(
            number=chapter["number"],
            title=chapter.get("title", ""),
            content=chapter.get("content", ""),
        )

    for event in data.get("events", []):
        db.add_event(
            title=event["title"],
            description=event.get("description", ""),
            chapter=event.get("chapter"),
        )

    print(f"Imported from: {input_file}")
    return data


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python migrate.py <export|import> <json_file> [db_path]")
        sys.exit(1)

    command = sys.argv[1]
    json_file = sys.argv[2]
    db_path = sys.argv[3] if len(sys.argv) > 3 else "data/codex.db"

    if command == "export":
        export_to_json(db_path, json_file)
    elif command == "import":
        import_from_json(db_path, json_file)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
