import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

class CodexDatabase:
    """The Codex - Core Data Engine for Nebula-Writer"""
    
    def __init__(self, db_path: str = "data/codex.db"):
        self.db_path = db_path
        self._init_db()
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Initialize all database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Entities Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('character', 'location', 'item')),
                description TEXT,
                is_alive INTEGER DEFAULT 1,
                current_location TEXT,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Attributes Table (with versioning)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attributes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)
        
        # Relationships Table (directed graph)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_entity_id INTEGER NOT NULL,
                to_entity_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL DEFAULT 0.5,
                description TEXT,
                FOREIGN KEY (from_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
                FOREIGN KEY (to_entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)
        
        # Events Table (plot points)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                chapter INTEGER,
                scene TEXT,
                significance TEXT DEFAULT 'normal',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Chapters Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER NOT NULL UNIQUE,
                title TEXT,
                content TEXT,
                summary TEXT,
                word_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Scenes Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER NOT NULL,
                number INTEGER NOT NULL,
                beat TEXT,
                content TEXT,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
            )
        """)
        
        # Version History Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapter_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER NOT NULL,
                content TEXT,
                word_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
            )
        """)
        
        # Character Knowledge Tracking Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                chapter_id INTEGER NOT NULL,
                knowledge TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
            )
        """)
        
        # Story Templates Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                structure TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Consistency Issues Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consistency_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER,
                entity_id INTEGER,
                issue_type TEXT,
                description TEXT,
                severity TEXT DEFAULT 'medium',
                resolved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_entity ON attributes(entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapters_number ON chapters(number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapter_versions_chapter ON chapter_versions(chapter_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_knowledge_entity ON character_knowledge(entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_character_knowledge_chapter ON character_knowledge(chapter_id)")
        
        # Story Anchors (BRD v2.1 Section 4.1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_anchors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL CHECK(type IN ('beginning', 'midpoint', 'end')),
                description TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Open Tensions (BRD v2.1 Section 4.1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS open_tensions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'normal',
                status TEXT DEFAULT 'open' CHECK(status IN ('open', 'resolved')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_chapter INTEGER
            )
        """)
        
        # Story Compass / Narrative Momentum (BRD v2.1 Section 4.1)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS story_compass (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                momentum_score REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Lookahead Cards (BRD v2.1 Section 4.2)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lookahead_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_number INTEGER NOT NULL,
                title TEXT,
                scene_intention TEXT,
                opening_image TEXT,
                character_in_focus TEXT,
                story_question TEXT,
                status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'approved', 'discarded')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Conversations Table (v2.1 Persistence)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                messages JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Insert default story templates
        self._insert_default_templates()
        
        # Initialize default story compass if not exists
        self._init_story_compass()
        
        print(f"[OK] Codex database initialized at {self.db_path}")

    def _init_story_compass(self):
        """Ensure at least one story compass record exists"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM story_compass")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO story_compass (momentum_score) VALUES (0.0)")
            conn.commit()
        conn.close()
    
    def _insert_default_templates(self):
        """Insert default story structure templates"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        templates = {
            "three_act": {
                "name": "Three-Act Structure",
                "structure": json.dumps({
                    "acts": [
                        {"number": 1, "name": "Setup", "chapters": "1-3", "beats": ["Opening image", "Theme stated", "Set-up", "Catalyst"]},
                        {"number": 2, "name": "Confrontation", "chapters": "4-15", "beats": ["Debate", "Break into two", "B story", "Fun and games", "Midpoint", "Bad guys close in", "All is lost", "Dark night of the soul"]},
                        {"number": 3, "name": "Resolution", "chapters": "16-20", "beats": ["Final image", "Closure"]}
                    ]
                })
            },
            "heros_journey": {
                "name": "Hero's Journey",
                "structure": json.dumps({
                    "acts": [
                        {"name": "Act 1 - Departure", "beats": ["Ordinary world", "Call to adventure", "Refusal of call", "Meeting the mentor", "Crossing the threshold"]},
                        {"name": "Act 2 - Initiation", "beats": ["Tests, allies, enemies", "Ordeal", "Reward (seizing the sword)"]},
                        {"name": "Act 3 - Return", "beats": ["The road back", "Resurrection", "Return with elixir"]}
                    ]
                })
            },
            "save_the_cat": {
                "name": "Save the Cat",
                "structure": json.dumps({
                    "acts": [
                        {"name": "Act 1", "beats": ["Opening image", "Theme stated", "Set-up", "Catalyst", "Debate"]},
                        {"name": "Act 2A", "beats": ["Break into two", "B story", "Fun and games", "Midpoint"]},
                        {"name": "Act 2B", "beats": ["Bad guys close in", "All is lost", "Dark night of the soul"]},
                        {"name": "Act 3", "beats": ["Final image", "Finale"]}
                    ]
                })
            },
            "seven_point": {
                "name": "Seven-Point Plot",
                "structure": json.dumps({
                    "acts": [
                        {"name": "Hook", "beats": ["Opening hook", "Plot turn 1"]},
                        {"name": "Pinch 1", "beats": ["Pinch point 1", "Midpoint"]},
                        {"name": "Pinch 2", "beats": ["Pinch point 2", "Plot turn 2"]},
                        {"name": "Resolution", "beats": ["Resolution", "Final hook"]}
                    ]
                })
            },
            "snowflake": {
                "name": "Snowflake Method",
                "structure": json.dumps({
                    "acts": [
                        {"step": 1, "name": "One Sentence", "description": "Write a one-sentence summary of your novel"},
                        {"step": 2, "name": "One Paragraph", "description": "Expand to a one-paragraph summary including setup, 3 disasters, ending"},
                        {"step": 3, "name": "Character Synopses", "description": "Create character synopses for each major character"},
                        {"step": 4, "name": "Four Pages", "description": "Expand each sentence of the paragraph into a paragraph"},
                        {"step": 5, "name": "Character Charts", "description": "Full character profiles with arcs"},
                        {"step": 6, "name": "Four-Page Outline", "description": "Expand to a four-page synopsis"},
                        {"step": 7, "name": "Full Draft", "description": "Write your complete novel"}
                    ]
                })
            }
        }
        
        for key, template in templates.items():
            cursor.execute("""
                INSERT OR IGNORE INTO story_templates (name, structure) 
                VALUES (?, ?)
            """, (template["name"], template["structure"]))
        
        conn.commit()
        conn.close()
    
    # ============ ENTITY OPERATIONS ============
    
    def add_entity(self, name: str, entity_type: str, description: str = None, 
                   current_location: str = None, is_alive: bool = True, 
                   image_url: str = None) -> int:
        """Add a new entity to the Codex"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO entities (name, type, description, current_location, is_alive, image_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, entity_type, description, current_location, 1 if is_alive else 0, image_url))
        entity_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entity_id
    
    def get_entities(self, entity_type: str = None) -> List[Dict]:
        """Get all entities, optionally filtered by type"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if entity_type:
            cursor.execute("SELECT * FROM entities WHERE type = ? ORDER BY name", (entity_type,))
        else:
            cursor.execute("SELECT * FROM entities ORDER BY type, name")
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_entity(self, entity_id: int) -> Optional[Dict]:
        """Get a single entity by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_entity(self, entity_id: int, **kwargs) -> bool:
        """Update entity fields"""
        allowed = ['name', 'description', 'is_alive', 'current_location', 'image_url']
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return False
        
        updates['updated_at'] = datetime.now().isoformat()
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [entity_id]
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE entities SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def delete_entity(self, entity_id: int) -> bool:
        """Delete an entity"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    # ============ ATTRIBUTE OPERATIONS ============
    
    def add_attribute(self, entity_id: int, key: str, value: str) -> int:
        """Add an attribute to an entity"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attributes (entity_id, key, value)
            VALUES (?, ?, ?)
        """, (entity_id, key, value))
        attr_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return attr_id
    
    def get_attributes(self, entity_id: int) -> List[Dict]:
        """Get all attributes for an entity"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attributes WHERE entity_id = ? ORDER BY key", (entity_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_attribute(self, attr_id: int) -> bool:
        """Delete an attribute"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attributes WHERE id = ?", (attr_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    # ============ RELATIONSHIP OPERATIONS ============
    
    def add_relationship(self, from_id: int, to_id: int, rel_type: str, 
                         strength: float = 0.5, description: str = None) -> int:
        """Add a relationship between two entities"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO relationships (from_entity_id, to_entity_id, relationship_type, strength, description)
            VALUES (?, ?, ?, ?, ?)
        """, (from_id, to_id, rel_type, strength, description))
        rel_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return rel_id
    
    def get_relationships(self, entity_id: int = None) -> List[Dict]:
        """Get relationships, optionally filtered by entity"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if entity_id:
            cursor.execute("""
                SELECT r.*, 
                       e1.name as from_name, e1.type as from_type,
                       e2.name as to_name, e2.type as to_type
                FROM relationships r
                JOIN entities e1 ON r.from_entity_id = e1.id
                JOIN entities e2 ON r.to_entity_id = e2.id
                WHERE r.from_entity_id = ? OR r.to_entity_id = ?
                ORDER BY r.strength DESC
            """, (entity_id, entity_id))
        else:
            cursor.execute("""
                SELECT r.*, 
                       e1.name as from_name, e1.type as from_type,
                       e2.name as to_name, e2.type as to_type
                FROM relationships r
                JOIN entities e1 ON r.from_entity_id = e1.id
                JOIN entities e2 ON r.to_entity_id = e2.id
                ORDER BY r.strength DESC
            """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def delete_relationship(self, rel_id: int) -> bool:
        """Delete a relationship"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM relationships WHERE id = ?", (rel_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    # ============ EVENT OPERATIONS ============
    
    def add_event(self, title: str, description: str = None, chapter: int = None, 
                  scene: str = None, significance: str = 'normal') -> int:
        """Log a plot event"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events (title, description, chapter, scene, significance)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, chapter, scene, significance))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id
    
    def get_events(self, chapter: int = None) -> List[Dict]:
        """Get events, optionally filtered by chapter"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if chapter:
            cursor.execute("SELECT * FROM events WHERE chapter = ? ORDER BY timestamp", (chapter,))
        else:
            cursor.execute("SELECT * FROM events ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ============ CHAPTER OPERATIONS ============
    
    def add_chapter(self, number: int, title: str = None, content: str = "") -> int:
        """Add a new chapter"""
        conn = self._get_connection()
        cursor = conn.cursor()
        word_count = len(content.split()) if content else 0
        cursor.execute("""
            INSERT INTO chapters (number, title, content, word_count)
            VALUES (?, ?, ?, ?)
        """, (number, title, content, word_count))
        chapter_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return chapter_id
    
    def get_chapters(self) -> List[Dict]:
        """Get all chapters"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chapters ORDER BY number")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_chapter(self, chapter_id: int = None, number: int = None) -> Optional[Dict]:
        """Get a chapter by ID or number"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if chapter_id:
            cursor.execute("SELECT * FROM chapters WHERE id = ?", (chapter_id,))
        else:
            cursor.execute("SELECT * FROM chapters WHERE number = ?", (number,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_chapter(self, chapter_id: int, content: str = None, title: str = None, 
                       summary: str = None) -> bool:
        """Update chapter content"""
        updates = {}
        if content is not None:
            updates['content'] = content
            updates['word_count'] = len(content.split())
        if title is not None:
            updates['title'] = title
        if summary is not None:
            updates['summary'] = summary
        updates['updated_at'] = datetime.now().isoformat()
        
        if not updates:
            return False
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [chapter_id]
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE chapters SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def delete_chapter(self, chapter_id: int) -> bool:
        """Delete a chapter"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chapters WHERE id = ?", (chapter_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    # ============ SCENE OPERATIONS ============
    
    def add_scene(self, chapter_id: int, number: int, beat: str = None, content: str = "") -> int:
        """Add a scene to a chapter"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scenes (chapter_id, number, beat, content)
            VALUES (?, ?, ?, ?)
        """, (chapter_id, number, beat, content))
        scene_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return scene_id
    
    def get_scenes(self, chapter_id: int) -> List[Dict]:
        """Get all scenes for a chapter"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scenes WHERE chapter_id = ? ORDER BY number", (chapter_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ============ STATISTICS ============
    
    def get_stats(self) -> Dict:
        """Get overall statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT type, COUNT(*) as count FROM entities GROUP BY type")
        stats['entities_by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT COUNT(*) FROM entities")
        stats['total_entities'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chapters")
        stats['total_chapters'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(word_count) FROM chapters")
        stats['total_words'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM relationships")
        stats['total_relationships'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM events")
        stats['total_events'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    # ============ SEARCH ============
    
    def search(self, query: str) -> Dict:
        """Search across all entities, chapters, events"""
        conn = self._get_connection()
        cursor = conn.cursor()
        q = f"%{query}%"
        
        results = {
            'entities': [],
            'chapters': [],
            'events': []
        }
        
        # Search entities
        cursor.execute("""
            SELECT * FROM entities 
            WHERE name LIKE ? OR description LIKE ?
            LIMIT 10
        """, (q, q))
        results['entities'] = [dict(row) for row in cursor.fetchall()]
        
        # Search chapters
        cursor.execute("""
            SELECT * FROM chapters 
            WHERE title LIKE ? OR content LIKE ? OR summary LIKE ?
            LIMIT 10
        """, (q, q, q))
        results['chapters'] = [dict(row) for row in cursor.fetchall()]
        
        # Search events
        cursor.execute("""
            SELECT * FROM events 
            WHERE title LIKE ? OR description LIKE ?
            LIMIT 10
        """, (q, q))
        results['events'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    # ============ VERSION HISTORY ============
    
    def save_version(self, chapter_id: int, content: str) -> int:
        """Save a chapter version for history"""
        conn = self._get_connection()
        cursor = conn.cursor()
        word_count = len(content.split()) if content else 0
        cursor.execute("""
            INSERT INTO chapter_versions (chapter_id, content, word_count)
            VALUES (?, ?, ?)
        """, (chapter_id, content, word_count))
        version_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return version_id
    
    def get_versions(self, chapter_id: int) -> List[Dict]:
        """Get all versions of a chapter"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chapter_versions 
            WHERE chapter_id = ? 
            ORDER BY created_at DESC
        """, (chapter_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_version(self, version_id: int) -> Optional[Dict]:
        """Get a specific version"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chapter_versions WHERE id = ?", (version_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # ============ CHARACTER KNOWLEDGE ============
    
    def update_character_knowledge(self, entity_id: int, chapter_id: int, knowledge: str) -> int:
        """Update what a character knows at a specific chapter"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute("""
            SELECT id FROM character_knowledge 
            WHERE entity_id = ? AND chapter_id = ?
        """, (entity_id, chapter_id))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE character_knowledge SET knowledge = ? WHERE id = ?
            """, (knowledge, existing[0]))
            conn.commit()
            conn.close()
            return existing[0]
        else:
            cursor.execute("""
                INSERT INTO character_knowledge (entity_id, chapter_id, knowledge)
                VALUES (?, ?, ?)
            """, (entity_id, chapter_id, knowledge))
            knowledge_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return knowledge_id
    
    def get_character_knowledge(self, entity_id: int, chapter_id: int = None) -> List[Dict]:
        """Get what a character knows"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if chapter_id:
            cursor.execute("""
                SELECT * FROM character_knowledge 
                WHERE entity_id = ? AND chapter_id <= ?
                ORDER BY chapter_id DESC
            """, (entity_id, chapter_id))
        else:
            cursor.execute("""
                SELECT * FROM character_knowledge 
                WHERE entity_id = ?
                ORDER BY chapter_id DESC
            """, (entity_id,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    # ============ STORY TEMPLATES ============
    
    def get_templates(self) -> List[Dict]:
        """Get all story templates"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM story_templates ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def get_template(self, template_id: int) -> Optional[Dict]:
        """Get a specific template"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM story_templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    # ============ CONSISTENCY CHECKING ============
    
    def add_consistency_issue(self, chapter_id: int = None, entity_id: int = None, 
                          issue_type: str = "", description: str = "", severity: str = "medium") -> int:
        """Add a consistency issue"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO consistency_issues (chapter_id, entity_id, issue_type, description, severity)
            VALUES (?, ?, ?, ?, ?)
        """, (chapter_id, entity_id, issue_type, description, severity))
        issue_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return issue_id
    
    def get_consistency_issues(self, chapter_id: int = None, unresolved_only: bool = False) -> List[Dict]:
        """Get consistency issues"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if chapter_id:
            query = "SELECT * FROM consistency_issues WHERE chapter_id = ?"
            params = (chapter_id,)
        elif unresolved_only:
            query = "SELECT * FROM consistency_issues WHERE resolved = 0"
            params = ()
        else:
            query = "SELECT * FROM consistency_issues"
            params = ()
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def resolve_consistency_issue(self, issue_id: int) -> bool:
        """Mark a consistency issue as resolved"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE consistency_issues SET resolved = 1 WHERE id = ?", (issue_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def run_consistency_check(self) -> List[Dict]:
        """Run full consistency check across the story"""
        issues = []
        
        # Get all chapters in order
        chapters = self.get_chapters()
        
        # Get all entities
        entities = {e['id']: e for e in self.get_entities()}
        
        # Get all relationships
        relationships = self.get_relationships()
        
        # Check for orphan entities (referenced but never in scene)
        for entity in entities.values():
            found = False
            for chapter in chapters:
                if chapter.get('content') and entity['name'].lower() in chapter['content'].lower():
                    found = True
                    break
            if not found and len(chapters) > 0:
                issues.append({
                    'type': 'orphan_entity',
                    'severity': 'low',
                    'description': f"Entity '{entity['name']}' may not appear in any chapter"
                })
        
        # Check timeline consistency
        events = self.get_events()
        for i, event in enumerate(events):
            if event.get('chapter'):
                # Check if chapter exists
                chapter_exists = any(c['number'] == event['chapter'] for c in chapters)
                if not chapter_exists:
                    issues.append({
                        'type': 'timeline_gap',
                        'severity': 'medium',
                        'description': f"Event '{event['title']}' references non-existent Chapter {event['chapter']}"
                    })
        
        # Save issues to database
        for issue in issues:
            self.add_consistency_issue(
                chapter_id=None,
                entity_id=None,
                issue_type=issue['type'],
                description=issue['description'],
                severity=issue['severity']
            )
        
        return issues
    
    # ============ AUTO-EXTRACT ENTITIES ============
    
    def extract_entities_from_text(self, text: str) -> Dict:
        """Extract potential entities from prose text using pattern matching"""
        import re
        
        extracted = {'characters': [], 'locations': [], 'items': []}
        
        # Common patterns for names (capitalized words)
        potential_names = re.findall(r'\b([A-Z][a-z]+)\b', text)
        
        # Get existing entity names
        existing = {e['name'].lower(): e['type'] for e in self.get_entities()}
        
        # Filter potential new entities
        name_counts = {}
        for name in potential_names:
            name_lower = name.lower()
            if name_lower not in existing and name_lower not in name_counts:
                name_counts[name_lower] = 1
            elif name_lower in name_counts:
                name_counts[name_lower] += 1
        
        # Entities mentioned 2+ times are likely important
    # ============ STORY COMPASS & LOOKAHEAD (v2.1) ============
    
    def add_story_anchor(self, anchor_type: str, description: str) -> int:
        """Add a story anchor (beginning, midpoint, end)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO story_anchors (type, description)
            VALUES (?, ?)
        """, (anchor_type, description))
        anchor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return anchor_id
    
    def get_story_anchors(self) -> List[Dict]:
        """Get all story anchors"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM story_anchors")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_story_anchor(self, anchor_id: int, description: str) -> bool:
        """Update a story anchor"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE story_anchors 
            SET description = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (description, anchor_id))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def add_open_tension(self, description: str, priority: str = 'normal') -> int:
        """Add a new open tension"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO open_tensions (description, priority)
            VALUES (?, ?)
        """, (description, priority))
        tension_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return tension_id
    
    def get_open_tensions(self, status: str = 'open') -> List[Dict]:
        """Get open tensions"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM open_tensions WHERE status = ? ORDER BY created_at DESC", (status,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def resolve_tension(self, tension_id: int, resolved_chapter: int) -> bool:
        """Mark a tension as resolved"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE open_tensions 
            SET status = 'resolved', resolved_chapter = ? 
            WHERE id = ?
        """, (resolved_chapter, tension_id))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def update_narrative_momentum(self, score: float) -> bool:
        """Update the narrative momentum score"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute("SELECT id FROM story_compass LIMIT 1")
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE story_compass 
                SET momentum_score = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (score, existing[0]))
        else:
            cursor.execute("INSERT INTO story_compass (momentum_score) VALUES (?)", (score,))
            
        conn.commit()
        conn.close()
        return True
    
    def get_narrative_momentum(self) -> float:
        """Get the current narrative momentum score"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT momentum_score FROM story_compass ORDER BY last_updated DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0.0
    
    def add_lookahead_card(self, chapter_number: int, title: str = None, 
                           intention: str = None, opening: str = None, 
                           focus: str = None, question: str = None) -> int:
        """Add a lookahead card proposal"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lookahead_cards (
                chapter_number, title, scene_intention, 
                opening_image, character_in_focus, story_question
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (chapter_number, title, intention, opening, focus, question))
        card_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return card_id
    
    def get_lookahead_cards(self, status: str = 'draft') -> List[Dict]:
        """Get lookahead cards"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM lookahead_cards WHERE status = ? ORDER BY chapter_number", (status,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def update_lookahead_card_status(self, card_id: int, status: str) -> bool:
        """Update lookahead card status (approved, discarded)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE lookahead_cards SET status = ? WHERE id = ?", (status, card_id))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def clear_lookahead_cards(self, status: str = 'draft'):
        """Clear out lookahead cards"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM lookahead_cards WHERE status = ?", (status,))
        conn.commit()
        conn.close()
    
    # ============ AUTO-EXTRACT ENTITIES ============
    
    def extract_entities_from_text(self, text: str) -> Dict:
        """Extract potential entities from prose text using pattern matching"""
        import re
        
        extracted = {'characters': [], 'locations': [], 'items': []}
        
        # Common patterns for names (capitalized words)
        potential_names = re.findall(r'\b([A-Z][a-z]+)\b', text)
        
        # Get existing entity names
        existing = {e['name'].lower(): e['type'] for e in self.get_entities()}
        
        # Filter potential new entities
        name_counts = {}
        for name in potential_names:
            name_lower = name.lower()
            if name_lower not in existing and name_lower not in name_counts:
                name_counts[name_lower] = 1
            elif name_lower in name_counts:
                name_counts[name_lower] += 1
        
        # Entities mentioned 2+ times are likely important
        for name, count in name_counts.items():
            if count >= 2:
                # Try to determine type from context
                context = text.lower()
                words = name.split()
                for word in words:
                    if word in context:
                        # Simple heuristics
                        if any(loc in context for loc in ['city', 'street', 'house', 'room', 'building', 'town', 'village']):
                            extracted['locations'].append({'name': name.title(), 'confidence': 'low'})
                            break
                        elif any(item in context for item in ['weapon', 'key', 'book', 'phone', 'car']):
                            extracted['items'].append({'name': name.title(), 'confidence': 'low'})
                            break
                
                if name.title() not in [e['name'] for e in extracted['characters']]:
                    extracted['characters'].append({'name': name.title(), 'confidence': 'medium'})
        
        return extracted

    # ============ CONVERSATION PERSISTENCE ============

    def save_conversation(self, messages: List[Dict], user_id: str = "default") -> int:
        """Save conversation history to database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if a conversation exists for this user
        cursor.execute("SELECT id FROM conversations WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        messages_json = json.dumps(messages)
        now = datetime.now().isoformat()
        
        if row:
            conversation_id = row[0]
            cursor.execute("""
                UPDATE conversations 
                SET messages = ?, updated_at = ? 
                WHERE id = ?
            """, (messages_json, now, conversation_id))
        else:
            cursor.execute("""
                INSERT INTO conversations (user_id, messages, updated_at) 
                VALUES (?, ?, ?)
            """, (user_id, messages_json, now))
            conversation_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return conversation_id

    def load_conversation(self, user_id: str = "default") -> List[Dict]:
        """Load conversation history from database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT messages FROM conversations WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return []


if __name__ == "__main__":
    # Test the database
    db = CodexDatabase()
    
    # Add test data
    ravi_id = db.add_entity("Ravi", "character", "Protagonist - a detective from Mumbai")
    db.add_attribute(ravi_id, "age", "32")
    db.add_attribute(ravi_id, "occupation", "Detective")
    
    priya_id = db.add_entity("Priya", "character", "Ravi's partner and love interest")
    db.add_attribute(priya_id, "age", "28")
    db.add_attribute(priya_id, "occupation", "Journalist")
    
    db.add_relationship(ravi_id, priya_id, "loves", 0.9, "Deep romantic connection")
    db.add_relationship(ravi_id, priya_id, "works_with", 0.8)
    
    mumbai_id = db.add_entity("Mumbai", "location", "The bustling city where the story takes place")
    db.add_relationship(ravi_id, mumbai_id, "lives_in")
    
    db.add_chapter(1, "The Beginning", "It was a dark and stormy night in Mumbai...")
    db.add_event("Ravi and Priya meet", "They meet at a crime scene", 1, "Scene 1", "major")
    
    print("\n📊 Statistics:", db.get_stats())
    print("\n🔍 Relationships:", db.get_relationships())
    print("\n📖 Chapters:", db.get_chapters())
