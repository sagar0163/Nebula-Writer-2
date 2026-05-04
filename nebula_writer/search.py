"""
Nebula-Writer Search & Filter Module
Advanced search and filtering capabilities
"""

from typing import Dict, List

from nebula_writer.codex import CodexDatabase


class SearchEngine:
    """Advanced search across the Codex"""

    def __init__(self, db: CodexDatabase):
        self.db = db

    def search_all(self, query: str) -> Dict:
        """Search everything"""
        query = query.lower()
        results = {"entities": [], "chapters": [], "events": [], "relationships": []}

        # Search entities
        for e in self.db.get_entities():
            if query in e["name"].lower() or query in (e.get("description") or "").lower():
                e["attributes"] = self.db.get_attributes(e["id"])
                results["entities"].append(e)

        # Search chapters
        for ch in self.db.get_chapters():
            if (
                query in (ch.get("title") or "").lower()
                or query in (ch.get("content") or "").lower()
                or query in (ch.get("summary") or "").lower()
            ):
                results["chapters"].append(ch)

        # Search events
        for ev in self.db.get_events():
            if query in ev["title"].lower() or query in (ev.get("description") or "").lower():
                results["events"].append(ev)

        # Search relationships
        for rel in self.db.get_relationships():
            if query in rel.get("relationship_type", "").lower() or query in (rel.get("description") or "").lower():
                results["relationships"].append(rel)

        return results

    def filter_entities(
        self, entity_type: str = None, has_attributes: bool = None, is_alive: bool = None, location: str = None
    ) -> List[Dict]:
        """Filter entities by criteria"""
        entities = self.db.get_entities(entity_type)

        filtered = []
        for e in entities:
            if has_attributes is not None:
                attrs = self.db.get_attributes(e["id"])
                if has_attributes and not attrs:
                    continue
                if not has_attributes and attrs:
                    continue

            if is_alive is not None:
                if e.get("is_alive", True) != is_alive:
                    continue

            if location:
                if location.lower() not in (e.get("current_location") or "").lower():
                    continue

            filtered.append(e)

        return filtered

    def find_related_entities(self, entity_id: int) -> Dict:
        """Find all entities related to a given entity"""
        entity = self.db.get_entity(entity_id)
        if not entity:
            return {}

        relationships = self.db.get_relationships(entity_id)

        related = []
        for rel in relationships:
            if rel["from_entity_id"] == entity_id:
                related.append(
                    {
                        "entity": self.db.get_entity(rel["to_entity_id"]),
                        "relationship": rel["relationship_type"],
                        "direction": "outgoing",
                    }
                )
            else:
                related.append(
                    {
                        "entity": self.db.get_entity(rel["from_entity_id"]),
                        "relationship": rel["relationship_type"],
                        "direction": "incoming",
                    }
                )

        return {"entity": entity, "related": related}

    def get_timeline(self) -> List[Dict]:
        """Get chronological timeline of events"""
        events = self.db.get_events()
        chapters = self.db.get_chapters()

        timeline = []

        for ev in events:
            timeline.append(
                {
                    "type": "event",
                    "chapter": ev.get("chapter"),
                    "title": ev["title"],
                    "description": ev.get("description"),
                    "significance": ev.get("significance", "normal"),
                    "timestamp": ev.get("timestamp"),
                }
            )

        for ch in chapters:
            timeline.append(
                {
                    "type": "chapter",
                    "chapter": ch["number"],
                    "title": ch.get("title"),
                    "word_count": ch.get("word_count", 0),
                    "summary": ch.get("summary"),
                    "timestamp": ch.get("created_at"),
                }
            )

        # Sort by chapter, then by type
        timeline.sort(key=lambda x: (x.get("chapter") or 0, x["type"]))

        return timeline

    def get_story_stats(self) -> Dict:
        """Get comprehensive story statistics"""
        stats = self.db.get_stats()

        # Word count by chapter
        chapters = self.db.get_chapters()
        word_counts = [ch.get("word_count", 0) for ch in chapters]

        stats["writing_progress"] = {
            "total_words": sum(word_counts),
            "average_words_per_chapter": sum(word_counts) // len(word_counts) if word_counts else 0,
            "longest_chapter": max(word_counts) if word_counts else 0,
            "shortest_chapter": min(word_counts) if word_counts else 0,
        }

        # Entity stats
        entities = self.db.get_entities()
        alive_count = sum(1 for e in entities if e.get("is_alive", True))
        dead_count = len(entities) - alive_count

        stats["entity_status"] = {"alive": alive_count, "deceased": dead_count}

        return stats


if __name__ == "__main__":
    db = CodexDatabase()
    search = SearchEngine(db)

    print("Story Stats:", search.get_story_stats())
    print("Timeline:", search.get_timeline())
