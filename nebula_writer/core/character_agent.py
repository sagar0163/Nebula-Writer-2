from typing import Dict, List


class CharacterAgent:
    """
    Wrapper over Codex entities.
    Derives psychological state and current intent for better prose generation.
    """

    def __init__(self, entity_id: int, db):
        self.db = db
        self.entity_id = entity_id
        self.entity = db.get_entity(entity_id)
        self.attributes = db.get_attributes(entity_id)

    def derive_persona(self) -> Dict:
        """Extracts goals, fears, and voice from attributes."""
        persona = {"name": self.entity.get("name"), "goals": [], "fears": [], "voice": "standard"}

        for attr in self.attributes:
            if attr["key"] == "goal":
                persona["goals"].append(attr["value"])
            elif attr["key"] == "fear":
                persona["fears"].append(attr["value"])
            elif attr["key"] == "voice":
                persona["voice"] = attr["value"]

        return persona

    def get_current_intent(self, recent_chapters: List[Dict]) -> str:
        """Determines what the character wants right now based on recent events."""
        # Simple heuristic: what was their last recorded event?
        self.db.get_events()
        # Find last event mentioning this character
        return "Unknown"

    def predict_actions(self, scene_context: str) -> Dict:
        """
        Decision Engine: Predicts how this character would react to a specific beat.
        Calculates resistance levels and conflict stances.
        """
        persona = self.derive_persona()
        
        # 1. Determine Emotional State
        emotional_state = "anxious" if persona.get("fears") else "neutral"
        
        # 2. Determine Conflict Stance & Resistance
        resistance = 0.7 if "goal" in scene_context.lower() else 0.3
        stance = "resistant" if resistance > 0.5 else "cooperative"
        
        # 3. Intended Action
        goals = persona.get("goals", [])
        intended_action = f"Protect {goals[0] if goals else 'self'}"
        
        return {
            "entity_id": self.entity_id,
            "name": persona.get("name", "Unknown"),
            "emotional_state": emotional_state,
            "conflict_stance": stance,
            "resistance_level": resistance,
            "intended_actions": [intended_action],
            "voice_directive": persona.get("voice", "Neutral")
        }

    def simulate_action(self, scenario: str) -> str:
        """Predicts how this character might respond to a specific event."""
        persona = self.derive_persona()
        return f"{persona['name']} would likely react based on fear: {persona['fears'][0] if persona['fears'] else 'unknown'}"
