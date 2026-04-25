from dataclasses import dataclass
from typing import Dict, List
from nebula_writer.core.narrative_intent_engine import NarrativeIntent


@dataclass
class GenerationConstraints:
    """
    Step 6: Structured input layer for the AIWriter.
    Combines intent, simulation, bias, and context.
    """

    intent: NarrativeIntent
    character_simulations: List[Dict]
    narrative_bias: str
    context_string: str
    active_anchors: List[str]

    def to_system_prompt(self) -> str:
        """Converts constraints into a high-density system prompt."""
        sims = "\n".join([
            f"- {s['name']}: {s['emotional_state']}, stance: {s['conflict_stance']}, actions: {', '.join(s['intended_actions'])}"
            for s in self.character_simulations
        ])
        
        anchors = "\n".join([f"- {a}" for a in self.active_anchors])
        
        return f"""
### NARRATIVE INTENT
Purpose: {self.intent.scene_purpose.value}
Pacing: {self.intent.pacing.value}
Focus: {self.intent.character_focus}

### CHARACTER SIMULATIONS
{sims}

### STYLE & BIAS
{self.narrative_bias}

### STORY ANCHORS (NON-NEGOTIABLE)
{anchors}

### RELEVANT CONTEXT
{self.context_string}
"""
