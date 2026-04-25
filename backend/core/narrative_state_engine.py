from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class NarrativePhase(Enum):
    SETUP = "setup"
    ESCALATION = "escalation"
    CLIMAX = "climax"
    RESOLUTION = "resolution"

@dataclass
class NarrativeSnapshot:
    """A structured snapshot of the story's current state for the AI."""
    phase: NarrativePhase
    active_threads: List[Dict]
    unresolved_tensions: List[Dict]
    momentum_score: float
    current_chapter_summary: str
    key_entities: List[Dict]
    world_rules: List[Dict]

class NarrativeStateEngine:
    """
    Control Layer: View + Decision layer over the Codex.
    Derives state without storing new data.
    """
    
    def __init__(self, db, plot_manager):
        self.db = db
        self.pm = plot_manager
        
    def get_snapshot(self) -> NarrativeSnapshot:
        """Aggregate story state from various sources."""
        # 1. Determine Narrative Phase
        phase = self._compute_phase()
        
        # 2. Get prioritized threads and tensions
        threads = self.pm.get_plot_threads(status="open")
        tensions = self.db.get_open_tensions() if hasattr(self.db, 'get_open_tensions') else []
        
        # 3. Get momentum
        momentum = self.db.get_story_compass().get("momentum_score", 0.0) if hasattr(self.db, 'get_story_compass') else 0.0
        
        # 4. Get current context
        chapters = self.db.get_chapters()
        last_chapter = chapters[-1] if chapters else {}
        
        # 5. Get key entities (active in current phase)
        entities = self.db.get_entities()
        
        # 6. World rules
        rules = self.pm.get_world_rules()
        
        return NarrativeSnapshot(
            phase=phase,
            active_threads=threads[:5],  # Priority limit
            unresolved_tensions=tensions[:3],
            momentum_score=momentum,
            current_chapter_summary=last_chapter.get("summary", ""),
            key_entities=entities[:10],
            world_rules=rules
        )
        
    def _compute_phase(self) -> NarrativePhase:
        """Derive the current narrative phase based on word count and chapter number."""
        stats = self.db.get_stats()
        total_chapters = stats.get("total_chapters", 0)
        
        if total_chapters <= 3:
            return NarrativePhase.SETUP
        elif total_chapters >= 15:
            return NarrativePhase.CLIMAX
        else:
            return NarrativePhase.ESCALATION

    def get_character_arc_progression(self, entity_id: int) -> Dict:
        """Derives arc progression by analyzing event significance in the Codex."""
        events = self.db.get_events()
        # Logic to filter events related to entity_id and determine growth
        entity_events = [e for e in events if str(entity_id) in str(e.get("description", ""))]
        return {
            "entity_id": entity_id,
            "events_count": len(entity_events),
            "status": "evolving" if entity_events else "static"
        }
