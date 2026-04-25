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

    def simulate_behavior(self, scene_context: str) -> Dict:
        """
        Active Simulation (Step 3): Predicts character actions and internal state.
        Output guides the prompt constraints for generation.
        """
        persona = self.derive_persona()
        
        # 1. Determine Emotional State
        # In a real implementation, this would use a small LLM call or complex logic
        emotional_state = "anxious" if persona["fears"] else "neutral"
        
        # 2. Determine Conflict Stance
        # Is the character likely to push back or concede?
        stance = "resistant" if "goal" in scene_context.lower() else "cooperative"
        
        # 3. Intended Action
        intended_action = f"Protect {persona['goals'][0] if persona['goals'] else 'self'}"
        
        return {
            "name": persona["name"],
            "emotional_state": emotional_state,
            "conflict_stance": stance,
            "intended_actions": [intended_action],
            "voice_directive": persona["voice"]
        }

    def simulate_action(self, scenario: str) -> str:
        """Predicts how this character might respond to a specific event."""
        persona = self.derive_persona()
        return f"{persona['name']} would likely react based on fear: {persona['fears'][0] if persona['fears'] else 'unknown'}"
