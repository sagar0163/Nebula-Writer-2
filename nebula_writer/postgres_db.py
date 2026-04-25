"""
Nebula-Writer PostgreSQL Adapter for Supabase
Direct PostgreSQL connection to Supabase database
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresDB:
    """PostgreSQL database interface matching CodexDatabase API"""

    def __init__(self, connection_string: str = None, password: str = None):
        if not connection_string and not password:
            raise ValueError("POSTGRES_PASSWORD required")

        # Build connection string
        if not connection_string:
            connection_string = f"postgresql://postgres.slovnfrjidipspogvktb:{password}@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres"

        try:
            self.conn = psycopg2.connect(connection_string, cursor_factory=RealDictCursor)
            print("[OK] Connected to Supabase PostgreSQL")
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            raise

    def _query(self, sql: str, params: tuple = None) -> List[Dict]:
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            if cursor.description:
                return cursor.fetchall()
            self.conn.commit()
            return []

    def _execute(self, sql: str, params: tuple = None) -> str:
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.conn.commit()
            return str(cursor.lastrowid) if cursor.lastrowid else "0"

    # ============ ENTITY OPERATIONS ============

    def get_entities(self, entity_type: str = None) -> List[Dict]:
        if entity_type:
            return self._query("SELECT * FROM entities WHERE entity_type = %s", (entity_type,))
        return self._query("SELECT * FROM entities")

    def get_entity(self, entity_id: str) -> Optional[Dict]:
        result = self._query("SELECT * FROM entities WHERE id = %s", (entity_id,))
        return dict(result[0]) if result else None

    def add_entity(
        self,
        name: str,
        entity_type: str,
        description: str = None,
        current_location: str = None,
        is_alive: bool = True,
        image_url: str = None,
    ) -> str:
        return self._execute(
            """
            INSERT INTO entities (name, entity_type, description, current_location, is_alive, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (name, entity_type, description, current_location, is_alive, image_url),
        )

    def get_attributes(self, entity_id: str) -> List[Dict]:
        return self._query("SELECT * FROM attributes WHERE entity_id = %s", (entity_id,))

    def get_relationships(self, entity_id: str = None) -> List[Dict]:
        if entity_id:
            return self._query("SELECT * FROM relationships WHERE from_entity_id = %s", (entity_id,))
        return self._query("SELECT * FROM relationships")

    def get_events(self, chapter: int = None) -> List[Dict]:
        if chapter:
            return self._query("SELECT * FROM events WHERE chapter = %s", (chapter,))
        return self._query("SELECT * FROM events")

    def get_chapters(self) -> List[Dict]:
        return self._query("SELECT * FROM chapters ORDER BY number")

    def get_chapter(self, chapter_id: str = None, number: int = None) -> Optional[Dict]:
        if chapter_id:
            result = self._query("SELECT * FROM chapters WHERE id = %s", (chapter_id,))
        elif number:
            result = self._query("SELECT * FROM chapters WHERE number = %s", (number,))
        else:
            return None
        return dict(result[0]) if result else None

    def get_stats(self) -> Dict:
        try:
            entities = self._query("SELECT entity_type, COUNT(*) as count FROM entities GROUP BY entity_type")
            chapters = self._query("SELECT COUNT(*) as count FROM chapters")
            relationships = self._query("SELECT COUNT(*) as count FROM relationships")
            events = self._query("SELECT COUNT(*) as count FROM events")
            words = self._query("SELECT SUM(word_count) as total FROM chapters")

            return {
                "total_entities": sum(e["count"] for e in entities),
                "entities_by_type": {e["entity_type"]: e["count"] for e in entities},
                "total_chapters": chapters[0]["count"] if chapters else 0,
                "total_relationships": relationships[0]["count"] if relationships else 0,
                "total_events": events[0]["count"] if events else 0,
                "total_words": words[0]["total"] if words and words[0]["total"] else 0,
            }
        except Exception as e:
            print(f"Stats error: {e}")
            return {
                "total_entities": 0,
                "entities_by_type": {},
                "total_chapters": 0,
                "total_relationships": 0,
                "total_events": 0,
                "total_words": 0,
            }

    def add_chapter(self, number: int, title: str = None, content: str = "") -> str:
        return self._execute(
            """
            INSERT INTO chapters (number, title, content, word_count)
            VALUES (%s, %s, %s, %s)
        """,
            (number, title, content, len(content.split()) if content else 0),
        )

    def update_chapter(self, chapter_id: str, content: str = None, title: str = None, summary: str = None) -> bool:
        updates = []
        params = []
        if content is not None:
            updates.append("content = %s")
            params.append(content)
            updates.append("word_count = %s")
            params.append(len(content.split()))
        if title is not None:
            updates.append("title = %s")
            params.append(title)
        if summary is not None:
            updates.append("summary = %s")
            params.append(summary)
        updates.append("updated_at = %s")
        params.append(datetime.now().isoformat())
        params.append(chapter_id)

        self._query(f"UPDATE chapters SET {', '.join(updates)} WHERE id = %s", tuple(params))
        return True

    def search(self, query: str) -> Dict:
        q = f"%{query}%"
        return {
            "entities": self._query("SELECT * FROM entities WHERE name LIKE %s OR description LIKE %s", (q, q)),
            "chapters": self._query("SELECT * FROM chapters WHERE title LIKE %s OR content LIKE %s", (q, q)),
            "events": self._query("SELECT * FROM events WHERE title LIKE %s OR description LIKE %s", (q, q)),
        }

    # ============ PLOT/WORLD ============

    def get_plot_threads(self, status: str = None) -> List[Dict]:
        if status:
            return self._query("SELECT * FROM plot_threads WHERE status = %s", (status,))
        return self._query("SELECT * FROM plot_threads")

    def add_plot_thread(
        self, title: str, description: str = None, planted_chapter: int = None, importance: str = "normal"
    ) -> str:
        return self._execute(
            """
            INSERT INTO plot_threads (title, description, planted_chapter, importance, status)
            VALUES (%s, %s, %s, %s, 'planted')
        """,
            (title, description, planted_chapter, importance),
        )

    def resolve_plot_thread(self, thread_id: str, resolved_chapter: int = None) -> bool:
        self._query(
            "UPDATE plot_threads SET status = 'resolved', resolved_chapter = %s WHERE id = %s",
            (resolved_chapter, thread_id),
        )
        return True

    def get_foreshadowing(self, plot_thread_id: str = None, unfulfilled_only: bool = True) -> List[Dict]:
        if plot_thread_id:
            if unfulfilled_only:
                return self._query(
                    "SELECT * FROM foreshadowing WHERE plot_thread_id = %s AND fulfilled = false", (plot_thread_id,)
                )
            return self._query("SELECT * FROM foreshadowing WHERE plot_thread_id = %s", (plot_thread_id,))
        if unfulfilled_only:
            return self._query("SELECT * FROM foreshadowing WHERE fulfilled = false")
        return self._query("SELECT * FROM foreshadowing")

    def add_foreshadowing(
        self, plot_thread_id: str, chapter_id: int, content: str, hint_level: str = "subtle", payoff_chapter: int = None
    ) -> str:
        return self._execute(
            """
            INSERT INTO foreshadowing (plot_thread_id, chapter_id, content, hint_level, payoff_expected_chapter)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (plot_thread_id, chapter_id, content, hint_level, payoff_chapter),
        )

    def get_world_rules(self, category: str = None) -> List[Dict]:
        if category:
            return self._query("SELECT * FROM world_rules WHERE category = %s", (category,))
        return self._query("SELECT * FROM world_rules")

    def add_world_rule(
        self, category: str, rule: str, description: str = None, exceptions: str = None, applies_to: str = None
    ) -> str:
        return self._execute(
            """
            INSERT INTO world_rules (category, rule, description, exceptions, applies_to_entities)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (category, rule, description, exceptions, applies_to),
        )

    def get_consistency_issues(self, chapter_id: str = None, unresolved_only: bool = False) -> List[Dict]:
        if chapter_id:
            return self._query("SELECT * FROM consistency_issues WHERE chapter_id = %s", (chapter_id,))
        if unresolved_only:
            return self._query("SELECT * FROM consistency_issues WHERE resolved = false")
        return self._query("SELECT * FROM consistency_issues")

    def add_consistency_issue(
        self,
        chapter_id: str = None,
        entity_id: str = None,
        issue_type: str = "",
        description: str = "",
        severity: str = "medium",
    ) -> str:
        return self._execute(
            """
            INSERT INTO consistency_issues (chapter_id, entity_id, issue_type, description, severity)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (chapter_id, entity_id, issue_type, description, severity),
        )

    def resolve_consistency_issue(self, issue_id: str) -> bool:
        self._query("UPDATE consistency_issues SET resolved = true WHERE id = %s", (issue_id,))
        return True

    def run_consistency_check(self) -> List[Dict]:
        return []

    def get_templates(self) -> List[Dict]:
        return self._query("SELECT * FROM story_templates")

    def get_template(self, template_id: str) -> Optional[Dict]:
        result = self._query("SELECT * FROM story_templates WHERE id = %s", (template_id,))
        return dict(result[0]) if result else None

    def get_versions(self, chapter_id: str) -> List[Dict]:
        return self._query(
            "SELECT * FROM chapter_versions WHERE chapter_id = %s ORDER BY created_at DESC", (chapter_id,)
        )

    def get_version(self, version_id: str) -> Optional[Dict]:
        result = self._query("SELECT * FROM chapter_versions WHERE id = %s", (version_id,))
        return dict(result[0]) if result else None

    def save_version(self, chapter_id: str, content: str) -> str:
        return self._execute(
            """
            INSERT INTO chapter_versions (chapter_id, content, word_count)
            VALUES (%s, %s, %s)
        """,
            (chapter_id, content, len(content.split()) if content else 0),
        )

    def get_character_knowledge(self, entity_id: str, chapter_id: str = None) -> List[Dict]:
        if chapter_id:
            return self._query(
                "SELECT * FROM character_knowledge WHERE entity_id = %s AND chapter_id = %s", (entity_id, chapter_id)
            )
        return self._query("SELECT * FROM character_knowledge WHERE entity_id = %s", (entity_id,))

    def update_character_knowledge(self, entity_id: str, chapter_id: str, knowledge: str) -> str:
        return self._execute(
            """
            INSERT INTO character_knowledge (entity_id, chapter_id, knowledge)
            VALUES (%s, %s, %s)
        """,
            (entity_id, chapter_id, knowledge),
        )

    def extract_entities_from_text(self, text: str) -> Dict:
        import re

        re.findall(r"\b([A-Z][a-z]+)\b", text)
        return {"characters": [], "locations": [], "items": []}

    def delete_entity(self, entity_id: str) -> bool:
        self._query("DELETE FROM entities WHERE id = %s", (entity_id,))
        return True

    def delete_relationship(self, rel_id: str) -> bool:
        self._query("DELETE FROM relationships WHERE id = %s", (rel_id,))
        return True

    def delete_chapter(self, chapter_id: str) -> bool:
        self._query("DELETE FROM chapters WHERE id = %s", (chapter_id,))
        return True

    def add_attribute(self, entity_id: str, key: str, value: str) -> str:
        return self._execute(
            "INSERT INTO attributes (entity_id, key, value) VALUES (%s, %s, %s)", (entity_id, key, value)
        )

    def delete_attribute(self, attr_id: str) -> bool:
        self._query("DELETE FROM attributes WHERE id = %s", (attr_id,))
        return True

    def add_relationship(
        self, from_id: str, to_id: str, rel_type: str, strength: float = 0.5, description: str = None
    ) -> str:
        return self._execute(
            """
            INSERT INTO relationships (from_entity_id, to_entity_id, relationship_type, strength, description)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (from_id, to_id, rel_type, strength, description),
        )

    def add_event(
        self, title: str, description: str = None, chapter: int = None, scene: str = None, significance: str = "normal"
    ) -> str:
        return self._execute(
            """
            INSERT INTO events (title, description, chapter, scene, significance)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (title, description, chapter, scene, significance),
        )

    def close(self):
        if self.conn:
            self.conn.close()


def create_postgres_db(password: str = None) -> PostgresDB:
    """Create PostgreSQL database instance"""
    return PostgresDB(password=os.environ.get("POSTGRES_PASSWORD") or password)
