"""
Nebula-Writer Unified Supabase Database Layer
Single source of truth for all database operations.
Replaces codex.py, postgres_db.py, and supabase_client.py
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor


class SupabaseDB:
    """Unified Supabase/PostgreSQL database interface"""

    def __init__(self, connection_string: str = None):
        if not connection_string:
            connection_string = os.environ.get("POSTGRES_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("POSTGRES_CONNECTION_STRING environment variable is required")

        self._connection_string = connection_string
        self._connect()

    def _connect(self):
        try:
            self.conn = psycopg2.connect(self._connection_string, cursor_factory=RealDictCursor)
            self.conn.autocommit = False
            print("[OK] Connected to Supabase PostgreSQL")
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            raise

    def _ensure_connection(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            self._connect()

    def _query(self, sql: str, params: tuple = None) -> List[Dict]:
        self._ensure_connection()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, params)
                if cursor.description:
                    return [dict(row) for row in cursor.fetchall()]
                self.conn.commit()
                return []
        except psycopg2.Error:
            self.conn.rollback()
            raise

    def _execute_returning_id(self, sql: str, params: tuple = None) -> str:
        self._ensure_connection()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql + " RETURNING id", params)
                self.conn.commit()
                result = cursor.fetchone()
                return str(result['id']) if result else "0"
        except psycopg2.Error:
            self.conn.rollback()
            raise

    def _rowcount(self, sql: str, params: tuple = None) -> int:
        self._ensure_connection()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, params)
                self.conn.commit()
                return cursor.rowcount
        except psycopg2.Error:
            self.conn.rollback()
            raise

    # ============ ENTITIES ============

    def get_entities(self, entity_type: str = None) -> List[Dict]:
        if entity_type:
            return self._query("SELECT * FROM entities WHERE type = %s ORDER BY name", (entity_type,))
        return self._query("SELECT * FROM entities ORDER BY type, name")

    def get_entity(self, entity_id: str) -> Optional[Dict]:
        result = self._query("SELECT * FROM entities WHERE id = %s", (entity_id,))
        return result[0] if result else None

    def add_entity(
        self,
        name: str,
        entity_type: str,
        description: str = None,
        current_location: str = None,
        is_alive: bool = True,
        image_url: str = None,
    ) -> str:
        return self._execute_returning_id(
            """INSERT INTO entities (name, type, description, current_location, is_alive, image_url)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, entity_type, description, current_location, is_alive, image_url),
        )

    def update_entity(self, entity_id: str, **kwargs) -> bool:
        allowed = ["name", "description", "is_alive", "current_location", "image_url"]
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return False
        set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [entity_id]
        return self._rowcount(f"UPDATE entities SET {set_clause}, updated_at = NOW() WHERE id = %s", values) > 0

    def delete_entity(self, entity_id: str) -> bool:
        return self._rowcount("DELETE FROM entities WHERE id = %s", (entity_id,)) > 0

    # ============ ATTRIBUTES ============

    def add_attribute(self, entity_id: str, key: str, value: str) -> str:
        return self._execute_returning_id(
            "INSERT INTO attributes (entity_id, key, value) VALUES (%s, %s, %s)",
            (entity_id, key, value),
        )

    def get_attributes(self, entity_id: str) -> List[Dict]:
        return self._query("SELECT * FROM attributes WHERE entity_id = %s ORDER BY key", (entity_id,))

    def delete_attribute(self, attr_id: str) -> bool:
        return self._rowcount("DELETE FROM attributes WHERE id = %s", (attr_id,)) > 0

    # ============ RELATIONSHIPS ============

    def add_relationship(
        self, from_id: str, to_id: str, rel_type: str, strength: float = 0.5, description: str = None
    ) -> str:
        return self._execute_returning_id(
            """INSERT INTO relationships (from_entity_id, to_entity_id, relationship_type, strength, description)
               VALUES (%s, %s, %s, %s, %s)""",
            (from_id, to_id, rel_type, strength, description),
        )

    def get_relationships(self, entity_id: str = None) -> List[Dict]:
        if entity_id:
            return self._query(
                """SELECT r.*, e1.name as from_name, e1.type as from_type,
                          e2.name as to_name, e2.type as to_type
                   FROM relationships r
                   JOIN entities e1 ON r.from_entity_id = e1.id
                   JOIN entities e2 ON r.to_entity_id = e2.id
                   WHERE r.from_entity_id = %s OR r.to_entity_id = %s
                   ORDER BY r.strength DESC""",
                (entity_id, entity_id),
            )
        return self._query(
            """SELECT r.*, e1.name as from_name, e1.type as from_type,
                      e2.name as to_name, e2.type as to_type
               FROM relationships r
               JOIN entities e1 ON r.from_entity_id = e1.id
               JOIN entities e2 ON r.to_entity_id = e2.id
               ORDER BY r.strength DESC"""
        )

    def delete_relationship(self, rel_id: str) -> bool:
        return self._rowcount("DELETE FROM relationships WHERE id = %s", (rel_id,)) > 0

    # ============ EVENTS ============

    def add_event(
        self, title: str, description: str = None, chapter: int = None, scene: str = None, significance: str = "normal"
    ) -> str:
        return self._execute_returning_id(
            """INSERT INTO events (title, description, chapter, scene, significance)
               VALUES (%s, %s, %s, %s, %s)""",
            (title, description, chapter, scene, significance),
        )

    def get_events(self, chapter: int = None, chapter_id: str = None) -> List[Dict]:
        # If chapter_id is a UUID, we need to get the chapter number first
        chapter_num = chapter
        if chapter_id and isinstance(chapter_id, str) and len(chapter_id) > 10 and '-' in chapter_id:
            chap = self.get_chapter(chapter_id=chapter_id)
            if chap:
                chapter_num = chap.get("number")
        
        if chapter_num is not None:
            return self._query("SELECT * FROM events WHERE chapter = %s ORDER BY timestamp", (chapter_num,))
        return self._query("SELECT * FROM events ORDER BY timestamp DESC")

    # ============ CHAPTERS ============

    def add_chapter(self, number: int, title: str = None, content: str = "") -> str:
        return self._execute_returning_id(
            "INSERT INTO chapters (number, title, content, word_count) VALUES (%s, %s, %s, %s)",
            (number, title, content, len(content.split()) if content else 0),
        )

    def get_chapters(self) -> List[Dict]:
        return self._query("SELECT * FROM chapters ORDER BY number")

    def get_chapter(self, chapter_id: str = None, number: int = None) -> Optional[Dict]:
        # If chapter_id looks like a UUID (contains hyphens and length > 10), query by id
        # Otherwise if number is provided, query by number
        if chapter_id and isinstance(chapter_id, str) and len(chapter_id) > 10 and '-' in chapter_id:
            result = self._query("SELECT * FROM chapters WHERE id = %s", (chapter_id,))
        elif number is not None:
            result = self._query("SELECT * FROM chapters WHERE number = %s", (number,))
        else:
            return None
        return result[0] if result else None

    def update_chapter(self, chapter_id: str, content: str = None, title: str = None, summary: str = None) -> bool:
        updates = []
        params = []
        if content is not None:
            updates.extend(["content = %s", "word_count = %s"])
            params.extend([content, len(content.split())])
        if title is not None:
            updates.append("title = %s")
            params.append(title)
        if summary is not None:
            updates.append("summary = %s")
            params.append(summary)
        if not updates:
            return False
        updates.append("updated_at = NOW()")
        params.append(chapter_id)
        return self._rowcount(f"UPDATE chapters SET {', '.join(updates)} WHERE id = %s", params) > 0

    def delete_chapter(self, chapter_id: str) -> bool:
        return self._rowcount("DELETE FROM chapters WHERE id = %s", (chapter_id,)) > 0

    # ============ SCENES ============

    def add_scene(self, chapter_id: str, number: int, beat: str = None, content: str = "") -> str:
        return self._execute_returning_id(
            "INSERT INTO scenes (chapter_id, number, beat, content) VALUES (%s, %s, %s, %s)",
            (chapter_id, number, beat, content),
        )

    def get_scenes(self, chapter_id: str) -> List[Dict]:
        return self._query("SELECT * FROM scenes WHERE chapter_id = %s ORDER BY number", (chapter_id,))

    # ============ STATISTICS ============

    def get_stats(self) -> Dict:
        try:
            entities = self._query("SELECT type, COUNT(*) as count FROM entities GROUP BY type")
            chapters = self._query("SELECT COUNT(*) as count FROM chapters")
            relationships = self._query("SELECT COUNT(*) as count FROM relationships")
            events = self._query("SELECT COUNT(*) as count FROM events")
            words = self._query("SELECT SUM(word_count) as total FROM chapters")
            return {
                "total_entities": sum(e["count"] for e in entities),
                "entities_by_type": {e["type"]: e["count"] for e in entities},
                "total_chapters": chapters[0]["count"] if chapters else 0,
                "total_relationships": relationships[0]["count"] if relationships else 0,
                "total_events": events[0]["count"] if events else 0,
                "total_words": words[0]["total"] if words and words[0]["total"] else 0,
            }
        except Exception as e:
            print(f"Stats error: {e}")
            return {"total_entities": 0, "entities_by_type": {}, "total_chapters": 0,
                    "total_relationships": 0, "total_events": 0, "total_words": 0}

    # ============ SEARCH ============

    def search(self, query: str) -> Dict:
        q = f"%{query}%"
        return {
            "entities": self._query(
                "SELECT * FROM entities WHERE name ILIKE %s OR description ILIKE %s LIMIT 10", (q, q)),
            "chapters": self._query(
                "SELECT * FROM chapters WHERE title ILIKE %s OR content ILIKE %s OR summary ILIKE %s LIMIT 10",
                (q, q, q)),
            "events": self._query(
                "SELECT * FROM events WHERE title ILIKE %s OR description ILIKE %s LIMIT 10", (q, q)),
        }

    def fulltext_search(self, query: str, user_id: str = None) -> Dict:
        if user_id:
            result = self._query("SELECT * FROM search_story(%s, %s::uuid)", (query, user_id))
        else:
            return self.search(query)
        chapters = [r for r in result if r["source"] == "chapter"]
        entities = [r for r in result if r["source"] == "entity"]
        return {"chapters": chapters, "entities": entities}

    # ============ VERSION HISTORY ============

    def save_version(self, chapter_id: str, content: str) -> str:
        return self._execute_returning_id(
            "INSERT INTO chapter_versions (chapter_id, content, word_count) VALUES (%s, %s, %s)",
            (chapter_id, content, len(content.split()) if content else 0),
        )

    def get_versions(self, chapter_id: str) -> List[Dict]:
        return self._query(
            "SELECT * FROM chapter_versions WHERE chapter_id = %s ORDER BY created_at DESC", (chapter_id,))

    def get_version(self, version_id: str) -> Optional[Dict]:
        result = self._query("SELECT * FROM chapter_versions WHERE id = %s", (version_id,))
        return result[0] if result else None

    # ============ CHARACTER KNOWLEDGE ============

    def update_character_knowledge(self, entity_id: str, chapter_id: str, knowledge: str) -> str:
        existing = self._query(
            "SELECT id FROM character_knowledge WHERE entity_id = %s AND chapter_id = %s",
            (entity_id, chapter_id),
        )
        if existing:
            self._query("UPDATE character_knowledge SET knowledge = %s WHERE id = %s",
                        (knowledge, existing[0]['id']))
            return str(existing[0]['id'])
        return self._execute_returning_id(
            "INSERT INTO character_knowledge (entity_id, chapter_id, knowledge) VALUES (%s, %s, %s)",
            (entity_id, chapter_id, knowledge),
        )

    def get_character_knowledge(self, entity_id: str, chapter_id: str = None) -> List[Dict]:
        if chapter_id:
            return self._query(
                "SELECT * FROM character_knowledge WHERE entity_id = %s AND chapter_id <= %s ORDER BY chapter_id DESC",
                (entity_id, chapter_id),
            )
        return self._query(
            "SELECT * FROM character_knowledge WHERE entity_id = %s ORDER BY chapter_id DESC", (entity_id,))

    def delete_character_knowledge(self, knowledge_id: str) -> bool:
        return self._rowcount("DELETE FROM character_knowledge WHERE id = %s", (knowledge_id,)) > 0

    # ============ STORY TEMPLATES ============

    def get_templates(self) -> List[Dict]:
        return self._query("SELECT * FROM story_templates ORDER BY name")

    def get_template(self, template_id: str) -> Optional[Dict]:
        result = self._query("SELECT * FROM story_templates WHERE id = %s", (template_id,))
        return result[0] if result else None

    # ============ CONSISTENCY CHECKING ============

    def add_consistency_issue(
        self,
        chapter_id: str = None,
        entity_id: str = None,
        issue_type: str = "",
        description: str = "",
        severity: str = "medium",
    ) -> str:
        return self._execute_returning_id(
            """INSERT INTO consistency_issues (chapter_id, entity_id, issue_type, description, severity)
               VALUES (%s, %s, %s, %s, %s)""",
            (chapter_id, entity_id, issue_type, description, severity),
        )

    def get_consistency_issues(self, chapter_id: str = None, unresolved_only: bool = False) -> List[Dict]:
        if chapter_id:
            return self._query("SELECT * FROM consistency_issues WHERE chapter_id = %s", (chapter_id,))
        if unresolved_only:
            return self._query("SELECT * FROM consistency_issues WHERE resolved = false")
        return self._query("SELECT * FROM consistency_issues")

    def resolve_consistency_issue(self, issue_id: str) -> bool:
        return self._rowcount("UPDATE consistency_issues SET resolved = true WHERE id = %s", (issue_id,)) > 0

    def run_consistency_check(self) -> List[Dict]:
        issues = []
        chapters = self.get_chapters()
        entities = {e["id"]: e for e in self.get_entities()}
        chapter_contents_lower = [(c.get("content") or "").lower() for c in chapters]

        for entity in entities.values():
            found = any(entity["name"].lower() in content_lower for content_lower in chapter_contents_lower)
            if not found and chapters:
                issues.append({"type": "orphan_entity", "severity": "low",
                               "description": f"Entity '{entity['name']}' may not appear in any chapter"})

        events = self.get_events()
        for event in events:
            if event.get("chapter"):
                if not any(c["number"] == event["chapter"] for c in chapters):
                    issues.append({"type": "timeline_gap", "severity": "medium",
                                   "description": f"Event '{event['title']}' references non-existent Chapter {event['chapter']}"})

        for issue in issues:
            self.add_consistency_issue(issue_type=issue["type"], description=issue["description"],
                                       severity=issue["severity"])
        return issues

    # ============ AUTO-EXTRACT ENTITIES ============

    def extract_entities_from_text(self, text: str) -> Dict:
        potential_names = re.findall(r"\b([A-Z][a-z]+)\b", text)
        existing = {e["name"].lower(): e["type"] for e in self.get_entities()}
        name_counts = {}
        for name in potential_names:
            name_lower = name.lower()
            if name_lower not in existing:
                name_counts[name_lower] = name_counts.get(name_lower, 0) + 1

        extracted = {"characters": [], "locations": [], "items": []}
        for name, count in name_counts.items():
            if count >= 2:
                context = text.lower()
                if any(loc in context for loc in ["city", "street", "house", "room", "building", "town", "village"]):
                    extracted["locations"].append({"name": name.title(), "confidence": "low"})
                elif any(item in context for item in ["weapon", "key", "book", "phone", "car"]):
                    extracted["items"].append({"name": name.title(), "confidence": "low"})
                else:
                    extracted["characters"].append({"name": name.title(), "confidence": "medium"})
        return extracted

    # ============ STORY COMPASS & LOOKAHEAD ============

    def add_story_anchor(self, anchor_type: str, description: str) -> str:
        return self._execute_returning_id(
            "INSERT INTO story_anchors (type, description) VALUES (%s, %s)",
            (anchor_type, description),
        )

    def get_story_anchors(self) -> List[Dict]:
        return self._query("SELECT * FROM story_anchors")

    def update_story_anchor(self, anchor_id: str, description: str) -> bool:
        return self._rowcount(
            "UPDATE story_anchors SET description = %s, updated_at = NOW() WHERE id = %s",
            (description, anchor_id),
        ) > 0

    def add_open_tension(self, description: str, priority: str = "normal") -> str:
        return self._execute_returning_id(
            "INSERT INTO open_tensions (description, priority) VALUES (%s, %s)",
            (description, priority),
        )

    def get_open_tensions(self, status: str = "open") -> List[Dict]:
        return self._query(
            "SELECT * FROM open_tensions WHERE status = %s ORDER BY created_at DESC", (status,))

    def resolve_tension(self, tension_id: str, resolved_chapter: int) -> bool:
        return self._rowcount(
            "UPDATE open_tensions SET status = 'resolved', resolved_chapter = %s WHERE id = %s",
            (resolved_chapter, tension_id),
        ) > 0

    def update_narrative_momentum(self, score: float) -> bool:
        existing = self._query("SELECT id FROM story_compass LIMIT 1")
        if existing:
            self._query("UPDATE story_compass SET momentum_score = %s, last_updated = NOW() WHERE id = %s",
                        (score, existing[0]['id']))
        else:
            self._query("INSERT INTO story_compass (momentum_score) VALUES (%s)", (score,))
        return True

    def get_narrative_momentum(self) -> float:
        result = self._query("SELECT momentum_score FROM story_compass ORDER BY last_updated DESC LIMIT 1")
        return float(result[0]['momentum_score']) if result else 0.0

    def add_lookahead_card(
        self,
        chapter_number: int,
        title: str = None,
        intention: str = None,
        opening: str = None,
        focus: str = None,
        question: str = None,
    ) -> str:
        return self._execute_returning_id(
            """INSERT INTO lookahead_cards (chapter_number, title, scene_intention,
               opening_image, character_in_focus, story_question)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (chapter_number, title, intention, opening, focus, question),
        )

    def get_lookahead_cards(self, status: str = "draft") -> List[Dict]:
        return self._query(
            "SELECT * FROM lookahead_cards WHERE status = %s ORDER BY chapter_number", (status,))

    def update_lookahead_card_status(self, card_id: str, status: str) -> bool:
        return self._rowcount(
            "UPDATE lookahead_cards SET status = %s WHERE id = %s", (status, card_id)) > 0

    def clear_lookahead_cards(self, status: str = "draft"):
        self._query("DELETE FROM lookahead_cards WHERE status = %s", (status,))

    # ============ CONVERSATION PERSISTENCE ============

    def save_conversation(self, messages: List[Dict], user_id: str = "default") -> str:
        existing = self._query("SELECT id FROM conversations WHERE user_id = %s", (user_id,))
        messages_json = json.dumps(messages)
        now = datetime.now().isoformat()
        if existing:
            conversation_id = existing[0]['id']
            self._query(
                "UPDATE conversations SET messages = %s, updated_at = %s WHERE id = %s",
                (messages_json, now, conversation_id),
            )
            return str(conversation_id)
        return self._execute_returning_id(
            "INSERT INTO conversations (user_id, messages, updated_at) VALUES (%s, %s, %s)",
            (user_id, messages_json, now),
        )

    def load_conversation(self, user_id: str = "default") -> List[Dict]:
        result = self._query(
            "SELECT messages FROM conversations WHERE user_id = %s ORDER BY updated_at DESC LIMIT 1",
            (user_id,),
        )
        if result:
            messages = result[0]['messages']
            if isinstance(messages, str):
                return json.loads(messages)
            return messages
        return []

    # ============ STORY PLAN ============

    def get_story_plan(self) -> Optional[Dict]:
        result = self._query("SELECT * FROM story_plan ORDER BY updated_at DESC LIMIT 1")
        return result[0] if result else None

    def update_story_plan(self, plan: Dict) -> bool:
        allowed_keys = {"target_ending", "major_milestones", "thematic_focus", "arc_targets"}
        filtered = {k: v for k, v in plan.items() if k in allowed_keys}
        if not filtered:
            return False
        existing = self._query("SELECT id FROM story_plan LIMIT 1")
        if existing:
            set_clause = ", ".join([f"{k} = %s" for k in filtered.keys()])
            values = list(filtered.values()) + [existing[0]['id']]
            self._query(f"UPDATE story_plan SET {set_clause}, updated_at = NOW() WHERE id = %s", values)
        else:
            cols = ", ".join(filtered.keys())
            placeholders = ", ".join(["%s" for _ in filtered])
            self._query(f"INSERT INTO story_plan ({cols}) VALUES ({placeholders})", list(filtered.values()))
        return True

    # ============ PLOT / WORLD (v2.1) ============

    def get_plot_threads(self, status: str = None) -> List[Dict]:
        if status:
            return self._query("SELECT * FROM plot_threads WHERE status = %s ORDER BY created_at DESC", (status,))
        return self._query("SELECT * FROM plot_threads ORDER BY created_at DESC")

    def add_plot_thread(
        self, title: str, description: str = None, planted_chapter: int = None, importance: str = "normal"
    ) -> str:
        return self._execute_returning_id(
            "INSERT INTO plot_threads (title, description, planted_chapter, importance, status) VALUES (%s, %s, %s, %s, 'planted')",
            (title, description, planted_chapter, importance),
        )

    def resolve_plot_thread(self, thread_id: str, resolved_chapter: int = None) -> bool:
        return self._rowcount(
            "UPDATE plot_threads SET status = 'resolved', resolved_chapter = %s WHERE id = %s",
            (resolved_chapter, thread_id),
        ) > 0

    def get_foreshadowing(self, plot_thread_id: str = None, unfulfilled_only: bool = True) -> List[Dict]:
        if plot_thread_id:
            if unfulfilled_only:
                return self._query(
                    "SELECT * FROM foreshadowing WHERE plot_thread_id = %s AND fulfilled = false ORDER BY created_at",
                    (plot_thread_id,))
            return self._query(
                "SELECT * FROM foreshadowing WHERE plot_thread_id = %s ORDER BY created_at", (plot_thread_id,))
        if unfulfilled_only:
            return self._query("SELECT * FROM foreshadowing WHERE fulfilled = false ORDER BY created_at")
        return self._query("SELECT * FROM foreshadowing ORDER BY created_at")

    def add_foreshadowing(
        self, plot_thread_id: str, chapter_id: str, content: str,
        hint_level: str = "subtle", payoff_chapter: int = None,
    ) -> str:
        return self._execute_returning_id(
            "INSERT INTO foreshadowing (plot_thread_id, chapter_id, content, hint_level, payoff_expected_chapter) VALUES (%s, %s, %s, %s, %s)",
            (plot_thread_id, chapter_id, content, hint_level, payoff_chapter),
        )

    def get_world_rules(self, category: str = None) -> List[Dict]:
        if category:
            return self._query("SELECT * FROM world_rules WHERE category = %s ORDER BY created_at", (category,))
        return self._query("SELECT * FROM world_rules ORDER BY category, created_at")

    def add_world_rule(
        self, category: str, rule: str, description: str = None,
        exceptions: str = None, applies_to: str = None,
    ) -> str:
        return self._execute_returning_id(
            "INSERT INTO world_rules (category, rule, description, exceptions, applies_to_entities) VALUES (%s, %s, %s, %s, %s)",
            (category, rule, description, exceptions, applies_to),
        )

    def get_voice_profiles(self, entity_id: str = None) -> List[Dict]:
        if entity_id:
            return self._query("SELECT * FROM voice_profiles WHERE entity_id = %s", (entity_id,))
        return self._query("SELECT * FROM voice_profiles ORDER BY entity_id")

    # ============ VISION GAP PLAN ENTITIES ============

    def get_projects(self) -> List[Dict]:
        result = self._request("GET", "projects")
        return result if isinstance(result, list) else []

    def get_project(self, project_id: str) -> Optional[Dict]:
        result = self._request("GET", "projects", filters={"id": project_id})
        return result[0] if isinstance(result, list) and result else None

    def add_project(self, project_id: str, title: str = "Untitled Novel", author: str = "Unknown") -> str:
        data = {"id": project_id, "title": title, "author": author}
        result = self._request("POST", "projects", data=data)
        return result.get("id", project_id) if isinstance(result, dict) else project_id

    def get_characters(self, project_id: str) -> List[Dict]:
        result = self._request("GET", "characters", filters={"project_id": project_id})
        return result if isinstance(result, list) else []

    def add_character(self, project_id: str, name: str, role: str = "major", core_desire: str = "", arc_current_state: str = "") -> str:
        data = {
            "project_id": project_id,
            "name": name,
            "role": role,
            "core_desire": core_desire,
            "arc_current_state": arc_current_state
        }
        result = self._request("POST", "characters", data=data)
        return str(result.get("id", "0")) if isinstance(result, dict) else "0"

    def update_character(self, character_id: int, core_desire: str = None, arc_current_state: str = None) -> bool:
        data = {}
        if core_desire is not None:
            data["core_desire"] = core_desire
        if arc_current_state is not None:
            data["arc_current_state"] = arc_current_state
        if not data:
            return True
        data["updated_at"] = datetime.now().isoformat()
        self._request("PATCH", "characters", data=data, filters={"id": character_id})
        return True

    def get_research_nodes(self, project_id: str) -> List[Dict]:
        result = self._request("GET", "research_nodes", filters={"project_id": project_id})
        return result if isinstance(result, list) else []

    def add_research_node(self, project_id: str, topic: str, summary: str, queries_used: str = "[]", sources: str = "[]", confidence: str = "medium") -> str:
        data = {
            "project_id": project_id,
            "topic": topic,
            "summary": summary,
            "queries_used": queries_used,
            "sources": sources,
            "confidence": confidence
        }
        result = self._request("POST", "research_nodes", data=data)
        return str(result.get("id", "0")) if isinstance(result, dict) else "0"

    def get_lookahead_cards(self, project_id: str) -> List[Dict]:
        result = self._request("GET", "lookahead_cards", filters={"project_id": project_id})
        if isinstance(result, list):
            return sorted(result, key=lambda x: x.get("card_index", 0))
        return []

    def add_lookahead_card(self, project_id: str, card_index: int, chapter_number: int, title: str, scene_intention: str, opening_image: str, character_focus: str, tension_targeted: str) -> str:
        data = {
            "project_id": project_id,
            "card_index": card_index,
            "chapter_number": chapter_number,
            "title": title,
            "scene_intention": scene_intention,
            "opening_image": opening_image,
            "character_focus": character_focus,
            "tension_targeted": tension_targeted
        }
        # Supabase upsert equivalent
        result = self._request("POST", "lookahead_cards", data=data)
        return str(result.get("id", "0")) if isinstance(result, dict) else "0"

    def get_comments(self, chapter_id: str) -> List[Dict]:
        result = self._request("GET", "comments", filters={"chapter_id": chapter_id})
        return result if isinstance(result, list) else []

    def add_comment(self, chapter_id: str, anchor_start: int, anchor_end: int, anchor_text: str, comment_text: str) -> str:
        data = {
            "chapter_id": chapter_id,
            "anchor_start": anchor_start,
            "anchor_end": anchor_end,
            "anchor_text": anchor_text,
            "comment_text": comment_text
        }
        result = self._request("POST", "comments", data=data)
        return str(result.get("id", "0")) if isinstance(result, dict) else "0"

    def update_comment(self, comment_id: int, ai_response: str = None, revised_text: str = None, status: str = None) -> bool:
        data = {}
        if ai_response is not None:
            data["ai_response"] = ai_response
        if revised_text is not None:
            data["revised_text"] = revised_text
        if status is not None:
            data["status"] = status
        if not data:
            return True
        data["updated_at"] = datetime.now().isoformat()
        self._request("PATCH", "comments", data=data, filters={"id": comment_id})
        return True


def create_supabase_db(connection_string: str = None) -> SupabaseDB:
    """Create Supabase database instance"""
    return SupabaseDB(connection_string=connection_string or os.environ.get("POSTGRES_CONNECTION_STRING"))
