import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool


class PostgresDB:
    """PostgreSQL database interface matching CodexDatabase API"""

    def __init__(self, connection_string: str = None, password: str = None, min_conn: int = 1, max_conn: int = 5):
        # Build connection string
        if not connection_string:
            connection_string = os.environ.get("POSTGRES_CONNECTION_STRING")

        if not connection_string:
            raise ValueError("POSTGRES_CONNECTION_STRING environment variable is required")

        self.connection_string = connection_string
        self.pool = SimpleConnectionPool(min_conn, max_conn, connection_string, cursor_factory=RealDictCursor)
        print("[OK] Connected to Supabase PostgreSQL (pool)")

    def _get_conn(self):
        """Get a connection from the pool"""
        conn = self.pool.getconn()
        conn.autocommit = False
        return conn

    def _put_conn(self, conn):
        """Return a connection to the pool"""
        self.pool.putconn(conn)

    def _query(self, sql: str, params: tuple = None) -> List[Dict]:
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                if cursor.description:
                    return cursor.fetchall()
                conn.commit()
                return []
        except psycopg2.InterfaceError:
            # Connection lost, try to reconnect
            self.pool.putconn(conn, close=True)
            conn = self.pool.getconn()
            conn.autocommit = False
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                if cursor.description:
                    return cursor.fetchall()
                conn.commit()
                return []
        finally:
            self._put_conn(conn)

    def _execute(self, sql: str, params: tuple = None) -> str:
        conn = self._get_conn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return str(cursor.lastrowid) if cursor.lastrowid else "0"
        except psycopg2.InterfaceError:
            self.pool.putconn(conn, close=True)
            conn = self.pool.getconn()
            conn.autocommit = False
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return str(cursor.lastrowid) if cursor.lastrowid else "0"
        finally:
            self._put_conn(conn)

    def close(self):
        """Close all connections in the pool"""
        self.pool.closeall()

    # ============ ENTITY OPERATIONS ============

    def get_entities(self, entity_type: str = None) -> List[Dict]:
        if entity_type:
            return self._query("SELECT * FROM entities WHERE type = %s ORDER BY name", (entity_type,))
        return self._query("SELECT * FROM entities")

    def get_entity(self, entity_id: str) -> Optional[Dict]:
        result = self._query("SELECT * FROM entities WHERE id = %s", (entity_id,))
        return dict(result[0]) if result else None

    def add_entity(
            self,
            name: str,
            type: str,
            description: str = None,
            current_location: str = None,
            is_alive: bool = True,
            image_url: str = None,
        ) -> str:
            return self._execute(
                """
                INSERT INTO entities (name, type, description, current_location, is_alive, image_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (name, type, description, current_location, is_alive, image_url),
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

    # ============ VISION GAP PLAN ENTITIES ============

    def get_projects(self) -> List[Dict]:
        return self._query("SELECT * FROM projects")

    def get_project(self, project_id: str) -> Optional[Dict]:
        result = self._query("SELECT * FROM projects WHERE id = %s", (project_id,))
        return dict(result[0]) if result else None

    def add_project(self, project_id: str, title: str = "Untitled Novel", author: str = "Unknown") -> str:
        return self._execute(
            "INSERT INTO projects (id, title, author) VALUES (%s, %s, %s)",
            (project_id, title, author)
        )

    def get_characters(self, project_id: str) -> List[Dict]:
        return self._query("SELECT * FROM characters WHERE project_id = %s", (project_id,))

    def add_character(self, project_id: str, name: str, role: str = "major", core_desire: str = "", arc_current_state: str = "") -> str:
        return self._execute(
            """
            INSERT INTO characters (project_id, name, role, core_desire, arc_current_state)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (project_id, name, role, core_desire, arc_current_state)
        )

    def update_character(self, character_id: int, core_desire: str = None, arc_current_state: str = None) -> bool:
        updates = []
        params = []
        if core_desire is not None:
            updates.append("core_desire = %s")
            params.append(core_desire)
        if arc_current_state is not None:
            updates.append("arc_current_state = %s")
            params.append(arc_current_state)
        if not updates:
            return True
        updates.append("updated_at = %s")
        params.append(datetime.now().isoformat())
        params.append(character_id)
        self._query(f"UPDATE characters SET {', '.join(updates)} WHERE id = %s", tuple(params))
        return True

    def get_research_nodes(self, project_id: str) -> List[Dict]:
        return self._query("SELECT * FROM research_nodes WHERE project_id = %s", (project_id,))

    def add_research_node(self, project_id: str, topic: str, summary: str, queries_used: str = "[]", sources: str = "[]", confidence: str = "medium") -> str:
        return self._execute(
            """
            INSERT INTO research_nodes (project_id, topic, summary, queries_used, sources, confidence)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (project_id, topic, summary, queries_used, sources, confidence)
        )

    def get_lookahead_cards(self, project_id: str) -> List[Dict]:
        return self._query("SELECT * FROM lookahead_cards WHERE project_id = %s ORDER BY card_index", (project_id,))

    def add_lookahead_card(self, project_id: str, card_index: int, chapter_number: int, title: str, scene_intention: str, opening_image: str, character_focus: str, tension_targeted: str) -> str:
        return self._execute(
            """
            INSERT INTO lookahead_cards (project_id, card_index, chapter_number, title, scene_intention, opening_image, character_focus, tension_targeted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (project_id, card_index) DO UPDATE SET
                chapter_number = EXCLUDED.chapter_number,
                title = EXCLUDED.title,
                scene_intention = EXCLUDED.scene_intention,
                opening_image = EXCLUDED.opening_image,
                character_focus = EXCLUDED.character_focus,
                tension_targeted = EXCLUDED.tension_targeted
            """,
            (project_id, card_index, chapter_number, title, scene_intention, opening_image, character_focus, tension_targeted)
        )

    def get_comments(self, chapter_id: str) -> List[Dict]:
        return self._query("SELECT * FROM comments WHERE chapter_id = %s", (chapter_id,))

    def add_comment(self, chapter_id: str, anchor_start: int, anchor_end: int, anchor_text: str, comment_text: str) -> str:
        return self._execute(
            """
            INSERT INTO comments (chapter_id, anchor_start, anchor_end, anchor_text, comment_text)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (chapter_id, anchor_start, anchor_end, anchor_text, comment_text)
        )

    def update_comment(self, comment_id: int, ai_response: str = None, revised_text: str = None, status: str = None) -> bool:
        updates = []
        params = []
        if ai_response is not None:
            updates.append("ai_response = %s")
            params.append(ai_response)
        if revised_text is not None:
            updates.append("revised_text = %s")
            params.append(revised_text)
        if status is not None:
            updates.append("status = %s")
            params.append(status)
        if not updates:
            return True
        updates.append("updated_at = %s")
        params.append(datetime.now().isoformat())
        params.append(comment_id)
        self._query(f"UPDATE comments SET {', '.join(updates)} WHERE id = %s", tuple(params))
        return True

    def close(self):
        if self.conn:
            self.conn.close()

    # ============ CONVERSATION PERSISTENCE ============

    def _ensure_conversations_table(self):
        """Create conversations table if it doesn't exist"""
        self._query("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                messages JSONB NOT NULL DEFAULT '[]',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        # Create index on user_id
        self._query("""
            CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
            ON conversations(user_id)
        """)

    def save_conversation(self, messages: List[Dict], user_id: str = "default") -> int:
        """Save conversation history to database"""
        self._ensure_conversations_table()
        
        messages_json = json.dumps(messages)
        now = datetime.now().isoformat()
        
        # Check if conversation exists
        existing = self._query(
            "SELECT id FROM conversations WHERE user_id = %s", (user_id,)
        )
        
        if existing:
            conversation_id = existing[0]['id']
            self._query(
                "UPDATE conversations SET messages = %s, updated_at = %s WHERE id = %s",
                (messages_json, now, conversation_id)
            )
        else:
            result = self._query(
                "INSERT INTO conversations (user_id, messages, updated_at) VALUES (%s, %s, %s) RETURNING id",
                (user_id, messages_json, now)
            )
            conversation_id = result[0]['id'] if result else 0
        
        return conversation_id

    def load_conversation(self, user_id: str = "default") -> List[Dict]:
        """Load conversation history from database"""
        self._ensure_conversations_table()
        
        result = self._query(
            "SELECT messages FROM conversations WHERE user_id = %s ORDER BY updated_at DESC LIMIT 1",
            (user_id,)
        )
        
        if result and result[0]['messages']:
            return result[0]['messages']
        return []

    def close(self):
        if self.conn:
            self.conn.close()
