from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class FeedbackType(Enum):
    PACING = "pacing"
    TONE = "tone"
    CHARACTER_INCONSISTENCY = "character_inconsistency"
    PLOT_DIRECTION = "plot_direction"


@dataclass
class StyleProfile:
    pacing_bias: str = "balanced"
    tone_bias: str = "neutral"
    verbosity_bias: str = "medium"


class FeedbackEngine:
    """
    Learning System: Parses user feedback and updates narrative bias rules.
    Based on Step 5 of Phase 2.
    """

    def __init__(self, db):
        self.db = db
        self.profile = StyleProfile()

    def parse_feedback(self, feedback_text: str) -> Dict:
        """Classifies feedback and returns suggested bias updates."""
        feedback_text = feedback_text.lower()
        
        updates = {}
        if "too slow" in feedback_text or "faster" in feedback_text:
            updates["pacing_bias"] = "fast"
        elif "too fast" in feedback_text or "slower" in feedback_text:
            updates["pacing_bias"] = "slow"
            
        if "darker" in feedback_text or "grim" in feedback_text:
            updates["tone_bias"] = "dark"
        elif "lighter" in feedback_text or "funny" in feedback_text:
            updates["tone_bias"] = "light"

        self._apply_updates(updates)
        return updates

    def _apply_updates(self, updates: Dict):
        for key, value in updates.items():
            if hasattr(self.profile, key):
                setattr(self.profile, key, value)
        
        # In a real implementation, this would persist to the DB per project
        # self.db.update_style_profile(self.profile.__dict__)

    def get_narrative_bias(self) -> str:
        """Returns a string representation of the current narrative bias for prompting."""
        return f"Pacing: {self.profile.pacing_bias}, Tone: {self.profile.tone_bias}, Verbosity: {self.profile.verbosity_bias}"
