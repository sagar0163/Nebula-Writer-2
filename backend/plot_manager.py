"""
Nebula-Writer Plot & Continuity Manager
Track plot threads, foreshadowing, and world rules
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class PlotManager:
    """Manage plot threads, foreshadowing, and world consistency"""

    def __init__(self, db_path: str = "data/codex.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize plot tracking tables"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Plot Threads Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plot_threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'open',
                planted_chapter INTEGER,
                resolved_chapter INTEGER,
                importance TEXT DEFAULT 'normal',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Foreshadowing Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS foreshadowing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plot_thread_id INTEGER,
                chapter_id INTEGER,
                content TEXT NOT NULL,
                hint_level TEXT DEFAULT 'subtle',
                payoff_expected_chapter INTEGER,
                fulfilled INTEGER DEFAULT 0,
                fulfilled_chapter INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (plot_thread_id) REFERENCES plot_threads(id) ON DELETE SET NULL
            )
        """)

        # World Rules Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS world_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                rule TEXT NOT NULL,
                description TEXT,
                exceptions TEXT,
                applies_to_entities TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Character Voice Profiles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL UNIQUE,
                vocabulary_level TEXT DEFAULT 'average',
                speech_patterns TEXT,
                common_phrases TEXT,
                emotional_register TEXT DEFAULT 'neutral',
                formal_level TEXT DEFAULT 'neutral',
                dialect TEXT,
                quirks TEXT,
                sample_dialogue TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            )
        """)

        # Research Citations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_citations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                fact TEXT NOT NULL,
                source TEXT,
                source_url TEXT,
                linked_entity_id INTEGER,
                linked_location TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (linked_entity_id) REFERENCES entities(id) ON DELETE SET NULL
            )
        """)

        conn.commit()
        conn.close()
        print("[OK] Plot manager initialized")

    # ============ PLOT THREADS ============

    def add_plot_thread(
        self, title: str, description: str = None, planted_chapter: int = None, importance: str = "normal"
    ) -> int:
        """Add a new plot thread"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO plot_threads (title, description, planted_chapter, importance, status)
            VALUES (?, ?, ?, ?, 'planted')
        """,
            (title, description, planted_chapter, importance),
        )
        thread_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return thread_id

    def get_plot_threads(self, status: str = None) -> List[Dict]:
        """Get plot threads, optionally filtered by status"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute(
                """
                SELECT * FROM plot_threads WHERE status = ? ORDER BY importance DESC, created_at DESC
            """,
                (status,),
            )
        else:
            cursor.execute("""
                SELECT * FROM plot_threads ORDER BY importance DESC, created_at DESC
            """)

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def resolve_plot_thread(self, thread_id: int, resolved_chapter: int = None) -> bool:
        """Mark a plot thread as resolved"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE plot_threads
            SET status = 'resolved', resolved_chapter = ?
            WHERE id = ?
        """,
            (resolved_chapter, thread_id),
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def update_plot_thread_status(self, thread_id: int, status: str) -> bool:
        """Update plot thread status"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE plot_threads SET status = ? WHERE id = ?
        """,
            (status, thread_id),
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # ============ FORESHADOWING ============

    def add_foreshadowing(
        self, plot_thread_id: int, chapter_id: int, content: str, hint_level: str = "subtle", payoff_chapter: int = None
    ) -> int:
        """Add foreshadowing for a plot thread"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO foreshadowing (plot_thread_id, chapter_id, content, hint_level, payoff_expected_chapter)
            VALUES (?, ?, ?, ?, ?)
        """,
            (plot_thread_id, chapter_id, content, hint_level, payoff_chapter),
        )
        foreshadow_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return foreshadow_id

    def get_foreshadowing(self, plot_thread_id: int = None, unfulfilled_only: bool = True) -> List[Dict]:
        """Get foreshadowing elements"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if plot_thread_id:
            if unfulfilled_only:
                cursor.execute(
                    """
                    SELECT * FROM foreshadowing
                    WHERE plot_thread_id = ? AND fulfilled = 0
                    ORDER BY chapter_id
                """,
                    (plot_thread_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM foreshadowing
                    WHERE plot_thread_id = ?
                    ORDER BY chapter_id
                """,
                    (plot_thread_id,),
                )
        else:
            if unfulfilled_only:
                cursor.execute("""
                    SELECT * FROM foreshadowing
                    WHERE fulfilled = 0
                    ORDER BY chapter_id
                """)
            else:
                cursor.execute("SELECT * FROM foreshadowing ORDER BY chapter_id")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def fulfill_foreshadowing(self, foreshadow_id: int, fulfilled_chapter: int) -> bool:
        """Mark foreshadowing as fulfilled"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE foreshadowing
            SET fulfilled = 1, fulfilled_chapter = ?
            WHERE id = ?
        """,
            (fulfilled_chapter, foreshadow_id),
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # ============ WORLD RULES ============

    def add_world_rule(
        self, category: str, rule: str, description: str = None, exceptions: str = None, applies_to: str = None
    ) -> int:
        """Add a world rule"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO world_rules (category, rule, description, exceptions, applies_to_entities)
            VALUES (?, ?, ?, ?, ?)
        """,
            (category, rule, description, exceptions, applies_to),
        )
        rule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return rule_id

    def get_world_rules(self, category: str = None) -> List[Dict]:
        """Get world rules"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if category:
            cursor.execute(
                """
                SELECT * FROM world_rules WHERE category = ?
            """,
                (category,),
            )
        else:
            cursor.execute("SELECT * FROM world_rules ORDER BY category")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def check_world_rule_violation(self, text: str) -> List[Dict]:
        """Check text for world rule violations"""
        rules = self.get_world_rules()
        violations = []

        text_lower = text.lower()

        for rule in rules:
            # Simple violation check - should be enhanced with NLP
            if rule["rule"].lower() in text_lower:
                # Check if there's an exception
                exceptions = rule.get("exceptions", "")
                if exceptions and exceptions.lower() in text_lower:
                    continue  # Exception applies
                violations.append(
                    {
                        "rule_id": rule["id"],
                        "rule": rule["rule"],
                        "category": rule["category"],
                        "description": rule.get("description", ""),
                    }
                )

        return violations

    # ============ VOICE PROFILES ============

    def set_voice_profile(
        self,
        entity_id: int,
        vocabulary_level: str = "average",
        speech_patterns: str = None,
        common_phrases: str = None,
        emotional_register: str = "neutral",
        formal_level: str = "neutral",
        dialect: str = None,
        quirks: str = None,
        sample_dialogue: str = None,
    ) -> int:
        """Set or update character voice profile"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check if exists
        cursor.execute("SELECT id FROM voice_profiles WHERE entity_id = ?", (entity_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE voice_profiles
                SET vocabulary_level = ?, speech_patterns = ?, common_phrases = ?,
                    emotional_register = ?, formal_level = ?, dialect = ?, quirks = ?,
                    sample_dialogue = ?, updated_at = ?
                WHERE entity_id = ?
            """,
                (
                    vocabulary_level,
                    speech_patterns,
                    common_phrases,
                    emotional_register,
                    formal_level,
                    dialect,
                    quirks,
                    sample_dialogue,
                    datetime.now().isoformat(),
                    entity_id,
                ),
            )
            conn.commit()
            conn.close()
            return existing[0]
        else:
            cursor.execute(
                """
                INSERT INTO voice_profiles (entity_id, vocabulary_level, speech_patterns, common_phrases,
                    emotional_register, formal_level, dialect, quirks, sample_dialogue)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entity_id,
                    vocabulary_level,
                    speech_patterns,
                    common_phrases,
                    emotional_register,
                    formal_level,
                    dialect,
                    quirks,
                    sample_dialogue,
                ),
            )
            profile_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return profile_id

    def get_voice_profile(self, entity_id: int) -> Optional[Dict]:
        """Get character voice profile"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM voice_profiles WHERE entity_id = ?", (entity_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def generate_voice_prompt(self, entity_id: int) -> str:
        """Generate a prompt snippet for character voice"""
        profile = self.get_voice_profile(entity_id)
        if not profile:
            return ""

        parts = []

        # Vocabulary
        vocab = profile.get("vocabulary_level", "average")
        if vocab != "average":
            parts.append(f"vocabulary: {vocab}")

        # Formality
        formal = profile.get("formal_level", "neutral")
        if formal != "neutral":
            parts.append(f"formality: {formal}")

        # Speech patterns
        patterns = profile.get("speech_patterns", "")
        if patterns:
            parts.append(f"speech patterns: {patterns}")

        # Common phrases
        phrases = profile.get("common_phrases", "")
        if phrases:
            parts.append(f"common phrases: {phrases}")

        # Quirks
        quirks = profile.get("quirks", "")
        if quirks:
            parts.append(f"quirks: {quirks}")

        # Sample dialogue
        sample = profile.get("sample_dialogue", "")
        if sample:
            parts.append(f'example dialogue: "{sample}"')

        return "; ".join(parts)

    # ============ RESEARCH CITATIONS ============

    def add_citation(
        self,
        topic: str,
        fact: str,
        source: str = None,
        source_url: str = None,
        linked_entity_id: int = None,
        linked_location: str = None,
    ) -> int:
        """Add a research citation"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO research_citations (topic, fact, source, source_url, linked_entity_id, linked_location)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (topic, fact, source, source_url, linked_entity_id, linked_location),
        )
        citation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return citation_id

    def get_citations(self, topic: str = None, entity_id: int = None) -> List[Dict]:
        """Get research citations"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if topic:
            cursor.execute(
                """
                SELECT * FROM research_citations WHERE topic LIKE ?
            """,
                (f"%{topic}%",),
            )
        elif entity_id:
            cursor.execute(
                """
                SELECT * FROM research_citations WHERE linked_entity_id = ?
            """,
                (entity_id,),
            )
        else:
            cursor.execute("SELECT * FROM research_citations ORDER BY created_at DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ============ CONTINUITY CHECK ============

    def check_continuity(self, chapter_id: int, chapter_text: str, entities: List[Dict], events: List[Dict]) -> Dict:
        """Run continuity check on a chapter"""
        issues = {"chapter_id": chapter_id, "checked_at": datetime.now().isoformat(), "issues": []}

        # Check world rules
        rule_violations = self.check_world_rule_violation(chapter_text)
        for v in rule_violations:
            issues["issues"].append(
                {
                    "type": "world_rule_violation",
                    "severity": "high",
                    "description": f"Possible violation of rule: {v['rule']}",
                    "details": v,
                }
            )

        # Check for unresolved foreshadowing
        foreshadowing = self.get_foreshadowing(unfulfilled_only=True)
        for f in foreshadowing:
            # Check if past expected payoff chapter
            expected = f.get("payoff_expected_chapter")
            if expected and chapter_id > expected and not f.get("fulfilled"):
                issues["issues"].append(
                    {
                        "type": "unfulfilled_foreshadowing",
                        "severity": "medium",
                        "description": f"Foreshadowing from Ch. {f['chapter_id']} not fulfilled by Ch. {chapter_id}",
                        "details": f,
                    }
                )

        # Check for open plot threads not advancing
        open_threads = self.get_plot_threads(status="open")
        if open_threads and len(open_threads) > 5:
            issues["issues"].append(
                {
                    "type": "too_many_open_threads",
                    "severity": "low",
                    "description": f" {len(open_threads)} open plot threads - consider resolving some",
                }
            )

        return issues

    # ============ STORY COMPASS (v2.1) ============

    def calculate_narrative_momentum(
        self, open_tensions_count: int, pacing_score: float, chapters_since_major_event: int
    ) -> float:
        """
        Calculate Narrative Momentum - BRD Section 4.1
        A measure of forward pull: how urgently does the story need something to happen?
        """
        # Base momentum from open tensions (more tensions = more momentum)
        tension_momentum = min(5.0, open_tensions_count * 0.5)

        # Pacing boost (low pacing score = high urgency for momentum)
        pacing_momentum = max(0.0, (10.0 - pacing_score) * 0.3)

        # Major event decay (longer since event = higher urgency)
        event_momentum = min(3.0, chapters_since_major_event * 0.7)

        total_momentum = tension_momentum + pacing_momentum + event_momentum

        return round(min(10.0, total_momentum), 1)


def create_plot_manager() -> PlotManager:
    """Create a default plot manager"""
    from pathlib import Path

    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    return PlotManager(str(data_dir / "codex.db"))


if __name__ == "__main__":
    print("Testing plot manager...")
    pm = create_plot_manager()

    # Add a plot thread
    thread_id = pm.add_plot_thread(
        "The Mystery of the Red Lantern",
        "Someone is sending red lanterns as warnings",
        planted_chapter=1,
        importance="central",
    )
    print(f"Created plot thread: {thread_id}")

    # Add foreshadowing
    f_id = pm.add_foreshadowing(
        thread_id, 2, "A strange red glow appeared in the window", hint_level="subtle", payoff_chapter=8
    )
    print(f"Added foreshadowing: {f_id}")

    # Get threads
    threads = pm.get_plot_threads()
    print(f"Plot threads: {len(threads)}")

    # Add world rule
    rule_id = pm.add_world_rule(
        "magic",
        "No magic in the mortal realm",
        description="Magic cannot be used in the human world",
        exceptions="ancient artifacts",
    )
    print(f"Added world rule: {rule_id}")

    print("\nPlot manager working!")
