from dataclasses import dataclass
from typing import List, Dict, Optional
import json

@dataclass
class LongTermPlan:
    target_ending: str
    major_milestones: List[str]
    thematic_focus: str
    arc_targets: Dict[str, str]

class NarrativePlanner:
    """
    Long-Term Planning Layer: Ensures early chapters align with end goals.
    Maintains the 'North Star' for the NarrativeDirector.
    """
    def __init__(self, db):
        self.db = db

    def get_plan(self) -> LongTermPlan:
        """Retrieve the current long-term plan from the database."""
        # We'll use the 'story_plan' table (to be added)
        try:
            plan_data = self.db.get_story_plan()
            if not plan_data:
                return self._create_default_plan()
            
            return LongTermPlan(
                target_ending=plan_data.get("target_ending", ""),
                major_milestones=json.loads(plan_data.get("major_milestones", "[]")),
                thematic_focus=plan_data.get("thematic_focus", ""),
                arc_targets=json.loads(plan_data.get("arc_targets", "{}"))
            )
        except Exception:
            return self._create_default_plan()

    def update_plan(self, plan: LongTermPlan):
        """Persist an updated plan."""
        self.db.update_story_plan({
            "target_ending": plan.target_ending,
            "major_milestones": json.dumps(plan.major_milestones),
            "thematic_focus": plan.thematic_focus,
            "arc_targets": json.dumps(plan.arc_targets)
        })

    def check_alignment(self, scene_outcome: str, plan: LongTermPlan) -> Dict:
        """
        Check if a proposed scene outcome aligns with long-term goals.
        """
        # Placeholder for semantic alignment check
        return {
            "aligned": True,
            "relevance": "high",
            "milestone_progress": "N/A"
        }

    def _create_default_plan(self) -> LongTermPlan:
        return LongTermPlan(
            target_ending="Undetermined",
            major_milestones=[],
            thematic_focus="General Narrative",
            arc_targets={}
        )
