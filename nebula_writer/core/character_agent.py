"""Character Agent — LangChain-powered personality simulation.

Uses structured output (Pydantic) for deterministic, typed
character predictions instead of ad-hoc dicts.
"""

from __future__ import annotations

from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from nebula_writer.models import create_chat_model


class CharacterPersona(BaseModel):
    name: str
    goals: List[str] = Field(default_factory=list)
    fears: List[str] = Field(default_factory=list)
    voice: str = "standard"


class ActionPrediction(BaseModel):
    entity_id: str
    name: str
    emotional_state: str
    conflict_stance: str
    resistance_level: float
    intended_actions: List[str]
    voice_directive: str


PREDICTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a character psychology simulator. Predict how this character would react."),
    ("human", "Character: {persona}\nScene context: {scene_context}\nPredict their actions and emotional state."),
])


class CharacterAgent:
    """LangChain-powered character decision engine."""

    def __init__(self, entity_id: int, db):
        self.db = db
        self.entity_id = entity_id
        self.entity = db.get_entity(entity_id)
        self.attributes = db.get_attributes(entity_id)

    def derive_persona(self) -> CharacterPersona:
        goals: List[str] = []
        fears: List[str] = []
        voice: str = "standard"

        for attr in self.attributes:
            if attr["key"] == "goal":
                goals.append(attr["value"])
            elif attr["key"] == "fear":
                fears.append(attr["value"])
            elif attr["key"] == "voice":
                voice = attr["value"]

        return CharacterPersona(
            name=self.entity.get("name", "Unknown"),
            goals=goals,
            fears=fears,
            voice=voice,
        )

    def get_current_intent(self, recent_chapters: List[Dict]) -> str:
        return "Unknown"

    def predict_actions(self, scene_context: str) -> Dict[str, Any]:
        persona = self.derive_persona()

        emotional_state = "anxious" if persona.fears else "neutral"
        resistance = 0.7 if "goal" in scene_context.lower() else 0.3
        stance = "resistant" if resistance > 0.5 else "cooperative"
        intended_action = f"Protect {persona.goals[0] if persona.goals else 'self'}"

        return {
            "entity_id": str(self.entity_id),
            "name": persona.name,
            "emotional_state": emotional_state,
            "conflict_stance": stance,
            "resistance_level": resistance,
            "intended_actions": [intended_action],
            "voice_directive": persona.voice,
        }

    async def predict_actions_ai(self, scene_context: str) -> ActionPrediction:
        """AI-enhanced prediction using LangChain structured output."""
        persona = self.derive_persona()
        model = create_chat_model(temperature=0.3).with_structured_output(ActionPrediction)

        chain = PREDICTION_PROMPT | model
        result = await chain.ainvoke({
            "persona": persona.model_dump_json(),
            "scene_context": scene_context,
        })
        return result

    def simulate_action(self, scenario: str) -> str:
        persona = self.derive_persona()
        fear = persona.fears[0] if persona.fears else "unknown"
        return f"{persona.name} would likely react based on fear: {fear}"
