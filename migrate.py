"""
Nebula-Writer Migration Script
Migrate data between versions
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent / "backend"))
from codex import CodexDatabase


def backup_database(db_path: str, backup_dir: str = "backups"):
    """Create a backup of the database"""
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_path / f"codex_backup_{timestamp}.db"
    
    shutil.copy2(db_path, backup_file)
    print(f"✅ Backed up to: {backup_file}")
    return str(backup_file)


def export_to_json(db_path: str, output_file: str):
    """Export database to JSON"""
    db = CodexDatabase(db_path)
    
    data = {
        "exported": datetime.now().isoformat(),
        "entities": db.get_entities(),
        "relationships": db.get_relationships(),
        "events": db.get_events(),
        "chapters": db.get_chapters()
    }
    
    # Add attributes for each entity
    for entity in data["entities"]:
        entity["attributes"] = db.get_attributes(entity["id"])
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Exported to: {output_file}")
    return data


def import_from_json(db_path: str, input_file: str):
    """Import data from JSON"""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    db = CodexDatabase(db_path)
    
    # Import entities
    entity_id_map = {}
    for entity in data.get("entities", []):
        old_id = entity["id"]
        new_id = db.add_entity(
            name=entity["name"],
            entity_type=entity["type"],
            description=entity.get("description"),
            current_location=entity.get("current_location"),
            is_alive=entity.get("is_alive", True)
        )
        entity_id_map[old_id] = new_id
        
        # Import attributes
        for attr in entity.get("attributes", []):
            db.add_attribute(new_id, attr["key"], attr["value"])
    
    # Import relationships
    for rel in data.get("relationships", []):
        from_id = entity_id_map.get(rel["from_entity_id"])
        to_id = entity_id_map.get(rel["to_entity_id"])
        if from_id and to_id:
            db.add_relationship(
                from_id=from_id,
                to_id=to_id,
                rel_type=rel["relationship_type"],
                strength=rel.get("strength", 0.5),
                description=rel.get("description")
            )
    
    # Import chapters
    for ch in data.get("chapters", []):
        db.add_chapter(
            number=ch["number"],
            title=ch.get("title"),
            content=ch.get("content", "")
        )
    
    # Import events
    for ev in data.get("events", []):
        db.add_event(
            title=ev["title"],
            description=ev.get("description"),
            chapter=ev.get("chapter"),
            scene=ev.get("scene"),
            significance=ev.get("significance", "normal")
        )
    
    print(f"✅ Imported from: {input_file}")
    print(f"   - {len(data.get('entities', []))} entities")
    print(f"   - {len(data.get('relationships', []))} relationships")
    print(f"   - {len(data.get('chapters', []))} chapters")
    print(f"   - {len(data.get('events', []))} events")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Nebula-Writer Migration Tool")
    subparsers = parser.add_subparsers()
    
    # Backup
    backup_parser = subparsers.add_parser("backup", help="Backup database")
    backup_parser.add_argument("--db", default="data/codex.db", help="Database path")
    backup_parser.add_argument("--dir", default="backups", help="Backup directory")
    backup_parser.set_defaults(func=lambda args: backup_database(args.db, args.dir))
    
    # Export
    export_parser = subparsers.add_parser("export", help="Export to JSON")
    export_parser.add_argument("--db", default="data/codex.db", help="Database path")
    export_parser.add_argument("--output", default="export.json", help="Output file")
    export_parser.set_defaults(func=lambda args: export_to_json(args.db, args.output))
    
    # Import
    import_parser = subparsers.add_parser("import", help="Import from JSON")
    import_parser.add_argument("--db", default="data/codex.db", help="Database path")
    import_parser.add_argument("--input", required=True, help="Input file")
    import_parser.set_defaults(func=lambda args: import_from_json(args.db, args.input))
    
    args = parser.parse_args()
    
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
