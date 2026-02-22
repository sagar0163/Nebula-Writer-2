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
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attributes_entity ON attributes(entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_entity_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chapters_number ON chapters(number)")
        
        conn.commit()
        conn.close()
        print(f"✅ Codex database initialized at {self.db_path}")
    
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
