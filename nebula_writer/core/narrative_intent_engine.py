from dataclasses import dataclass
from enum import Enum
from typing import List

from nebula_writer.core.narrative_state_engine import NarrativePhase, NarrativeSnapshot


class ScenePurpose(Enum):
    INTRODUCE_CONFLICT = "introduce_conflict"
    ESCALATE = "escalate"
    RESOLVE = "resolve"
    REVEAL = "reveal"
    CHARACTER_BEAT = "character_beat"


class PacingDirective(Enum):
    SLOW = "slow"
    FAST = "fast"
    INTENSE = "intense"
    CONTEMPLATIVE = "contemplative"


@dataclass
class NarrativeIntent:
    """The decision layer's output: what the story NEEDS next."""

    scene_purpose: ScenePurpose
    tension_progression: str  # e.g., "rising", "peak", "plateau"
    pacing: PacingDirective
    character_focus: List[int]  # List of entity_ids
    thematic_focus: str
    constraints: List[str]


class NarrativeIntentEngine:
    """
    Decision Layer: Converts NarrativeSnapshot -> NarrativeIntent.
    Guided by narrative theory (e.g., three-act structure).
    """

    def __init__(self):
        pass

    def derive_intent(self, snapshot: NarrativeSnapshot) -> NarrativeIntent:
        """
        Analyze the snapshot and decide the direction of the next scene.
        """
        # 1. Determine Purpose based on phase and momentum
        purpose = self._decide_purpose(snapshot)

        # 2. Determine Pacing
        pacing = self._decide_pacing(snapshot)

        # 3. Prioritize characters
        focus = self._prioritize_characters(snapshot)

        return NarrativeIntent(
            scene_purpose=purpose,
            tension_progression="rising" if snapshot.momentum_score < 0.7 else "peak",
            pacing=pacing,
            character_focus=focus,
            thematic_focus="identity" if snapshot.phase == NarrativePhase.SETUP else "consequence",
            constraints=self._generate_constraints(snapshot, purpose),
        )

    def _decide_purpose(self, snapshot: NarrativeSnapshot) -> ScenePurpose:
        if snapshot.phase == NarrativePhase.SETUP:
            return ScenePurpose.INTRODUCE_CONFLICT
        if snapshot.phase == NarrativePhase.CLIMAX:
            return ScenePurpose.REVEAL

        # Mid-story escalation logic
        if snapshot.momentum_score < 0.5:
            return ScenePurpose.ESCALATE
        return ScenePurpose.CHARACTER_BEAT

    def _decide_pacing(self, snapshot: NarrativeSnapshot) -> PacingDirective:
        if snapshot.momentum_score > 0.8:
            return PacingDirective.FAST
        if snapshot.phase == NarrativePhase.RESOLUTION:
            return PacingDirective.CONTEMPLATIVE
        return PacingDirective.INTENSE if snapshot.phase == NarrativePhase.CLIMAX else PacingDirective.SLOW

    def _prioritize_characters(self, snapshot: NarrativeSnapshot) -> List[int]:
        # Return IDs of characters with highest activity or unresolved threads
        return [e["id"] for e in snapshot.key_entities[:2]]

    def _generate_constraints(self, snapshot: NarrativeSnapshot, purpose: ScenePurpose) -> List[str]:
        constraints = []
        if purpose == ScenePurpose.REVEAL:
            constraints.append("Must mention at least one hidden fact from Codex.")
        if snapshot.momentum_score < 0.3:
            constraints.append("Include a sudden shift in environment to increase stakes.")
        return constraints
