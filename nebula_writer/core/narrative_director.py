from dataclasses import dataclass
from typing import List, Dict, Optional
from nebula_writer.core.narrative_state_engine import NarrativeSnapshot

@dataclass
class NarrativeDirective:
    """
    Enforced Narrative Plan for the next generation.
    Guides what MUST happen and what MUST NOT happen.
    """
    required_outcome: str
    tension_progression: str
    constraints: List[str]  # Forbidden actions/outcomes
    pacing_target: float    # 0.0 to 10.0
    narrative_priority: str # 'character', 'plot', 'world'
    active_anchors: List[str]

class NarrativeDirector:
    """
    Control Layer: Converts NarrativeSnapshot -> Enforced Narrative Plan.
    Ensures the story adheres to logical constraints and intended direction.
    """
    def __init__(self, db):
        self.db = db

    def derive_directive(self, snapshot: NarrativeSnapshot, long_term_plan: Optional[Dict] = None) -> NarrativeDirective:
        """
        Analyze current state and generate a strict directive for the AI.
        """
        # 1. Analyze unresolved tensions for the required outcome
        primary_tension = snapshot.unresolved_tensions[0] if snapshot.unresolved_tensions else {"description": "General development"}
        required_outcome = f"Address the tension: {primary_tension['description']}"

        # 2. Derive tension progression based on momentum
        tension_progression = "Escalate" if snapshot.momentum_score < 5.0 else "Resolution/Cool-down"
        
        # 3. Identify Constraints (Forbidden Actions)
        constraints = []
        for rule in snapshot.world_rules:
            if rule.get('critical'):
                constraints.append(f"DO NOT VIOLATE RULE: {rule['rule']}")
        
        for anchor in (snapshot.anchors or []):
            constraints.append(f"PRESERVE ANCHOR: {anchor['description']}")

        # 4. Define Pacing Target
        pacing = 7.0 if snapshot.phase.value == "climax" else 4.0
        
        # 5. Narrative Priority
        priority = "plot" if snapshot.active_threads else "character"

        return NarrativeDirective(
            required_outcome=required_outcome,
            tension_progression=tension_progression,
            constraints=constraints,
            pacing_target=pacing,
            narrative_priority=priority,
            active_anchors=[a['description'] for a in (snapshot.anchors or [])]
        )

    def validate_scene_plan(self, plan: str, directive: NarrativeDirective) -> bool:
        """
        Validate a proposed scene plan against the directive.
        """
        # Simple heuristic check: do forbidden constraints appear in the plan?
        # In a real implementation, this would use semantic analysis or LLM check.
        for constraint in directive.constraints:
            if "NOT" in constraint.upper() and constraint.split(":")[-1].strip().lower() in plan.lower():
                return False
        return True
